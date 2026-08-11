"""
ARA-1 Tool: company_profile

Delegates to tools.financial_api.get_company_profile for real company profile data.
"""

from tools import financial_api


def execute(ticker: str, **kwargs):
    """Execute company_profile tool."""
    return financial_api.get_company_profile(ticker=ticker)
