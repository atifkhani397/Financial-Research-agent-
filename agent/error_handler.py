"""
ARA-1 Agent Infrastructure: error_handler.py

Classifies runtime errors and tool failures into the 11 categories from Section A4.2
and routes each to the appropriate recovery strategy (Retry, Fallback, Fail-Fast).
"""

from enum import Enum, auto
import logging
import random
import time
from typing import Any, Dict, Optional, Tuple, Type

logger = logging.getLogger("ara1.agent.error_handler")


class ErrorCategory(Enum):
    API_UNAVAILABILITY = auto()          # HTTP 500/502/503/504, ConnectionError -> Transient (Retry)
    RATE_LIMITING = auto()               # HTTP 429, RateLimitExceededError -> Transient (Retry + Backoff)
    AUTH_FAILURE = auto()                # HTTP 401/403, Missing API Key -> Non-Transient (Fail Fast)
    MALFORMED_RESPONSE = auto()          # JSONDecodeError, Schema Error -> Non-Transient (Fail Fast)
    TIMEOUT_HALLUCINATION = auto()       # Socket/HTTP Timeout -> Transient (Retry)
    LOGICAL_INCONSISTENCY = auto()       # Out of bound math, invalid args -> Fallback
    PREMATURE_CONCLUSION = auto()        # Early exit missing steps -> Re-plan / Fallback
    CIRCULAR_REASONING_STALE_DATA = auto()# Repeated identical tool calls -> Circuit Break
    CONFLICTING_SOURCES = auto()         # Multi-source variance -> Synthesis Engine
    MISATTRIBUTION = auto()              # Ticker / entity mismatch -> Fallback
    UNIT_CONFUSION = auto()              # Scale mismatch (e.g. B vs M) -> Scale Adjust / Fallback
    UNKNOWN_ERROR = auto()               # Catch-all -> Fallback


class ErrorHandler:
    """
    Error Classifier and Exponential Backoff Retry Manager per Section 6 & A4.2.
    """

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 32.0,
        max_retries: int = 5,
        max_jitter_ms: int = 500,
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self.max_jitter_ms = max_jitter_ms

    def classify_error(self, exc_or_msg: Any) -> ErrorCategory:
        """Classify an exception or error response dict/string into one of 11 categories."""
        msg = str(exc_or_msg).lower()

        if any(k in msg for k in ["429", "rate limit", "ratelimit"]):
            return ErrorCategory.RATE_LIMITING

        if any(k in msg for k in ["401", "403", "unauthorized", "forbidden", "missing api key"]):
            return ErrorCategory.AUTH_FAILURE

        if any(k in msg for k in ["500", "502", "503", "504", "connectionerror", "unavailable", "server error"]):
            return ErrorCategory.API_UNAVAILABILITY

        if any(k in msg for k in ["timeout", "timed out", "readtimeout"]):
            return ErrorCategory.TIMEOUT_HALLUCINATION

        if any(k in msg for k in ["json", "decode", "schema", "validationerror", "malformed"]):
            return ErrorCategory.MALFORMED_RESPONSE

        if any(k in msg for k in ["unit", "scale", "billion", "million", "magnitude"]):
            return ErrorCategory.UNIT_CONFUSION

        if any(k in msg for k in ["misattribution", "ticker mismatch", "wrong entity"]):
            return ErrorCategory.MISATTRIBUTION

        if any(k in msg for k in ["circular", "stale", "repeated", "loop"]):
            return ErrorCategory.CIRCULAR_REASONING_STALE_DATA

        if any(k in msg for k in ["inconsistency", "out of bound", "division by zero"]):
            return ErrorCategory.LOGICAL_INCONSISTENCY

        return ErrorCategory.UNKNOWN_ERROR

    def is_transient(self, category: ErrorCategory) -> bool:
        """Returns True if the error category is transient and eligible for exponential retry."""
        return category in (
            ErrorCategory.API_UNAVAILABILITY,
            ErrorCategory.RATE_LIMITING,
            ErrorCategory.TIMEOUT_HALLUCINATION,
        )

    def calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay with random jitter (0-500ms).
        Formula: min(max_delay, base_delay * 2^attempt) + jitter
        """
        exponent_delay = min(self.max_delay, self.base_delay * (2 ** (attempt - 1)))
        jitter = random.uniform(0.0, self.max_jitter_ms / 1000.0)
        return round(exponent_delay + jitter, 3)

    def execute_with_retry(
        self,
        func,
        *args,
        tool_name: str = "tool",
        **kwargs,
    ) -> Tuple[bool, Any, Optional[ErrorCategory]]:
        """
        Executes a callable with exponential backoff retries for transient errors.
        Fails fast immediately for non-transient errors (Auth, Malformed Schema).
        """
        attempt = 1
        last_error_category = None

        while attempt <= self.max_retries:
            try:
                res = func(*args, **kwargs)
                if isinstance(res, dict) and "error" in res:
                    err_msg = str(res.get("error"))
                    category = self.classify_error(err_msg)
                    last_error_category = category

                    if self.is_transient(category) and attempt < self.max_retries:
                        delay = self.calculate_backoff_delay(attempt)
                        logger.warning(
                            f"[Retry {attempt}/{self.max_retries}] Transient error '{category.name}' in {tool_name}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        attempt += 1
                        continue
                    else:
                        logger.error(
                            f"[Fail-Fast / Max Retries Exceeded] Tool {tool_name} failed with category '{category.name}'."
                        )
                        return False, res, category

                return True, res, None

            except Exception as exc:
                category = self.classify_error(exc)
                last_error_category = category

                if self.is_transient(category) and attempt < self.max_retries:
                    delay = self.calculate_backoff_delay(attempt)
                    logger.warning(
                        f"[Retry {attempt}/{self.max_retries}] Exception '{category.name}' ({exc}) in {tool_name}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    attempt += 1
                    continue
                else:
                    logger.error(
                        f"[Fail-Fast Exception] Tool {tool_name} raised non-transient exception '{category.name}': {exc}"
                    )
                    return False, {"error": str(exc), "_category": category.name}, category

        return False, {"error": f"Max retries ({self.max_retries}) exceeded", "_category": last_error_category.name if last_error_category else "UNKNOWN"}, last_error_category
