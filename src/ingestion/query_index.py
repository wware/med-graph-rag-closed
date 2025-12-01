"""
Query the OpenSearch index for medical papers.

Usage:
    python -m src.ingestion.query_index "your search query here"
"""

import sys
from src.ingestion.pipeline import OpenSearchIndexer, PaperIndexingPipeline
from src.ingestion.embedding_generator import EmbeddingGenerator


def search(query_text: str, k: int = 10, vector_weight: float = 0.5):
    """Search the medical papers index.
    
    Args:
        query_text: The search query
        k: Number of results to return
        vector_weight: Weight for vector search (0-1), keyword gets (1 - vector_weight)
    """
    # Initialize components
    indexer = OpenSearchIndexer(create_index=False)
    embedder = EmbeddingGenerator()
    
    # Generate embedding for query
    print(f"Searching for: {query_text}\n")
    query_embedding = embedder.embed_text(query_text)
    
    # Perform hybrid search
    results = indexer.search_hybrid(
        query_text=query_text,
        query_embedding=query_embedding,
        k=k,
        vector_weight=vector_weight
    )
    
    # Display results
    print(f"Found {len(results)} results:\n")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        source = result['source']
        print(f"\n{i}. Score: {result['score']:.4f}")
        print(f"   Paper: {source.get('pmc_id', 'N/A')}")
        print(f"   Title: {source.get('title', 'N/A')}")
        print(f"   Section: {source.get('section', 'N/A')}")
        
        # Show entities if present
        entities = source.get('entities', [])
        if entities:
            entity_types = {}
            for e in entities:
                entity_types.setdefault(e['type'], []).append(e['text'])
            print(f"   Entities: {dict(entity_types)}")
        
        # Show chunk preview
        chunk_text = source.get('chunk_text', '')
        preview = chunk_text[:200] + '...' if len(chunk_text) > 200 else chunk_text
        print(f"   Text: {preview}")
        print("-" * 80)


def search_by_entity(entity_type: str = None, entity_text: str = None, k: int = 10):
    """Search for papers containing specific entities.
    
    Args:
        entity_type: Type of entity (disease, drug, gene, protein)
        entity_text: Text of the entity to search for
        k: Number of results to return
    """
    from opensearchpy import OpenSearch
    
    indexer = OpenSearchIndexer(create_index=False)
    
    # Build nested query for entities
    query = {
        "size": k,
        "query": {
            "nested": {
                "path": "entities",
                "query": {
                    "bool": {
                        "must": []
                    }
                }
            }
        }
    }
    
    if entity_type:
        query["query"]["nested"]["query"]["bool"]["must"].append({
            "term": {"entities.type": entity_type}
        })
    
    if entity_text:
        query["query"]["nested"]["query"]["bool"]["must"].append({
            "match": {"entities.text": entity_text}
        })
    
    # Execute search
    response = indexer.client.search(index=indexer.index_name, body=query)
    
    print(f"Found {len(response['hits']['hits'])} papers with {entity_type or 'any'} entities matching '{entity_text or 'any'}':\n")
    print("=" * 80)
    
    for i, hit in enumerate(response['hits']['hits'], 1):
        source = hit['_source']
        print(f"\n{i}. Score: {hit['_score']:.4f}")
        print(f"   Paper: {source.get('pmc_id', 'N/A')}")
        print(f"   Title: {source.get('title', 'N/A')}")
        print(f"   Section: {source.get('section', 'N/A')}")
        
        # Show matching entities
        entities = source.get('entities', [])
        if entities:
            print(f"   Entities found: {len(entities)}")
            for e in entities[:5]:  # Show first 5
                print(f"      - {e['type']}: {e['text']}")
        
        print("-" * 80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Query the medical papers index")
    parser.add_argument("query", nargs="?", help="Search query text")
    parser.add_argument("--entity-type", choices=["disease", "drug", "gene", "protein"],
                       help="Filter by entity type")
    parser.add_argument("--entity-text", help="Search for specific entity text")
    parser.add_argument("-k", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument("--vector-weight", type=float, default=0.5,
                       help="Weight for vector search 0-1 (default: 0.5)")
    
    args = parser.parse_args()
    
    if args.entity_type or args.entity_text:
        search_by_entity(args.entity_type, args.entity_text, args.k)
    elif args.query:
        search(args.query, args.k, args.vector_weight)
    else:
        parser.print_help()
