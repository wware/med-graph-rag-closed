from schema.entity import EntityMention
from typing import List
from schema.entity import EntityCollection, ExtractedEntity, ProcessedPaper
from schema.relationship import Relationship
from ingestion.embedding_cache import EmbeddingCache
from ingestion.embedding_generator import EmbeddingGenerator
from ingestion.jats_parser import JATSParser
from ingestion.s3_writer import S3PaperWriter
from ingestion.pipeline import OpenSearchIndexer


class EntityExtractor:
    """Extracts biomedical entities from text using entity linking and NER.
    
    This class performs named entity recognition (NER) by matching text against
    a reference collection of known biomedical entities. It supports exact string
    matching with entity names, synonyms, and abbreviations.
    
    Attributes:
        entities: Collection of reference biomedical entities for linking.
        cache: Cache for storing and retrieving embeddings.
        embedder: Generator for creating text embeddings.
    
    Example:
        >>> entity_collection = EntityCollection.load('reference_entities.jsonl')
        >>> cache = EmbeddingCache()
        >>> extractor = EntityExtractor(entity_collection, cache)
        >>> entities = extractor.extract_entities("Alzheimer's disease affects memory", "chunk_1")
    """
    
    def __init__(self, entity_collection: EntityCollection, cache: EmbeddingCache) -> None:
        """Initialize the entity extractor.
        
        Args:
            entity_collection: Collection of reference entities for entity linking.
            cache: Cache for storing and retrieving embeddings.
        """
        self.entities = entity_collection
        self.cache = cache
        self.embedder = EmbeddingGenerator()
        
        # Build lookup dict for fast string matching
        self._build_lookup_index()

    def _build_lookup_index(self):
        """Pre-build index of all entity names/synonyms for fast lookup"""
        self.lookup = {}  # normalized_text -> (entity_id, entity_type)
        
        for entity_type, collection in [
            ('disease', self.entities.diseases),
            ('gene', self.entities.genes),
            ('drug', self.entities.drugs),
            ('protein', self.entities.proteins)
        ]:
            for entity in collection.values():
                variants = [entity.name] + entity.synonyms + entity.abbreviations
                for variant in variants:
                    normalized = variant.lower().strip()
                    if len(normalized) > 2:  # Skip very short strings
                        self.lookup[normalized] = (entity.entity_id, entity_type)
    

    def extract_entities(self, text: str, chunk_id: str) -> List[ExtractedEntity]:
        """Extract biomedical entities from text using string matching.
        
        Performs entity recognition by matching text against known entity names,
        synonyms, and abbreviations from the reference entity collection. Currently
        uses exact string matching (case-insensitive).
        
        Args:
            text: The text to extract entities from.
            chunk_id: Unique identifier for the text chunk being processed.
        
        Returns:
            List of extracted entities with their positions, types, and canonical IDs.
        
        Note:
            V1: Uses simple noun phrase extraction and entity linking.
            V2 (planned): Will add scispacy/biobert NER for improved accuracy.
        
        Example:
            >>> text = "Patients with diabetes may develop neuropathy."
            >>> entities = extractor.extract_entities(text, "chunk_123")
            >>> print(entities[0].mention_text)  # "diabetes"
            >>> print(entities[0].entity_type)  # "disease"
        """
        import re
        extracted = []
        seen_positions = set()  # Avoid overlapping matches
        
        # Try exact matches first (case-insensitive, word boundaries)
        for variant, (entity_id, entity_type) in self.lookup.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(variant) + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start, end = match.span()
                
                # Check for overlap with existing matches
                if any(start < e < end or start < s < end 
                       for s, e in seen_positions):
                    continue
                
                seen_positions.add((start, end))
                extracted.append(ExtractedEntity(
                    mention_text=match.group(),
                    canonical_id=entity_id,
                    entity_type=entity_type,
                    start_char=start,
                    end_char=end,
                    chunk_id=chunk_id,
                    confidence=1.0,  # Exact match
                    extraction_method='string_match'
                ))
        
        return extracted


class RelationshipExtractor:
    """Extracts relationships between biomedical entities from text.
    
    This class identifies relationships between entities by analyzing their
    co-occurrence patterns within sentences. Currently uses simple co-occurrence
    heuristics to detect associations between drugs and diseases.
    
    Example:
        >>> extractor = RelationshipExtractor()
        >>> entities = [drug_entity, disease_entity]
        >>> relationships = extractor.extract_relationships(entities, text, "chunk_1")
        >>> print(relationships[0].predicate)  # "ASSOCIATED_WITH"
    """
    
    def extract_relationships(self,
                             entities: List[ExtractedEntity],
                             text: str,
                             chunk_id: str) -> List[Relationship]:
        """Extract relationships between entities based on co-occurrence.
        
        Identifies relationships by finding entities that appear together in the
        same sentence. Currently focuses on drug-disease associations.
        
        Args:
            entities: List of extracted entities to find relationships between.
            text: The original text containing the entities.
            chunk_id: Unique identifier for the text chunk being processed.
        
        Returns:
            List of relationships found between entities, including evidence text
            and confidence scores.
        
        Note:
            V1: Uses simple co-occurrence within sentences.
            V2 (planned): Will add semantic relationship extraction using NLP models.
        
        Example:
            >>> entities = [
            ...     ExtractedEntity(mention_text="aspirin", entity_type="drug", ...),
            ...     ExtractedEntity(mention_text="headache", entity_type="disease", ...)
            ... ]
            >>> rels = extractor.extract_relationships(entities, text, "chunk_1")
            >>> print(rels[0].predicate)  # "ASSOCIATED_WITH"
        """
        relationships = []
        
        # Split into sentences (better approach)
        import re
        sentences = re.split(r'[.!?]+', text)
        
        current_pos = 0
        for sent in sentences:
            if not sent.strip():
                continue
            
            sent_start = text.index(sent, current_pos)
            sent_end = sent_start + len(sent)
            current_pos = sent_end
            
            # Find entities in this sentence
            sent_entities = [
                e for e in entities 
                if sent_start <= e.start_char < sent_end
            ]
            
            # Create co-occurrence relationships
            for i, e1 in enumerate(sent_entities):
                for e2 in sent_entities[i+1:]:
                    # Only create meaningful relationships
                    if (e1.entity_type == 'drug' and e2.entity_type == 'disease') or \
                       (e1.entity_type == 'disease' and e2.entity_type == 'drug') or \
                       (e1.entity_type == 'gene' and e2.entity_type == 'disease'):
                        
                        relationships.append(Relationship(
                            subject_id=e1.canonical_id,
                            predicate='ASSOCIATED_WITH',
                            object_id=e2.canonical_id,
                            evidence_text=sent.strip(),
                            chunk_id=chunk_id,
                            confidence=0.5,
                            extraction_method='cooccurrence'
                        ))
        
        return relationships


def aggregate_entity_mentions(entities: List[ExtractedEntity]) -> List[EntityMention]:
    """Aggregate extracted entities into entity mentions.
    
    Converts a list of extracted entities into entity mentions, grouping them
    by their canonical entity ID. Each mention includes the entity type and
    all occurrences of that entity.
    
    Args:
        entities: List of extracted entities from text chunks.
    
    Returns:
        List of entity mentions with canonical IDs and grouped occurrences.
    
    Example:
        >>> extracted = [
        ...     ExtractedEntity(canonical_id="D000544", entity_type="disease", ...),
        ...     ExtractedEntity(canonical_id="D000544", entity_type="disease", ...)
        ... ]
        >>> mentions = aggregate_entity_mentions(extracted)
        >>> print(len(mentions[0].mentions))  # 2
    """
    from collections import defaultdict
    
    entity_groups = defaultdict(lambda: {
        'mentions': [],
        'chunk_ids': set(),
        'count': 0
    })
    
    for entity in entities:
        key = (entity.canonical_id, entity.entity_type)
        entity_groups[key]['mentions'].append(entity.mention_text)
        entity_groups[key]['chunk_ids'].add(entity.chunk_id)
        entity_groups[key]['count'] += 1
    
    result = []
    for (entity_id, entity_type), data in entity_groups.items():
        result.append(EntityMention(
            entity_id=entity_id,
            canonical_name=data['mentions'][0],  # Use first mention as canonical
            entity_type=entity_type,
            mention_count=data['count'],
            mentions=list(set(data['mentions'])),  # Unique mentions
            chunk_ids=list(data['chunk_ids'])
        ))
    
    return result


class MasterIngestionPipeline:
    """Orchestrates the complete paper ingestion and processing pipeline.
    
    This pipeline handles the end-to-end processing of biomedical papers, from
    parsing JATS XML files to extracting entities and relationships, and finally
    storing the processed data in S3 and indexing it in OpenSearch.
    
    The pipeline operates in two stages:
    1. Parallel processing: Parse papers, extract entities/relationships, write to S3
    2. Bulk import: Read from S3 and bulk index into OpenSearch/Neo4j
    
    Attributes:
        cache: Cache for storing and retrieving embeddings.
        entity_collection: Collection of reference biomedical entities.
        s3_writer: Writer for storing processed papers in S3.
    
    Example:
        >>> pipeline = MasterIngestionPipeline()
        >>> # Stage 1: Process individual papers (can be parallelized)
        >>> pipeline.process_paper_to_s3("PMC1234567")
        >>> # Stage 2: Bulk import all processed papers
        >>> pipeline.bulk_import_from_s3(batch_size=1000)
    """
    
    def __init__(self) -> None:
        """Initialize the ingestion pipeline with required components.
        
        Sets up the embedding cache, loads the reference entity collection,
        and initializes the S3 writer for storing processed papers.
        """
        self.cache = EmbeddingCache()
        self.entity_collection = EntityCollection.load('reference_entities.jsonl')
        self.s3_writer = S3PaperWriter()

    def process_paper_to_s3(self, pmc_id: str) -> None:
        """Process a single paper and write results to S3.
        
        Stage 1 of the pipeline: Parses a JATS XML file, extracts entities and
        relationships, and writes the processed paper to S3. This method is
        designed to run in parallel across multiple papers (e.g., using AWS Lambda
        or Ray).
        
        Args:
            pmc_id: PubMed Central ID of the paper to process (e.g., "PMC1234567").
        
        Note:
            This method expects the JATS XML file to be available at
            `/tmp/{pmc_id}.xml`. Ensure the file is downloaded before calling.
        
        Example:
            >>> pipeline = MasterIngestionPipeline()
            >>> pipeline.process_paper_to_s3("PMC1234567")
            # Paper is parsed, entities extracted, and results written to S3
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
            doi=paper.metadata.doi,
            title=paper.metadata.title,
            abstract=paper.metadata.abstract,
            authors=paper.metadata.authors,
            publication_date=paper.metadata.publication_date,
            journal=paper.metadata.journal,
            entities=aggregate_entity_mentions(entities),
            relationships=relationships,
            entity_count=len(entities),
            relationship_count=len(relationships),
            full_text=paper.full_text
        )

        # Write to S3
        self.s3_writer.write_paper(processed)

    def bulk_import_from_s3(self, batch_size: int = 1000) -> None:
        """Bulk import processed papers from S3 to OpenSearch and Neo4j.
        
        Stage 2 of the pipeline: Reads all processed papers from S3 and performs
        bulk indexing into OpenSearch for full-text search. Optionally can also
        import into Neo4j for graph queries.
        
        Args:
            batch_size: Number of papers to process in each bulk indexing batch.
                Larger batches are more efficient but use more memory. Default: 1000.
        
        Note:
            Run this method only after all papers have been processed in Stage 1
            (process_paper_to_s3). This ensures all data is available in S3.
        
        Example:
            >>> pipeline = MasterIngestionPipeline()
            >>> # After processing all papers with process_paper_to_s3
            >>> pipeline.bulk_import_from_s3(batch_size=500)
            # All papers are indexed in OpenSearch
        """
        # Read all processed papers from S3
        papers = self.s3_writer.list_papers()

        # Bulk import to OpenSearch
        indexer = OpenSearchIndexer()
        indexer.bulk_index(papers, chunk_size=batch_size)

        # Bulk import to Neo4j (if using)
        # ...
