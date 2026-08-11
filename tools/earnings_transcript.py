"""
ARA-1 Tool: earnings_transcript (Real Integration via Tavily/SEC)

Fetches earnings call transcript commentary and forward guidance using real web/SEC search.
"""

from typing import Any, Dict, Optional
from tools import web_search


def execute(ticker: str, year: Optional[int] = None, quarter: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Retrieve management commentary and forward guidance for earnings calls."""
    ticker_clean = ticker.strip().upper()
    q_str = f"{quarter} " if quarter else ""
    y_str = f"{year} " if year else ""
    query = f"{ticker_clean} {y_str}{q_str}earnings call transcript management commentary guidance highlights"

    search_res = web_search.execute(query=query, max_results=4)
    results = search_res.get("results", [])

    quotes = []
    guidance = []
    for item in results:
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        if "guidance" in snippet.lower() or "outlook" in snippet.lower() or "expect" in snippet.lower():
            guidance.append({"source": title, "text": snippet})
        else:
            quotes.append({"source": title, "text": snippet})

    return {
        "ticker": ticker_clean,
        "year": year,
        "quarter": quarter,
        "query": query,
        "key_quotes": quotes[:3],
        "guidance": guidance[:3],
        "sources": [r.get("url") for r in results if r.get("url")],
        "_source": "earnings_transcript_real",
        "_mock": False,
    }
