import sys
import time
import logging
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("terminal_research")

def run():
    query = "Perform an executive equity research analysis on NVIDIA Corporation (NVDA) including FY2024 revenue, Data Center growth, and R&D capital expenditure."
    session_id = "sess_terminal_complete"

    print(f"=== Starting Terminal Financial Research Task ===")
    print(f"Session ID: {session_id}")
    print(f"Query: {query}\n")

    from agent.core import FinancialResearchAgent, AgentConfig
    from agent.llm import get_llm
    from tools.tool_registry import ToolRegistry
    from api.routes.research import _convert_markdown_to_pdf_bytes

    llm = get_llm()
    registry = ToolRegistry()
    config = AgentConfig(max_tool_calls=20, max_wall_clock_seconds=1200)

    agent = FinancialResearchAgent(llm_wrapper=llm, tool_registry=registry, config=config)

    start_t = time.time()
    result = agent.run(query=query, session_id=session_id)
    elapsed = time.time() - start_t

    report_markdown = result.get("report", "")
    print(f"\n=== Research Task Completed in {elapsed:.1f}s ===")
    print(f"Steps Completed: {len(result.get('step_results', []))}")
    print(f"Termination Reason: {result.get('termination_reason')}")

    # 1. Save Markdown
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    md_file = results_dir / f"{session_id}.md"
    md_file.write_text(report_markdown, encoding="utf-8")
    print(f"Saved Markdown Report: {md_file.resolve()}")

    # 2. Convert to PDF
    pdf_bytes = _convert_markdown_to_pdf_bytes(report_markdown)
    pdf_file = results_dir / f"{session_id}.pdf"
    pdf_file.write_bytes(pdf_bytes)
    print(f"Saved PDF Report: {pdf_file.resolve()}")
    print(f"PDF File Size: {len(pdf_bytes)} bytes")
    print(f"\n=== PDF DOWNLOAD READY ===")
    print(f"Download URL: http://localhost:8000/api/research/{session_id}/pdf")

if __name__ == "__main__":
    run()
