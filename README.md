# Medical Graph RAG - MCP Server

A Model Context Protocol (MCP) server that provides advanced medical literature reasoning capabilities to AI assistants.

## The Medical AI Ecosystem Today

AI-assisted medical literature search is already here and doctors use it daily:

**Clinical Decision Support Platforms:**
- **UpToDate** (Wolters Kluwer) - Evidence-based clinical summaries, 3M+ clinician users, recently added GenAI features
- **Glass Health** (YC W21) - AI-powered differential diagnosis and clinical plans
- **OpenEvidence** - Evidence-based answers with citations for medical questions
- **Medwise, iatroX** - AI clinical assistants focused on specific markets

**Basic MCP Servers (10+ exist):**
- Multiple PubMed search servers providing keyword search and abstract retrieval
- Return paper titles, abstracts, and metadata
- Limited to single-paper results, no cross-paper reasoning

These tools excel at **finding individual papers** and **answering straightforward questions**. But they struggle with complex diagnostic reasoning that requires connecting evidence across multiple papers.

## What We Offer: Deep Literature Reasoning

This MCP server fills a critical gap - **multi-hop reasoning across medical literature** for complex clinical questions.

### Core Capabilities

**1. Multi-hop reasoning across papers**
- Follow citation chains to trace how evidence builds
- Connect findings from multiple studies into coherent answers
- Example: "Gene X → Protein Y → Pathway Z → Drug target" across 4 different papers

**2. Surfacing contradictory evidence**
- Automatically detect when papers disagree on the same relationship
- Don't hide conflicts - present both sides with evidence strength
- Example: "Paper A (2023, n=500) shows benefit; Paper B (2024, n=1200) found no effect"

**3. Following diagnostic chains**
- Trace symptom → rare condition → cited treatment studies
- The kind of "detective work" that helped diagnose complex cases
- Example: "Elevated ALP + fatigue → Primary biliary cholangitis → Ursodeoxycholic acid studies"

**4. Provenance at the paragraph level**
- Every claim traces back to specific papers, sections, and paragraphs
- Not just "according to PMC123456" but "PMC123456, Results section, paragraph 4"
- Enables doctors to verify and dig deeper

## Architecture: MCP Server + Graph RAG Backend

```
┌─────────────────────────────────────────────────────────────┐
│  Doctor using Claude Desktop / Glass Health / Other AI      │
│  "Why might patient have elevated ALP but normal AST/ALT?"  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                    ┌─────▼─────┐
                    │    MCP    │
                    │   Server  │ ← pubmed-graph-rag
                    │  (stdio)  │
                    └─────┬─────┘
                          │
         ┌────────────────┴────────────────┐
         │                                 │
    ┌────▼────┐                      ┌────▼────┐
    │OpenSearch│                      │ Bedrock │
    │ Vector + │                      │Embeddings│
    │ Graph    │                      │   +LLM  │
    └──────────┘                      └─────────┘
```

**Backend (80% of the work - already built):**
- JATS XML parser for PubMed Central papers
- OpenSearch for vector + keyword + graph search
- AWS Bedrock for embeddings (Titan V2) and LLM queries
- Entity extraction and relationship detection
- Multi-hop graph traversal algorithms

**MCP Layer (20% - thin wrapper):**
- Exposes backend capabilities as MCP tools
- Packaged for `uvx` distribution
- Works with any MCP-compatible AI assistant

## MCP Tools

The server exposes three tools to AI assistants:

### `pubmed_graph_search`
Multi-hop reasoning across PubMed papers with automatic provenance tracking.

**Input:**
```json
{
  "query": "PARP inhibitors for BRCA mutations",
  "max_hops": 3,
  "include_contradictions": true,
  "evidence_threshold": 0.7
}
```

**Returns:**
- Top papers with relevance scores
- Multi-hop reasoning chains showing connections
- Contradictory evidence flagged with details
- Paragraph-level citations for every claim

### `diagnostic_chain_trace`
Follow symptom → diagnosis → treatment chains through literature.

**Input:**
```json
{
  "initial_finding": "isolated elevated alkaline phosphatase",
  "depth": 3,
  "filter_by_recency": true
}
```

**Returns:**
- Diagnostic pathway tree from symptom to conditions
- Supporting evidence with confidence scores
- Alternative diagnostic paths considered
- Treatment studies for identified conditions

### `evidence_contradiction_check`
Find conflicting evidence on a medical claim.

**Input:**
```json
{
  "claim": "aspirin reduces cardiovascular risk in diabetics",
  "time_window": "last_5_years",
  "min_studies": 2
}
```

**Returns:**
- Papers supporting the claim
- Papers contradicting the claim
- Meta-analyses and systematic reviews
- Study quality indicators for evaluation

## Installation

**For Doctors / End Users:**
```bash
# Install via uvx
uvx pubmed-graph-rag

# Add to Claude Desktop config
# Edit: ~/.config/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "pubmed-graph-rag": {
      "command": "uvx",
      "args": ["pubmed-graph-rag"]
    }
  }
}
```

**For Developers:**
```bash
# Clone repository
git clone https://github.com/wware/med-graph-rag
cd med-graph-rag

# Install in development mode
pip install -e .

# Run locally with test data
python -m med_graph_rag.mcp_server
```

## Local Development

The system can run entirely locally for development:

```bash
# Start OpenSearch locally
docker-compose up -d

# Download sample papers
python -m med_graph_rag.scripts.download_papers \
  --query "breast cancer BRCA1" \
  --max-results 100

# Run ingestion pipeline
python -m med_graph_rag.ingestion.pipeline

# Test MCP server
python -m med_graph_rag.mcp_server
```

See [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) for complete setup instructions.

## Technology Stack

- **Python 3.12+**: Core implementation
- **MCP SDK**: Model Context Protocol server implementation
- **OpenSearch**: Vector + keyword + graph search
- **AWS Bedrock**: Titan Embeddings V2, Claude for query understanding
- **JATS XML Parser**: PubMed Central paper ingestion
- **Docker**: Local development environment

## Competitive Advantage

**vs. Basic PubMed MCP Servers (10+ exist):**
- They do: Keyword search, return abstracts
- We add: Multi-hop reasoning, contradiction detection, diagnostic chains, paragraph provenance

**vs. Clinical Platforms (Glass Health, UpToDate):**
- They do: Clinical summaries, differential diagnosis
- We add: Deep literature reasoning they can integrate as backend infrastructure

**vs. Traditional Search (PubMed):**
- They do: Find individual papers
- We add: Connect evidence across papers, surface contradictions automatically

## Project Status

**✅ Complete:**
- JATS XML parsing and ingestion pipeline
- OpenSearch integration with vector + keyword search
- Entity extraction and relationship detection
- Multi-hop query algorithms
- Provenance tracking infrastructure

**🚧 In Progress:**
- MCP server wrapper implementation
- Tool schema definitions and validation
- PyPI packaging for uvx distribution

**📋 Planned:**
- Full Neptune graph database integration (currently using OpenSearch)
- Advanced NER models (SciSpacy, Comprehend Medical)
- Query performance optimization
- Contradiction detection algorithms

## Documentation

- [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) - Local setup guide
- [knowledge_graph_schema.md](knowledge_graph_schema.md) - Graph schema documentation
- [data-flow-architecture.md](data-flow-architecture.md) - System architecture details
- [AWS_BOM.md](AWS_BOM.md) - AWS deployment costs and configuration
- [MONETIZE.md](MONETIZE.md) - Business strategy and revenue models
- [TECH_CHAT.md](TECH_CHAT.md) - Technical architecture discussion

## Contributing

Contributions welcome! The project needs:
- MCP server implementation expertise
- Medical NLP/entity extraction improvements
- Graph algorithm optimization
- Documentation and examples

## License

[To be determined]

## References

- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [PubMed Central](https://www.ncbi.nlm.nih.gov/pmc/) - Medical paper source
- [JATS](https://jats.nlm.nih.gov/) - Journal Article Tag Suite XML
- [AWS Bedrock](https://aws.amazon.com/bedrock/) - Foundation models
- [OpenSearch](https://opensearch.org/) - Search and analytics engine
