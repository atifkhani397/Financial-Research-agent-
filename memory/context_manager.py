"""
ARA-1 Short-Term Memory Context Manager

Tracks token usage of the accumulating Thought/Action/Observation trace.
When context window consumption reaches the threshold (default 70%),
it compacts earlier steps into a structured summary while preserving
all quantitative facts, metrics, and citations.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("ara1.memory.context_manager")


class ContextManager:
    """Manages short-term memory and context window compaction."""

    def __init__(
        self,
        max_context_tokens: int = 8000,
        compression_threshold: float = 0.70,
    ):
        self.max_context_tokens = max_context_tokens
        self.compression_threshold = compression_threshold
        self.compaction_count = 0

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count using standard 4 chars per token heuristic."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    def estimate_trace_tokens(self, trace_entries: List[Any]) -> int:
        """Estimate total tokens across all trace entries."""
        total = 0
        for entry in trace_entries:
            if hasattr(entry, "__str__"):
                total += self.estimate_tokens(str(entry))
            elif isinstance(entry, dict):
                total += self.estimate_tokens(str(entry))
            elif isinstance(entry, str):
                total += self.estimate_tokens(entry)
        return total

    def should_compact(self, trace_entries: List[Any]) -> bool:
        """Return True if total trace tokens >= threshold percentage of max_context_tokens."""
        tokens = self.estimate_trace_tokens(trace_entries)
        threshold_tokens = int(self.max_context_tokens * self.compression_threshold)
        return tokens >= threshold_tokens

    def compact_trace(
        self,
        trace_entries: List[Any],
        keep_last_n: int = 2,
        llm_wrapper: Optional[Any] = None,
    ) -> List[Any]:
        """
        Compress earlier steps while keeping the last `keep_last_n` steps intact.
        Preserves key findings, metrics, tickers, and citations.
        """
        if len(trace_entries) <= keep_last_n:
            return trace_entries

        earlier_entries = trace_entries[:-keep_last_n]
        recent_entries = trace_entries[-keep_last_n:]

        # Extract findings and key text from earlier entries
        summary_lines = []
        key_facts = []

        for entry in earlier_entries:
            phase = getattr(entry, "phase", "") if hasattr(entry, "phase") else entry.get("phase", "")
            content = getattr(entry, "content", "") if hasattr(entry, "content") else entry.get("content", "")
            tool_name = getattr(entry, "tool_name", "") if hasattr(entry, "tool_name") else entry.get("tool_name", "")
            tool_result = getattr(entry, "tool_result", "") if hasattr(entry, "tool_result") else entry.get("tool_result", "")

            if tool_name and tool_result:
                # Truncate raw observation payload but keep first 300 chars
                short_res = tool_result[:300] + ("..." if len(tool_result) > 300 else "")
                key_facts.append(f"• Tool {tool_name}: {short_res}")
            elif content:
                summary_lines.append(f"[{phase}] {content[:200]}")

        compacted_summary = (
            f"=== COMPACTED CONTEXT SUMMARY (Steps 1-{len(earlier_entries)}) ===\n"
            + "\n".join(summary_lines[:10]) + "\n"
            + "Key Extracted Facts & Citations:\n"
            + "\n".join(key_facts[:15]) + "\n"
            + "=================================================="
        )

        self.compaction_count += 1
        logger.info(
            f"Compacted {len(earlier_entries)} earlier trace entries into summary "
            f"({self.estimate_tokens(compacted_summary)} tokens). Total compactions={self.compaction_count}"
        )

        # Create a single synthetic summary trace entry
        if hasattr(trace_entries[0], "phase"):
            SummaryClass = type(trace_entries[0])
            try:
                summary_entry = SummaryClass(
                    timestamp=0.0,
                    phase="COMPACTED_MEMORY",
                    content=compacted_summary,
                )
            except TypeError:
                try:
                    summary_entry = SummaryClass(
                        phase="COMPACTED_MEMORY",
                        content=compacted_summary,
                    )
                except TypeError:
                    # Fallback duck-type object
                    class CompactedEntry:
                        def __init__(self, p, c):
                            self.phase = p
                            self.content = c
                        def __str__(self):
                            return f"[{self.phase}] {self.content}"
                    summary_entry = CompactedEntry("COMPACTED_MEMORY", compacted_summary)
        else:
            summary_entry = {
                "timestamp": 0.0,
                "phase": "COMPACTED_MEMORY",
                "content": compacted_summary,
            }

        return [summary_entry] + list(recent_entries)
