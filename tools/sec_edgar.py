"""
ARA-1 Tool: SEC EDGAR Search (Real Integration)

Searches SEC EDGAR for official filings (10-K, 10-Q, 8-K) and structured XBRL facts.
Requires a descriptive User-Agent header per SEC regulations.
"""

import logging
from typing import Any, Dict, List, Optional
import httpx

from config import get_settings
from tools.utils_cache import cache_manager, rate_limiter, APIExecutionError, RateLimitExceededError

logger = logging.getLogger("ara1.tools.sec_edgar")

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

_CIK_CACHE = {}


def _get_headers() -> Dict[str, str]:
    settings = get_settings()
    user_agent = settings.sec_user_agent or "QuantumEdge Research atif.khan@example.com"
    return {"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"}


def _get_cik_map() -> Dict[str, str]:
    """Fetch and cache ticker -> CIK mapping from SEC."""
    global _CIK_CACHE
    if _CIK_CACHE:
        return _CIK_CACHE

    cached = cache_manager.get("sec_edgar", {"type": "tickers_map"})
    if cached:
        _CIK_CACHE = cached
        return cached

    rate_limiter.wait("www.sec.gov", min_interval_sec=0.1)
    headers = _get_headers()
    try:
        resp = httpx.get(SEC_TICKERS_URL, headers=headers, timeout=5.0)
        if resp.status_code == 429:
            raise RateLimitExceededError("SEC EDGAR rate limit hit (429)")
        resp.raise_for_status()
        data = resp.json()
        
        cik_map = {}
        for entry in data.values():
            ticker = entry.get("ticker", "").upper()
            cik = str(entry.get("cik_str", "")).zfill(10)
            if ticker and cik:
                cik_map[ticker] = cik
                
        _CIK_CACHE = cik_map
        cache_manager.set("sec_edgar", {"type": "tickers_map"}, cik_map)
        return cik_map
    except RateLimitExceededError:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch SEC ticker map: {e}")
        # Fallback dictionary for common tickers to guarantee resilience
        fallback = {
            "MSFT": "0000789019",
            "AAPL": "0000320193",
            "GOOGL": "0001652044",
            "AMZN": "0001018724",
            "NVDA": "0001045810",
        }
        return fallback


def execute(ticker: str, filing_type: str, year: Optional[int] = None, **kwargs) -> Dict[str, Any]:
    """
    Search SEC EDGAR for official filings and financial facts.

    Args:
        ticker: Stock ticker symbol (e.g. MSFT, AAPL)
        filing_type: Type of filing ("10-K", "10-Q", "8-K")
        year: Fiscal year filter (optional)

    Returns:
        Structured filing data including accession info, document URL, and key financial highlights.
    """
    ticker_clean = ticker.strip().upper()
    filing_type_clean = filing_type.strip().upper()

    params = {"ticker": ticker_clean, "filing_type": filing_type_clean, "year": year}
    cached_result = cache_manager.get("sec_edgar", params)
    if cached_result:
        return cached_result

    # 1. Resolve CIK
    cik_map = _get_cik_map()
    cik = cik_map.get(ticker_clean)
    if not cik:
        return {
            "ticker": ticker_clean,
            "filing_type": filing_type_clean,
            "year": year,
            "results": [],
            "error": f"Ticker '{ticker_clean}' not found in SEC EDGAR directory.",
            "_source": "sec_edgar",
            "_mock": False,
        }

    rate_limiter.wait("data.sec.gov", min_interval_sec=0.1)
    headers = _get_headers()

    # 2. Fetch Submissions
    submissions_url = SEC_SUBMISSIONS_URL.format(cik=cik)
    sub_data = {}
    try:
        resp = httpx.get(submissions_url, headers=headers, timeout=6.0)
        if resp.status_code == 429:
            raise RateLimitExceededError("SEC EDGAR rate limit hit (429)")
        if resp.status_code == 200:
            sub_data = resp.json()
    except RateLimitExceededError:
        raise
    except Exception as e:
        logger.warning(f"Failed to fetch SEC submissions for CIK {cik}: {e}")

    recent = sub_data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    filing_dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    docs = recent.get("primaryDocument", [])
    report_dates = recent.get("reportDate", [])

    matched_filings = []
    cik_no_zeros = str(int(cik))

    for idx, form in enumerate(forms):
        if form != filing_type_clean:
            continue
        
        f_date = filing_dates[idx] if idx < len(filing_dates) else ""
        f_year = int(f_date.split("-")[0]) if f_date and "-" in f_date else None
        
        if year and f_year and f_year != year:
            continue

        acc_num = accessions[idx] if idx < len(accessions) else ""
        acc_no_hyphens = acc_num.replace("-", "")
        doc = docs[idx] if idx < len(docs) else ""
        rep_date = report_dates[idx] if idx < len(report_dates) else ""

        doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{acc_no_hyphens}/{doc}" if acc_num and doc else ""

        matched_filings.append({
            "form": form,
            "filing_date": f_date,
            "report_date": rep_date,
            "fiscal_year": f_year,
            "accession_number": acc_num,
            "document_url": doc_url,
        })

        if len(matched_filings) >= 5:
            break

    result = {
        "ticker": ticker_clean,
        "filing_type": filing_type_clean,
        "year": year,
        "company_name": sub_data.get("name", ticker_clean),
        "cik": cik,
        "matched_count": len(matched_filings),
        "filings": matched_filings,
        "_source": "sec_edgar",
        "_mock": False,
    }

    cache_manager.set("sec_edgar", params, result)
    return result
