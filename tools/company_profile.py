"""
ARA-1 Tool: company_profile (Real Integration)

Retrieves static corporate background metadata, sector, industry, and executive details.
Backed by Financial Modeling Prep (FMP) with yfinance fallback.
"""

from typing import Dict, Any
from tools import financial_api


def execute(ticker: str, **kwargs) -> Dict[str, Any]:
    """Execute real company_profile tool."""
    return financial_api.get_company_profile(ticker=ticker)
