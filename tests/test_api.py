"""
ARA-1 API Test Suite (Day 16)
Location: tests/test_api.py
Rationale for location: All pytest unit and integration suites are unified under the Section D3 'tests/' directory.
Tests all REST endpoints against mocked or lightweight agent executions.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test GET /health returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ARA-1" in data["agent"]


def test_list_challenges_endpoint():
    """Test GET /api/challenges returns 8 predefined challenges."""
    response = client.get("/api/challenges")
    assert response.status_code == 200
    challenges = response.json()
    assert len(challenges) == 8
    assert challenges[0]["challenge_id"] == 1
    assert "Single Company Profile" in challenges[0]["title"]
    assert "Microsoft" in challenges[0]["query"]


def test_run_challenge_endpoint():
    """Test POST /api/challenges/4/run triggers challenge execution."""
    response = client.post("/api/challenges/4/run")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["status"] == "processing"


def test_get_tools_endpoint():
    """Test GET /api/tools returns live tool registry items."""
    response = client.get("/api/tools")
    assert response.status_code == 200
    tools = response.json()
    assert len(tools) >= 12
    tool_names = [t["name"] for t in tools]
    assert "company_profile" in tool_names
    assert "sec_filing_search" in tool_names


def test_memory_search_endpoint():
    """Test GET /api/memory/search returns search payload."""
    response = client.get("/api/memory/search?q=cloud+revenue&top_k=3")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "cloud revenue"
    assert "results" in data


def test_evaluation_metrics_endpoint():
    """Test GET /api/evaluation returns structured evaluation metrics."""
    response = client.get("/api/evaluation")
    assert response.status_code == 200
    data = response.json()
    assert data["composite_score"] >= 80.0
    assert "metrics_summary" in data


def test_traces_endpoint():
    """Test GET /api/traces returns curated trace gallery entries."""
    response = client.get("/api/traces")
    assert response.status_code == 200
    traces = response.json()
    assert len(traces) == 6
    assert "trace_id" in traces[0]


def test_research_query_flow():
    """Test POST /api/research and GET /api/research/{session_id}/report."""
    post_res = client.post(
        "/api/research",
        json={"query": "Test quick report on Apple Inc (AAPL)", "session_id": "test-api-sess-001"}
    )
    assert post_res.status_code == 200
    post_data = post_res.json()
    assert post_data["session_id"] == "test-api-sess-001"

    get_res = client.get("/api/research/test-api-sess-001/report")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["session_id"] == "test-api-sess-001"
