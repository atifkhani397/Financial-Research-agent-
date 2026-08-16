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


def _execute_agent_task(query: str, session_id: str, max_tool_calls: int, loop: asyncio.AbstractEventLoop):
    """Background worker executing the agent's research loop."""
    try:
        from agent.core import FinancialResearchAgent, AgentConfig
        from agent.llm import get_llm
        from tools.tool_registry import ToolRegistry

        llm = get_llm()
        registry = ToolRegistry()
        config = AgentConfig(max_tool_calls=max_tool_calls, max_wall_clock_seconds=1200)

        agent = FinancialResearchAgent(llm_wrapper=llm, tool_registry=registry, config=config)

        # Broadcast trace callback hook — schedules onto the FastAPI event loop
        def trace_callback(phase: str, content: str, step_id: int = 0, cycle: int = 1, tool_name: str = None):
            event = {
                "timestamp": time.time(),
                "phase": phase,
                "step_id": step_id,
                "cycle": cycle,
                "tool_name": tool_name,
                "content": content or "",
            }
            # Thread-safe: schedule the coroutine onto the main FastAPI event loop
            asyncio.run_coroutine_threadsafe(ws_manager.broadcast_event(session_id, event), loop)

        # Register trace callback on agent
        agent.trace_callback = trace_callback

        RESEARCH_SESSIONS[session_id]["status"] = "processing"
        # Fire initial processing event
        trace_callback(phase="PLAN", content=f"Starting autonomous research: {query}", step_id=0, cycle=0)

        result = agent.run(query=query, session_id=session_id)

        RESEARCH_SESSIONS[session_id]["status"] = "completed"
        RESEARCH_SESSIONS[session_id]["result"] = result
        RESEARCH_SESSIONS[session_id]["report"] = result.get("report", "")
        RESEARCH_SESSIONS[session_id]["metadata"] = result.get("metadata", {})
        logger.info(f"Research task completed successfully for session={session_id}")

        # Persist report file (.md) and PDF file (.pdf) to results directory in real time
        try:
            from pathlib import Path
            results_dir = Path("results")
            results_dir.mkdir(exist_ok=True)
            report_text = result.get("report", "")

            # 1. Save Markdown file
            report_file = results_dir / f"{session_id}.md"
            report_file.write_text(report_text, encoding="utf-8")

            # 2. Real-time PDF generation
            pdf_bytes = _convert_markdown_to_pdf_bytes(report_text)
            pdf_file = results_dir / f"{session_id}.pdf"
            pdf_file.write_bytes(pdf_bytes)
            logger.info(f"Real-time PDF generated and saved for session={session_id}")
        except Exception as file_err:
            logger.warning(f"Could not save report/PDF file for session {session_id}: {file_err}")

        # Broadcast completion event
        trace_callback(phase="SYNTHESIS", content="Research report generated successfully. Click 'View Finished Report' to see the full analysis.", step_id=99, cycle=1)

    except Exception as e:
        logger.error(f"Research task failed for session={session_id}: {e}", exc_info=True)
        RESEARCH_SESSIONS[session_id]["status"] = "failed"
        RESEARCH_SESSIONS[session_id]["error"] = str(e)
        RESEARCH_SESSIONS[session_id]["report"] = f"# Partial Research Report\n\n> ⚠️ Execution Error: {str(e)}"


@router.get("/reports/all")
async def list_all_reports():
    """Lists all research reports (from memory and results/ directory)."""
    from pathlib import Path
    import os

    reports = []
    seen_ids = set()

    # 1. From in-memory sessions
    for sess_id, sess_data in RESEARCH_SESSIONS.items():
        if sess_data.get("report"):
            seen_ids.add(sess_id)
            report_text = sess_data.get("report", "")
            title = sess_data.get("query") or sess_id
            lines = report_text.strip().split("\n")
            for line in lines[:5]:
                if line.startswith("# "):
                    title = line.replace("# ", "").strip()
                    break

            reports.append({
                "session_id": sess_id,
                "title": title,
                "query": sess_data.get("query", title),
                "status": sess_data.get("status", "completed"),
                "date": time.strftime("%Y-%m-%d %H:%M", time.localtime(sess_data.get("start_time", time.time()))),
                "pdf_url": f"/api/research/{sess_id}/pdf",
            })

    # 2. From results directory
    results_dir = Path("results")
    if results_dir.exists():
        for file_path in results_dir.glob("*.md"):
            sess_id = file_path.stem
            if sess_id in seen_ids:
                continue

            try:
                report_text = file_path.read_text(encoding="utf-8")
                title = sess_id.replace("_", " ").title()
                lines = report_text.strip().split("\n")
                for line in lines[:5]:
                    if line.startswith("# "):
                        title = line.replace("# ", "").strip()
                        break

                mtime = os.path.getmtime(file_path)
                date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime))

                reports.append({
                    "session_id": sess_id,
                    "title": title,
                    "query": title,
                    "status": "completed",
                    "date": date_str,
                    "pdf_url": f"/api/research/{sess_id}/pdf",
                })
                seen_ids.add(sess_id)
            except Exception as e:
                logger.warning(f"Error reading report file {file_path}: {e}")

    return {"reports": reports, "count": len(reports)}


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

    # Capture the running FastAPI event loop so the background thread can schedule async calls
    loop = asyncio.get_running_loop()

    # Launch background thread with loop reference
    executor.submit(_execute_agent_task, req.query, session_id, req.max_tool_calls, loop)

    return ResearchQueryResponse(
        session_id=session_id,
        status="processing",
        message="Autonomous research task initiated successfully."
    )


@router.get("/{session_id}/report", response_model=ReportResponse)
async def get_research_report(session_id: str):
    """Retrieves finished markdown report, citations, and execution metadata for a session."""
    from pathlib import Path
    
    if session_id not in RESEARCH_SESSIONS:
        # Check if saved in results directory
        results_dir = Path("results")
        target_file = results_dir / f"{session_id}.md"
        if not target_file.exists():
            # Check challenge mapping or latest results
            candidates = list(results_dir.glob("*.md"))
            for cand in candidates:
                if session_id.lower() in cand.stem.lower():
                    target_file = cand
                    break
            if not target_file.exists() and candidates:
                target_file = candidates[0]
        
        if target_file and target_file.exists():
            report_text = target_file.read_text(encoding="utf-8")
            RESEARCH_SESSIONS[session_id] = {
                "session_id": session_id,
                "query": f"Session {session_id}",
                "status": "completed",
                "report": report_text,
                "metadata": {"source": str(target_file)},
            }
        else:
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
        status=sess.get("status", "completed" if report_text else sess.get("status", "processing")),
        report_markdown=report_text or f"# Processing Session: {session_id}\n\n*Agent is currently performing multi-source research...",
        citations=unique_citations,
        metadata=sess.get("metadata", {}),
    )


def _convert_markdown_to_pdf_bytes(markdown_text: str) -> bytes:
    """Converts Markdown text to professional PDF binary bytes using Python markdown + xhtml2pdf."""
    from io import BytesIO
    import markdown
    from xhtml2pdf import pisa
    import re
    from agent.core import sanitize_report_text

    # Pre-process math and LaTeX notation into readable text for PDF
    clean_md = sanitize_report_text(markdown_text)
    clean_md = re.sub(r'\\\((.*?)\\\)', r'\1', clean_md)
    clean_md = re.sub(r'\\\[(.*?)\\\]', r'\1', clean_md)
    clean_md = re.sub(r'\$\$(.*?)\$\$', r'\1', clean_md, flags=re.DOTALL)
    clean_md = re.sub(r'\$(.*?)\$', r'\1', clean_md)

    # Convert Markdown to HTML with extra (tables, fenced_code) & nl2br extensions
    html_body = markdown.markdown(clean_md, extensions=['extra', 'nl2br', 'sane_lists'])

    # Styled HTML Template for PDF output
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: a4 portrait;
                margin: 1.5cm;
            }}
            body {{
                font-family: 'Helvetica', 'Arial', sans-serif;
                font-size: 10pt;
                line-height: 1.5;
                color: #0f172a;
            }}
            h1 {{
                font-size: 17pt;
                color: #0369a1;
                border-bottom: 2px solid #0284c7;
                padding-bottom: 6px;
                margin-top: 0;
                margin-bottom: 12px;
            }}
            h2 {{
                font-size: 13pt;
                color: #0f172a;
                margin-top: 16px;
                margin-bottom: 8px;
                border-bottom: 1px solid #cbd5e1;
                padding-bottom: 4px;
            }}
            h3 {{
                font-size: 11pt;
                color: #334155;
                margin-top: 12px;
                margin-bottom: 6px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 14px 0;
                font-size: 8.5pt;
            }}
            th {{
                background-color: #0f172a;
                color: #ffffff;
                font-weight: bold;
                text-align: left;
                padding: 7px 9px;
                border: 1px solid #1e293b;
            }}
            td {{
                padding: 6px 8px;
                border: 1px solid #cbd5e1;
            }}
            tr:nth-child(even) {{
                background-color: #f8fafc;
            }}
            code {{
                font-family: 'Courier', monospace;
                background-color: #f1f5f9;
                color: #0284c7;
                padding: 2px 4px;
                font-size: 8.5pt;
            }}
            pre {{
                background-color: #0f172a;
                color: #f8fafc;
                padding: 10px;
                font-family: 'Courier', monospace;
                font-size: 8.5pt;
                white-space: pre-wrap;
            }}
            blockquote {{
                border-left: 4px solid #0284c7;
                margin: 10px 0;
                padding-left: 10px;
                color: #475569;
                background-color: #f0f9ff;
            }}
            ul, ol {{
                margin-top: 4px;
                margin-bottom: 10px;
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 3px;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(BytesIO(full_html.encode("utf-8")), dest=pdf_buffer)
    if pisa_status.err:
        logger.error("pisa.CreatePDF failed to generate PDF")
        raise HTTPException(status_code=500, detail="PDF generation failed")

    return pdf_buffer.getvalue()


@router.get("/{session_id}/pdf")
async def download_research_report_pdf(session_id: str):
    """Generates and streams a PDF file from the session's Markdown research report using Python."""
    from fastapi.responses import Response
    from pathlib import Path

    # 1. Check if pre-generated PDF file exists in results directory
    results_dir = Path("results")
    pdf_file = results_dir / f"{session_id}.pdf"
    if pdf_file.exists():
        pdf_bytes = pdf_file.read_bytes()
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Research_Report_{session_id}.pdf"
            }
        )

    # 2. Otherwise generate from report markdown
    report_resp = await get_research_report(session_id)
    report_markdown = report_resp.report_markdown

    if not report_markdown or "currently performing multi-source research" in report_markdown:
        raise HTTPException(status_code=400, detail="Research report is not yet completed.")

    pdf_bytes = _convert_markdown_to_pdf_bytes(report_markdown)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Research_Report_{session_id}.pdf"
        }
    )

