"""Mock stub for web_search tool — returns realistic Microsoft search results."""


def execute(**kwargs):
    """Return structurally realistic web search results."""
    query = kwargs.get("query", "")

    if "microsoft" in query.lower() or "msft" in query.lower():
        return {
            "query": query,
            "results": [
                {
                    "title": "Microsoft Corporation (MSFT) Stock Price & News",
                    "url": "https://finance.yahoo.com/quote/MSFT",
                    "snippet": "Microsoft Corporation market cap $3.12T. Current price $419.72. 52-week range $388.45 - $468.35. YTD return +12.4%.",
                    "source": "Yahoo Finance",
                },
                {
                    "title": "Microsoft Reports FY25 Q4 Results - Revenue $64.7B",
                    "url": "https://www.microsoft.com/en-us/investor",
                    "snippet": "Microsoft Q4 FY2025 revenue was $64.7 billion, up 15% YoY. Azure and cloud services revenue grew 29%. Microsoft Cloud revenue surpassed $40 billion.",
                    "source": "Microsoft Investor Relations",
                },
                {
                    "title": "MSFT: Microsoft's AI Strategy Is Paying Off",
                    "url": "https://www.bloomberg.com/news/articles/msft-ai-strategy",
                    "snippet": "Microsoft's investment in OpenAI and integration of Copilot AI across its product suite is driving revenue growth and competitive differentiation.",
                    "source": "Bloomberg",
                },
            ],
            "total_results": 3,
            "_source": "web_search",
            "_mock": True,
        }

    return {
        "query": query,
        "results": [
            {
                "title": f"Search results for: {query}",
                "url": "https://example.com",
                "snippet": f"Mock search results for query: {query}",
                "source": "Mock Search",
            },
        ],
        "total_results": 1,
        "_source": "web_search",
        "_mock": True,
    }
