"""
ARA-1 Tool: peer_comparison (Real Integration)

Compares a ticker's metrics against industry peers using real financial_api data.
"""

from typing import Any, Dict
from tools import financial_api


def execute(ticker: str, metric: str = "market_cap", **kwargs) -> Dict[str, Any]:
    """Fetch comparative metrics for primary ticker and industry peers."""
    ticker_clean = ticker.strip().upper()
    metric_clean = metric.strip().lower()

    # Define standard peer groups
    peers_map = {
        "MSFT": ["AAPL", "GOOGL", "AMZN", "NVDA", "ORCL"],
        "AAPL": ["MSFT", "GOOGL", "AMZN", "NVDA", "SSNLF"],
        "GOOGL": ["MSFT", "AAPL", "AMZN", "META", "NVDA"],
        "NVDA": ["AMD", "INTC", "TSM", "AVGO", "MSFT"],
    }
    peer_list = peers_map.get(ticker_clean, ["MSFT", "AAPL", "GOOGL", "AMZN"])

    primary_data = financial_api.get_financial_metrics(ticker_clean, metric_clean)

    peer_results = []
    # Fetch primary ticker
    peer_results.append({
        "ticker": ticker_clean,
        "name": f"{ticker_clean} Corp",
        "value": primary_data.get("market_cap") if metric_clean == "market_cap" else primary_data.get("revenue"),
    })

    # Fetch peers
    for p_ticker in peer_list[:4]:
        if p_ticker == ticker_clean:
            continue
        try:
            p_data = financial_api.get_financial_metrics(p_ticker, metric_clean)
            val = p_data.get("market_cap") if metric_clean == "market_cap" else p_data.get("revenue")
            peer_results.append({"ticker": p_ticker, "name": f"{p_ticker} Corp", "value": val})
        except Exception:
            pass

    return {
        "ticker": ticker_clean,
        "metric": metric_clean,
        "peers": peer_results,
        "_source": "peer_comparison_real",
        "_mock": False,
    }
