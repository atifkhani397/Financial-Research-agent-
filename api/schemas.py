"""
ARA-1 API Pydantic Schemas (Day 16)
Defines request and response models for all REST endpoints and WebSocket events.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ── Research Schemas ────────────────────────────────────────────────────────
class ResearchQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language financial research query", example="Produce a complete investment report on NVIDIA (NVDA).")
    session_id: Optional[str] = Field(None, description="Optional custom session identifier")
    max_tool_calls: int = Field(20, ge=1, le=50, description="Maximum tool calls budget")


class ResearchQueryResponse(BaseModel):
    session_id: str = Field(..., description="Unique research session identifier")
    status: str = Field(..., description="Execution status: queued, processing, completed, or failed")
    message: str = Field(..., description="User-facing status message")


class TraceEvent(BaseModel):
    timestamp: float = Field(..., description="Unix timestamp of event")
    phase: str = Field(..., description="Event phase: PLAN, THOUGHT, ACTION, OBSERVATION, LIMIT, SYNTHESIS")
    step_id: int = Field(0, description="Step number in execution plan")
    cycle: int = Field(1, description="ReAct inner loop cycle number")
    tool_name: Optional[str] = Field(None, description="Name of tool if ACTION phase")
    content: str = Field(..., description="Human-readable event details")


class ReportResponse(BaseModel):
    session_id: str = Field(..., description="Research session identifier")
    query: str = Field(..., description="Original research query")
    status: str = Field(..., description="Report completion status")
    report_markdown: str = Field(..., description="Publication-grade markdown report content")
    citations: List[str] = Field(default_factory=list, description="Extracted tool citations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata (time, tools used, steps)")


# ── Challenge Schemas ───────────────────────────────────────────────────────
class ChallengeItem(BaseModel):
    challenge_id: int = Field(..., description="Challenge number (1-8)")
    title: str = Field(..., description="Challenge title")
    difficulty: str = Field(..., description="Difficulty rating (e.g. 1/5, 5/5)")
    query: str = Field(..., description="Predefined research query text")
    expected_tools: List[str] = Field(default_factory=list, description="Expected primary tool names")


# ── Tool Registry Schemas ───────────────────────────────────────────────────
class ToolItem(BaseModel):
    name: str = Field(..., description="Registered tool name")
    description: str = Field(..., description="Tool capability description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema parameters")
    source_tier: str = Field(..., description="Authoritative source tier (Tier 1-5 or Internal)")
    usage_count: int = Field(0, description="Execution count in current session")


# ── Memory Schemas ──────────────────────────────────────────────────────────
class MemorySearchResponse(BaseModel):
    query: str = Field(..., description="Search query string")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Matching document chunks")
    count: int = Field(0, description="Number of retrieved results")


# ── Evaluation Schemas ──────────────────────────────────────────────────────
class EvaluationResponse(BaseModel):
    framework_version: str = Field("ARA-1 Day 13 V2", description="Evaluation framework version")
    composite_score: float = Field(..., description="Overall average composite score (0-100)")
    metrics_summary: Dict[str, Any] = Field(default_factory=dict, description="Aggregated metric domain averages")
    challenge_scores: List[Dict[str, Any]] = Field(default_factory=list, description="Per-challenge score breakdown")


# ── Trace Gallery Schemas ───────────────────────────────────────────────────
class TraceGalleryItem(BaseModel):
    trace_id: str = Field(..., description="Unique trace identifier")
    title: str = Field(..., description="Trace title/topic")
    query: str = Field(..., description="Original research query")
    session_id: str = Field(..., description="Session identifier")
    highlights: str = Field(..., description="Key architectural takeaway")
    annotations: Dict[str, str] = Field(default_factory=dict, description="Agent performance annotations")
