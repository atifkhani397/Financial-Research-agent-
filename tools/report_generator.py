"""Mock stub for report_generator tool."""


def execute(**kwargs):
    """Return a formatted report structure."""
    sections = kwargs.get("sections", [])

    return {
        "report_format": "markdown",
        "sections_received": len(sections),
        "sections": sections,
        "status": "generated",
        "_source": "report_generator",
        "_mock": True,
    }
