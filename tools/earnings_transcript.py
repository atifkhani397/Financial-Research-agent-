"""Mock stub for earnings_transcript tool — returns realistic Microsoft earnings data."""


def execute(**kwargs):
    """Return structurally realistic earnings transcript data."""
    ticker = kwargs.get("ticker", "UNKNOWN")
    year = kwargs.get("year", 2025)
    quarter = kwargs.get("quarter", "Q4")

    if ticker.upper() == "MSFT":
        return {
            "ticker": "MSFT",
            "year": year,
            "quarter": quarter,
            "date": "2025-07-22",
            "participants": [
                "Satya Nadella - Chairman & CEO",
                "Amy Hood - Executive VP & CFO",
                "Brett Iversen - VP, Investor Relations",
            ],
            "key_quotes": [
                {
                    "speaker": "Satya Nadella",
                    "quote": "We are seeing strong and accelerating demand for our AI platform. Azure AI services revenue more than doubled year-over-year as customers move from experimentation to production deployment.",
                },
                {
                    "speaker": "Amy Hood",
                    "quote": "Commercial remaining performance obligation increased 21% and 22% in constant currency to $295 billion, demonstrating strong long-term demand signals across our cloud portfolio.",
                },
                {
                    "speaker": "Satya Nadella",
                    "quote": "Copilot is becoming the UI for AI. We now have over 2.5 million Copilot users across enterprise customers, with usage growing at triple-digit rates quarter-over-quarter.",
                },
            ],
            "guidance": {
                "next_quarter_revenue": "We expect Q1 FY2026 revenue between $67.2B and $68.5B.",
                "azure_growth_outlook": "We expect Azure revenue growth to accelerate in Q1 driven by continued AI infrastructure buildout.",
                "capex_outlook": "Capital expenditures will increase sequentially as we expand cloud and AI capacity globally.",
            },
            "_source": "earnings_transcript",
            "_mock": True,
        }

    return {
        "ticker": ticker,
        "year": year,
        "quarter": quarter,
        "participants": [],
        "key_quotes": [],
        "guidance": {},
        "note": f"No mock transcript for {ticker}",
        "_source": "earnings_transcript",
        "_mock": True,
    }
