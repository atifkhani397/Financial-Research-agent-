"""
ARA-1 Agent Infrastructure: disambiguation.py

Handles query disambiguation (stated assumptions vs clarifying questions),
private company / recent IPO edge cases, and rate-of-change temporal sensitivity flagging.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ara1.agent.disambiguation")


KNOWN_DISAMBIGUATION_MAP: Dict[str, Dict[str, str]] = {
    "amazon": {
        "assumed_entity": "Amazon.com Inc. (AMZN)",
        "ticker": "AMZN",
        "reasoning": "Interpreting 'Amazon' as Amazon.com Inc. (ticker AMZN), the global e-commerce and AWS cloud infrastructure company, based on market capitalization and primary research context.",
        "clarifying_question": "Did you mean Amazon.com Inc. (AMZN) or Amazon Fine Art / subsidiary operations?",
    },
    "apple": {
        "assumed_entity": "Apple Inc. (AAPL)",
        "ticker": "AAPL",
        "reasoning": "Interpreting 'Apple' as Apple Inc., consumer electronics and software platform provider, ticker AAPL.",
        "clarifying_question": "Did you mean Apple Inc. (AAPL) or Apple Corps (Beatles record label)?",
    },
    "banks": {
        "assumed_entity": "U.S. Money-Center G-SIB Banks (JPM, BAC, C, WFC)",
        "ticker": "JPM, BAC, C, WFC",
        "reasoning": "Interpreting 'the banks' as the four major U.S. money-center banks (JPMorgan Chase, Bank of America, Citigroup, Wells Fargo) to evaluate net interest margin and credit loss trends across the financial sector.",
        "clarifying_question": "Are you asking about major U.S. money-center banks (JPM, BAC, C, WFC) or regional banks (KRE index)?",
    },
}

RATE_OF_CHANGE_KEYWORDS = [
    "m&a", "merger", "acquisition", "takeover", "buyout", "ceo transition",
    "executive departure", "resignation", "restatement", "sec investigation",
    "spinoff", "bankruptcy", "chapter 11", "reorganization"
]


class DisambiguationEngine:
    """
    Manages explicit stated assumptions, edge-case disclosures, and rate-of-change banners.
    """

    def resolve_query_ambiguity(
        self,
        query: str,
        ambiguity_level: str = "LOW",
        force_assumption_path: bool = True,
    ) -> Dict[str, Any]:
        """Formulate stated assumptions or clarifying question for ambiguous queries."""
        q_clean = query.lower().strip()

        matched_key = next((k for k in KNOWN_DISAMBIGUATION_MAP if k in q_clean), None)
        if matched_key:
            info = KNOWN_DISAMBIGUATION_MAP[matched_key]
            path = "stated_assumption" if force_assumption_path else "clarifying_question"
            return {
                "ambiguity_detected": True,
                "disambiguation_path": path,
                "stated_assumption": info["reasoning"],
                "target_ticker": info.get("ticker", ""),
                "clarifying_question": info["clarifying_question"],
                "disclosure_markdown": (
                    f"> [!NOTE]\n"
                    f"> **Query Disambiguation Stated Assumption**: {info['reasoning']}\n"
                ),
            }

        if ambiguity_level in ["MEDIUM", "HIGH"]:
            assumption = (
                f"Interpreting query '{query}' in the context of major publicly traded U.S. enterprise equities "
                f"and standard financial performance metrics based on market representation."
            )
            return {
                "ambiguity_detected": True,
                "disambiguation_path": "stated_assumption",
                "stated_assumption": assumption,
                "target_ticker": "",
                "clarifying_question": f"Could you specify the target ticker symbol or company name for '{query}'?",
                "disclosure_markdown": f"> [!NOTE]\n> **Query Disambiguation Stated Assumption**: {assumption}\n",
            }

        return {
            "ambiguity_detected": False,
            "disambiguation_path": "direct",
            "stated_assumption": None,
            "disclosure_markdown": "",
        }

    def format_private_company_disclosure(self, company_name: str) -> Dict[str, Any]:
        """Generate plain disclosure for private entities with zero SEC filings."""
        msg = (
            f"SEC EDGAR database contains **zero public filings** for private company **{company_name}**. "
            f"Per ARA-1 integrity rules, zero 10-K financial figures were fabricated. Research depth is adapted "
            f"to secondary financial profile APIs, corporate press disclosures, and verified web sources."
        )
        return {
            "is_private": True,
            "company_name": company_name,
            "disclosure_text": msg,
            "disclosure_markdown": (
                f"> [!IMPORTANT]\n"
                f"> **Private Entity SEC Filing Disclosure**: {msg}\n"
            ),
        }

    def format_recent_ipo_disclosure(self, company_name: str, ipo_year: str = "2023/2024") -> Dict[str, Any]:
        """Generate disclosure for newly public companies with <1 year of filing history."""
        msg = (
            f"**{company_name}** is a newly public entity (IPO {ipo_year}) with less than 1 year of 10-K filing history. "
            f"Temporal expectations have been adapted to rely on available S-1 registration statements and recent 10-Q filings."
        )
        return {
            "is_recent_ipo": True,
            "company_name": company_name,
            "disclosure_text": msg,
            "disclosure_markdown": (
                f"> [!NOTE]\n"
                f"> **Recent IPO Disclosure**: {msg}\n"
            ),
        }

    def detect_rate_of_change(self, text_content: str) -> Optional[Dict[str, Any]]:
        """Detect fast-moving events (M&A, leadership changes, restatements) and return temporal sensitivity banner."""
        txt_lower = str(text_content).lower()
        matched_triggers = [kw for kw in RATE_OF_CHANGE_KEYWORDS if kw in txt_lower]

        if matched_triggers:
            triggers_str = ", ".join(set(matched_triggers)).upper()
            banner = (
                f"> [!IMPORTANT]\n"
                f"> **High Temporal Sensitivity Notice**: Fast-moving situation detected ({triggers_str}). "
                f"> Financial metrics and strategic positioning reflect disclosures as of current reporting period and are subject to rapid evolution.\n"
            )
            return {
                "rate_of_change_detected": True,
                "triggers": matched_triggers,
                "banner_markdown": banner,
            }

        return None
