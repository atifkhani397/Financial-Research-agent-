"""
ARA-1 API Utilities: Caching & Rate Limiting

Provides:
  - CacheManager: In-memory and file-based JSON response caching
  - RateLimiter: Sleep-based rate limiter per API host/domain (ensures SEC <= 10 req/s, FMP/News/Tavily rate limits)
  - Custom Exception classes for API rate limits and API failures
"""

import os
import json
import time
import hashlib
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("ara1.tools.cache")


class RateLimitExceededError(Exception):
    """Raised specifically when an API returns 429 Too Many Requests."""
    pass


class APIExecutionError(Exception):
    """Raised for generic API failure (5xx, 4xx non-429)."""
    pass


class RateLimiter:
    """Sleep-based rate limiter per domain."""

    def __init__(self):
        self.last_call_time: Dict[str, float] = {}

    def wait(self, domain: str, min_interval_sec: float = 0.2):
        """Ensure at least min_interval_sec has elapsed since last call to domain."""
        now = time.time()
        last = self.last_call_time.get(domain, 0.0)
        elapsed = now - last
        if elapsed < min_interval_sec:
            sleep_time = min_interval_sec - elapsed
            logger.debug(f"Rate limiting {domain}: sleeping {sleep_time:.3f}s")
            time.sleep(sleep_time)
        self.last_call_time[domain] = time.time()


class CacheManager:
    """File and in-memory cache for API requests."""

    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, Any] = {}

    def _get_cache_key(self, namespace: str, params: dict) -> str:
        param_str = json.dumps(params, sort_keys=True, default=str)
        hash_digest = hashlib.md5(param_str.encode("utf-8")).hexdigest()
        return f"{namespace}_{hash_digest}"

    def get(self, namespace: str, params: dict) -> Optional[Any]:
        key = self._get_cache_key(namespace, params)
        if key in self._memory_cache:
            logger.debug(f"Cache HIT (memory): {key}")
            return self._memory_cache[key]

        file_path = self.cache_dir / f"{key}.json"
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._memory_cache[key] = data
                logger.debug(f"Cache HIT (file): {key}")
                return data
            except Exception as e:
                logger.warning(f"Failed to read cache file {file_path}: {e}")

        return None

    def set(self, namespace: str, params: dict, data: Any):
        key = self._get_cache_key(namespace, params)
        self._memory_cache[key] = data
        file_path = self.cache_dir / f"{key}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            logger.debug(f"Cache STORE: {key}")
        except Exception as e:
            logger.warning(f"Failed to write cache file {file_path}: {e}")


# Singletons
rate_limiter = RateLimiter()
cache_manager = CacheManager()
