"""
ARA-1 Vector DB Search Tool

Searches long-term vector memory (Chroma) for stored findings,
supporting semantic query search and metadata filtering.
"""

from typing import Optional, Dict, Any
from memory.vector_store import VectorStore, get_vector_store


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
    vs = get_vector_store()
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
