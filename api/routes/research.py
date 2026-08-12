"""
ARA-1 API Research Routes (Day 16)
REST endpoints for initiating research queries and retrieving finished markdown reports.
"""

import asyncio
import time
import uuid
import logging
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException, BackgroundTasks
from api.schemas import ResearchQueryRequest, ResearchQueryResponse, ReportResponse
from api.websocket import ws_manager

logger = logging.getLogger("ara1.api.routes.research")
router = APIRouter(prefix="/api/research", tags=["Research Queries"])

# Global session store for active and completed research tasks
RESEARCH_SESSIONS: Dict[str, Dict[str, Any]] = {}
executor = ThreadPoolExecutor(max_workers=4)


def _execute_agent_task(query: str, session_id: str, max_tool_calls: int):
    """Background worker executing the agent's research loop."""
    try:
        from agent.core import FinancialResearchAgent, AgentConfig
        from agent.llm import get_llm
        from tools.tool_registry import ToolRegistry

        llm = get_llm()
        registry = ToolRegistry()
        config = AgentConfig(max_tool_calls=max_tool_calls)

        agent = FinancialResearchAgent(llm_wrapper=llm, tool_registry=registry, config=config)

        # Broadcast trace callback hook
        def trace_callback(phase: str, content: str, step_id: int = 0, cycle: int = 1, tool_name: str = None):
            event = {
                "timestamp": time.time(),
                "phase": phase,
                "step_id": step_id,
                "cycle": cycle,
                "tool_name": tool_name,
                "content": content,
            }
            # Schedule async broadcast into loop
            asyncio.run(ws_manager.broadcast_event(session_id, event))

        # Register trace callback on agent
        agent.trace_callback = trace_callback

        RESEARCH_SESSIONS[session_id]["status"] = "processing"
        result = agent.run(query=query, session_id=session_id)

        RESEARCH_SESSIONS[session_id]["status"] = "completed"
        RESEARCH_SESSIONS[session_id]["result"] = result
        RESEARCH_SESSIONS[session_id]["report"] = result.get("report", "")
        RESEARCH_SESSIONS[session_id]["metadata"] = result.get("metadata", {})
        logger.info(f"Research task completed successfully for session={session_id}")

    except Exception as e:
        logger.error(f"Research task failed for session={session_id}: {e}", exc_info=True)
        RESEARCH_SESSIONS[session_id]["status"] = "failed"
        RESEARCH_SESSIONS[session_id]["error"] = str(e)
        RESEARCH_SESSIONS[session_id]["report"] = f"# Partial Research Report\n\n> ⚠️ Execution Error: {str(e)}"


@router.post("", response_model=ResearchQueryResponse)
async def submit_research_query(req: ResearchQueryRequest, background_tasks: BackgroundTasks):
    """Submits a free-text financial research query and kicks off autonomous processing."""
    session_id = req.session_id or f"sess_{uuid.uuid4().hex[:10]}"
    
    if session_id in RESEARCH_SESSIONS and RESEARCH_SESSIONS[session_id]["status"] == "processing":
        return ResearchQueryResponse(
            session_id=session_id,
            status="processing",
            message="Research task is already processing."
        )

    RESEARCH_SESSIONS[session_id] = {
        "session_id": session_id,
        "query": req.query,
        "status": "queued",
        "start_time": time.time(),
        "report": "",
        "metadata": {},
    }

    # Launch background thread
    executor.submit(_execute_agent_task, req.query, session_id, req.max_tool_calls)

    return ResearchQueryResponse(
        session_id=session_id,
        status="processing",
        message="Autonomous research task initiated successfully."
    )


@router.get("/{session_id}/report", response_model=ReportResponse)
async def get_research_report(session_id: str):
    """Retrieves finished markdown report, citations, and execution metadata for a session."""
    if session_id not in RESEARCH_SESSIONS:
        raise HTTPException(status_code=404, detail=f"Research session '{session_id}' not found.")

    sess = RESEARCH_SESSIONS[session_id]
    report_text = sess.get("report", "")

    # Extract citations
    import re
    citations = re.findall(r'\[Source:?\s*([^\]]+)\]', report_text, re.IGNORECASE)
    citations += re.findall(r'`([a-zA-Z0-9_]+)`', report_text)
    unique_citations = sorted(list(set(citations)))

    return ReportResponse(
        session_id=session_id,
        query=sess.get("query", ""),
        status=sess.get("status", "unknown"),
        report_markdown=report_text or f"# Processing Session: {session_id}\n\n*Agent is currently researching...",
        citations=unique_citations,
        metadata=sess.get("metadata", {}),
    )
