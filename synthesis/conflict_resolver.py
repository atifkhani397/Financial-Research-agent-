"""
ARA-1 Synthesis Layer: conflict_resolver.py

Implements multi-source conflict resolution and 5-tier source reliability weighting.

Source Reliability Hierarchy (per Day 8 Brief Instructions):
  - Tier 1 (1.00): SEC Filings (10-K, 10-Q) — Highest Authority
  - Tier 2 (0.85): Financial Data APIs (FMP, yfinance)
  - Tier 3 (0.75): Earnings Call Transcripts
  - Tier 4 (0.50): Social / Forum Content
  - Tier 5 (0.30): Major News Outlets — Lowest Authority

  # ARCHITECTURAL NOTE / ERROR-LOG FLAG:
  # Ranking Major News Outlets (Tier 5, 0.30) below unverified Social/Forum Content (Tier 4, 0.50)
  # is implemented strictly per the brief's stated order. However, in standard financial analysis
  # and institutional journalism practice, peer-reviewed news outlets (e.g., WSJ, Reuters, Bloomberg)
  # carry substantially higher credibility than anonymous social media or forum posts.
  # This intentional inversion is preserved here per specification and flagged for evaluation/error-log discussion.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("ara1.synthesis.conflict_resolver")

# Configurable 5-Tier Weighting Table (per brief specification)
DEFAULT_SOURCE_TIER_WEIGHTS: Dict[str, float] = {
    "sec_filing": 1.00,
    "sec_edgar": 1.00,
    "10-k": 1.00,
    "10-q": 1.00,
    "financial_api": 0.85,
    "financial_data_api": 0.85,
    "company_profile": 0.85,
    "fmp_api": 0.85,
    "yfinance_fallback": 0.85,
    "earnings_transcript": 0.75,
    "fmp_transcript_api": 0.75,
    "social_forum": 0.50,
    "forum_post": 0.50,
    "social_media": 0.50,
    "news_outlet": 0.30,
    "news_sentiment": 0.30,
    "web_search": 0.30,
    "web_search_tavily": 0.30,
}


class ConflictResolver:
    """
    Resolves data conflicts across multi-source tool outputs using tier weights and temporal checks.
    """

    def __init__(self, tier_weights: Optional[Dict[str, float]] = None):
        self.tier_weights = tier_weights or DEFAULT_SOURCE_TIER_WEIGHTS
        self.resolved_conflicts_log: List[Dict[str, Any]] = []

    def get_source_weight(self, source_tag: str) -> float:
        """Return numeric authority weight for a given source tag or tool name."""
        s_clean = source_tag.strip().lower()
        for k, weight in self.tier_weights.items():
            if k in s_clean:
                return weight
        return 0.30  # Default to lowest tier if unclassified

    def _extract_numbers(self, text: Union[str, float, int]) -> List[float]:
        """Extract numeric values from string or return single float."""
        if isinstance(text, (int, float)):
            return [float(text)]
        matches = re.findall(r'(\d+(?:\.\d+)?)', str(text))
        return [float(m) for m in matches if m]

    def check_temporal_restatement(
        self,
        date_a: Optional[str],
        date_b: Optional[str],
        text_a: str = "",
        text_b: str = "",
    ) -> Optional[Dict[str, Any]]:
        """
        Check if a discrepancy between sources is explained by temporal differences
        or filing restatements (e.g. restated 10-K vs original 10-Q, or newer quarter date).
        """
        is_restatement = any(k in text_a.lower() or k in text_b.lower() for k in ["restate", "restated", "amended", "10-k/a"])

        if date_a and date_b:
            if date_a != date_b:
                newer = "source_a" if date_a > date_b else "source_b"
                return {
                    "explained_by": "temporal_difference",
                    "newer_source": newer,
                    "date_a": date_a,
                    "date_b": date_b,
                    "is_restatement": is_restatement,
                    "note": f"Discrepancy is temporal: Source A dated {date_a} vs Source B dated {date_b}. Newer date preferred.",
                }

        if is_restatement:
            restatement_source = "source_a" if "restate" in text_a.lower() else "source_b"
            return {
                "explained_by": "restatement",
                "newer_source": restatement_source,
                "is_restatement": True,
                "note": "Discrepancy is due to an official financial restatement (10-K/A). Restated figures preferred.",
            }

        return None

    def resolve(
        self,
        metric_name: str,
        value_a: Any,
        source_a: str,
        date_a: Optional[str] = None,
        value_b: Any = None,
        source_b: str = "",
        date_b: Optional[str] = None,
        tolerance_pct: float = 2.0,
    ) -> Dict[str, Any]:
        """
        Executes conflict resolution protocol across two claims for the same metric:
          1. Detect conflict (numeric or textual deviation).
          2. Check for temporal/restatement explanation.
          3. Compare tier weights if unresolved.
          4. Log conflict and resolution method.
        """
        weight_a = self.get_source_weight(source_a)
        weight_b = self.get_source_weight(source_b) if source_b else 0.0

        if value_b is None:
            return {
                "metric": metric_name,
                "resolved_value": value_a,
                "confidence": weight_a,
                "primary_source": source_a,
                "conflict_detected": False,
                "resolution_method": "single_source",
                "transparency_note": f"Metric {metric_name} derived solely from {source_a} (Weight: {weight_a:.2f}).",
            }

        nums_a = self._extract_numbers(value_a)
        nums_b = self._extract_numbers(value_b)

        # 1. Detect conflict
        is_conflict = False
        if nums_a and nums_b:
            val_a = nums_a[0]
            val_b = nums_b[0]
            denom = abs(val_a) if val_a != 0 else 1.0
            diff_pct = (abs(val_a - val_b) / denom) * 100.0
            if diff_pct > tolerance_pct:
                is_conflict = True
        elif str(value_a).strip().lower() != str(value_b).strip().lower():
            is_conflict = True

        if not is_conflict:
            return {
                "metric": metric_name,
                "resolved_value": value_a,
                "confidence": max(weight_a, weight_b),
                "primary_source": source_a,
                "secondary_source": source_b,
                "conflict_detected": False,
                "resolution_method": "source_agreement",
                "transparency_note": f"Metric {metric_name} is consistent across {source_a} and {source_b}.",
            }

        # 2. Check temporal / restatement explanation
        temporal_check = self.check_temporal_restatement(date_a, date_b, str(value_a), str(value_b))
        if temporal_check:
            if temporal_check["newer_source"] == "source_a":
                chosen_val, chosen_src, chosen_w = value_a, source_a, weight_a
            else:
                chosen_val, chosen_src, chosen_w = value_b, source_b, weight_b

            resolution_note = (
                f"Conflict on {metric_name} ({value_a} vs {value_b}): "
                f"Resolved via {temporal_check['explained_by']} ({temporal_check['note']}). Selected {chosen_val} from {chosen_src}."
            )

            log_entry = {
                "metric": metric_name,
                "resolved_value": chosen_val,
                "value_a": value_a,
                "source_a": source_a,
                "value_b": value_b,
                "source_b": source_b,
                "confidence": chosen_w,
                "primary_source": chosen_src,
                "conflict_detected": True,
                "resolution_method": temporal_check["explained_by"],
                "transparency_note": resolution_note,
            }
            self.resolved_conflicts_log.append(log_entry)
            return log_entry

        # 3. Prefer higher tier
        if weight_a >= weight_b:
            chosen_val, chosen_src, chosen_w = value_a, source_a, weight_a
            rejected_val, rejected_src = value_b, source_b
        else:
            chosen_val, chosen_src, chosen_w = value_b, source_b, weight_b
            rejected_val, rejected_src = value_a, source_a

        resolution_note = (
            f"Conflict detected for {metric_name}: {source_a} claimed '{value_a}' (Weight: {weight_a:.2f}), "
            f"while {source_b} claimed '{value_b}' (Weight: {weight_b:.2f}). "
            f"Resolved to '{chosen_val}' due to {chosen_src} having a higher authority tier."
        )

        log_entry = {
            "metric": metric_name,
            "resolved_value": chosen_val,
            "rejected_value": rejected_val,
            "confidence": chosen_w,
            "primary_source": chosen_src,
            "secondary_source": rejected_src,
            "conflict_detected": True,
            "resolution_method": "tier_weight_hierarchy",
            "transparency_note": resolution_note,
        }
        self.resolved_conflicts_log.append(log_entry)
        return log_entry
