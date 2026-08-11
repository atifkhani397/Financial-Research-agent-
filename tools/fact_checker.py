"""Mock stub for fact_checker tool."""


def execute(**kwargs):
    """Return structurally realistic fact check results."""
    claim = kwargs.get("claim", "")
    source_context = kwargs.get("source_context", "")

    return {
        "claim": claim,
        "verified": True,
        "confidence": 0.92,
        "source_match": True,
        "notes": "Claim is consistent with the provided source context.",
        "_source": "fact_checker",
        "_mock": True,
    }
