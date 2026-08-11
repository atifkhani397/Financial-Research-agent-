"""Mock stub for company_profile tool — returns realistic Microsoft data."""


def execute(**kwargs):
    """Return structurally realistic mock company profile data."""
    ticker = kwargs.get("ticker", "UNKNOWN")

    MOCK_DATA = {
        "MSFT": {
            "ticker": "MSFT",
            "name": "Microsoft Corporation",
            "exchange": "NASDAQ",
            "sector": "Technology",
            "industry": "Software—Infrastructure",
            "country": "United States",
            "website": "https://www.microsoft.com",
            "description": (
                "Microsoft Corporation develops and supports software, services, "
                "devices, and solutions worldwide. The company operates through "
                "three segments: Productivity and Business Processes, Intelligent "
                "Cloud, and More Personal Computing. The Productivity and Business "
                "Processes segment offers Office, Exchange, SharePoint, Microsoft "
                "Teams, Office 365 Security and Compliance, Microsoft Viva, and "
                "Microsoft 365 Copilot. The Intelligent Cloud segment offers "
                "Azure and other cloud services, SQL Server, Windows Server, "
                "Visual Studio, System Center, GitHub, and Nuance. The More "
                "Personal Computing segment offers Windows, devices (Surface), "
                "gaming (Xbox), and search (Bing)."
            ),
            "ceo": "Satya Nadella",
            "full_time_employees": 228000,
            "founded": 1975,
            "headquarters": "Redmond, Washington",
            "market_cap": 3120000000000,
            "isin": "US5949181045",
            "cusip": "594918104",
            "executives": [
                {"name": "Satya Nadella", "title": "Chairman & CEO"},
                {"name": "Amy E. Hood", "title": "Executive VP & CFO"},
                {"name": "Bradford L. Smith", "title": "Vice Chair & President"},
                {"name": "Judson B. Althoff", "title": "Executive VP & Chief Commercial Officer"},
                {"name": "Rajesh Jha", "title": "Executive VP, Experiences & Devices"},
                {"name": "Scott Guthrie", "title": "Executive VP, Cloud & AI"},
            ],
            "_source": "company_profile",
            "_mock": True,
        },
    }

    default = {
        "ticker": ticker,
        "name": f"{ticker} Corporation",
        "sector": "Unknown",
        "industry": "Unknown",
        "description": f"Mock profile for {ticker}",
        "executives": [],
        "_source": "company_profile",
        "_mock": True,
    }

    return MOCK_DATA.get(ticker.upper(), default)
