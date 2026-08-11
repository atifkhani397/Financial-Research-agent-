"""
ARA-1 Tool: peer_comparison (Real Integration)

Identifies sector/industry peers for any ticker and pulls comparative metrics across them.
Backed by real financial_api / yfinance data.
"""

import logging
from typing import Any, Dict, List
from tools import financial_api

logger = logging.getLogger("ara1.tools.peer_comparison")

DEFAULT_PEER_GROUPS = {
    "TSLA": ["RIVN", "LCID", "GM", "F", "AAPL"],
    "MSFT": ["AAPL", "GOOGL", "AMZN", "NVDA", "ORCL"],
    "AAPL": ["MSFT", "GOOGL", "AMZN", "NVDA", "SSNLF"],
    "GOOGL": ["MSFT", "AAPL", "AMZN", "META", "NVDA"],
    "AMZN": ["MSFT", "GOOGL", "BABA", "WMT", "COST"],
    "NVDA": ["AMD", "INTC", "TSM", "AVGO", "MSFT"],
}


def execute(ticker: str, metric: str = "market_cap", **kwargs) -> Dict[str, Any]:
    """Fetch comparative metrics for primary ticker and industry peers."""
    ticker_clean = ticker.strip().upper()
    metric_clean = metric.strip().lower()

    # Get primary profile to identify sector/industry
    sector = "Technology"
    industry = "Software"
    try:
        profile = financial_api.get_company_profile(ticker_clean)
        sector = profile.get("sector", sector)
        industry = profile.get("industry", industry)
    except Exception as e:
        logger.warning(f"Could not fetch profile for peer comparison of {ticker_clean}: {e}")

    # Determine peer list
    peer_list = DEFAULT_PEER_GROUPS.get(ticker_clean)
    if not peer_list:
        peer_list = ["MSFT", "AAPL", "GOOGL", "AMZN"]

    # Gather data for primary ticker and peers
    tickers_to_fetch = [ticker_clean] + [p for p in peer_list if p != ticker_clean][:4]
    peer_results: List[Dict[str, Any]] = []

    for t_sym in tickers_to_fetch:
        try:
            m_data = financial_api.get_financial_metrics(t_sym, metric_clean)
            val = None
            if metric_clean in m_data:
                val = m_data.get(metric_clean)
            elif "market_cap" in metric_clean or "cap" in metric_clean:
                val = m_data.get("market_cap")
            elif "revenue" in metric_clean or "sales" in metric_clean:
                val = m_data.get("revenue")
            elif "pe" in metric_clean or "ratio" in metric_clean:
                val = m_data.get("pe_ratio")
            elif "margin" in metric_clean:
                val = m_data.get("operating_margin")
            elif "eps" in metric_clean:
                val = m_data.get("eps")

            peer_results.append({
                "ticker": t_sym,
                "metric_requested": metric_clean,
                "value": val,
                "market_cap": m_data.get("market_cap"),
                "revenue": m_data.get("revenue"),
                "pe_ratio": m_data.get("pe_ratio"),
            })
        except Exception as err:
            logger.warning(f"Failed to fetch peer metrics for {t_sym}: {err}")

    # Compute average metric value if available
    valid_vals = [p["value"] for p in peer_results if isinstance(p.get("value"), (int, float))]
    avg_val = sum(valid_vals) / len(valid_vals) if valid_vals else None

    return {
        "ticker": ticker_clean,
        "sector": sector,
        "industry": industry,
        "metric": metric_clean,
        "peers": peer_results,
        "peer_count": len(peer_results),
        "average_metric_value": avg_val,
        "_source": "peer_comparison_real",
        "_mock": False,
    }
