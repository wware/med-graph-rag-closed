# Testing Python parser files

**Created:** 11/30/2025 15:55:03  
**Updated:** 11/30/2025 16:14:40  
**Exported:** 11/30/2025 16:22:33  
**Link:** [https://claude.ai/chat/c0e16cce-c9ea-427b-b186-3b26eadfab95](https://claude.ai/chat/c0e16cce-c9ea-427b-b186-3b26eadfab95)  

## Response:
11/30/2025, 4:14:40 PM

Looking at your `docker-compose.yml`, you have a complete local development setup with:

1. **OpenSearch** on `localhost:9200` (security disabled)
2. **LocalStack** mocking AWS services
3. **Ingestion service** container

So the issue isn't about adding local mode - **it's about the inconsistency between how `medical_papers_client.py` is written (AWS-only) and how your local environment works (no auth).**

---

## The Real Problem

Your `medical_papers_client.py` **always requires AWS credentials** (lines 66-69):

```python
# Set up AWS session
session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
credentials = session.get_credentials()
auth = AWSV4SignerAuth(credentials, aws_region, 'es')
```

But your local OpenSearch has **security disabled** (docker-compose.yml line 16):
```yaml
- plugins.security.disabled=true
```

So when you try to connect from your laptop with:
```python
client = MedicalPapersClient(opensearch_host='localhost')
```

It will **fail** because:
1. ❌ It tries to connect to port **443** (hardcoded line 73), not 9200
2. ❌ It requires **AWS credentials** even though local OpenSearch has no auth
3. ❌ It uses **SSL** even though your local setup doesn't use SSL

---

## How to Fix It

You need to **detect local vs AWS mode**. Here's the minimal fix to `medical_papers_client.py`:

```python
def __init__(self,
             opensearch_host: str,
             aws_region: str = 'us-east-1',
             index_name: str = 'medical-papers',
             aws_profile: Optional[str] = None):
    """
    Initialize client
    
    Automatically detects local vs AWS mode based on opensearch_host.
    Local mode: opensearch_host='localhost' or '127.0.0.1' or 'opensearch'
    AWS mode: opensearch_host='search-xxx.us-east-1.es.amazonaws.com'
    """
    
    # Detect if running in local mode
    local_hosts = ['localhost', '127.0.0.1', 'opensearch']
    is_local = opensearch_host in local_hosts
    
    if is_local:
        # Local OpenSearch (docker-compose) - no auth, port 9200
        self.client = OpenSearch(
            hosts=[{'host': opensearch_host, 'port': 9200}],
            http_compress=True,
            use_ssl=False,
            verify_certs=False,
            connection_class=RequestsHttpConnection,
            timeout=60
        )
        self.bedrock = None  # No Bedrock in local mode
        self.local_mode = True
    else:
        # AWS OpenSearch - with auth, port 443, SSL
        session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
        credentials = session.get_credentials()
        auth = AWSV4SignerAuth(credentials, aws_region, 'es')
        
        self.client = OpenSearch(
            hosts=[{'host': opensearch_host, 'port': 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=60
        )
        
        # Bedrock client for generating query embeddings
        self.bedrock = session.client('bedrock-runtime', region_name=aws_region)
        self.local_mode = False
    
    self.index_name = index_name
    self.model_id = 'amazon.titan-embed-text-v2:0'
```

And update `_generate_query_embedding()`:

```python
def _generate_query_embedding(self, text: str) -> List[float]:
    """Generate embedding for a query"""
    if self.local_mode:
        # In local mode, use sentence-transformers instead of Bedrock
        try:
            from sentence_transformers import SentenceTransformer
            if not hasattr(self, '_local_model'):
                # Cache the model
                self._local_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            embedding = self._local_model.encode(text)
            # Pad to 1024 dimensions to match Titan
            if len(embedding) < 1024:
                import numpy as np
                padding = np.zeros(1024 - len(embedding))
                embedding = np.concatenate([embedding, padding])
            return embedding.tolist()
        except ImportError:
            # Fallback: random embedding (for testing only)
            import random
            print("WARNING: Using random embeddings. Install sentence-transformers for real embeddings.")
            return [random.random() for _ in range(1024)]
    
    # AWS Bedrock embedding (production)
    request_body = {
        "inputText": text,
        "dimensions": 1024,
        "normalize": True
    }
    
    response = self.bedrock.invoke_model(
        modelId=self.model_id,
        contentType='application/json',
        accept='application/json',
        body=json.dumps(request_body)
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['embedding']
```

---

## Still Need to Fix: `hybrid_search()` Method

Your MCP server calls `client.hybrid_search()` but that method **doesn't exist**. Add it:

```python
def hybrid_search(self, query: str, k: int = 10, 
                  vector_weight: float = 0.5) -> List[Dict[str, Any]]:
    """
    Convenience method for hybrid search (backward compatibility with MCP server)
    
    Returns raw dicts instead of SearchResult objects
    """
    results = self.search(
        query=query,
        k=k,
        search_type='hybrid',
        vector_weight=vector_weight
    )
    
    # Convert SearchResult objects to dicts for MCP server
    return [asdict(r) for r in results]
```

---

## Updated `requirements.txt`

Add this for local embeddings:

```txt
# Existing dependencies
opensearch-py>=2.0.0
boto3>=1.28.0
pandas>=2.0.0

# For local development embeddings
sentence-transformers>=2.2.0
```

---

## Now Your Local Workflow Works

**From your laptop:**
```python
from medical_papers_client import MedicalPapersClient

# Automatically uses local mode (port 9200, no auth, no SSL)
client = MedicalPapersClient(opensearch_host='localhost')

results = client.search(query="BRCA1 breast cancer", k=5)
for r in results:
    print(r)
```

**From ingestion service container:**
```python
# docker-compose.yml sets OPENSEARCH_HOST=opensearch
client = MedicalPapersClient(opensearch_host='opensearch')  # Also local mode
```

**In production (AWS):**
```python
# Uses AWS mode (port 443, AWS auth, SSL, Bedrock)
client = MedicalPapersClient(
    opensearch_host='search-abc123.us-east-1.es.amazonaws.com'
)
```

---

## Test It

```bash
# Start your local stack
docker-compose up -d opensearch

# Wait for health check
sleep 10

# Test from Python
python3 -c "
from medical_papers_client import MedicalPapersClient
client = MedicalPapersClient(opensearch_host='localhost')
print('✓ Connected to local OpenSearch')
"
```
