# AWS Components Bill of Materials (BOM)
## Medical Graph RAG - MCP Server Backend

**Architecture:** MCP server (runs locally or on user's machine) + AWS backend for data processing

**What's deployed to AWS:**
- Data ingestion pipeline (JATS parser, embeddings, indexing)
- OpenSearch cluster (vector + keyword search)
- S3 storage (raw papers, processed data)

**What runs locally:**
- MCP server (stdio transport to AI assistants)
- User's Claude Desktop or other MCP-compatible client

## Core Services (Minimal Deployment)

### 1. Amazon OpenSearch Service
**Purpose**: Vector search + metadata storage for paper chunks

**POC Configuration** (~$30-50/month):
- Instance Type: `t3.small.search` (single node for POC)
- Number of Instances: 1 (no HA for POC)
- Storage: 50 GB EBS (gp3)
- Enable: k-NN plugin for vector search
- VPC: Deploy in private subnet

**Production Configuration** (~$150-200/month):
- Instance Type: `t3.medium.search`
- Number of Instances: 2 (for HA)
- Storage: 100 GB EBS (gp3) per instance

**IAM Requirements**:
- IAM role for Lambda to access OpenSearch
- Fine-grained access control enabled

### 2. AWS Bedrock
**Purpose**: Embeddings only (Titan Embeddings V2)

**Configuration**:
- Model Access: Enable Titan Embeddings V2
- No infrastructure to provision (serverless)
- ~$0.0001 per 1K tokens

**Estimated Cost**:
- 100 papers: ~$0.50
- 1,000 papers: ~$5
- 10,000 papers: ~$50
- **Ongoing**: Minimal (only when adding new papers)

**IAM Requirements**:
- IAM policy to invoke Bedrock models

### 3. Amazon S3
**Purpose**: Storage for raw papers, processed data

**Buckets**:
```
medical-kg-papers/
  ├── raw/             # Downloaded JATS XML files
  ├── processed/       # Parsed/extracted data
  └── logs/            # Ingestion logs
```

**Configuration**:
- Versioning: Enabled
- Lifecycle: Move to Glacier after 90 days
- Encryption: SSE-S3

**Estimated Cost**:
- 1,000 papers: ~$1/month
- 10,000 papers: ~$5/month
- 100,000 papers: ~$20/month

### 4. AWS Lambda
**Purpose**: Serverless ingestion pipeline

**Functions**:

1. **Paper Ingestion Trigger** (S3 → Lambda)
   - Triggered when new XML uploaded to S3
   - Parses JATS XML, generates embeddings, indexes to OpenSearch
   - Runtime: Python 3.12
   - Memory: 2048 MB
   - Timeout: 15 minutes

2. **Batch Processor** (scheduled or manual)
   - Processes multiple papers in batch
   - Runtime: Python 3.12
   - Memory: 3008 MB
   - Timeout: 15 minutes

**Estimated Cost**: ~$2-5/month (mostly idle, pay per invocation)

**IAM Requirements**:
- Lambda execution role with access to S3, OpenSearch, Bedrock

### 5. Amazon CloudWatch
**Purpose**: Logs, metrics, basic monitoring

**Configuration**:
- Log Groups:
  - `/aws/lambda/paper-ingestion`
  - `/aws/lambda/batch-processor`
- Retention: 7 days (POC), 14 days (production)
- Basic alarms:
  - OpenSearch disk space > 80%
  - Lambda errors > 5/hour

**Estimated Cost**: ~$2-5/month

### 6. AWS Secrets Manager
**Purpose**: Store OpenSearch credentials

**Secrets**:
- OpenSearch admin credentials
- (Optional) API keys for PubMed access

**Estimated Cost**: ~$1/month ($0.40 per secret)

### 7. Amazon VPC
**Purpose**: Network isolation for OpenSearch

**Configuration**:
```
VPC: 10.0.0.0/16
  └── Private Subnets: 10.0.10.0/24, 10.0.11.0/24
      └── OpenSearch, Lambda (in VPC)
```

**Components**:
- 2 Availability Zones (for production)
- VPC Endpoints for S3, Bedrock (no NAT Gateway needed)
- Security Groups for OpenSearch, Lambda

**Estimated Cost**: ~$15/month (VPC endpoints)

## Deferred Services (Cost Savings)

### ❌ Amazon Neptune - NOT DEPLOYED (Saves $200-300/month)
**Why deferred**:
- Graph relationships stored in OpenSearch for now
- Simple graph traversal via application logic
- Can migrate to Neptune later if complex graph queries needed

### ❌ Application Load Balancer - NOT NEEDED (Saves $20-25/month)
**Why not needed**:
- MCP server runs locally (stdio transport)
- No web API to load balance

### ❌ Amazon ECS/Fargate - MINIMAL USE (Saves $50-100/month)
**Why minimal**:
- Ingestion via Lambda (serverless)
- No API server needed (MCP runs locally)
- Optional: ECS task for bulk ingestion only

### ❌ NAT Gateway - NOT NEEDED (Saves $45-90/month)
**Why not needed**:
- VPC endpoints for S3, Bedrock
- Lambda functions don't need internet access

## Total Estimated Monthly Costs

### POC Environment (Single Node, Minimal Features)
- OpenSearch (t3.small): $30
- S3 (1K papers): $2
- Lambda (light use): $2
- CloudWatch: $2
- Secrets Manager: $1
- VPC Endpoints: $15
- Bedrock (one-time ingestion): $5
- **Total POC: ~$50-60/month**

### Production Environment (HA, 10K Papers)
- OpenSearch (t3.medium x2): $150
- S3 (10K papers): $5
- Lambda (moderate use): $5
- CloudWatch: $5
- Secrets Manager: $1
- VPC Endpoints: $15
- Bedrock (ongoing ingestion): $10/month avg
- **Total Production: ~$190-200/month**

### Deferred Costs (Not Paying Now)
- Neptune: $200-300/month (using OpenSearch instead)
- ALB: $20-25/month (no web API)
- NAT Gateway: $45-90/month (using VPC endpoints)
- ECS: $50-100/month (using Lambda instead)
- **Savings: ~$315-515/month**

## Cost Comparison by Corpus Size

| Papers | OpenSearch | S3 | Bedrock (one-time) | Monthly Total |
|--------|------------|----|--------------------|---------------|
| 100 | $30 | $1 | $0.50 | ~$50 |
| 1,000 | $30 | $2 | $5 | ~$55 |
| 10,000 | $150 | $5 | $50 (one-time) | ~$175 |
| 100,000 | $400 | $20 | $500 (one-time) | ~$450 |

**Note:** Bedrock costs are one-time for initial ingestion, then minimal for new papers.

## Development vs Production Architecture

### Development/POC (Local First)
```
Developer's Laptop:
  ├── MCP Server (local Python process)
  ├── Claude Desktop (calls MCP server)
  └── Docker (local OpenSearch for testing)

AWS (Optional):
  └── [Nothing deployed - test locally first]

Monthly Cost: $0 (just local Bedrock API calls ~$2)
```

### POC Deployment (Validate with Users)
```
User's Laptop:
  ├── MCP Server (via uvx pubmed-graph-rag)
  └── Claude Desktop

AWS Backend:
  ├── OpenSearch (t3.small, single node)
  ├── Lambda (ingestion)
  ├── S3 (papers storage)
  └── Bedrock (embeddings)

Monthly Cost: ~$50-60
```

### Production (Scaled to 10K+ Papers)
```
User's Laptop:
  ├── MCP Server (via uvx pubmed-graph-rag)
  └── Claude Desktop

AWS Backend:
  ├── OpenSearch (t3.medium x2, HA)
  ├── Lambda (ingestion)
  ├── S3 (papers storage)
  └── Bedrock (embeddings)

Monthly Cost: ~$190-200
```

## Cost Optimization Tips

1. **Start Local**: Develop with local Docker OpenSearch ($0/month)
2. **Use VPC Endpoints**: Save $45-90/month on NAT Gateway
3. **Single Node POC**: Start with t3.small single node ($30 vs $150)
4. **Defer Neptune**: Use OpenSearch for simple graph queries (save $200/month)
5. **Lambda over ECS**: Serverless ingestion (save $50-100/month)
6. **S3 Lifecycle**: Move old papers to Glacier (save ~50% storage)
7. **Reserved Instances**: For OpenSearch if running 1+ year (40% savings)

## IAM Roles Summary

### Lambda Execution Role
```
Permissions:
- S3: GetObject, PutObject (papers bucket)
- OpenSearch: ESHttpPost, ESHttpPut
- Bedrock: InvokeModel (Titan Embeddings only)
- CloudWatch: CreateLogGroup, PutLogEvents
- Secrets Manager: GetSecretValue
```

### Developer Role
```
Permissions:
- Full access to all POC resources
- CDK deploy permissions
- CloudFormation management
- OpenSearch access for debugging
```

## Security Groups

**OpenSearch SG**:
- Inbound: 443 from Lambda SG only
- Outbound: All (for cluster communication)

**Lambda SG** (if in VPC):
- Inbound: None needed
- Outbound: All (to OpenSearch, Bedrock via VPC endpoint)

## VPC Endpoints (Critical for Cost Savings)

**Gateway Endpoints** (Free):
- S3 (avoids NAT Gateway)

**Interface Endpoints** ($7.50/month each):
- Bedrock ($7.50/month) - **Recommended**: Saves $45/month in NAT costs
- Secrets Manager ($7.50/month) - **Optional**: Only if using secrets

**Total VPC Endpoint Cost**: ~$15/month (saves $45-90/month in NAT)

## Backup and Disaster Recovery

1. **OpenSearch**: Manual snapshots to S3 (weekly for POC)
2. **S3**: Versioning enabled (automatic)
3. **Infrastructure**: CDK templates in Git

**RTO**: 8 hours (time to restore from scratch)
**RPO**: 7 days (acceptable data loss for POC)

## Deployment Phases

### Phase 1: Local Development ($0/month)
- Docker Compose OpenSearch
- Local testing with 100 papers
- MCP server development
- **Duration**: 2-4 weeks

### Phase 2: POC Deployment ($50/month)
- Deploy single-node OpenSearch to AWS
- Lambda ingestion pipeline
- 1,000 papers corpus
- **Duration**: 4-8 weeks validation

### Phase 3: Production ($190-200/month)
- HA OpenSearch (2 nodes)
- 10,000+ papers corpus
- Monitoring and alarms
- **Duration**: When validated and funded

## Tags for Resource Management

All resources tagged:
```
Project: med-graph-rag
Environment: poc|prod
ManagedBy: cdk
Purpose: mcp-backend
CostCenter: validation
```

## Next Steps

**POC Deployment**:
1. ✅ Develop and test locally (weeks 1-2)
2. ✅ Deploy VPC + OpenSearch (week 3)
3. ✅ Deploy Lambda ingestion (week 3)
4. ✅ Ingest 1,000 papers (week 4)
5. ✅ Test with 10 beta doctors (weeks 5-8)

**Production (if POC succeeds)**:
1. Upgrade to HA OpenSearch
2. Add monitoring and alarms
3. Scale to 10,000+ papers
4. Consider Neptune for complex graph queries
