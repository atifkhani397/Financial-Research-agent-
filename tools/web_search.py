"""
ARA-1 Tool: web_search (Real Integration with Tavily)

Performs real web search using Tavily API. Purpose-built for LLM agents to return
clean, structured markdown search results.
"""

import logging
from typing import Any, Dict
from tavily import TavilyClient

from config import get_settings
from tools.utils_cache import cache_manager, rate_limiter, APIExecutionError, RateLimitExceededError

logger = logging.getLogger("ara1.tools.web_search")


def execute(query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
    """
    Perform a web search using Tavily.

    Args:
        query: Search query string.
        max_results: Number of top search results to return.

    Returns:
        Structured search findings with titles, URLs, and text snippets.
    """
    query_clean = query.strip()
    params = {"query": query_clean, "max_results": max_results}

    cached = cache_manager.get("web_search", params)
    if cached:
        return cached

    settings = get_settings()
    api_key = settings.tavily_api_key
    if not api_key:
        raise APIExecutionError("TAVILY_API_KEY is not configured in .env")

    rate_limiter.wait("api.tavily.com", min_interval_sec=0.2)

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query_clean, max_results=max_results, search_depth="basic")

        results = []
        raw_results = response.get("results", [])
        for item in raw_results:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", item.get("snippet", "")),
                "source": "tavily",
            })

        output = {
            "query": query_clean,
            "total_results": len(results),
            "results": results,
            "_source": "web_search_tavily",
            "_mock": False,
        }

        cache_manager.set("web_search", params, output)
        return output

    except Exception as e:
        error_str = str(e).lower()
        if "429" in error_str or "rate limit" in error_str or "quota" in error_str:
            raise RateLimitExceededError(f"Tavily rate limit hit: {e}")
        logger.error(f"Tavily search failed for query '{query_clean}': {e}")
        raise APIExecutionError(f"Tavily web search failed: {str(e)}")
