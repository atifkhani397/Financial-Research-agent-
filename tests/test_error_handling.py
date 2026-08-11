import pytest
import time
from agent.error_handler import ErrorHandler, ErrorCategory
from agent.fallback_chains import FallbackChainManager
from agent.circuit_breaker import CircuitBreaker, CircuitState
from tools.tool_registry import ToolRegistry


def test_error_classification():
    handler = ErrorHandler()
    assert handler.classify_error("HTTP 429 Rate limit exceeded") == ErrorCategory.RATE_LIMITING
    assert handler.classify_error("HTTP 401 Unauthorized") == ErrorCategory.AUTH_FAILURE
    assert handler.classify_error("502 Bad Gateway ConnectionError") == ErrorCategory.API_UNAVAILABILITY
    assert handler.classify_error("ReadTimeoutError: read timed out") == ErrorCategory.TIMEOUT_HALLUCINATION
    assert handler.classify_error("JSONDecodeError: invalid json schema") == ErrorCategory.MALFORMED_RESPONSE
    assert handler.classify_error("Unit scale mismatch: M vs B") == ErrorCategory.UNIT_CONFUSION


def test_transient_vs_fail_fast():
    handler = ErrorHandler()
    assert handler.is_transient(ErrorCategory.API_UNAVAILABILITY) is True
    assert handler.is_transient(ErrorCategory.RATE_LIMITING) is True
    assert handler.is_transient(ErrorCategory.TIMEOUT_HALLUCINATION) is True

    assert handler.is_transient(ErrorCategory.AUTH_FAILURE) is False
    assert handler.is_transient(ErrorCategory.MALFORMED_RESPONSE) is False


def test_exponential_backoff_calculation():
    handler = ErrorHandler(base_delay=1.0, max_delay=32.0, max_jitter_ms=500)
    delay1 = handler.calculate_backoff_delay(attempt=1)
    delay2 = handler.calculate_backoff_delay(attempt=2)
    delay3 = handler.calculate_backoff_delay(attempt=3)

    assert 1.0 <= delay1 <= 1.5
    assert 2.0 <= delay2 <= 2.5
    assert 4.0 <= delay3 <= 4.5


def test_circuit_breaker_tripping():
    cb = CircuitBreaker(max_consecutive_failures=3)
    tool_name = "financial_data_api"

    assert cb.is_open(tool_name) is False
    cb.record_failure(tool_name)
    cb.record_failure(tool_name)
    assert cb.is_open(tool_name) is False

    # 3rd consecutive failure trips circuit
    cb.record_failure(tool_name)
    assert cb.is_open(tool_name) is True
    assert cb.get_state(tool_name) == CircuitState.OPEN

    # Successful call resets circuit
    cb.record_success(tool_name)
    assert cb.is_open(tool_name) is False


def test_fallback_chain_confidence_penalties():
    registry = ToolRegistry()
    fb_manager = FallbackChainManager()

    success, res = fb_manager.execute_fallback_chain(
        registry=registry,
        primary_tool_name="financial_data_api",
        tool_args={"ticker": "MSFT", "metric": "overview"},
    )
    assert success is True
    assert res["_fallback_used"] is True
    assert res["_confidence_penalty"] == 0.15
    assert res["_confidence"] <= 0.75


def test_simulated_tool_failure_injection():
    registry = ToolRegistry()
    # Execute with 100% simulated failure
    res = registry.execute_tool("company_profile", {"ticker": "MSFT"}, simulate_failure_rate=1.0)
    assert res.get("error") is not None
    assert res.get("_simulated_failure") is True
