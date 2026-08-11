"""
ARA-1 Vector DB Search Tool

Searches long-term vector memory (Chroma) for stored findings,
supporting semantic query search and metadata filtering.
"""

from typing import Optional, Dict, Any
from memory.vector_store import VectorStore

# Module-level VectorStore instance
_vector_store_instance: Optional[VectorStore] = None


def _get_vector_store() -> VectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance


def execute(
    query: str,
    top_k: int = 5,
    ticker: Optional[str] = None,
    source_type: Optional[str] = None,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Execute semantic search against the long-term Chroma vector store."""
    vs = _get_vector_store()
    results = vs.search(
        query=query,
        top_k=top_k,
        ticker=ticker,
        source_type=source_type,
        date_start=date_start,
        date_end=date_end,
    )

    return {
        "query": query,
        "top_k": top_k,
        "results_count": len(results),
        "results": results,
        "_source": "vector_db_search",
        "_mock": False,
    }
