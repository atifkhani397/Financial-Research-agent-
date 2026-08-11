"""
ARA-1 Day 4 — Challenge 1 Mock Run

Runs the full Plan-and-Execute agent end-to-end against mock tool data
with a simulated LLM wrapper (no Groq API key required).

Challenge 1: "Create a comprehensive profile of Microsoft Corporation
including business overview, financial summary, key executives, and
recent developments."

Outputs the full Thought/Action/Observation trace.
"""

import sys
import os
import json
import time
from pathlib import Path

# Ensure project root is on the path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, PROJECT_ROOT)

# Fix Windows console encoding for emoji output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from tools.tool_registry import ToolRegistry
from agent.core import FinancialResearchAgent, AgentConfig


# ═══════════════════════════════════════════════════════════════════════
# Mock LLM Wrapper — simulates the Day 3 LLMWrapper without Groq calls
# ═══════════════════════════════════════════════════════════════════════
class MockLLMWrapper:
    """
    Simulates LLMWrapper.invoke() with deterministic responses.
    Routes calls to the planner, executor, or synthesizer based on
    the system prompt content.
    """

    def __init__(self):
        self._call_count = 0

    def invoke(self, messages, role="planning", tools=None, session_id=""):
        self._call_count += 1
        system = messages[0].get("content", "") if messages else ""
        user_msg = ""
        for m in messages:
            if m.get("role") == "user":
                user_msg = m.get("content", "")

        # Route to appropriate mock response
        if "PLANNER" in system and "decompose" in system.lower():
            return self._planner_response()
        elif "SYNTHESIS" in system:
            return self._synthesis_response(system)
        elif "PLANNER" in system and "revising" in system.lower():
            return self._revision_response()
        else:
            return self._executor_response(system, user_msg, tools)

    def _planner_response(self):
        """Return a deterministic plan for the Microsoft research challenge."""
        plan = {
            "plan_title": "Comprehensive Microsoft Corporation (MSFT) Profile",
            "steps": [
                {
                    "step_id": 1,
                    "description": "Retrieve Microsoft company profile for business overview and executive data",
                    "tool_hint": "company_profile",
                    "expected_output": "Company description, sector, industry, headquarters, CEO, and full executive list",
                    "depends_on": [],
                },
                {
                    "step_id": 2,
                    "description": "Fetch key financial metrics from the financial data API for quantitative summary",
                    "tool_hint": "financial_data_api",
                    "expected_output": "Revenue, net income, PE ratio, market cap, EPS, margins, and growth rates",
                    "depends_on": [],
                },
                {
                    "step_id": 3,
                    "description": "Search SEC 10-K filing for authoritative financial data to cross-reference",
                    "tool_hint": "sec_filing_search",
                    "expected_output": "Official revenue, net income, segment breakdowns, and risk factors from latest 10-K",
                    "depends_on": [],
                },
                {
                    "step_id": 4,
                    "description": "Gather recent news and sentiment analysis for developments section",
                    "tool_hint": "news_sentiment",
                    "expected_output": "Recent headlines, sentiment scores, and key stories from the last 7 days",
                    "depends_on": [],
                },
                {
                    "step_id": 5,
                    "description": "Search the web for latest Microsoft developments and market context",
                    "tool_hint": "web_search",
                    "expected_output": "Current stock price, YTD return, and recent strategic developments",
                    "depends_on": [],
                },
                {
                    "step_id": 6,
                    "description": "Retrieve latest earnings call transcript for management commentary and guidance",
                    "tool_hint": "earnings_transcript",
                    "expected_output": "Key management quotes, forward guidance, and strategic commentary",
                    "depends_on": [],
                },
                {
                    "step_id": 7,
                    "description": "Cross-reference revenue figures between financial API and SEC filing",
                    "tool_hint": "calculation_engine",
                    "expected_output": "Validation that revenue figures match across sources",
                    "depends_on": [2, 3],
                },
                {
                    "step_id": 8,
                    "description": "Compile and synthesize all gathered data into the final comprehensive report",
                    "tool_hint": None,
                    "expected_output": "Complete research report with all sections populated and sources cited",
                    "depends_on": [1, 2, 3, 4, 5, 6, 7],
                },
            ],
        }
        return {
            "content": json.dumps(plan),
            "tool_calls": [],
            "usage": {"prompt_tokens": 800, "completion_tokens": 400},
            "model": "mock-planner",
            "latency_ms": 50.0,
        }

    def _executor_response(self, system, user_msg, tools):
        """Return mock executor responses with native tool calls."""
        # Determine which step we're on from the system prompt
        step_id = 0
        tool_hint = ""
        if "Current step" in system:
            try:
                # Parse "Current step (N/M):" pattern
                idx = system.index("Current step (")
                rest = system[idx + 14:]
                step_id = int(rest.split("/")[0])
            except (ValueError, IndexError):
                pass

        if "Tool hint:" in system:
            try:
                idx = system.index("Tool hint:")
                tool_hint = system[idx + 10:].split("\n")[0].strip()
            except (ValueError, IndexError):
                pass

        # Return tool-calling response based on step
        tool_call_map = {
            1: {"name": "company_profile", "args": {"ticker": "MSFT"}},
            2: {"name": "financial_data_api", "args": {"ticker": "MSFT", "metric": "overview"}},
            3: {"name": "sec_filing_search", "args": {"ticker": "MSFT", "filing_type": "10-K"}},
            4: {"name": "news_sentiment", "args": {"ticker": "MSFT", "days_back": 7}},
            5: {"name": "web_search", "args": {"query": "Microsoft Corporation MSFT latest developments 2025"}},
            6: {"name": "earnings_transcript", "args": {"ticker": "MSFT", "year": 2025, "quarter": "Q4"}},
            7: {"name": "calculation_engine", "args": {"operation": "subtract", "operands": [245122000000, 245122000000]}},
        }

        # Check if this is a follow-up cycle (tool result already in messages)
        is_followup = "Tool result from" in user_msg

        if is_followup:
            # After observing tool result, mark step complete
            return {
                "content": f"STEP_COMPLETE: Successfully gathered data for step {step_id}. "
                           f"The {tool_hint} tool returned the expected data. Key findings "
                           f"have been extracted and will be used in the final report synthesis.",
                "tool_calls": [],
                "usage": {"prompt_tokens": 500, "completion_tokens": 100},
                "model": "mock-executor",
                "latency_ms": 30.0,
            }

        if step_id in tool_call_map and step_id != 8:
            tc = tool_call_map[step_id]
            return {
                "content": f"I need to call {tc['name']} to gather data for this step.",
                "tool_calls": [
                    {
                        "name": tc["name"],
                        "args": tc["args"],
                        "id": f"call_{step_id}_{tc['name']}",
                    }
                ],
                "usage": {"prompt_tokens": 500, "completion_tokens": 80},
                "model": "mock-executor",
                "latency_ms": 25.0,
            }

        # Step 8 or unknown — synthesis step
        return {
            "content": "STEP_COMPLETE: All data has been gathered. Ready for final report synthesis.",
            "tool_calls": [],
            "usage": {"prompt_tokens": 300, "completion_tokens": 50},
            "model": "mock-executor",
            "latency_ms": 20.0,
        }

    def _synthesis_response(self, system):
        """Return a mock final report."""
        report = """# Microsoft Corporation (MSFT) — Comprehensive Research Profile

## Executive Summary
Microsoft Corporation is a $3.12 trillion technology giant operating across cloud computing, productivity software, and personal computing segments. The company is experiencing strong growth driven by its AI strategy and Azure cloud platform, with FY2025 revenue of $245.1 billion (up 15.6% YoY) and net income of $88.5 billion. [Source: financial_data_api(MSFT), sec_filing_search(MSFT, 10-K)]

## Business Overview
**Company**: Microsoft Corporation
**Ticker**: MSFT (NASDAQ)
**Headquarters**: Redmond, Washington, USA
**Founded**: 1975
**Employees**: ~228,000 full-time
**Sector**: Technology | **Industry**: Software—Infrastructure
[Source: company_profile(MSFT)]

Microsoft operates through three reportable segments:
1. **Productivity and Business Processes** ($80.5B revenue) — Office 365, Microsoft Teams, LinkedIn, Dynamics 365, Microsoft 365 Copilot
2. **Intelligent Cloud** ($105.7B revenue) — Azure, SQL Server, Windows Server, GitHub, Nuance
3. **More Personal Computing** ($58.9B revenue) — Windows, Surface, Xbox/Activision Blizzard, Bing/Search
[Source: sec_filing_search(MSFT, 10-K)]

## Financial Summary

| Metric | Value | Source |
|--------|-------|--------|
| Revenue (FY2025 TTM) | $245.1B | financial_data_api, sec_filing_search |
| Net Income (FY2025 TTM) | $88.5B | financial_data_api, sec_filing_search |
| Market Cap | $3.12T | financial_data_api |
| P/E Ratio | 35.2x | financial_data_api |
| EPS (Diluted) | $11.89 | financial_data_api |
| Operating Margin | 44.9% | financial_data_api |
| ROE | 38.9% | financial_data_api |
| Debt-to-Equity | 0.29 | financial_data_api |
| Free Cash Flow | $74.1B | financial_data_api |
| Dividend Yield | 0.72% | financial_data_api |
| YoY Revenue Growth | 15.6% | financial_data_api |

**Cross-reference check**: Revenue of $245,122,000,000 matches between financial_data_api and sec_filing_search (10-K filing). Discrepancy = $0. ✅ [Source: calculation_engine(subtract)]

## Key Executives

| Name | Title |
|------|-------|
| Satya Nadella | Chairman & CEO |
| Amy E. Hood | Executive VP & CFO |
| Bradford L. Smith | Vice Chair & President |
| Judson B. Althoff | Executive VP & Chief Commercial Officer |
| Rajesh Jha | Executive VP, Experiences & Devices |
| Scott Guthrie | Executive VP, Cloud & AI |
[Source: company_profile(MSFT)]

## Recent Developments

### Market & AI Momentum
- **Azure Revenue Growth**: Azure cloud revenue grew 29% YoY in Q4 FY2025, driven by strong enterprise AI adoption [Source: news_sentiment(MSFT), earnings_transcript(MSFT, Q4 2025)]
- **Copilot Expansion**: Microsoft is expanding its AI Copilot assistant to all Office 365 enterprise tiers starting Q4 2025, with 2.5M+ enterprise users [Source: news_sentiment(MSFT), earnings_transcript(MSFT, Q4 2025)]
- **Gaming Record**: Xbox and Activision Blizzard integration drove gaming segment to record $5.7B quarterly revenue [Source: news_sentiment(MSFT)]
- **Stock Performance**: YTD return of +12.4%, current price $419.72, 52-week range $388.45 - $468.35 [Source: web_search(MSFT)]

### Forward Guidance (Q1 FY2026)
- Revenue guidance: $67.2B - $68.5B
- Azure growth expected to accelerate further
- CapEx to increase for AI infrastructure buildout
[Source: earnings_transcript(MSFT, Q4 2025)]

### Regulatory Risks
- EU and US regulators are examining Microsoft's strategic investments in OpenAI for potential antitrust concerns [Source: news_sentiment(MSFT)]
- Key risk factors include intense competition in cloud/AI, cybersecurity threats, and foreign currency exposure [Source: sec_filing_search(MSFT, 10-K)]

## Data Conflicts
No material conflicts were identified between sources. Revenue figures from the financial data API ($245.1B) match the SEC 10-K filing ($245,122,000,000) exactly. [Source: calculation_engine(subtract, [245122000000, 245122000000]) → $0 discrepancy]

## Coverage Gaps
- Detailed competitive analysis vs. specific cloud peers (AWS, GCP) was not performed in this run
- Historical multi-year financial trend data was not retrieved
- Insider trading activity was not analyzed

> ⚠️ **Disclaimer**: This report presents factual data only and does not constitute investment advice. All data sourced from mock tools for demonstration purposes.
"""
        return {
            "content": report,
            "tool_calls": [],
            "usage": {"prompt_tokens": 2000, "completion_tokens": 1200},
            "model": "mock-synthesizer",
            "latency_ms": 80.0,
        }

    def _revision_response(self):
        """Not used in this challenge, but implemented for completeness."""
        return {
            "content": "{}",
            "tool_calls": [],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
            "model": "mock-planner",
            "latency_ms": 20.0,
        }


# ═══════════════════════════════════════════════════════════════════════
# Main — Run Challenge 1
# ═══════════════════════════════════════════════════════════════════════
def main():
    print("=" * 80)
    print("  ARA-1 Day 4 — Challenge 1 Mock Run")
    print("  Microsoft Corporation Comprehensive Profile")
    print("=" * 80)
    print()

    # Initialize components
    mock_llm = MockLLMWrapper()
    tool_registry = ToolRegistry(schemas_dir="tools/schemas")

    config = AgentConfig(
        max_tool_calls=20,
        max_plan_steps=15,
        max_react_cycles=3,
        max_wall_clock_seconds=300,
    )

    agent = FinancialResearchAgent(
        llm_wrapper=mock_llm,
        tool_registry=tool_registry,
        config=config,
    )

    # The challenge query
    query = (
        "Create a comprehensive profile of Microsoft Corporation including "
        "business overview, financial summary, key executives, and recent "
        "developments."
    )

    print(f"[QUERY] {query}")
    print()
    print("-" * 80)
    print("  EXECUTION TRACE")
    print("-" * 80)
    print()

    # Run the agent
    result = agent.run(query, session_id="challenge1-mock")

    # ── Print the full trace ─────────────────────────────────────────
    for i, entry in enumerate(agent.trace):
        ts = f"[{entry.timestamp:6.2f}s]"
        phase = entry.phase.ljust(12)

        if entry.phase == "ACTION":
            print(f"  {ts} [TOOL] {phase} Step {entry.step_id} Cycle {entry.cycle}")
            print(f"           Tool: {entry.tool_name}")
            print(f"           Args: {json.dumps(entry.tool_args, indent=2)}")
        elif entry.phase == "OBSERVATION":
            # Truncate very long observations
            result_preview = entry.tool_result[:500] if entry.tool_result else entry.content
            print(f"  {ts} [OBS]  {phase} Step {entry.step_id} Cycle {entry.cycle}")
            print(f"           Tool: {entry.tool_name}")
            print(f"           Result: {result_preview}...")
        elif entry.phase == "THOUGHT":
            print(f"  {ts} [THK]  {phase} Step {entry.step_id} Cycle {entry.cycle}")
            print(f"           {entry.content[:200]}")
        elif entry.phase == "PLAN":
            print(f"  {ts} [PLAN] {phase}")
            print(f"           {entry.content[:200]}")
        elif entry.phase == "SYNTHESIS":
            print(f"  {ts} [SYN]  {phase}")
            print(f"           {entry.content[:200]}")
        elif entry.phase == "LIMIT":
            print(f"  {ts} [LIM]  {phase}")
            print(f"           {entry.content[:200]}")
        elif entry.phase == "ERROR":
            print(f"  {ts} [ERR]  {phase}")
            print(f"           {entry.content[:200]}")
        else:
            print(f"  {ts} [INFO] {phase}")
            print(f"           {entry.content[:200]}")
        print()

    # ── Print summary ────────────────────────────────────────────────
    print("-" * 80)
    print("  EXECUTION SUMMARY")
    print("-" * 80)
    metadata = result["metadata"]
    print(f"  Session ID:        {metadata['session_id']}")
    print(f"  Termination:       {metadata['termination_reason']}")
    print(f"  Tool calls:        {metadata['total_tool_calls']}/{config.max_tool_calls}")
    print(f"  Steps completed:   {metadata['steps_completed']}/{metadata['steps_total']}")
    print(f"  Wall-clock time:   {metadata['elapsed_seconds']:.2f}s")
    print()

    # ── Print step results ───────────────────────────────────────────
    print("-" * 80)
    print("  STEP RESULTS")
    print("-" * 80)
    for sr in result["step_results"]:
        status_icon = "[OK]" if sr["status"] == "completed" else "[!!]"
        print(f"  {status_icon} Step {sr['step_id']}: {sr['description'][:70]}")
        print(f"     Status: {sr['status']} | Tool calls: {sr['tool_calls_made']}")
        print()

    # ── Print the plan ───────────────────────────────────────────────
    if result["plan"]:
        print("-" * 80)
        print("  EXECUTION PLAN")
        print("-" * 80)
        print(f"  Title: {result['plan'].get('plan_title', 'N/A')}")
        for step in result["plan"].get("steps", []):
            print(f"  Step {step['step_id']}: {step['description'][:70]}")
            print(f"    Tool: {step.get('tool_hint', 'None')} | Depends: {step.get('depends_on', [])}")
        print()

    # ── Print the final report ───────────────────────────────────────
    print("=" * 80)
    print("  FINAL REPORT")
    print("=" * 80)
    print()
    print(result["report"])

    # ── Write trace to file ──────────────────────────────────────────
    trace_output = {
        "challenge": "Challenge 1 — Microsoft Corporation Comprehensive Profile",
        "query": query,
        "metadata": metadata,
        "plan": result["plan"],
        "step_results": result["step_results"],
        "trace": result["trace"],
    }

    trace_path = Path(PROJECT_ROOT) / "tests" / "challenge1_trace.json"
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(trace_output, f, indent=2, default=str)
    print(f"\n>> Full trace saved to: {trace_path}")

    report_path = Path(PROJECT_ROOT) / "tests" / "challenge1_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(result["report"])
    print(f">> Report saved to: {report_path}")

    return result


if __name__ == "__main__":
    main()
