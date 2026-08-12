"""
ARA-1 API Challenge Routes (Day 16)
Lists the 8 Section B2 progressive challenges and allows initiating challenge execution.
"""

from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from api.schemas import ChallengeItem, ResearchQueryResponse
from api.routes.research import submit_research_query, ResearchQueryRequest

router = APIRouter(prefix="/api/challenges", tags=["Challenges"])

PREDEFINED_CHALLENGES: List[dict] = [
    {
        "challenge_id": 1,
        "title": "Challenge 1: Single Company Profile",
        "difficulty": "1/5",
        "query": "Produce a quick snapshot report on Microsoft Corp (MSFT) revenue and cloud growth.",
        "expected_tools": ["company_profile", "vector_db_store"]
    },
    {
        "challenge_id": 2,
        "title": "Challenge 2: SEC EDGAR & Financial API Synthesis",
        "difficulty": "2/5",
        "query": "Retrieve Apple Inc (AAPL) SEC 10-K disclosures and verify financial API metrics.",
        "expected_tools": ["sec_filing_search", "financial_data_api", "fact_checker"]
    },
    {
        "challenge_id": 3,
        "title": "Challenge 3: DCF Valuation & Peer Benchmarking",
        "difficulty": "3/5",
        "query": "Produce a complete financial report on Tesla Inc (TSLA) including 5-year FCF DCF valuation and peer comparison against AMD, INTC, AVGO.",
        "expected_tools": ["company_profile", "financial_data_api", "calculation_engine", "peer_comparison"]
    },
    {
        "challenge_id": 4,
        "title": "Challenge 4: Cloud Triopoly (AWS vs Azure vs GCP)",
        "difficulty": "3/5",
        "query": "Perform an end-to-end comparative financial and market analysis of the Cloud Infrastructure Triopoly: Amazon Web Services (AWS), Microsoft Azure, and Google Cloud Platform (GCP).",
        "expected_tools": ["financial_data_api", "peer_comparison", "calculation_engine", "report_generator"]
    },
    {
        "challenge_id": 5,
        "title": "Challenge 5: Sentiment vs Fundamentals Contradiction",
        "difficulty": "4/5",
        "query": "Analyze Palantir Technologies (PLTR) revenue growth and evaluate conflicting news sentiment claims against SEC EDGAR 10-K disclosures.",
        "expected_tools": ["news_sentiment", "sec_filing_search", "fact_checker", "report_generator"]
    },
    {
        "challenge_id": 6,
        "title": "Challenge 6: Banking Disambiguation & Fallback Resilience",
        "difficulty": "4/5",
        "query": "Retrieve bank stress test metrics and capital adequacy ratios for JPMorgan Chase (JPM) under simulated API failure conditions.",
        "expected_tools": ["sec_filing_search", "financial_data_api", "web_search", "report_generator"]
    },
    {
        "challenge_id": 7,
        "title": "Challenge 7: Cross-Company Thematic Memory Retrieval",
        "difficulty": "4/5",
        "query": "Synthesize cloud revenue growth trends across Microsoft (MSFT), Amazon (AMZN), and Alphabet (GOOGL) using stored vector memory.",
        "expected_tools": ["vector_db_search", "calculation_engine", "report_generator"]
    },
    {
        "challenge_id": 8,
        "title": "Challenge 8: NVIDIA Corporation 50% Failure Rate Stress Test",
        "difficulty": "5/5",
        "query": "Produce a complete investment research report on NVIDIA Corporation (NVDA) under 50% intermittent failure injection on financial data and SEC filing tools.",
        "expected_tools": ["company_profile", "earnings_transcript", "web_search", "report_generator"]
    }
]


@router.get("", response_model=List[ChallengeItem])
async def list_challenges():
    """Returns list of all 8 predefined Section B2 challenges."""
    return PREDEFINED_CHALLENGES


@router.post("/{challenge_id}/run", response_model=ResearchQueryResponse)
async def run_challenge(challenge_id: int, background_tasks: BackgroundTasks):
    """Triggers execution of a specific predefined challenge by ID."""
    match = next((c for c in PREDEFINED_CHALLENGES if c["challenge_id"] == challenge_id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Challenge ID {challenge_id} not found.")

    req = ResearchQueryRequest(
        query=match["query"],
        session_id=f"challenge-{challenge_id}",
        max_tool_calls=20
    )
    return await submit_research_query(req, background_tasks)
