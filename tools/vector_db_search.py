"""Mock stub for vector_db_search tool."""


def execute(**kwargs):
    """Return mock vector DB search results."""
    query = kwargs.get("query", "")
    top_k = kwargs.get("top_k", 5)

    return {
        "query": query,
        "top_k": top_k,
        "results": [],
        "note": "No previous session data in vector DB (fresh session).",
        "_source": "vector_db_search",
        "_mock": True,
    }
