"""
ARA-1 5-Tier Source Reliability Hierarchy Module
Defines source reliability tiers (Section A4.1) per Section D3 layout.
"""

from typing import Dict

# 5-Tier Source Reliability Hierarchy
SOURCE_HIERARCHY: Dict[str, int] = {
    "sec_filing_search": 1,      # Tier 1: SEC EDGAR (10-K, 10-Q) - Highest Authority
    "sec_edgar": 1,
    "financial_data_api": 2,     # Tier 2: Financial Data APIs (FMP / AlphaVantage)
    "company_profile": 2,
    "peer_comparison": 2,
    "earnings_transcript": 3,   # Tier 3: Management Commentary
    "news_sentiment": 4,        # Tier 4: Financial News Outlets
    "web_search": 5,            # Tier 5: General Web Content - Lowest Authority
}


def get_source_tier(source_name: str) -> int:
    """Return numeric tier (1-5) for a given source name."""
    s_lower = source_name.lower().strip()
    for key, tier in SOURCE_HIERARCHY.items():
        if key in s_lower:
            return tier
    return 5
