"""
Debug gene entity loading - shows what's actually added to FlashText processor.

Usage:
    python -m src.scripts.debug_gene_loading
"""

from src.schema.entity import EntityCollection
from src.ingestion.embedding_cache import EmbeddingCache
from src.ingestion.extractor import EntityExtractor


def debug_gene_loading():
    """Show what genes are being added to the FlashText processor."""

    print("Loading entity collection...")
    try:
        collection = EntityCollection.load("reference_entities.jsonl")
    except Exception as e:
        print(f"Error loading collection: {e}")
        return

    print(f"Loaded {len(collection.genes)} genes\n")

    # Create extractor (this builds the processors)
    print("Building EntityExtractor...")
    cache = EmbeddingCache("redis://localhost:6379")
    extractor = EntityExtractor(collection, cache)

    # Check what's in the gene processor
    print(f"\n{'='*80}")
    print("GENE PROCESSOR ANALYSIS")
    print(f"{'='*80}\n")

    # Get all keywords from the gene processor
    all_keywords = extractor.gene_processor.extract_keywords(
        " ".join(extractor.gene_processor.get_all_keywords().keys())
    )

    # Show some statistics
    gene_keywords = extractor.gene_processor.get_all_keywords()

    print(f"Total gene keywords loaded: {len(gene_keywords)}")
    print(f"Case sensitive: {extractor.gene_processor.case_sensitive}")

    # Find short keywords (potential problems)
    short_keywords = {k: v for k, v in gene_keywords.items() if len(k) <= 3}
    print(f"Keywords ≤3 chars: {len(short_keywords)}")

    if short_keywords:
        print(f"\nShort keywords (first 30):")
        for i, (keyword, clean_name) in enumerate(list(short_keywords.items())[:30], 1):
            entity_id, entity_type = clean_name.split("|")
            print(f"  {i:2d}. '{keyword}' → {entity_id}")

    # Check for common words
    COMMON_WORDS = ["FOR", "IF", "AND", "OR", "IN", "ON", "UP", "AS", "AT", "OF"]
    found_common = {w: gene_keywords.get(w) for w in COMMON_WORDS if w in gene_keywords}

    print(f"\n{'='*80}")
    print(f"COMMON WORDS CHECK")
    print(f"{'='*80}\n")

    if found_common:
        print(f"⚠️  Found {len(found_common)} common words in gene processor:")
        for word, clean_name in found_common.items():
            entity_id, _ = clean_name.split("|")
            print(f"  - '{word}' → {entity_id}")
    else:
        print(f"✓ No common words found (good!)")

    # Test extraction on sample text
    print(f"\n{'='*80}")
    print("TEST EXTRACTION")
    print(f"{'='*80}\n")

    test_text = (
        "The BRCA1 gene is important for DNA repair. Patients with TP53 mutations..."
    )
    entities = extractor.extract_entities(test_text, "test_chunk")

    print(f"Test text: {test_text}")
    print(f"\nExtracted {len(entities)} entities:")
    for e in entities:
        print(f"  - '{e.mention_text}' ({e.entity_type}) → {e.canonical_id}")

    # Test with lowercase common words
    print(f"\n{'='*80}")
    print("LOWERCASE COMMON WORDS TEST")
    print(f"{'='*80}\n")

    test_text2 = "This is for the patient. We can see if the results are conclusive."
    entities2 = extractor.extract_entities(test_text2, "test_chunk_2")

    print(f"Test text: {test_text2}")
    print(f"\nExtracted {len(entities2)} entities:")
    if entities2:
        for e in entities2:
            print(f"  - '{e.mention_text}' ({e.entity_type}) → {e.canonical_id}")
    else:
        print("  ✓ No false positives (good!)")


if __name__ == "__main__":
    debug_gene_loading()
