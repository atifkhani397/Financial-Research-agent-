"""
ARA-1 Tool: earnings_transcript (Real API & Web Search Integration)

Fetches management commentary, Q&A highlights, and forward guidance from earnings calls.

Data Sourcing Strategy & Terms-of-Service Considerations:
  - Primary Tier: Financial Modeling Prep (FMP) official transcript endpoint (/v3/earning_call_transcript).
  - Secondary Tier: Tavily Search API targeting indexed transcript summaries and press releases.
  - Fallback Tier: SEC 10-K/10-Q Item 2 Management's Discussion and Analysis (MD&A).

  Note on Scraping: Direct web scraping of third-party transcript sites (e.g., SeekingAlpha, MotleyFool)
  is avoided to comply with site Terms of Service and prevent runtime fragility due to DOM changes.
"""

import logging
from typing import Any, Dict, Optional, List
from tools import financial_api, web_search

logger = logging.getLogger("ara1.tools.earnings_transcript")


def execute(
    ticker: str,
    year: Optional[int] = None,
    quarter: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Retrieve management commentary, Q&A highlights, and forward guidance for earnings calls.
    """
    ticker_clean = ticker.strip().upper()
    q_str = f"{quarter} " if quarter else ""
    y_str = f"{year} " if year else ""

    key_quotes: List[Dict[str, str]] = []
    guidance: List[Dict[str, str]] = []
    sources: List[str] = []
    data_source = "web_search_tavily"
    is_mock = False

    # 1. Try FMP Transcripts Endpoint if API key is present
    try:
        fmp_params = {"symbol": ticker_clean}
        if year:
            fmp_params["year"] = str(year)
        if quarter:
            fmp_params["quarter"] = quarter

        fmp_data = financial_api.fetch_fmp_endpoint("earning_call_transcript", fmp_params)
        if isinstance(fmp_data, list) and len(fmp_data) > 0:
            call = fmp_data[0]
            content = call.get("content", "")
            if content:
                data_source = "fmp_transcript_api"
                paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

                for p in paragraphs:
                    p_lower = p.lower()
                    if any(k in p_lower for k in ["guidance", "outlook", "expect", "target", "project"]):
                        guidance.append({"source": f"FMP {ticker_clean} {q_str}{y_str}Call", "text": p[:400]})
                    elif len(p) > 50:
                        key_quotes.append({"source": f"FMP {ticker_clean} {q_str}{y_str}Call", "text": p[:400]})

                sources.append(f"FMP Earning Call Transcript ({ticker_clean} {q_str}{y_str})")
    except Exception as e:
        logger.debug(f"FMP transcript endpoint unavailable for {ticker_clean}: {e}")

    # 2. Fallback to Tavily Web Search if FMP yielded no quotes
    if not key_quotes and not guidance:
        query = f"{ticker_clean} {y_str}{q_str}earnings call transcript management commentary guidance highlights"
        search_res = web_search.execute(query=query, max_results=5)
        results = search_res.get("results", [])

        for item in results:
            title = item.get("title", "Web Summary")
            snippet = item.get("snippet", "")
            url = item.get("url", "")
            if url:
                sources.append(url)

            s_lower = snippet.lower()
            if any(k in s_lower for k in ["guidance", "outlook", "expect", "forecast", "margin target"]):
                guidance.append({"source": title, "text": snippet})
            else:
                key_quotes.append({"source": title, "text": snippet})

    return {
        "ticker": ticker_clean,
        "year": year,
        "quarter": quarter,
        "key_quotes": key_quotes[:5],
        "guidance": guidance[:5],
        "sources": list(set(sources))[:5],
        "_source": data_source,
        "_mock": is_mock,
    }
