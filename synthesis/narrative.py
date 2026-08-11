"""
ARA-1 Synthesis Layer: narrative.py

Performs narrative threading and quantitative triangulation across multi-source tool outputs.
Transforms disjointed facts into thesis-driven analytical narratives.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("ara1.synthesis.narrative")


class NarrativeBuilder:
    """
    Synthesizes facts into structured, thesis-driven narratives and performs quantitative triangulation.
    """

    def triangulate_numeric_claims(
        self,
        metric_name: str,
        sources_and_values: List[Dict[str, Any]],
        unit: str = "",
    ) -> Dict[str, Any]:
        """
        Quantitative Triangulation for claims with >= 2 sources:
          - Compares values across sources.
          - If values align within 2%, reports single confidence-scored value.
          - If values diverge > 2%, reports an explicit range with explanation.
        """
        if not sources_and_values:
            return {
                "metric": metric_name,
                "triangulated_value": "N/A",
                "confidence": 0.0,
                "is_range": False,
                "explanation": f"No source data gathered for {metric_name}.",
            }

        if len(sources_and_values) == 1:
            item = sources_and_values[0]
            val = item.get("value")
            src = item.get("source", "Unknown")
            return {
                "metric": metric_name,
                "triangulated_value": f"{val} {unit}".strip(),
                "numeric_val": val,
                "confidence": item.get("confidence", 0.80),
                "is_range": False,
                "sources_used": [src],
                "explanation": f"Single-source metric from {src}.",
            }

        valid_entries = []
        for sv in sources_and_values:
            v = sv.get("value")
            try:
                num_v = float(v)
                valid_entries.append((num_v, sv.get("source", "Source")))
            except (ValueError, TypeError):
                pass

        if not valid_entries:
            return {
                "metric": metric_name,
                "triangulated_value": str(sources_and_values[0].get("value")),
                "confidence": 0.50,
                "is_range": False,
                "explanation": "Non-numeric claim comparison across sources.",
            }

        nums = [e[0] for e in valid_entries]
        srcs = [e[1] for e in valid_entries]

        min_val = min(nums)
        max_val = max(nums)
        mean_val = sum(nums) / len(nums)

        spread_pct = ((max_val - min_val) / abs(mean_val) * 100.0) if mean_val != 0 else 0.0

        if spread_pct <= 2.0:
            # High agreement -> single triangulated value
            formatted_val = f"{mean_val:,.2f} {unit}".strip()
            explanation = f"Triangulated across {len(valid_entries)} sources ({', '.join(srcs)}) with <2% variance."
            return {
                "metric": metric_name,
                "triangulated_value": formatted_val,
                "numeric_val": round(mean_val, 2),
                "confidence": 0.95,
                "is_range": False,
                "sources_used": srcs,
                "explanation": explanation,
            }
        else:
            # Real divergence -> explicit range report
            range_val = f"{min_val:,.2f} {unit} to {max_val:,.2f} {unit}".strip()
            explanation = (
                f"Triangulated range due to source variance ({spread_pct:.1f}% spread): "
                f"Low of {min_val:,.2f} from {srcs[nums.index(min_val)]}, High of {max_val:,.2f} from {srcs[nums.index(max_val)]}."
            )
            return {
                "metric": metric_name,
                "triangulated_value": range_val,
                "min_val": min_val,
                "max_val": max_val,
                "confidence": 0.75,
                "is_range": True,
                "sources_used": srcs,
                "explanation": explanation,
            }

    def build_thesis_narrative(
        self,
        company_name: str,
        ticker: str,
        core_thesis: str,
        triangulated_metrics: List[Dict[str, Any]],
        divergence_findings: List[Dict[str, Any]],
        conflicts_logged: List[Dict[str, Any]],
    ) -> str:
        """
        Connects data points into a coherent thesis-driven narrative.
        """
        lines = []
        lines.append(f"### Investment & Analytical Thesis for {company_name} ({ticker})")
        lines.append(core_thesis)
        lines.append("")

        if triangulated_metrics:
            lines.append("#### Quantitative Triangulation Summary")
            for tm in triangulated_metrics:
                m_name = tm.get("metric", "Metric")
                t_val = tm.get("triangulated_value", "N/A")
                expl = tm.get("explanation", "")
                conf = tm.get("confidence", 0.0)
                lines.append(f"- **{m_name}**: `{t_val}` (Confidence: {conf:.2f}) — *{expl}*")
            lines.append("")

        if divergence_findings:
            lines.append("#### Key Analytical Divergences")
            for df in divergence_findings:
                title = df.get("title", "Divergence")
                detail = df.get("detail", "")
                lines.append(f"- **{title}**: {detail}")
            lines.append("")

        if conflicts_logged:
            lines.append("#### Transparent Conflict Resolution Logs")
            for cl in conflicts_logged:
                note = cl.get("transparency_note", "")
                lines.append(f"- [Conflict Log] {note}")
            lines.append("")

        return "\n".join(lines)
