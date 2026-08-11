"""
ARA-1 Agent Infrastructure: circuit_breaker.py

Implements Circuit Breaker Pattern per Section 6 & Day 9 Brief.
Trips a tool to OPEN after N consecutive failures (default 3), stopping further
retries for that tool to save tool-call budget and routing straight to fallback chains.
"""

from enum import Enum, auto
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("ara1.agent.circuit_breaker")


class CircuitState(Enum):
    CLOSED = auto()     # Normal operation (calls allowed)
    OPEN = auto()       # Tripped (calls blocked, route straight to fallback)
    HALF_OPEN = auto()  # Testing recovery


class CircuitBreaker:
    """
    Tracks tool failure counts and manages circuit breaker state per session.
    """

    def __init__(self, max_consecutive_failures: int = 3):
        self.max_consecutive_failures = max_consecutive_failures
        self._failure_counts: Dict[str, int] = {}
        self._states: Dict[str, CircuitState] = {}
        self.tripped_tools_log: List[Dict[str, Any]] = []

    def get_state(self, tool_name: str) -> CircuitState:
        """Return current circuit state for a tool."""
        t_clean = tool_name.strip().lower()
        return self._states.get(t_clean, CircuitState.CLOSED)

    def is_open(self, tool_name: str) -> bool:
        """Return True if tool circuit breaker is OPEN (tripped)."""
        return self.get_state(tool_name) == CircuitState.OPEN

    def record_failure(self, tool_name: str, error_detail: str = ""):
        """Record a tool failure. Trips circuit to OPEN if consecutive failures >= N."""
        t_clean = tool_name.strip().lower()
        count = self._failure_counts.get(t_clean, 0) + 1
        self._failure_counts[t_clean] = count

        if count >= self.max_consecutive_failures and self._states.get(t_clean) != CircuitState.OPEN:
            self._states[t_clean] = CircuitState.OPEN
            logger.error(
                f"[Circuit Breaker TRIPPED -> OPEN] Tool '{tool_name}' failed {count} consecutive times. "
                f"Bypassing tool for remainder of session."
            )
            self.tripped_tools_log.append({
                "tool_name": tool_name,
                "consecutive_failures": count,
                "error_detail": error_detail,
                "state": "OPEN",
                "note": f"Circuit breaker tripped after {count} consecutive failures. Bypassing tool.",
            })

    def record_success(self, tool_name: str):
        """Record a successful tool execution. Resets failure count and closes circuit."""
        t_clean = tool_name.strip().lower()
        if self._failure_counts.get(t_clean, 0) > 0 or self._states.get(t_clean) != CircuitState.CLOSED:
            logger.info(f"[Circuit Breaker CLOSED] Resetting failure count for tool '{tool_name}'.")
        self._failure_counts[t_clean] = 0
        self._states[t_clean] = CircuitState.CLOSED

    def get_open_tools(self) -> List[str]:
        """Return list of all tools currently in OPEN state."""
        return [t for t, state in self._states.items() if state == CircuitState.OPEN]
