from src.client.medical_papers_client import MedicalPapersClient
import os

# Set env vars for local mode
os.environ["OPENSEARCH_HOST"] = "localhost"
os.environ["OPENSEARCH_PORT"] = "9200"

print("Initializing client...")
client = MedicalPapersClient()

print("Attempting keyword search...")
try:
    results = client.search(query="cancer", k=1, search_type="keyword")
    print("Search successful!")
except Exception as e:
    print(f"Search failed as expected: {e}")
