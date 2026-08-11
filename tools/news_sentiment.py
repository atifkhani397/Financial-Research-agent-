"""Mock stub for news_sentiment tool — returns realistic Microsoft news data."""


def execute(**kwargs):
    """Return structurally realistic news sentiment data."""
    ticker = kwargs.get("ticker", "UNKNOWN")
    days_back = kwargs.get("days_back", 7)

    if ticker.upper() == "MSFT":
        return {
            "ticker": "MSFT",
            "period": f"Last {days_back} days",
            "overall_sentiment": "positive",
            "sentiment_score": 0.72,
            "articles_analyzed": 47,
            "top_stories": [
                {
                    "title": "Microsoft Azure Revenue Surges 29% as AI Demand Accelerates",
                    "source": "Reuters",
                    "date": "2025-08-08",
                    "sentiment": "very_positive",
                    "score": 0.91,
                    "summary": "Microsoft reported Azure cloud revenue growth of 29% year-over-year, driven by strong enterprise adoption of AI services and Copilot integrations.",
                },
                {
                    "title": "Microsoft Expands Copilot AI to All Office 365 Enterprise Plans",
                    "source": "Bloomberg",
                    "date": "2025-08-06",
                    "sentiment": "positive",
                    "score": 0.78,
                    "summary": "Microsoft announced that its AI-powered Copilot assistant will be included in all Office 365 enterprise subscription tiers starting Q4 2025.",
                },
                {
                    "title": "Antitrust Regulators Eye Microsoft's AI Partnerships",
                    "source": "Financial Times",
                    "date": "2025-08-05",
                    "sentiment": "negative",
                    "score": -0.34,
                    "summary": "EU and US regulators are examining Microsoft's strategic investments in OpenAI and other AI startups for potential antitrust concerns.",
                },
                {
                    "title": "Microsoft Gaming Division Reports Record Quarter",
                    "source": "CNBC",
                    "date": "2025-08-03",
                    "sentiment": "positive",
                    "score": 0.65,
                    "summary": "Xbox and Activision Blizzard integration drives gaming segment to record $5.7B quarterly revenue.",
                },
            ],
            "_source": "news_sentiment",
            "_mock": True,
        }

    return {
        "ticker": ticker,
        "period": f"Last {days_back} days",
        "overall_sentiment": "neutral",
        "sentiment_score": 0.0,
        "articles_analyzed": 0,
        "top_stories": [],
        "_source": "news_sentiment",
        "_mock": True,
    }
