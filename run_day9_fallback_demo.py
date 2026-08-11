r"""
ARA-1 Day 9: Fallback & Circuit Breaker Demonstration Script
Forces primary tool failures to demonstrate:
  1. Exponential Backoff Retries
  2. Circuit Breaker Tripping (N=3)
  3. Fallback Chain Execution with Confidence Penalty Logging
"""

import sys
import logging
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.error_handler import ErrorHandler
from agent.fallback_chains import FallbackChainManager
from agent.circuit_breaker import CircuitBreaker
from tools.tool_registry import ToolRegistry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ara1.fallback_demo")

def main():
    print("\n" + "="*80)
    print("  DAY 9 DEMO: SIMULATED FAILURE, EXPONENTIAL RETRY & FALLBACK CHAIN")
    print("="*80 + "\n")

    registry = ToolRegistry(schemas_dir="tools/schemas")
    error_handler = ErrorHandler(base_delay=0.1, max_retries=2)
    fallback_manager = FallbackChainManager()
    circuit_breaker = CircuitBreaker(max_consecutive_failures=3)

    primary_tool = "financial_data_api"
    args = {"ticker": "JPM", "metric": "overview"}

    print(f"Simulating repeated failures for primary tool '{primary_tool}'...\n")

    for call_idx in range(1, 4):
        logger.info(f"--- Attempting Primary Call {call_idx} for '{primary_tool}' ---")
        
        # Check circuit breaker
        if circuit_breaker.is_open(primary_tool):
            logger.warning(f"[Circuit Breaker OPEN] Bypassing '{primary_tool}' directly to fallback chain.")
            fb_success, fb_res = fallback_manager.execute_fallback_chain(registry, primary_tool, args, circuit_breaker)
            print(f"Result from Fallback: {fb_res.get('_source')} (Confidence: {fb_res.get('_confidence')})")
        else:
            # Force simulated failure
            success, res, err_cat = False, {"error": "HTTP 503 Service Unavailable"}, None
            circuit_breaker.record_failure(primary_tool, error_detail="HTTP 503 Service Unavailable")
            logger.warning(f"[Primary Tool Failed] Triggering Fallback Chain for '{primary_tool}'.")
            fb_success, fb_res = fallback_manager.execute_fallback_chain(registry, primary_tool, args, circuit_breaker)
            print(f"Result from Fallback: {fb_res.get('_source')} (Confidence: {fb_res.get('_confidence')})")

    print("\n" + "="*80)
    print(f"Tripped Circuit Breakers: {circuit_breaker.get_open_tools()}")
    print(f"Logged Fallback Events: {len(fallback_manager.fallback_history_log)}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
