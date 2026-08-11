"""Mock stub for sec_filing_search tool — returns realistic Microsoft SEC data."""


def execute(**kwargs):
    """Return structurally realistic SEC filing search results."""
    ticker = kwargs.get("ticker", "UNKNOWN")
    filing_type = kwargs.get("filing_type", "10-K")
    year = kwargs.get("year")

    if ticker.upper() == "MSFT" and filing_type == "10-K":
        return {
            "ticker": "MSFT",
            "filing_type": "10-K",
            "fiscal_year": year or 2025,
            "filed_date": "2025-07-30",
            "accession_number": "0000950170-25-089741",
            "highlights": {
                "total_revenue": 245122000000,
                "operating_income": 110088000000,
                "net_income": 88523000000,
                "total_assets": 512163000000,
                "total_liabilities": 205753000000,
                "shareholders_equity": 306410000000,
                "cash_and_equivalents": 75534000000,
                "risk_factors_summary": (
                    "Key risks include: intense competition in cloud and AI markets, "
                    "regulatory scrutiny of AI partnerships and acquisitions, "
                    "cybersecurity threats, dependence on continued enterprise "
                    "digital transformation spending, foreign currency fluctuations, "
                    "and potential disruption from emerging technologies."
                ),
                "business_segments": [
                    {
                        "name": "Productivity and Business Processes",
                        "revenue": 80500000000,
                        "operating_income": 38200000000,
                    },
                    {
                        "name": "Intelligent Cloud",
                        "revenue": 105700000000,
                        "operating_income": 49100000000,
                    },
                    {
                        "name": "More Personal Computing",
                        "revenue": 58922000000,
                        "operating_income": 22788000000,
                    },
                ],
            },
            "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=MSFT&type=10-K",
            "_source": "sec_filing_search",
            "_mock": True,
        }

    if ticker.upper() == "MSFT" and filing_type == "10-Q":
        return {
            "ticker": "MSFT",
            "filing_type": "10-Q",
            "quarter": "Q4 FY2025",
            "filed_date": "2025-07-22",
            "highlights": {
                "quarterly_revenue": 64727000000,
                "quarterly_net_income": 24108000000,
                "azure_growth_yoy": 0.29,
            },
            "_source": "sec_filing_search",
            "_mock": True,
        }

    return {
        "ticker": ticker,
        "filing_type": filing_type,
        "year": year,
        "results": [],
        "note": f"No mock filings for {ticker} {filing_type}",
        "_source": "sec_filing_search",
        "_mock": True,
    }
