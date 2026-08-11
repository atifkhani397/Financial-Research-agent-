"""
ARA-1 Tool: fact_checker (Real Implementation)

Cross-references specific numeric or factual claims against primary and secondary
tool outputs (SEC filings, financial APIs, transcripts) per Section A2.2 schema.
Calculates percentage tolerances, confidence scores, and conflict resolution details.
"""

import re
import logging
from typing import Any, Dict, Optional, List

logger = logging.getLogger("ara1.tools.fact_checker")


def _extract_numbers(text: str) -> List[float]:
    """Extract numeric values from text string."""
    matches = re.findall(r'\b\d+(?:\.\d+)?\b', text)
    nums = []
    for m in matches:
        try:
            val = float(m)
            nums.append(val)
        except ValueError:
            pass
    return nums


def execute(
    claim: str,
    source_context: str,
    secondary_context: Optional[str] = None,
    tolerance_pct: float = 2.0,
    **kwargs,
) -> Dict[str, Any]:
    """
    Cross-reference claim against >= 1 or >= 2 independent source contexts.
    """
    claim_str = claim.strip()
    src_primary = source_context.strip() if source_context else ""
    src_secondary = secondary_context.strip() if secondary_context else ""

    claim_nums = _extract_numbers(claim_str)
    primary_nums = _extract_numbers(src_primary)
    secondary_nums = _extract_numbers(src_secondary) if src_secondary else []

    verified = True
    confidence = 0.95
    conflict_detected = False
    conflict_note = "No conflicting metrics detected."

    primary_match = False
    secondary_match = False

    # Check numeric alignment
    if claim_nums:
        target_num = claim_nums[0]

        # Primary check
        p_matches = [
            p for p in primary_nums
            if abs(p - target_num) / (abs(target_num) if target_num != 0 else 1.0) <= (tolerance_pct / 100.0)
        ]
        if p_matches:
            primary_match = True

        # Secondary check if secondary_context provided
        if secondary_nums:
            s_matches = [
                s for s in secondary_nums
                if abs(s - target_num) / (abs(target_num) if target_num != 0 else 1.0) <= (tolerance_pct / 100.0)
            ]
            if s_matches:
                secondary_match = True
            else:
                # Secondary context has different numbers -> conflict!
                conflict_detected = True
                confidence = 0.70
                conflict_note = (
                    f"Claim number ({target_num}) matched primary context ({p_matches}) "
                    f"but differed from secondary context figures ({secondary_nums[:3]})."
                )

        if not primary_match and not secondary_match:
            verified = False
            confidence = 0.35
            conflict_note = f"Claim number ({target_num}) was not found within {tolerance_pct}% in provided source context."
    else:
        # Textual keyword matching fallback
        c_lower = claim_str.lower()
        if c_lower in src_primary.lower():
            primary_match = True
        else:
            words = [w for w in c_lower.split() if len(w) > 4]
            matches = sum(1 for w in words if w in src_primary.lower())
            if words and matches / len(words) >= 0.6:
                primary_match = True
            else:
                verified = False
                confidence = 0.50

    return {
        "claim": claim_str,
        "verified": verified,
        "confidence": round(confidence, 2),
        "primary_source_match": primary_match,
        "secondary_source_match": secondary_match,
        "conflict_detected": conflict_detected,
        "conflict_resolution_note": conflict_note,
        "primary_evidence": src_primary[:300] if src_primary else "No primary context provided.",
        "secondary_evidence": src_secondary[:300] if src_secondary else "No secondary context provided.",
        "_source": "fact_checker_real",
        "_mock": False,
    }
