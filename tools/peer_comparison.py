"""Mock stub for peer_comparison tool — returns realistic comparison data."""


def execute(**kwargs):
    """Return structurally realistic peer comparison data."""
    ticker = kwargs.get("ticker", "UNKNOWN")
    metric = kwargs.get("metric", "market_cap")

    if ticker.upper() == "MSFT":
        return {
            "ticker": "MSFT",
            "metric": metric,
            "peers": [
                {"ticker": "AAPL", "name": "Apple Inc.", "value": 3450000000000},
                {"ticker": "MSFT", "name": "Microsoft Corp.", "value": 3120000000000},
                {"ticker": "GOOGL", "name": "Alphabet Inc.", "value": 2180000000000},
                {"ticker": "AMZN", "name": "Amazon.com Inc.", "value": 2050000000000},
                {"ticker": "NVDA", "name": "NVIDIA Corp.", "value": 2950000000000},
            ],
            "msft_rank": 2,
            "msft_percentile": 95,
            "_source": "peer_comparison",
            "_mock": True,
        }

    return {
        "ticker": ticker,
        "metric": metric,
        "peers": [],
        "note": f"No mock peer data for {ticker}",
        "_source": "peer_comparison",
        "_mock": True,
    }
