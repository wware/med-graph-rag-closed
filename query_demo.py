from src.client.medical_papers_client import MedicalPapersClient
import os

# Ensure env vars are set (though client defaults to these)
os.environ["OPENSEARCH_HOST"] = "localhost"
os.environ["OPENSEARCH_PORT"] = "9200"

print("Initializing client...")
client = MedicalPapersClient()

query = "BRCA1 breast cancer"
print(f"\nSearching for: '{query}' (keyword search)...")

try:
    results = client.search(query=query, k=5, search_type="keyword")

    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Title: {result.title}")
        print(f"PMC ID: {result.pmc_id}")
        print(f"Section: {result.section}")
        print(f"Snippet: {result.chunk_text[:300]}...")

except Exception as e:
    print(f"Error running search: {e}")
