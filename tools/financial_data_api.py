"""Mock stub for financial_data_api tool — returns realistic Microsoft financials."""


def execute(**kwargs):
    """Return structurally realistic financial data."""
    ticker = kwargs.get("ticker", "UNKNOWN")
    metric = kwargs.get("metric", "overview")

    MSFT_METRICS = {
        "revenue": {
            "ticker": "MSFT",
            "metric": "revenue",
            "value": 245122000000,
            "formatted": "$245.1B",
            "period": "FY2025 (TTM)",
            "currency": "USD",
            "yoy_growth": 0.156,
            "source_note": "Financial Modeling Prep API",
        },
        "net_income": {
            "ticker": "MSFT",
            "metric": "net_income",
            "value": 88523000000,
            "formatted": "$88.5B",
            "period": "FY2025 (TTM)",
            "currency": "USD",
            "yoy_growth": 0.219,
        },
        "pe_ratio": {
            "ticker": "MSFT",
            "metric": "pe_ratio",
            "value": 35.2,
            "period": "Current",
            "comparison": {"sector_avg": 28.4, "sp500_avg": 23.1},
        },
        "market_cap": {
            "ticker": "MSFT",
            "metric": "market_cap",
            "value": 3120000000000,
            "formatted": "$3.12T",
            "rank": 2,
            "as_of": "2025-08-10",
        },
        "eps": {
            "ticker": "MSFT",
            "metric": "eps",
            "value": 11.89,
            "period": "FY2025 (TTM)",
            "diluted": True,
        },
        "dividend_yield": {
            "ticker": "MSFT",
            "metric": "dividend_yield",
            "value": 0.0072,
            "formatted": "0.72%",
            "annual_dividend": 3.32,
        },
        "overview": {
            "ticker": "MSFT",
            "metric": "overview",
            "revenue": 245122000000,
            "net_income": 88523000000,
            "pe_ratio": 35.2,
            "market_cap": 3120000000000,
            "eps": 11.89,
            "dividend_yield": 0.0072,
            "debt_to_equity": 0.29,
            "roe": 0.389,
            "operating_margin": 0.449,
            "free_cash_flow": 74073000000,
            "period": "FY2025 (TTM)",
        },
    }

    if ticker.upper() == "MSFT":
        data = MSFT_METRICS.get(metric.lower(), MSFT_METRICS["overview"])
    else:
        data = {
            "ticker": ticker,
            "metric": metric,
            "value": None,
            "note": f"Mock data not available for {ticker}/{metric}",
        }

    data["_source"] = "financial_data_api"
    data["_mock"] = True
    return data
