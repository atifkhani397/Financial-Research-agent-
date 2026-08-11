"""
ARA-1 Tool: financial_data_api

Delegates to tools.financial_api.execute for real financial metrics.
"""

from tools import financial_api


def execute(ticker: str, metric: str = "overview", **kwargs):
    """Execute financial_data_api tool."""
    return financial_api.execute(ticker=ticker, metric=metric, **kwargs)
