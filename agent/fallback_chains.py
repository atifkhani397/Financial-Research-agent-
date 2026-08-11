"""
ARA-1 Agent Infrastructure: fallback_chains.py

Defines >= 2 fallback tools/strategies for every primary tool per Section 6 & Day 9 Brief.
Logs every fallback event and applies confidence score penalties to final report metrics.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("ara1.agent.fallback_chains")

# Fallback tool chains (>= 2 fallback strategies per primary tool)
FALLBACK_MAP: Dict[str, List[str]] = {
    "financial_data_api": ["sec_filing_search", "web_search", "vector_db_search"],
    "company_profile": ["sec_filing_search", "web_search", "vector_db_search"],
    "sec_filing_search": ["financial_data_api", "web_search", "vector_db_search"],
    "earnings_transcript": ["sec_filing_search", "web_search", "vector_db_search"],
    "news_sentiment": ["web_search", "vector_db_search"],
    "peer_comparison": ["company_profile", "web_search", "vector_db_search"],
    "calculation_engine": ["web_search"],
    "fact_checker": ["web_search", "vector_db_search"],
    "web_search": ["vector_db_search"],
    "vector_db_search": ["web_search"],
}

# Confidence penalties per fallback hop
FALLBACK_PENALTY_STEP_1 = 0.15
FALLBACK_PENALTY_STEP_2 = 0.30
FALLBACK_PENALTY_STEP_3 = 0.45


class FallbackChainManager:
    """
    Manages fallback tool routing when primary tools fail or circuit breakers trip.
    """

    def __init__(self, fallback_map: Optional[Dict[str, List[str]]] = None):
        self.fallback_map = fallback_map or FALLBACK_MAP
        self.fallback_history_log: List[Dict[str, Any]] = []

    def get_fallbacks(self, tool_name: str) -> List[str]:
        """Return list of fallback tool names for a primary tool."""
        return self.fallback_map.get(tool_name.strip().lower(), ["web_search", "vector_db_search"])

    def execute_fallback_chain(
        self,
        registry,
        primary_tool_name: str,
        tool_args: Dict[str, Any],
        circuit_breaker=None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Iterates through the fallback chain for a failed primary tool.
        Returns (success: bool, result_payload: dict).
        """
        fallbacks = self.get_fallbacks(primary_tool_name)
        ticker = tool_args.get("ticker", "UNKNOWN")

        for idx, fallback_tool in enumerate(fallbacks, 1):
            if circuit_breaker and circuit_breaker.is_open(fallback_tool):
                logger.warning(f"Fallback tool '{fallback_tool}' circuit breaker is OPEN. Skipping.")
                continue

            penalty = (
                FALLBACK_PENALTY_STEP_1 if idx == 1 else
                FALLBACK_PENALTY_STEP_2 if idx == 2 else
                FALLBACK_PENALTY_STEP_3
            )

            # Adapt arguments if necessary for fallback tool
            fallback_args = dict(tool_args)
            if fallback_tool == "web_search" and "query" not in fallback_args:
                fallback_args["query"] = f"{ticker} {primary_tool_name} financial metrics report"
            elif fallback_tool == "vector_db_search" and "query" not in fallback_args:
                fallback_args["query"] = f"{ticker} financial data"
            elif fallback_tool == "sec_filing_search" and "filing_type" not in fallback_args:
                fallback_args["filing_type"] = "10-K"

            logger.info(
                f"[Fallback Hop {idx}] Primary '{primary_tool_name}' failed -> Calling fallback '{fallback_tool}' "
                f"(Confidence Penalty: -{penalty:.2f})"
            )

            try:
                result = registry.execute_tool(fallback_tool, fallback_args)

                if isinstance(result, dict) and not result.get("error"):
                    base_confidence = result.get("_confidence", 0.85)
                    adjusted_confidence = max(0.20, round(base_confidence - penalty, 2))

                    result["_fallback_used"] = True
                    result["_primary_tool_failed"] = primary_tool_name
                    result["_fallback_tool"] = fallback_tool
                    result["_confidence_penalty"] = penalty
                    result["_confidence"] = adjusted_confidence
                    result["_source"] = f"fallback_{fallback_tool}"

                    log_entry = {
                        "primary_tool": primary_tool_name,
                        "fallback_tool": fallback_tool,
                        "hop_index": idx,
                        "confidence_penalty": penalty,
                        "adjusted_confidence": adjusted_confidence,
                        "ticker": ticker,
                        "note": f"Primary tool '{primary_tool_name}' failed; retrieved via fallback '{fallback_tool}' (Penalty: -{penalty:.2f}).",
                    }
                    self.fallback_history_log.append(log_entry)
                    if circuit_breaker:
                        circuit_breaker.record_success(fallback_tool)

                    return True, result
                else:
                    if circuit_breaker:
                        circuit_breaker.record_failure(fallback_tool)
            except Exception as e:
                logger.warning(f"Fallback tool '{fallback_tool}' failed: {e}")
                if circuit_breaker:
                    circuit_breaker.record_failure(fallback_tool)

        # All fallbacks failed
        logger.error(f"All fallback strategies exhausted for primary tool '{primary_tool_name}'.")
        return False, {
            "error": f"Primary tool '{primary_tool_name}' and all fallback strategies failed.",
            "_primary_tool": primary_tool_name,
            "_fallbacks_attempted": fallbacks,
            "_fallback_failed": True,
        }
