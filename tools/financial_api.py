"""
ARA-1 Tool: Financial API (Real Integration)

Integrates with Financial Modeling Prep (FMP) for company financials, quotes, metrics, and profiles.
Provides specific RateLimitExceededError on HTTP 429 rate limit responses.
Includes yfinance fallback if FMP API key is unavailable or rate limited.
"""

import logging
from typing import Any, Dict, Optional
import httpx

from config import get_settings
from tools.utils_cache import cache_manager, rate_limiter, APIExecutionError, RateLimitExceededError

logger = logging.getLogger("ara1.tools.financial_api")

FMP_BASE_URL = "https://financialmodelingprep.com/stable"


def fetch_fmp_endpoint(endpoint: str, params: dict) -> list | dict:
    """Helper to query FMP stable endpoints with rate limiting and 429 detection."""
    settings = get_settings()
    api_key = settings.fmp_api_key
    if not api_key:
        raise APIExecutionError("FMP_API_KEY is not configured in .env")

    request_params = {**params, "apikey": api_key}
    url = f"{FMP_BASE_URL}/{endpoint}"

    rate_limiter.wait("financialmodelingprep.com", min_interval_sec=0.2)

    try:
        resp = httpx.get(url, params=request_params, timeout=10.0)
        if resp.status_code == 429:
            raise RateLimitExceededError("FMP API rate limit hit (HTTP 429)")
        if resp.status_code in (401, 403) and "limit" in resp.text.lower():
            raise RateLimitExceededError(f"FMP API limit/auth error (HTTP {resp.status_code}): {resp.text}")
        
        resp.raise_for_status()
        data = resp.json()
        
        # Check if FMP returned error message in JSON payload
        if isinstance(data, dict) and "Error Message" in data:
            err_msg = data["Error Message"]
            if "limit" in err_msg.lower() or "429" in err_msg:
                raise RateLimitExceededError(f"FMP limit error: {err_msg}")
            raise APIExecutionError(f"FMP API error: {err_msg}")

        return data
    except RateLimitExceededError:
        raise
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise RateLimitExceededError(f"FMP API rate limit hit: {e}")
        raise APIExecutionError(f"FMP HTTP error {e.response.status_code}: {e}")
    except Exception as e:
        logger.error(f"FMP request to {endpoint} failed: {e}")
        raise APIExecutionError(f"FMP request failed: {str(e)}")


def _yfinance_fallback_profile(ticker: str) -> Dict[str, Any]:
    """Fallback profile using yfinance."""
    import yfinance as yf
    t = yf.Ticker(ticker)
    info = t.info or {}
    return {
        "ticker": ticker,
        "name": info.get("longName", f"{ticker} Corp"),
        "sector": info.get("sector", "Technology"),
        "industry": info.get("industry", "Software"),
        "description": info.get("longBusinessSummary", ""),
        "ceo": info.get("companyOfficers", [{}])[0].get("name", "N/A") if info.get("companyOfficers") else "N/A",
        "market_cap": info.get("marketCap"),
        "full_time_employees": info.get("fullTimeEmployees"),
        "country": info.get("country", "US"),
        "website": info.get("website", ""),
        "executives": [
            {"name": o.get("name"), "title": o.get("title")}
            for o in info.get("companyOfficers", [])[:6]
        ] if info.get("companyOfficers") else [],
        "_source": "yfinance_fallback",
        "_mock": False,
    }


def _yfinance_fallback_financials(ticker: str, metric: str) -> Dict[str, Any]:
    """Fallback financial data using yfinance."""
    import yfinance as yf
    t = yf.Ticker(ticker)
    info = t.info or {}
    return {
        "ticker": ticker,
        "metric": metric,
        "revenue": info.get("totalRevenue"),
        "net_income": info.get("netIncomeToCommon"),
        "pe_ratio": info.get("trailingPE"),
        "market_cap": info.get("marketCap"),
        "eps": info.get("trailingEps"),
        "operating_margin": info.get("operatingMargins"),
        "free_cash_flow": info.get("freeCashflow"),
        "dividend_yield": info.get("dividendYield"),
        "_source": "yfinance_fallback",
        "_mock": False,
    }


def get_company_profile(ticker: str) -> Dict[str, Any]:
    """Fetch company profile using FMP (or yfinance fallback)."""
    ticker_clean = ticker.strip().upper()
    params = {"ticker": ticker_clean, "type": "profile"}
    cached = cache_manager.get("financial_api", params)
    if cached:
        return cached

    try:
        data = fetch_fmp_endpoint("profile", {"symbol": ticker_clean})
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
            result = {
                "ticker": ticker_clean,
                "name": item.get("companyName"),
                "exchange": item.get("exchange"),
                "sector": item.get("sector"),
                "industry": item.get("industry"),
                "country": item.get("country"),
                "website": item.get("website"),
                "description": item.get("description"),
                "ceo": item.get("ceo"),
                "full_time_employees": item.get("fullTimeEmployees"),
                "market_cap": item.get("marketCap"),
                "price": item.get("price"),
                "isin": item.get("isin"),
                "cusip": item.get("cusip"),
                "executives": [{"name": item.get("ceo"), "title": "CEO"}],
                "_source": "fmp_api",
                "_mock": False,
            }
            cache_manager.set("financial_api", params, result)
            return result
    except RateLimitExceededError:
        raise
    except Exception as e:
        logger.warning(f"FMP profile failed for {ticker_clean}, trying yfinance: {e}")

    try:
        res = _yfinance_fallback_profile(ticker_clean)
        cache_manager.set("financial_api", params, res)
        return res
    except Exception as e:
        raise APIExecutionError(f"Company profile failed for {ticker_clean}: {e}")


def get_financial_metrics(ticker: str, metric: str = "overview") -> Dict[str, Any]:
    """Fetch quantitative metrics (revenue, PE ratio, net income, etc.) using FMP."""
    ticker_clean = ticker.strip().upper()
    metric_clean = metric.strip().lower()
    params = {"ticker": ticker_clean, "metric": metric_clean, "type": "metrics"}

    cached = cache_manager.get("financial_api", params)
    if cached:
        return cached

    try:
        # Fetch income statement & quote
        inc_data = fetch_fmp_endpoint("income-statement", {"symbol": ticker_clean, "limit": 2})
        quote_data = fetch_fmp_endpoint("quote", {"symbol": ticker_clean})

        latest_inc = inc_data[0] if isinstance(inc_data, list) and inc_data else {}
        latest_quote = quote_data[0] if isinstance(quote_data, list) and quote_data else {}

        res = {
            "ticker": ticker_clean,
            "metric": metric_clean,
            "revenue": latest_inc.get("revenue"),
            "net_income": latest_inc.get("netIncome"),
            "operating_income": latest_inc.get("operatingIncome"),
            "gross_profit": latest_inc.get("grossProfit"),
            "eps": latest_inc.get("eps") or latest_quote.get("eps"),
            "pe_ratio": latest_quote.get("pe") or latest_inc.get("pe"),
            "market_cap": latest_quote.get("marketCap"),
            "price": latest_quote.get("price"),
            "period": latest_inc.get("calendarYear") or "FY2025/2026",
            "date": latest_inc.get("date"),
            "_source": "fmp_api",
            "_mock": False,
        }

        cache_manager.set("financial_api", params, res)
        return res

    except RateLimitExceededError:
        raise
    except Exception as e:
        logger.warning(f"FMP metrics failed for {ticker_clean}, trying yfinance: {e}")

    try:
        res = _yfinance_fallback_financials(ticker_clean, metric_clean)
        cache_manager.set("financial_api", params, res)
        return res
    except Exception as e:
        raise APIExecutionError(f"Financial metrics failed for {ticker_clean}: {e}")


def execute(ticker: str, metric: str = "overview", **kwargs) -> Dict[str, Any]:
    """Registry tool entry point for financial_data_api."""
    return get_financial_metrics(ticker=ticker, metric=metric)
