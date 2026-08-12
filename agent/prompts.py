"""
ARA-1 Prompt Construction Module

Builds system prompts for the Planner and Executor LLM calls.
Injects the tool registry (from Day 2) and the agent's hard constraints
from the project brief.

Constraints injected:
  - Never fabricate data
  - Cite every claim
  - Cross-reference numbers from >= 2 sources
  - Report conflicts rather than silently picking one value
  - No investment recommendations
  - Hard cap on tool calls per task (configurable, default 20)
"""

import json
from typing import Optional


# ── Agent Constraints ────────────────────────────────────────────────
AGENT_CONSTRAINTS = """
## MANDATORY CONSTRAINTS — VIOLATION OF ANY IS A CRITICAL FAILURE

1. **NEVER FABRICATE DATA.** Every number, date, name, and fact MUST come
   from a tool observation. If a tool did not return it, you MUST NOT
   include it. Say "Data not available" instead.

2. **CITE EVERY CLAIM.** Every factual statement in the final report must
   reference the tool and call that produced it, e.g. [Source: company_profile(MSFT)].

3. **CROSS-REFERENCE NUMBERS.** Any quantitative claim (revenue, P/E ratio,
   market cap, etc.) must be confirmed by at least 2 independent tool calls
   where possible. If only one source is available, flag it:
   "[Single-source: financial_data_api]".

4. **REPORT CONFLICTS.** If two tools return different values for the same
   metric, report BOTH values with their sources and note the discrepancy.
   NEVER silently pick one value.

5. **NO INVESTMENT RECOMMENDATIONS.** Do not say "buy", "sell", "hold", or
   any synonym. Do not predict future prices. Present facts only.

6. **MEMORY PRIORITIZATION.** Always search local long-term memory (`vector_db_search`)
   first if researching entities or themes covered in prior sessions. Avoid redundant external API calls.

7. **TOOL-CALL BUDGET & EFFICIENCY.** You have a hard cap of {max_tool_calls} tool calls
   for this entire research task. Combine multi-metric queries into single tool calls where supported.

8. **TOKEN BUDGET & OUTPUT LENGTH CONTROL.** Keep final report synthesis concise and focused
   on primary quantitative evidence (40% primary data / 30% supporting evidence / 20% system prompt & tools / 10% generation headroom).
"""


# ── Planner System Prompt ────────────────────────────────────────────
PLANNER_SYSTEM_PROMPT = """You are the PLANNER component of ARA-1, an Autonomous
Financial Research Agent. Your job is to decompose a user's research query into
an optimal, efficient execution plan.

{constraints}

## YOUR TASK
Given a user query, produce a JSON execution plan with the following structure.
Return ONLY the JSON, no markdown fences, no extra text.

{{
  "plan_title": "Brief title of the research task",
  "steps": [
    {{
      "step_id": 1,
      "description": "What this step accomplishes",
      "tool_hint": "tool_name or null if synthesis-only",
      "expected_output": "What data we expect to get back",
      "depends_on": []
    }},
    ...
  ]
}}

## RULES FOR EFFICIENT PLAN CONSTRUCTION
- Avoid redundant steps: group requests for related metrics into a single tool step (e.g., `company_profile` or `financial_data_api`).
- Check long-term memory (`vector_db_search`) early if prior session context is available.
- Use tool names EXACTLY as listed in the tool registry below.
- Include a final synthesis/report step that does NOT call a tool.
- Order steps so dependencies are respected (use "depends_on" for required sequence).
- Stay strictly within the {max_tool_calls}-call budget.

## AVAILABLE TOOLS
{tool_registry}
"""


# ── Executor System Prompt ───────────────────────────────────────────
EXECUTOR_SYSTEM_PROMPT = """You are the EXECUTOR component of ARA-1, an Autonomous
Financial Research Agent. You execute ONE step of a research plan at a time using
a Thought → Action → Observation cycle.

{constraints}

## CURRENT PLAN CONTEXT
Plan title: {plan_title}
Current step ({step_id}/{total_steps}): {step_description}
Tool hint: {tool_hint}
Expected output: {expected_output}

## RESULTS FROM PREVIOUS STEPS
{previous_results}

## BUDGET STATUS
Tool calls used: {calls_used}/{max_tool_calls}
Steps completed: {steps_completed}/{total_steps}

## INSTRUCTIONS
1. Select the precise tool call needed for this step. Avoid duplicate calls if previous steps already returned the required data.
2. Execute the tool call using the function-calling interface.
3. Assess the observation:
   a. Does the result satisfy this step's expected output?
   b. Does this result conflict with any previous step's data?
   c. Does this result invalidate any future planned steps?
4. If satisfactory, output a concise summary starting with "STEP_COMPLETE:" followed by key metrics.
5. Do not exceed {max_react_cycles} cycles per step.

## AVAILABLE TOOLS
{tool_registry}
"""


# ── Synthesis Prompt ─────────────────────────────────────────────────
SYNTHESIS_SYSTEM_PROMPT = """You are the SYNTHESIS component of ARA-1, an Autonomous
Financial Research Agent. Your job is to compile all gathered data into a
comprehensive, well-structured, and publication-ready research report.

{constraints}

## GATHERED DATA
{all_results}

## INSTRUCTIONS
Produce a structured research report with these sections:
1. **Executive Summary** — Crisp 2-3 sentence thesis overview
2. **Business Overview** — Company description, sector, industry, business model
3. **Financial Summary** — Key quantitative metrics with sources cited
4. **Key Executives** — Leadership team
5. **Recent Developments & Risk Assessment** — Latest developments and risk factors
6. **Data Conflicts & Coverage Gaps** — Any discrepancies found between sources or missing data

IMPORTANT:
- Target length: 1,000 to 2,000 words (do not generate excessive fluff).
- Cite every fact with [Source: tool_name(args)].
- If data was unavailable, explicitly say so — never make anything up.
- Report any conflicts between sources.
- Do NOT make any investment recommendations.
"""


# ── Plan Revision Prompt ─────────────────────────────────────────────
PLAN_REVISION_PROMPT = """You are the PLANNER component of ARA-1 revising an
existing research plan because new information has changed assumptions.

{constraints}

## ORIGINAL PLAN
{original_plan}

## COMPLETED STEPS AND THEIR RESULTS
{completed_results}

## REASON FOR REVISION
{revision_reason}

## INSTRUCTIONS
Produce a REVISED JSON plan (same format as the original) that:
1. Keeps already-completed steps as-is (mark them with "status": "completed").
2. Adjusts remaining steps based on the new information.
3. Stays within the remaining tool-call budget of {remaining_budget} calls.

Return ONLY the JSON, no markdown fences, no extra text.
"""


def _format_tool_registry(tool_schemas: list[dict]) -> str:
    """Format tool schemas into a human-readable registry block for the prompt."""
    lines = []
    for schema in tool_schemas:
        name = schema.get("name", "unknown")
        desc = schema.get("description", "No description.")
        params = schema.get("parameters", {})
        props = params.get("properties", {})
        required = params.get("required", [])

        param_strs = []
        for pname, pdef in props.items():
            ptype = pdef.get("type", "any")
            pdesc = pdef.get("description", "")
            req_marker = " [REQUIRED]" if pname in required else ""
            param_strs.append(f"    - {pname} ({ptype}){req_marker}: {pdesc}")

        lines.append(f"### {name}")
        lines.append(f"  {desc}")
        if param_strs:
            lines.append("  Parameters:")
            lines.extend(param_strs)
        lines.append("")

    return "\n".join(lines)


def _format_tool_schemas_for_api(tool_schemas: list[dict]) -> list[dict]:
    """
    Convert our internal tool schemas into OpenAI-compatible function-calling
    format for the Groq API.
    """
    api_tools = []
    for schema in tool_schemas:
        api_tools.append({
            "type": "function",
            "function": {
                "name": schema["name"],
                "description": schema.get("description", ""),
                "parameters": schema.get("parameters", {}),
            },
        })
    return api_tools


def build_planner_prompt(
    tool_schemas: list[dict],
    max_tool_calls: int = 20,
) -> str:
    """Build the complete system prompt for the Planner LLM call."""
    constraints = AGENT_CONSTRAINTS.format(max_tool_calls=max_tool_calls)
    tool_registry = _format_tool_registry(tool_schemas)
    return PLANNER_SYSTEM_PROMPT.format(
        constraints=constraints,
        tool_registry=tool_registry,
        max_tool_calls=max_tool_calls,
    )


def build_executor_prompt(
    tool_schemas: list[dict],
    plan_title: str,
    step_id: int,
    total_steps: int,
    step_description: str,
    tool_hint: Optional[str],
    expected_output: str,
    previous_results: str,
    calls_used: int,
    max_tool_calls: int = 20,
    steps_completed: int = 0,
    max_react_cycles: int = 3,
) -> str:
    """Build the complete system prompt for an Executor step."""
    constraints = AGENT_CONSTRAINTS.format(max_tool_calls=max_tool_calls)
    tool_registry = _format_tool_registry(tool_schemas)
    return EXECUTOR_SYSTEM_PROMPT.format(
        constraints=constraints,
        plan_title=plan_title,
        step_id=step_id,
        total_steps=total_steps,
        step_description=step_description,
        tool_hint=tool_hint or "none (synthesis step)",
        expected_output=expected_output,
        previous_results=previous_results or "None yet.",
        calls_used=calls_used,
        max_tool_calls=max_tool_calls,
        steps_completed=steps_completed,
        tool_registry=tool_registry,
        max_react_cycles=max_react_cycles,
    )


def build_synthesis_prompt(
    all_results: str,
    max_tool_calls: int = 20,
) -> str:
    """Build the system prompt for final report synthesis."""
    constraints = AGENT_CONSTRAINTS.format(max_tool_calls=max_tool_calls)
    return SYNTHESIS_SYSTEM_PROMPT.format(
        constraints=constraints,
        all_results=all_results,
    )


def build_plan_revision_prompt(
    tool_schemas: list[dict],
    original_plan: str,
    completed_results: str,
    revision_reason: str,
    remaining_budget: int,
    max_tool_calls: int = 20,
) -> str:
    """Build the prompt for plan revision."""
    constraints = AGENT_CONSTRAINTS.format(max_tool_calls=max_tool_calls)
    return PLAN_REVISION_PROMPT.format(
        constraints=constraints,
        original_plan=original_plan,
        completed_results=completed_results,
        revision_reason=revision_reason,
        remaining_budget=remaining_budget,
    )


def get_api_tools(tool_schemas: list[dict]) -> list[dict]:
    """Get tool schemas formatted for the OpenAI-compatible function-calling API."""
    return _format_tool_schemas_for_api(tool_schemas)
