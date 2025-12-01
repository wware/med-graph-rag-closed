# test_ingestion.py
import sys
sys.path.append('src')

from embedding_cache import EmbeddingCache
from extractor import EntityExtractor
from schema.entity import EntityCollection, Disease

# Test 1: Cache connection
print("Testing Redis cache...")
cache = EmbeddingCache('redis://localhost:6379')

embedding = [0.1] * 1024
cache.set("test text", embedding)
result = cache.get("test text")
assert result == embedding
print("✓ Cache works!")

# Test 2: Entity extraction
print("\nTesting entity extraction...")

# Create minimal entity collection
collection = EntityCollection()
diabetes = Disease(
    entity_id="C0011860",
    name="Type 2 Diabetes Mellitus",
    synonyms=["Type II Diabetes", "Adult-Onset Diabetes"],
    abbreviations=["T2DM", "NIDDM"],
    umls_id="C0011860",
    source="umls"
)
collection.add_disease(diabetes)

extractor = EntityExtractor(collection, cache)

# Test extraction
text = "Patients with T2DM often develop complications."
entities = extractor.extract_entities(text, "test_chunk")

print(f"Found {len(entities)} entities:")
for e in entities:
    print(f"  - {e.mention_text} ({e.entity_type})")

assert len(entities) > 0
print("✓ Entity extraction works!")

print("\n✅ All tests passed!")
