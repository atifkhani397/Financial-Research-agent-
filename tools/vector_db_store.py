"""
ARA-1 Vector DB Store Tool

Embeds and stores findings into long-term vector memory (Chroma)
with structural chunking and Day 1 metadata tagging.
"""

from typing import Dict, Any, Optional
from memory.vector_store import VectorStore, get_vector_store


def execute(
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Store findings into Chroma vector store with structural chunking."""
    vs = get_vector_store()
    meta = metadata or {}

    ticker = meta.get("ticker", kwargs.get("ticker", ""))
    source_type = meta.get("source_type", kwargs.get("source_type", ""))
    date = meta.get("date", kwargs.get("date", ""))
    confidence = float(meta.get("confidence", kwargs.get("confidence", 1.0)))
    verified = bool(meta.get("verified", kwargs.get("verified", True)))
    researcher_session = meta.get("researcher_session", kwargs.get("researcher_session", ""))
    headline = meta.get("headline", kwargs.get("headline", ""))

    doc_ids = vs.chunk_and_store(
        content=content,
        ticker=ticker,
        source_type=source_type,
        date=date,
        confidence=confidence,
        verified=verified,
        researcher_session=researcher_session,
        headline=headline,
    )

    return {
        "stored": True,
        "chunk_count": len(doc_ids),
        "doc_ids": doc_ids,
        "content_length": len(content),
        "metadata": {
            "ticker": ticker,
            "source_type": source_type,
            "date": date,
            "confidence": confidence,
            "verified": verified,
            "researcher_session": researcher_session,
        },
        "_source": "vector_db_store",
        "_mock": False,
    }
