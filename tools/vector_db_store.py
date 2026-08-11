"""Mock stub for vector_db_store tool."""


def execute(**kwargs):
    """Return mock vector DB store confirmation."""
    content = kwargs.get("content", "")
    metadata = kwargs.get("metadata", {})

    return {
        "stored": True,
        "content_length": len(content),
        "metadata": metadata,
        "chunk_id": "mock-chunk-001",
        "_source": "vector_db_store",
        "_mock": True,
    }
