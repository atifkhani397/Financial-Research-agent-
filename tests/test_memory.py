"""
ARA-1 Day 6 Memory Architecture Unit and Integration Test Suite
"""

import os
import pytest
from pathlib import Path

# Ensure dummy GROQ_API_KEY for config loading during test run if missing
if not os.getenv("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = "gsk_test_dummy_key_for_memory_tests"

from memory.vector_store import (
    VectorStore,
    chunk_sec_filing,
    chunk_earnings_transcript,
    chunk_news_article,
    chunk_text,
)
from memory.context_manager import ContextManager
from memory.episodic import EpisodicMemory
from tools.tool_registry import ToolRegistry


# ── Structural Text Chunker Tests ────────────────────────────────────

def test_chunk_sec_filing():
    sec_text = """
ITEM 1. BUSINESS
Microsoft develops and supports software, services, devices, and solutions.

ITEM 1A. RISK FACTORS
Our operations are subject to competition, cybersecurity risks, and macroeconomic uncertainty.

ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS
Revenue increased by 15% year-over-year driven by Intelligent Cloud growth.
"""
    chunks = chunk_sec_filing(sec_text)
    assert len(chunks) == 3
    assert "ITEM 1. BUSINESS" in chunks[0]
    assert "ITEM 1A. RISK FACTORS" in chunks[1]
    assert "ITEM 7." in chunks[2]


def test_chunk_earnings_transcript():
    transcript = """
Operator: Good afternoon and welcome to the Q3 Earnings Call.
Satya Nadella: Thank you. This quarter we saw record demand for Microsoft Cloud and Copilot integrations.
Amy Hood: Total revenue reached $65.6B, up 16% constant currency.
Q: Can you provide more details on Azure growth trajectories?
A: Azure and other cloud services grew 33%.
"""
    chunks = chunk_earnings_transcript(transcript)
    assert len(chunks) >= 3
    assert any("Satya Nadella" in c for c in chunks)
    assert any("Amy Hood" in c for c in chunks)
    assert any("Azure and other cloud services" in c for c in chunks)


def test_chunk_news_article():
    headline = "Tech Sector Soars on Strong AI Cloud Earnings"
    body = """Microsoft and major cloud providers reported accelerating enterprise spending in AI infrastructure.

Capital expenditures are projected to increase further in FY2025 according to market analysts."""

    chunks = chunk_news_article(body, headline=headline)
    assert len(chunks) >= 1
    for c in chunks:
        assert f"Headline: {headline}" in c


def test_chunk_text_dispatcher():
    sec_chunks = chunk_text("ITEM 1. BUSINESS\nSample text", source_type="SEC_10K")
    assert len(sec_chunks) >= 1

    news_chunks = chunk_text("Para 1\n\nPara 2", source_type="NEWS", headline="Headline")
    assert len(news_chunks) >= 1
    assert "Headline" in news_chunks[0]


# ── VectorStore Tests ────────────────────────────────────────────────

@pytest.fixture
def temp_vector_store(tmp_path, monkeypatch):
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma_test"))
    from config import reset_settings
    reset_settings()
    vs = VectorStore(collection_name="test_memory_collection")
    yield vs


def test_vector_store_operations(temp_vector_store):
    vs = temp_vector_store

    # 1. Single Store
    doc_id = vs.store(
        content="Microsoft Azure revenue grew 33% YoY in Q1 FY25.",
        ticker="MSFT",
        source_type="EARNINGS_TRANSCRIPT",
        date="2024-10-30",
        confidence=0.95,
        researcher_session="sess_001",
        verified=True,
    )
    assert doc_id is not None
    assert vs.count() == 1

    # 2. Financial Statement Metadata Store
    fin_id = vs.store_financial_statement(
        financial_data={"revenue": 65585000000, "net_income": 24667000000},
        ticker="MSFT",
        date="2024-09-30",
        confidence=1.0,
    )
    assert fin_id is not None

    # 3. Chunk and Store
    sec_doc = "ITEM 1. BUSINESS\nMicrosoft Corporation is a technology leader.\n\nITEM 1A. RISK FACTORS\nCompetitors."
    ids = vs.chunk_and_store(
        content=sec_doc,
        ticker="MSFT",
        source_type="SEC_10K",
        date="2024-07-30",
    )
    assert len(ids) == 2

    # 4. Search with Ticker Filter
    res = vs.search(query="Azure cloud revenue growth", ticker="MSFT", top_k=5)
    assert len(res) >= 1
    assert res[0]["metadata"]["ticker"] == "MSFT"

    # 5. Search with Source Type Filter
    res_sec = vs.search(query="business competition", source_type="SEC_10K", top_k=5)
    assert len(res_sec) >= 1
    assert res_sec[0]["metadata"]["source_type"] == "SEC_10K"

    # 6. Date Range Filtering
    res_date = vs.search(query="revenue", date_start="2024-08-01", date_end="2024-11-01")
    assert len(res_date) >= 1


# ── ContextManager Tests ─────────────────────────────────────────────

def test_context_manager():
    cm = ContextManager(max_context_tokens=100, compression_threshold=0.70)

    # 1. Token Estimation
    assert cm.estimate_tokens("Hello world!") == 3  # 12 chars // 4

    # 2. Check Compaction Threshold
    short_trace = ["Short trace item"]
    assert not cm.should_compact(short_trace)

    long_trace = ["This is a very long trace entry. " * 20]  # ~640 chars -> ~160 tokens
    assert cm.should_compact(long_trace)

    # 3. Trace Compaction
    class DummyTraceEntry:
        def __init__(self, phase, content, tool_name="", tool_result=""):
            self.phase = phase
            self.content = content
            self.tool_name = tool_name
            self.tool_result = tool_result

        def __str__(self):
            return f"[{self.phase}] {self.content} {self.tool_name} {self.tool_result}"

    trace = [
        DummyTraceEntry("THOUGHT", "Step 1: Fetch MSFT profile"),
        DummyTraceEntry("ACTION", "company_profile", tool_name="company_profile"),
        DummyTraceEntry("OBSERVATION", "Res 1", tool_name="company_profile", tool_result="Microsoft Corp profile data"),
        DummyTraceEntry("THOUGHT", "Step 2: Fetch SEC filing"),
        DummyTraceEntry("ACTION", "sec_filing_search", tool_name="sec_filing_search"),
        DummyTraceEntry("OBSERVATION", "Res 2", tool_name="sec_filing_search", tool_result="10-K filing data"),
    ]

    compacted = cm.compact_trace(trace, keep_last_n=2)
    assert len(compacted) == 3  # 1 summary + 2 recent entries
    assert hasattr(compacted[0], "phase")
    assert compacted[0].phase == "COMPACTED_MEMORY"


# ── EpisodicMemory Tests ─────────────────────────────────────────────

def test_episodic_memory(tmp_path):
    ep_file = tmp_path / "episodic_test.json"
    em = EpisodicMemory(storage_path=str(ep_file))

    # Log Episode
    ep = em.log_episode(
        session_id="test_sess_101",
        query="What is Microsoft's cloud growth and AI strategy?",
        tools_used=["company_profile", "sec_filing_search", "earnings_transcript"],
        tools_succeeded=["company_profile", "earnings_transcript"],
        tools_failed=["sec_filing_search"],
        strategy_note="Earnings transcripts gave the best forward-looking signal for cloud growth.",
        query_type="cloud_growth",
        success=True,
    )
    assert ep["session_id"] == "test_sess_101"

    # Retrieve Episode
    recalled = em.get_similar_episodes(query="Microsoft cloud AI growth", top_k=1)
    assert len(recalled) == 1
    assert "earnings transcripts gave the best" in recalled[0]["strategy_note"].lower()


# ── Real Vector DB Tool Execution Tests ──────────────────────────────

def test_real_vector_db_tools(temp_vector_store):
    registry = ToolRegistry(schemas_dir="tools/schemas")

    # Store via registry
    store_res = registry.execute_tool(
        "vector_db_store",
        {
            "content": "Microsoft reported FY24 Q4 revenue of $64.7 billion, up 15% YoY.",
            "metadata": {
                "ticker": "MSFT",
                "source_type": "SEC_10K",
                "date": "2024-07-30",
                "confidence": 0.98,
                "verified": True,
            },
        },
    )
    assert store_res["stored"] is True
    assert store_res["chunk_count"] >= 1

    # Search via registry
    search_res = registry.execute_tool(
        "vector_db_search",
        {
            "query": "Microsoft quarterly revenue growth",
            "ticker": "MSFT",
            "top_k": 5,
        },
    )
    assert search_res["results_count"] >= 1
    assert "Microsoft reported" in search_res["results"][0]["content"]
