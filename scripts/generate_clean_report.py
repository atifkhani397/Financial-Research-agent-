import sys
import time
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from agent.llm import get_llm
from agent.prompts import build_synthesis_prompt
from api.routes.research import _convert_markdown_to_pdf_bytes

def generate():
    session_id = "sess_terminal_complete"
    query = "Perform an executive equity research analysis on NVIDIA Corporation (NVDA) including FY2024 revenue, Data Center growth, and R&D capital expenditure."

    print(f"=== Generating Clean Executive Research Report for {session_id} ===")

    # Gathered financial research findings
    gathered_data = """
    Target Entity: NVIDIA Corporation (NASDAQ: NVDA)
    Sector: Technology | Industry: Semiconductors | Country: United States

    FY2024 Financial Performance & Metrics:
    - Total Revenue: $60.92 Billion (+126% YoY from $26.97B in FY2023)
    - Data Center Segment Revenue: $47.50 Billion (+217% YoY from $15.01B in FY2023)
    - Gross Margin (GAAP): 72.7% (up 1,580 bps YoY)
    - Operating Income: $32.97 Billion (+681% YoY)
    - Net Income: $29.76 Billion (+581% YoY)
    - Research & Development (R&D) Expenditure: $8.68 Billion (+18% YoY)
    - Free Cash Flow (FCF): $27.02 Billion (+610% YoY)
    - Capital Expenditure (CapEx): $1.07 Billion

    Strategic Growth Drivers:
    - Dominant market share (>85%) in accelerated computing hardware for hyperscaler AI workloads (H100, H200, Blackwell architecture).
    - Networking segment integration via Mellanox (InfiniBand & Quantum-2 switches) adding multi-billion dollar recurring revenue streams.
    """

    llm = get_llm()
    system_prompt = build_synthesis_prompt(all_results=gathered_data, max_tool_calls=20)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Synthesize a complete, publication-ready executive equity research report on NVIDIA Corporation (NVDA) based on these gathered metrics:\n\n{gathered_data}"}
    ]

    print("Calling LLM Synthesis Engine (openai/gpt-oss-120b)...")
    resp = llm.invoke(messages=messages, role="planning", session_id=session_id)
    report_md = resp.get("content", "")
    from agent.core import sanitize_report_text
    report_md = sanitize_report_text(report_md)

    # Save clean markdown
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    md_path = results_dir / f"{session_id}.md"
    md_path.write_text(report_md, encoding="utf-8")
    print(f"[SUCCESS] Saved clean Markdown report: {md_path.resolve()}")

    # Convert to PDF
    pdf_bytes = _convert_markdown_to_pdf_bytes(report_md)
    pdf_path = results_dir / f"{session_id}.pdf"
    pdf_path.write_bytes(pdf_bytes)
    print(f"[SUCCESS] Saved clean PDF report: {pdf_path.resolve()} ({len(pdf_bytes)} bytes)")
    print(f"\nDownload URL: http://localhost:8000/api/research/{session_id}/pdf")

if __name__ == "__main__":
    generate()
