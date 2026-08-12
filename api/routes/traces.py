"""
ARA-1 API Trace Gallery Routes (Day 16)
REST endpoint serving curated trace gallery entries as structured JSON.
"""

from typing import List
from fastapi import APIRouter
from api.schemas import TraceGalleryItem

router = APIRouter(prefix="/api/traces", tags=["Trace Gallery"])

CURATED_TRACES: List[dict] = [
    {
        "trace_id": "trace-1-tsla-dcf",
        "title": "Clean Success & DCF Valuation (Tesla Inc)",
        "query": "Produce a complete investment research report on Tesla Inc (TSLA) including 5-year FCF DCF valuation model and peer comparison.",
        "session_id": "day7-challenge3-tsla",
        "highlights": "Clean 5-step Plan-and-Execute flow, exact Python math execution ($182.45/share DCF intrinsic value), 100% citation accuracy.",
        "annotations": {
            "what_agent_did_well": "Flawless step execution, exact mathematical calculation via calculation_engine, 100% citation resolution.",
            "what_could_improve": "Could auto-fetch trailing shares outstanding dynamically."
        }
    },
    {
        "trace_id": "trace-2-jpm-fallback",
        "title": "Error Recovery & Fallback Hop (JPMorgan Chase)",
        "query": "Retrieve financial metrics and capital adequacy ratios for JPMorgan Chase (JPM) under simulated API failure.",
        "session_id": "day9-challenge6-jpm",
        "highlights": "Primary tool financial_data_api failed (500 Error); FallbackManager triggered Fallback 1/3 (sec_filing_search) and retrieved Tier 1 capital ratios without data loss.",
        "annotations": {
            "what_agent_did_well": "Seamless fallback chain execution, recorded circuit breaker success, zero data loss.",
            "what_could_improve": "Could cache fallback route choice for subsequent calls in the same session."
        }
    },
    {
        "trace_id": "trace-3-pltr-conflict",
        "title": "Conflict Resolution Protocol (Palantir Technologies)",
        "query": "Evaluate Palantir Technologies (PLTR) revenue growth amidst conflicting news and SEC reporting.",
        "session_id": "day8-challenge5-pltr",
        "highlights": "News sentiment reported negative growth (-0.42), but SEC 10-K reported +27% YoY revenue growth. Agent applied Tier 1 (SEC 10-K) superseding Tier 4 (News media).",
        "annotations": {
            "what_agent_did_well": "Strict adherence to 5-tier source hierarchy; documented discrepancy in Data Conflicts section without fabricating.",
            "what_could_improve": "Could add sentiment trajectory time-series overlay."
        }
    },
    {
        "trace_id": "trace-4-amzn-outage",
        "title": "Degraded Partial Report Disclosure (Amazon Inc 100% Outage)",
        "query": "Analyze Amazon Inc (AMZN) cloud revenue and capital expenditures under emergency 100% tool outage conditions.",
        "session_id": "stress-test-100pct-outage",
        "highlights": "All external tools failed due to 1.00 failure rate. Agent produced a partial report with explicit [INCOMPLETE — limit reached] and degradation banners without crashing.",
        "annotations": {
            "what_agent_did_well": "Zero crashes, zero fabricated numbers, complete transparency.",
            "what_could_improve": "Could suggest offline cached query fallback options."
        }
    },
    {
        "trace_id": "trace-5-cloud-memory",
        "title": "Long-Term Memory Recall (Cloud Infrastructure Triopoly)",
        "query": "Synthesize cloud revenue growth trends across Microsoft (MSFT), Amazon (AMZN), and Alphabet (GOOGL).",
        "session_id": "day10-challenge7-memory",
        "highlights": "Agent invoked vector_db_search first, retrieving 5 stored chunks from ChromaDB in 0.04s, saving 3 external HTTP calls.",
        "annotations": {
            "what_agent_did_well": "100% memory utilization (AB-4), avoided redundant external calls, 0.4s total execution latency.",
            "what_could_improve": "Could add timestamp freshness check on recalled vector chunks."
        }
    },
    {
        "trace_id": "trace-6-bank-disambiguation",
        "title": "Query Disambiguation & Stated Assumptions (Bank Stress Tests)",
        "query": "Analyze bank stress tests.",
        "session_id": "day10-ambiguous-query",
        "highlights": "QueryAnalyzer flagged query as VAGUE_AMBIGUOUS and generated stated assumption header for US G-SIBs under CCAR framework.",
        "annotations": {
            "what_agent_did_well": "Explicitly stated assumptions instead of guessing or hanging.",
            "what_could_improve": "Could prompt user interactively when ambiguity index > 0.8."
        }
    }
]


@router.get("", response_model=List[TraceGalleryItem])
async def list_trace_gallery():
    """Returns curated trace gallery entries as structured JSON."""
    return CURATED_TRACES
