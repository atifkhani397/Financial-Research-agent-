"""
ARA-1 Agent Infrastructure: query_analyzer.py

Classifies incoming research queries by type (Section A8.3), estimated complexity (1-5 scale),
and ambiguity level (LOW, MEDIUM, HIGH).
"""

from enum import Enum, auto
import re
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ara1.agent.query_analyzer")


class QueryType(Enum):
    FACTUAL_PRECISION = auto()  # Narrow, metric-specific, quantitative inquiry
    ANALYTICAL_BREADTH = auto() # Broad, multi-faceted industry/thesis inquiry


class AmbiguityLevel(Enum):
    LOW = auto()    # Unambiguous (ticker/full company name specified)
    MEDIUM = auto() # Minor ambiguity (common name, single entity likely)
    HIGH = auto()   # High ambiguity (broad category, multi-entity interpretation e.g. "the banks")


class QueryAnalyzer:
    """
    Analyzes research queries to determine structure, complexity, and ambiguity.
    """

    FACTUAL_KEYWORDS = [
        "what was", "revenue", "net income", "margin", "eps", "ebitda", "pe ratio",
        "market cap", "debt", "cash flow", "guidance", "q1", "q2", "q3", "q4", "10-k", "10-q"
    ]

    BROAD_AMBIGUOUS_PATTERNS = [
        r"\bthe banks?\b", r"\bcloud leaders?\b", r"\bai stocks?\b", r"\bev market\b",
        r"\btech sector\b", r"\bsemiconductors?\b", r"\bbig tech\b", r"\brecent ipos?\b"
    ]

    TICKER_PATTERN = r"\b[A-Z]{1,5}\b"

    def analyze(self, query: str) -> Dict[str, Any]:
        """Classify query type, complexity, and ambiguity level."""
        q_lower = query.lower().strip()

        # 1. Determine Query Type (Section A8.3)
        factual_matches = sum(1 for kw in self.FACTUAL_KEYWORDS if kw in q_lower)
        if factual_matches >= 2 or re.search(r"\b\d{4}\b", q_lower):
            query_type = QueryType.FACTUAL_PRECISION
        else:
            query_type = QueryType.ANALYTICAL_BREADTH

        # 2. Determine Ambiguity Level
        high_ambiguity = any(re.search(pat, q_lower) for pat in self.BROAD_AMBIGUOUS_PATTERNS)
        ticker_found = re.findall(self.TICKER_PATTERN, query)
        # Exclude common English words that look like tickers
        ticker_found = [t for t in ticker_found if t not in ["WHAT", "HOW", "WHY", "NOTE", "THE", "AND", "FOR"]]

        if high_ambiguity or ("?" in query and len(query.split()) <= 6 and not ticker_found):
            ambiguity_level = AmbiguityLevel.HIGH
        elif ticker_found or len(query.split()) > 10:
            ambiguity_level = AmbiguityLevel.LOW
        else:
            ambiguity_level = AmbiguityLevel.MEDIUM

        # 3. Estimate Complexity (1-5 scale)
        word_count = len(query.split())
        complexity = 1
        if word_count > 8:
            complexity += 1
        if query_type == QueryType.ANALYTICAL_BREADTH:
            complexity += 1
        if ambiguity_level == AmbiguityLevel.HIGH:
            complexity += 1
        if any(k in q_lower for k in ["compare", "vs", "versus", "benchmark", "contradiction", "themes"]):
            complexity += 1
        complexity = min(5, complexity)

        # 4. Extract Entity Candidates & Edge Case Signals
        is_private_indicator = any(k in q_lower for k in ["stripe", "spacex", "bytedance", "private company", "unlisted"])
        is_recent_ipo_indicator = any(k in q_lower for k in ["arm", "reddit", "instacart", "klarna", "recent ipo", "newly public"])

        result = {
            "query": query,
            "query_type": query_type.name,
            "ambiguity_level": ambiguity_level.name,
            "complexity_score": complexity,
            "detected_tickers": ticker_found,
            "is_private_company_query": is_private_indicator,
            "is_recent_ipo_query": is_recent_ipo_indicator,
            "summary": (
                f"Query Type: {query_type.name} | Complexity: {complexity}/5 | Ambiguity: {ambiguity_level.name}"
            ),
        }
        logger.info(f"[QueryAnalyzer] {result['summary']}")
        return result
