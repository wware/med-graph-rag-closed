"""
Medical Knowledge Graph API

FastAPI-based REST API for querying the medical knowledge graph.
Provides endpoints for semantic search, keyword search, and hybrid search.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.client.medical_papers_client import MedicalPapersClient

# Initialize FastAPI app
app = FastAPI(
    title="Medical Knowledge Graph API",
    description="API for querying medical research papers using hybrid vector + keyword search",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize client
opensearch_host = os.getenv('OPENSEARCH_HOST', 'localhost')
opensearch_port = int(os.getenv('OPENSEARCH_PORT', '9200'))

try:
    client = MedicalPapersClient(
        opensearch_host=opensearch_host,
        opensearch_port=opensearch_port
    )
except Exception as e:
    print(f"Warning: Could not connect to OpenSearch: {e}")
    client = None


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for queries"""
    query: str = Field(..., description="Natural language query", min_length=1)
    k: int = Field(10, description="Number of results to return", ge=1, le=100)
    filter_sections: Optional[List[str]] = Field(None, description="Filter by paper sections")
    search_type: str = Field('hybrid', description="Type of search: semantic, keyword, or hybrid")


class SearchResult(BaseModel):
    """Single search result"""
    title: str
    pmc_id: Optional[str]
    pmid: Optional[str]
    doi: Optional[str]
    chunk_text: str
    section: Optional[str]
    score: float
    authors: Optional[str]
    journal: Optional[str]
    publication_date: Optional[str]


class QueryResponse(BaseModel):
    """Response model for queries"""
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    search_type: str


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Medical Knowledge Graph API",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    opensearch_status = "connected" if client else "disconnected"
    return {
        "status": "healthy",
        "opensearch": opensearch_status
    }


@app.post("/api/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Execute a query against the medical knowledge graph

    Supports three search types:
    - semantic: Vector similarity search using embeddings
    - keyword: Traditional keyword/BM25 search
    - hybrid: Combines semantic and keyword search (recommended)
    """
    if not client:
        raise HTTPException(status_code=503, detail="OpenSearch client not available")

    try:
        # Execute search based on type
        if request.search_type == 'semantic':
            results = client.semantic_search(
                query=request.query,
                k=request.k,
                filter_sections=request.filter_sections
            )
        elif request.search_type == 'keyword':
            results = client.keyword_search(
                query=request.query,
                size=request.k
            )
        elif request.search_type == 'hybrid':
            results = client.hybrid_search(
                query=request.query,
                k=request.k
            )
        else:
            raise HTTPException(status_code=400, detail=f"Invalid search_type: {request.search_type}")

        return QueryResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            search_type=request.search_type
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")


@app.get("/api/v1/search/semantic")
async def semantic_search(
    q: str = Query(..., description="Search query"),
    k: int = Query(10, description="Number of results", ge=1, le=100),
    sections: Optional[str] = Query(None, description="Comma-separated list of sections to filter")
):
    """Semantic search using vector embeddings"""
    if not client:
        raise HTTPException(status_code=503, detail="OpenSearch client not available")

    filter_sections = sections.split(',') if sections else None

    try:
        results = client.semantic_search(
            query=q,
            k=k,
            filter_sections=filter_sections
        )

        return QueryResponse(
            query=q,
            results=results,
            total_results=len(results),
            search_type='semantic'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/api/v1/search/keyword")
async def keyword_search(
    q: str = Query(..., description="Search query"),
    size: int = Query(10, description="Number of results", ge=1, le=100)
):
    """Keyword search using BM25"""
    if not client:
        raise HTTPException(status_code=503, detail="OpenSearch client not available")

    try:
        results = client.keyword_search(query=q, size=size)

        return QueryResponse(
            query=q,
            results=results,
            total_results=len(results),
            search_type='keyword'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/api/v1/search/hybrid")
async def hybrid_search(
    q: str = Query(..., description="Search query"),
    k: int = Query(10, description="Number of results", ge=1, le=100)
):
    """Hybrid search combining semantic and keyword"""
    if not client:
        raise HTTPException(status_code=503, detail="OpenSearch client not available")

    try:
        results = client.hybrid_search(query=q, k=k)

        return QueryResponse(
            query=q,
            results=results,
            total_results=len(results),
            search_type='hybrid'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
