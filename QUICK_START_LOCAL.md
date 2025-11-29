# Quick Start - Local Docker Compose

This guide shows you how to use your local docker-compose OpenSearch instead of AWS.

## 1. Start Docker Compose

```bash
docker-compose up -d
```

Wait for OpenSearch to be ready (check the logs):
```bash
docker-compose logs -f opensearch
```

## 2. Set Environment Variables

The code now auto-detects local vs AWS based on environment variables:

```bash
export OPENSEARCH_HOST=localhost
export OPENSEARCH_PORT=9200
```

Or create a `.env` file in the project root:
```bash
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
```

## 3. Test the Connection

```bash
python test_opensearch_connection.py
```

You should see:
```
✓ Connected to OpenSearch at localhost:9200 (SSL: False, AWS Auth: False)
✓ Cluster health: green
✓ Number of nodes: 1
```

## 4. Run Your Code

Now you can run any of the scripts and they will automatically connect to your local docker-compose OpenSearch:

### Option A: Direct Python Usage

```python
from src.ingestion.pipeline import PaperIndexingPipeline, OpenSearchIndexer

# No need to specify host/port - uses environment variables
pipeline = PaperIndexingPipeline()

# Or if you want to be explicit:
indexer = OpenSearchIndexer(
    host='localhost',
    port=9200
)
```

### Option B: Using the Client

```python
from src.client.medical_papers_client import MedicalPapersClient

# Auto-detects local mode
client = MedicalPapersClient()

# Test with keyword search (doesn't need AWS Bedrock)
results = client.search(
    query="cancer treatment",
    k=10,
    search_type='keyword'  # Use 'keyword' for local, 'hybrid' needs Bedrock
)
```

## How It Works

The code now automatically detects whether you're using:

- **Local mode** (localhost, 127.0.0.1, or opensearch):
  - No SSL
  - No AWS authentication
  - Port 9200 by default

- **AWS mode** (any other hostname or port 443):
  - SSL enabled
  - AWS Signature V4 authentication
  - Port 443

## Using with Bedrock (Optional)

If you want to use embeddings (hybrid/semantic search) while using local OpenSearch:

```bash
# Set up AWS credentials for Bedrock only
export AWS_PROFILE=default
export AWS_REGION=us-east-1

# OpenSearch still uses local
export OPENSEARCH_HOST=localhost
export OPENSEARCH_PORT=9200
```

## Troubleshooting

### Connection Refused

Make sure docker-compose is running:
```bash
docker-compose ps
curl http://localhost:9200
```

### Wrong Domain Error

If you still see errors about `your-domain.us-east-1.es.amazonaws.com`, make sure you've set the environment variables:
```bash
export OPENSEARCH_HOST=localhost
export OPENSEARCH_PORT=9200
```

Or check that your `.env` file is in the project root and is being loaded.
