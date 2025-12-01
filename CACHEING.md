# Caching, Ingestion

Looking at your code, you've got a solid foundation. Here are my suggestions for optimizing toward fast ingestion and building that moat:

## Critical Gaps for Fast Ingestion

**1. No caching layer yet**

You have embedding generation, but no Redis/DynamoDB caching. This is the biggest cost/speed multiplier. Add:

```python
# src/ingestion/embedding_cache.py
import redis
import hashlib
import json

class EmbeddingCache:
    def __init__(self, redis_url='redis://localhost:6379'):
        self.redis = redis.from_url(redis_url)
    
    def get(self, text: str, model: str = 'titan_v2') -> Optional[List[float]]:
        key = f"emb:{model}:{hashlib.md5(text.encode()).hexdigest()}"
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    def set(self, text: str, embedding: List[float], model: str = 'titan_v2'):
        key = f"emb:{model}:{hashlib.md5(text.encode()).hexdigest()}"
        self.redis.setex(key, 86400*30, json.dumps(embedding))  # 30 day TTL
```

Then modify `EmbeddingGenerator.embed_text()` to check cache first.

**2. No S3 intermediate storage**

Your pipeline writes directly to OpenSearch. For fast parallel ingestion, you want:

```python
# src/ingestion/s3_writer.py
import boto3
import json

class S3PaperWriter:
    def __init__(self, bucket='med-graph-corpus'):
        self.s3 = boto3.client('s3')
        self.bucket = bucket
    
    def write_paper(self, paper: ProcessedPaper):
        """Write processed paper to S3 for later bulk import"""
        key = f"processed-papers/{paper.pmc_id}.json"
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=paper.model_dump_json()
        )
```

**3. No parallelization strategy**

Add a Lambda/Ray wrapper:

```python
# src/ingestion/parallel_processor.py
def process_single_paper_lambda(event, context):
    """AWS Lambda handler for processing one paper"""
    pmc_id = event['pmc_id']
    
    # Download XML from PMC
    xml = download_from_pmc(pmc_id)
    
    # Parse
    parser = JATSParser(xml)
    paper = parser.parse()
    
    # Process (with caching)
    pipeline = PaperIndexingPipeline()
    processed = pipeline.process_paper(paper)
    
    # Write to S3 (not OpenSearch yet)
    writer = S3PaperWriter()
    writer.write_paper(processed)
    
    return {'status': 'success', 'pmc_id': pmc_id}
```

## Schema Issues

**Your `EntityCollection` is good, but missing the entity linking logic:**

```python
# Add to EntityCollection
def find_by_embedding(self, query_embedding: List[float], 
                     top_k: int = 5,
                     threshold: float = 0.85) -> List[Tuple[BaseMedicalEntity, float]]:
    """
    Find entities similar to query embedding.
    Returns list of (entity, similarity_score) tuples.
    """
    from numpy import dot
    from numpy.linalg import norm
    
    results = []
    
    for collection in [self.diseases, self.genes, self.drugs, self.proteins]:
        for entity in collection.values():
            if entity.embedding_titan_v2 is None:
                continue
            
            # Cosine similarity
            similarity = dot(query_embedding, entity.embedding_titan_v2) / \
                        (norm(query_embedding) * norm(entity.embedding_titan_v2))
            
            if similarity >= threshold:
                results.append((entity, similarity))
    
    # Sort by similarity
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]
```

## What's Missing for Production

**1. Entity extraction (NER) - you have the schema but not the implementation:**

```python
# src/ingestion/entity_extractor.py
class EntityExtractor:
    def __init__(self, entity_collection: EntityCollection, cache: EmbeddingCache):
        self.entities = entity_collection
        self.cache = cache
        self.embedder = EmbeddingGenerator()
    
    def extract_entities(self, text: str, chunk_id: str) -> List[ExtractedEntity]:
        """
        Simple NER: split on medical terms, embed, link to reference entities.
        V1: Just do noun phrase extraction + entity linking.
        V2: Add scispacy/biobert NER.
        """
        # For V1, just find matches to known entity names
        extracted = []
        
        for entity in self.entities.diseases.values():
            for variant in [entity.name] + entity.synonyms + entity.abbreviations:
                if variant.lower() in text.lower():
                    start = text.lower().index(variant.lower())
                    extracted.append(ExtractedEntity(
                        mention_text=variant,
                        canonical_id=entity.entity_id,
                        entity_type='disease',
                        start_char=start,
                        end_char=start + len(variant),
                        chunk_id=chunk_id,
                        confidence=1.0,  # Exact match
                        extraction_method='string_match'
                    ))
        
        return extracted
```

**2. Relationship extraction - you have the schema but no implementation:**

```python
# src/ingestion/relationship_extractor.py
class RelationshipExtractor:
    def extract_relationships(self, 
                             entities: List[ExtractedEntity],
                             text: str,
                             chunk_id: str) -> List[Relationship]:
        """
        V1: Simple co-occurrence within sentences.
        V2: Add semantic relationship extraction.
        """
        relationships = []
        
        # Group entities by sentence (simple version)
        sentences = text.split('. ')
        
        for sent in sentences:
            sent_entities = [e for e in entities if sent[e.start_char:e.end_char] == e.mention_text]
            
            # Create co-occurrence relationships
            for i, e1 in enumerate(sent_entities):
                for e2 in sent_entities[i+1:]:
                    if e1.entity_type == 'drug' and e2.entity_type == 'disease':
                        relationships.append(Relationship(
                            subject_id=e1.canonical_id,
                            predicate='ASSOCIATED_WITH',
                            object_id=e2.canonical_id,
                            evidence_text=sent,
                            chunk_id=chunk_id,
                            confidence=0.5,
                            extraction_method='cooccurrence'
                        ))
        
        return relationships
```

## Recommended Architecture Changes

**Current flow:**
```
XML → Parse → Embed → Index to OpenSearch
```

**Better flow for fast ingestion:**
```
XML → Parse → S3 (raw)
S3 (raw) → [Parallel] → Entity Extract + Embed → S3 (processed)
S3 (processed) → [Batch] → Bulk import to OpenSearch/Neo4j
```

**Create a new master pipeline:**

```python
# src/ingestion/master_pipeline.py
class MasterIngestionPipeline:
    def __init__(self):
        self.cache = EmbeddingCache()
        self.entity_collection = EntityCollection.load('reference_entities.jsonl')
        self.s3_writer = S3PaperWriter()
    
    def process_paper_to_s3(self, pmc_id: str):
        """
        Stage 1: Parse and write to S3.
        This is what runs in parallel (Lambda/Ray).
        """
        # Parse
        parser = JATSParser(f'/tmp/{pmc_id}.xml')
        paper = parser.parse()
        
        # Extract entities (with caching)
        extractor = EntityExtractor(self.entity_collection, self.cache)
        entities = []
        for chunk in paper.chunks:
            chunk_entities = extractor.extract_entities(chunk.text, chunk.chunk_id)
            entities.extend(chunk_entities)
        
        # Extract relationships
        rel_extractor = RelationshipExtractor()
        relationships = []
        for chunk in paper.chunks:
            chunk_rels = rel_extractor.extract_relationships(entities, chunk.text, chunk.chunk_id)
            relationships.extend(chunk_rels)
        
        # Create ProcessedPaper
        processed = ProcessedPaper(
            pmc_id=paper.metadata.pmc_id,
            pmid=paper.metadata.pmid,
            # ... all metadata
            entities=aggregate_entity_mentions(entities),
            relationships=relationships,
            entity_count=len(entities),
            relationship_count=len(relationships),
            full_text=paper.full_text
        )
        
        # Write to S3
        self.s3_writer.write_paper(processed)
    
    def bulk_import_from_s3(self, batch_size: int = 1000):
        """
        Stage 2: Read from S3, bulk import to OpenSearch/Neo4j.
        Run this after parallel processing completes.
        """
        # Read all processed papers from S3
        papers = self.s3_writer.list_papers()
        
        # Bulk import to OpenSearch
        indexer = OpenSearchIndexer()
        indexer.bulk_index(papers, chunk_size=batch_size)
        
        # Bulk import to Neo4j (if using)
        # ...
```

## Immediate Action Items

1. **Add caching** - This saves $$ and time immediately
2. **Add S3 intermediate storage** - Enables parallelization
3. **Implement entity extraction** - You have schema, need implementation
4. **Implement relationship extraction** - Start with co-occurrence
5. **Test on 1K papers** - Measure cache hit rate, embeddings cost, time
6. **Deploy parallel processing** - Lambda or Ray

## What's Actually Good

- ✅ JATS parser looks solid with good test coverage
- ✅ Entity schema is well thought out
- ✅ Relationship schema with provenance is excellent
- ✅ OpenSearch indexer has hybrid search
- ✅ Embedding generator has rate limiting

**Your schema is production-ready. Your ingestion pipeline needs caching + parallelization + entity/relationship extraction to be fast.**

Start with caching - that's 2 hours of work and 10x ROI.
