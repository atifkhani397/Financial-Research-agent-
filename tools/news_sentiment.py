"""
ARA-1 Tool: news_sentiment (Real Integration)

Aggregates news articles via NewsAPI.org (with Tavily news search fallback)
and performs sentiment scoring using TextBlob.

NOTE: TextBlob utilizes a lexicon-based heuristic rule set for sentiment polarity calculation,
which provides a quick baseline signal rather than a state-of-the-art deep neural sentiment assessment.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
import httpx
from textblob import TextBlob

from config import get_settings
from tools.utils_cache import cache_manager, rate_limiter, APIExecutionError, RateLimitExceededError

logger = logging.getLogger("ara1.tools.news_sentiment")


def _get_newsapi_articles(query: str, days_back: int) -> List[Dict[str, Any]]:
    """Fetch articles from NewsAPI.org."""
    settings = get_settings()
    api_key = settings.news_api_key
    if not api_key:
        return []

    from_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "from": from_date,
        "pageSize": 10,
        "apiKey": api_key,
    }

    rate_limiter.wait("newsapi.org", min_interval_sec=0.2)

    try:
        resp = httpx.get(url, params=params, timeout=10.0)
        if resp.status_code == 429:
            raise RateLimitExceededError("NewsAPI rate limit hit (429)")
        if resp.status_code != 200:
            logger.warning(f"NewsAPI HTTP {resp.status_code}: {resp.text[:100]}")
            return []

        data = resp.json()
        articles = data.get("articles", [])
        results = []
        for a in articles:
            results.append({
                "title": a.get("title", ""),
                "source": a.get("source", {}).get("name", "NewsAPI"),
                "date": a.get("publishedAt", "")[:10],
                "url": a.get("url", ""),
                "summary": a.get("description", "") or a.get("title", ""),
            })
        return results
    except RateLimitExceededError:
        raise
    except Exception as e:
        logger.warning(f"NewsAPI call failed: {e}")
        return []


def _get_tavily_fallback_news(query: str) -> List[Dict[str, Any]]:
    """Fallback news search using Tavily."""
    settings = get_settings()
    api_key = settings.tavily_api_key
    if not api_key:
        return []

    from tavily import TavilyClient
    rate_limiter.wait("api.tavily.com", min_interval_sec=0.2)

    try:
        client = TavilyClient(api_key=api_key)
        resp = client.search(query=f"{query} financial news", topic="news", max_results=5)
        results = []
        for r in resp.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "source": r.get("source", "Tavily"),
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "url": r.get("url", ""),
                "summary": r.get("content", "")[:250],
            })
        return results
    except Exception as e:
        logger.warning(f"Tavily fallback news search failed: {e}")
        return []


def execute(ticker: str, days_back: int = 7, **kwargs) -> Dict[str, Any]:
    """
    Fetch news and compute sentiment polarity for a company ticker.

    Args:
        ticker: Stock ticker symbol (e.g. MSFT, AAPL)
        days_back: Number of days to look back (default 7)

    Returns:
        Structured news sentiment analysis with scored top stories.
    """
    ticker_clean = ticker.strip().upper()
    params = {"ticker": ticker_clean, "days_back": days_back}

    cached = cache_manager.get("news_sentiment", params)
    if cached:
        return cached

    company_names = {
        "MSFT": "Microsoft",
        "AAPL": "Apple",
        "GOOGL": "Google Alphabet",
        "AMZN": "Amazon",
        "NVDA": "NVIDIA",
    }
    query_term = company_names.get(ticker_clean, ticker_clean)

    # 1. Fetch raw articles
    articles = _get_newsapi_articles(query_term, days_back)
    if not articles:
        articles = _get_tavily_fallback_news(query_term)

    if not articles:
        result = {
            "ticker": ticker_clean,
            "period": f"Last {days_back} days",
            "overall_sentiment": "neutral",
            "sentiment_score": 0.0,
            "articles_analyzed": 0,
            "top_stories": [],
            "methodology": "TextBlob lexicon-based heuristic polarity rule set",
            "_source": "news_sentiment",
            "_mock": False,
        }
        cache_manager.set("news_sentiment", params, result)
        return result

    # 2. Score sentiment using TextBlob (lexicon heuristic)
    scored_stories = []
    total_polarity = 0.0

    for a in articles:
        text_to_score = f"{a['title']}. {a['summary']}"
        blob = TextBlob(text_to_score)
        polarity = round(blob.sentiment.polarity, 3)
        total_polarity += polarity

        if polarity > 0.15:
            label = "positive"
        elif polarity < -0.15:
            label = "negative"
        else:
            label = "neutral"

        scored_stories.append({
            "title": a["title"],
            "source": a["source"],
            "date": a["date"],
            "url": a["url"],
            "sentiment": label,
            "score": polarity,
            "summary": a["summary"],
        })

    avg_score = round(total_polarity / len(scored_stories), 3) if scored_stories else 0.0
    if avg_score > 0.1:
        overall = "positive"
    elif avg_score < -0.1:
        overall = "negative"
    else:
        overall = "neutral"

    output = {
        "ticker": ticker_clean,
        "period": f"Last {days_back} days",
        "overall_sentiment": overall,
        "sentiment_score": avg_score,
        "articles_analyzed": len(scored_stories),
        "top_stories": scored_stories[:5],
        "methodology": "TextBlob lexicon-based heuristic polarity rule set",
        "_source": "news_sentiment",
        "_mock": False,
    }

    cache_manager.set("news_sentiment", params, output)
    return output
