from src.ingestion.pipeline import PaperIndexingPipeline, OpenSearchIndexer
import os

print("Testing implicit initialization with env vars...")
# Set env vars for the test
os.environ["OPENSEARCH_HOST"] = "localhost"
os.environ["OPENSEARCH_PORT"] = "9200"

try:
    pipeline = PaperIndexingPipeline()
    print("Successfully initialized PaperIndexingPipeline with env vars")
except Exception as e:
    print(f"Failed to initialize PaperIndexingPipeline: {e}")

print("\nTesting explicit initialization...")
try:
    indexer = OpenSearchIndexer(host="localhost", port=9200)
    print("Successfully initialized OpenSearchIndexer with explicit args")
except Exception as e:
    print(f"Failed to initialize OpenSearchIndexer: {e}")
