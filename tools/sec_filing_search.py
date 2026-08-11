"""
ARA-1 Tool: sec_filing_search

Delegates to tools.sec_edgar for real SEC EDGAR API search.
"""

from tools import sec_edgar


def execute(**kwargs):
    """Execute real SEC EDGAR filing search."""
    return sec_edgar.execute(**kwargs)
