"""
ARA-1 Synthesis Package
"""

from synthesis.conflict_resolver import ConflictResolver, DEFAULT_SOURCE_TIER_WEIGHTS
from synthesis.narrative import NarrativeBuilder
from synthesis.engine import SynthesisEngine

__all__ = [
    "ConflictResolver",
    "DEFAULT_SOURCE_TIER_WEIGHTS",
    "NarrativeBuilder",
    "SynthesisEngine",
]
