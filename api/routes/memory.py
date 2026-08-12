"""
ARA-1 API Memory Routes (Day 16)
REST endpoint for semantic long-term memory search over ChromaDB chunks.
"""

from typing import Optional
from fastapi import APIRouter, Query
from api.schemas import MemorySearchResponse

router = APIRouter(prefix="/api/memory", tags=["Long-Term Memory"])


@router.get("/search", response_model=MemorySearchResponse)
async def search_memory(
    q: str = Query(..., description="Semantic search query"),
    top_k: int = Query(5, ge=1, le=20, description="Number of document chunks to retrieve"),
    ticker: Optional[str] = Query(None, description="Optional stock ticker filter"),
    source_type: Optional[str] = Query(None, description="Optional source type filter")
):
    """Searches long-term vector memory (ChromaDB) for chunked findings."""
    from memory.vector_store import VectorStore
    vs = VectorStore()

    results = vs.search(
        query=q,
        top_k=top_k,
        ticker=ticker,
        source_type=source_type
    )

    return MemorySearchResponse(
        query=q,
        results=results,
        count=len(results)
    )
