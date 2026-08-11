"""
ARA-1 Core Agent — Plan-and-Execute with ReAct Inner Loop

Architecture:
  1. PLANNER: Decomposes the user query into a numbered step list with
     tool hints and expected outputs.
  2. EXECUTOR: Works through each step using a bounded Thought→Action→
     Observation (ReAct) cycle.
  3. PLAN REVISION: If a step's result invalidates later steps, the
     Planner is re-invoked to adjust the remaining plan.
  4. SYNTHESIS: After all steps complete (or limits hit), produce the
     final research report.

Termination conditions:
  - Max plan steps reached
  - Max total tool calls reached (configurable, default 20)
  - Max wall-clock time exceeded
  - Max ReAct cycles per step exceeded
  - On any limit hit, terminate gracefully into a partial report.
"""

import json
import time
import uuid
import logging
from dataclasses import dataclass, field
from typing import Optional

from agent.prompts import (
    build_planner_prompt,
    build_executor_prompt,
    build_synthesis_prompt,
    build_plan_revision_prompt,
    get_api_tools,
)
from agent.parser import (
    parse_llm_response,
    parse_plan_response,
    ParsedResponse,
    ToolCall,
)
from agent.logger import log_tool_call, log_agent_step
from memory.context_manager import ContextManager
from memory.episodic import EpisodicMemory
from agent.error_handler import ErrorHandler, ErrorCategory
from agent.fallback_chains import FallbackChainManager
from agent.circuit_breaker import CircuitBreaker
from agent.query_analyzer import QueryAnalyzer
from agent.disambiguation import DisambiguationEngine

logger = logging.getLogger("ara1.agent")


# ── Configuration Dataclass ──────────────────────────────────────────
@dataclass
class AgentConfig:
    """All configurable limits and parameters for the agent loop."""
    max_tool_calls: int = 20          # Hard cap from the brief
    max_plan_steps: int = 15          # Max steps the planner can produce
    max_react_cycles: int = 3         # Max Thought→Action→Observation per step
    max_wall_clock_seconds: int = 300 # 5-minute wall-clock timeout
    simulate_tool_failure_rate: float = 0.0  # Debug flag for simulated tool failure stress testing
    planning_model_role: str = "planning"
    executor_model_role: str = "fast"
    synthesis_model_role: str = "planning"


# ── Trace Entry ──────────────────────────────────────────────────────
@dataclass
class TraceEntry:
    """A single entry in the agent's execution trace."""
    timestamp: float
    phase: str           # "PLAN", "THOUGHT", "ACTION", "OBSERVATION", "REVISION", "SYNTHESIS", "ERROR", "LIMIT"
    step_id: int = 0
    cycle: int = 0
    content: str = ""
    tool_name: str = ""
    tool_args: dict = field(default_factory=dict)
    tool_result: str = ""

    def __str__(self) -> str:
        prefix = f"[{self.phase}]"
        if self.step_id:
            prefix += f" Step {self.step_id}"
        if self.cycle:
            prefix += f" Cycle {self.cycle}"
        if self.tool_name:
            return f"{prefix} {self.tool_name}({json.dumps(self.tool_args)}) → {self.tool_result[:200]}"
        return f"{prefix} {self.content[:300]}"


# ── Step Result ──────────────────────────────────────────────────────
@dataclass
class StepResult:
    """The result of executing one plan step."""
    step_id: int
    description: str
    status: str         # "completed", "partial", "failed", "skipped"
    findings: str = ""
    tool_calls_made: int = 0
    cycles_used: int = 0


# ── Agent Termination Reasons ────────────────────────────────────────
class TerminationReason:
    COMPLETED = "all_steps_completed"
    TOOL_LIMIT = "max_tool_calls_reached"
    TIME_LIMIT = "max_wall_clock_exceeded"
    STEP_LIMIT = "max_plan_steps_reached"
    ERROR = "unrecoverable_error"


# ── Main Agent Class ─────────────────────────────────────────────────
class FinancialResearchAgent:
    """
    Plan-and-Execute agent with a ReAct inner loop for each step.

    Wired to:
      - Day 2 ToolRegistry for tool execution (with mock/stub data)
      - Day 3 LLMWrapper for all LLM calls
    """

    def __init__(
        self,
        llm_wrapper,
        tool_registry,
        config: AgentConfig | None = None,
    ):
        self.llm = llm_wrapper
        self.registry = tool_registry
        self.config = config or AgentConfig()

        # Session state
        self.session_id: str = ""
        self.trace: list[TraceEntry] = []
        self.step_results: list[StepResult] = []
        self.total_tool_calls: int = 0
        self.start_time: float = 0.0
        self.plan: dict | None = None
        self.termination_reason: str = ""

        # Three-layer memory components
        self.context_manager = ContextManager(max_context_tokens=8000, compression_threshold=0.70)
        self.episodic_memory = EpisodicMemory()

        # Day 9 Error Handling, Fallback, & Circuit Breaker components
        self.error_handler = ErrorHandler(max_retries=5)
        self.fallback_manager = FallbackChainManager()
        self.circuit_breaker = CircuitBreaker(max_consecutive_failures=3)
        self.degraded_sections: dict[str, dict] = {}
        self.tool_results_history: list[dict] = []

        # Day 10 Query Analyzer & Disambiguation Engine components
        self.query_analyzer = QueryAnalyzer()
        self.disambiguator = DisambiguationEngine()
        self.query_analysis: dict = {}
        self.disambiguation_res: dict = {}
        self.rate_of_change_res: dict | None = None

    # ── Public Entry Point ───────────────────────────────────────────
    def run(self, query: str, session_id: str | None = None) -> dict:
        """
        Execute a full research task end-to-end.

        Args:
            query: The user's research question.
            session_id: Optional session ID for tracing.

        Returns:
            dict with keys: report, trace, plan, step_results, metadata
        """
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.trace = []
        self.step_results = []
        self.total_tool_calls = 0
        self.start_time = time.time()
        self.plan = None
        self.termination_reason = ""
        self.degraded_sections = {}
        self.tool_results_history = []

        # Day 10 Query Analysis & Disambiguation Pass
        self.query_analysis = self.query_analyzer.analyze(query)
        self.disambiguation_res = self.disambiguator.resolve_query_ambiguity(
            query=query,
            ambiguity_level=self.query_analysis.get("ambiguity_level", "LOW"),
        )
        self.rate_of_change_res = None

        logger.info(f"Starting research task | session={self.session_id}")
        self._add_trace("PLAN", content=f"User query: {query} | {self.query_analysis.get('summary')}")

        try:
            # ── Phase 1: Planning ────────────────────────────────────
            self.plan = self._run_planner(query)
            if not self.plan:
                self._add_trace("ERROR", content="Planner failed to produce a valid plan")
                return self._build_error_result("Planning failed — could not decompose query.")

            plan_steps = self.plan.get("steps", [])
            self._add_trace("PLAN", content=f"Plan created with {len(plan_steps)} steps: {self.plan.get('plan_title', 'Untitled')}")

            # ── Phase 2: Execution ───────────────────────────────────
            for step in plan_steps:
                # Check limits before each step
                limit_reason = self._check_limits()
                if limit_reason:
                    self.termination_reason = limit_reason
                    self._add_trace("LIMIT", content=f"Limit reached: {limit_reason}")
                    break

                step_result = self._execute_step(step, plan_steps)
                self.step_results.append(step_result)

                # Context window compaction check
                if self.context_manager.should_compact(self.trace):
                    self.trace = self.context_manager.compact_trace(self.trace)

                # Check if step result triggers plan revision
                if step_result.status == "revision_needed":
                    revised = self._revise_plan(step_result)
                    if revised:
                        plan_steps = revised.get("steps", plan_steps)
                        self.plan = revised

            if not self.termination_reason:
                self.termination_reason = TerminationReason.COMPLETED

            # ── Phase 3: Synthesis ───────────────────────────────────
            report = self._synthesize_report()

        except Exception as e:
            logger.exception(f"Agent error: {e}")
            self._add_trace("ERROR", content=f"Unhandled error: {str(e)}")
            self.termination_reason = TerminationReason.ERROR
            report = self._build_partial_report(f"Error during execution: {str(e)}")

        elapsed = time.time() - self.start_time

        # Log episode to Episodic Memory
        try:
            tools_used = [getattr(t, "tool_name", "") for t in self.trace if getattr(t, "tool_name", "")]
            tools_succeeded = [t for t in tools_used if t]
            self.episodic_memory.log_episode(
                session_id=self.session_id,
                query=query,
                tools_used=tools_used,
                tools_succeeded=tools_succeeded,
                tools_failed=[],
                strategy_note=f"Completed research task with {len(self.step_results)} steps",
                success=(self.termination_reason == TerminationReason.COMPLETED),
            )
        except Exception as ep_err:
            logger.warning(f"Failed to log episode: {ep_err}")

        logger.info(
            f"Research task complete | session={self.session_id} "
            f"| reason={self.termination_reason} "
            f"| tool_calls={self.total_tool_calls} "
            f"| elapsed={elapsed:.1f}s"
        )

        return {
            "report": report,
            "trace": [str(t) for t in self.trace],
            "plan": self.plan,
            "step_results": [
                {
                    "step_id": sr.step_id,
                    "description": sr.description,
                    "status": sr.status,
                    "findings": sr.findings,
                    "tool_calls_made": sr.tool_calls_made,
                }
                for sr in self.step_results
            ],
            "metadata": {
                "session_id": self.session_id,
                "termination_reason": self.termination_reason,
                "total_tool_calls": self.total_tool_calls,
                "elapsed_seconds": round(elapsed, 2),
                "steps_completed": sum(1 for sr in self.step_results if sr.status == "completed"),
                "steps_total": len(self.plan.get("steps", [])) if self.plan else 0,
            },
        }

    # ── Phase 1: Planner ─────────────────────────────────────────────
    def _run_planner(self, query: str) -> dict | None:
        """Invoke the planner LLM to decompose the query into steps."""
        tool_schemas = self.registry.get_all_schemas()
        system_prompt = build_planner_prompt(
            tool_schemas=tool_schemas,
            max_tool_calls=self.config.max_tool_calls,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        self._add_trace("PLAN", content="Invoking planner LLM...")

        response = self.llm.invoke(
            messages=messages,
            role=self.config.planning_model_role,
            session_id=self.session_id,
        )

        content = response.get("content", "")
        self._add_trace("PLAN", content=f"Planner response: {content[:500]}")

        plan = parse_plan_response(content)

        if plan:
            # Enforce max plan steps
            steps = plan.get("steps", [])
            if len(steps) > self.config.max_plan_steps:
                logger.warning(
                    f"Plan has {len(steps)} steps, truncating to {self.config.max_plan_steps}"
                )
                plan["steps"] = steps[: self.config.max_plan_steps]

        return plan

    # ── Phase 2: Step Executor (ReAct Loop) ──────────────────────────
    def _execute_step(self, step: dict, all_steps: list[dict]) -> StepResult:
        """
        Execute a single plan step using a bounded ReAct
        (Thought → Action → Observation) cycle.
        """
        step_id = step.get("step_id", 0)
        description = step.get("description", "")
        tool_hint = step.get("tool_hint")
        expected_output = step.get("expected_output", "")
        status = step.get("status", "")

        # Skip already-completed steps (from plan revision)
        if status == "completed":
            return StepResult(
                step_id=step_id,
                description=description,
                status="completed",
                findings="(from previous execution)",
            )

        self._add_trace("THOUGHT", step_id=step_id,
                        content=f"Starting step: {description}")
        log_agent_step("THOUGHT", f"Step {step_id}: {description}",
                       session_id=self.session_id)

        tool_schemas = self.registry.get_all_schemas()
        api_tools = get_api_tools(tool_schemas)
        available_tool_names = list(self.registry.schemas.keys())

        # Build context from previous results
        previous_results = self._format_previous_results()

        step_tool_calls = 0
        cycles_used = 0
        findings_parts = []
        conversation = []  # Message history for this step's ReAct loop

        # If tool_hint is None/null/"null", this is a synthesis step
        is_synthesis_step = (
            tool_hint is None
            or tool_hint == "null"
            or tool_hint == ""
            or "synth" in description.lower()
            or "report" in description.lower()
            or "compile" in description.lower()
        )

        for cycle in range(1, self.config.max_react_cycles + 1):
            cycles_used = cycle

            # Check limits
            limit = self._check_limits()
            if limit:
                self._add_trace("LIMIT", step_id=step_id, cycle=cycle,
                                content=f"Limit hit during step: {limit}")
                return StepResult(
                    step_id=step_id, description=description,
                    status="partial",
                    findings="\n".join(findings_parts) or "[INCOMPLETE — limit reached]",
                    tool_calls_made=step_tool_calls,
                    cycles_used=cycles_used,
                )

            # Build executor prompt
            system_prompt = build_executor_prompt(
                tool_schemas=tool_schemas,
                plan_title=self.plan.get("plan_title", "Research Task") if self.plan else "Research Task",
                step_id=step_id,
                total_steps=len(all_steps),
                step_description=description,
                tool_hint=tool_hint,
                expected_output=expected_output,
                previous_results=previous_results,
                calls_used=self.total_tool_calls,
                max_tool_calls=self.config.max_tool_calls,
                steps_completed=len(self.step_results),
                max_react_cycles=self.config.max_react_cycles,
            )

            messages = [{"role": "system", "content": system_prompt}]
            if not conversation:
                messages.append({
                    "role": "user",
                    "content": f"Execute step {step_id}: {description}",
                })
            else:
                messages.extend(conversation)

            # ── THOUGHT: LLM decides what to do ──────────────────────
            self._add_trace("THOUGHT", step_id=step_id, cycle=cycle,
                            content=f"Cycle {cycle}: Invoking executor LLM...")

            response = self.llm.invoke(
                messages=messages,
                role=self.config.executor_model_role,
                tools=api_tools if not is_synthesis_step else None,
                session_id=self.session_id,
            )

            parsed = parse_llm_response(response, available_tool_names)

            # Log the thought
            if parsed.reasoning:
                self._add_trace("THOUGHT", step_id=step_id, cycle=cycle,
                                content=parsed.reasoning)
                log_agent_step("THOUGHT", parsed.reasoning,
                               session_id=self.session_id)

            # ── ACTION + OBSERVATION: Execute tool calls ─────────────
            if parsed.has_tool_calls:
                for tc in parsed.tool_calls:
                    # Budget check before each call
                    if self.total_tool_calls >= self.config.max_tool_calls:
                        self._add_trace("LIMIT", step_id=step_id, cycle=cycle,
                                        content="Tool call budget exhausted")
                        findings_parts.append("[INCOMPLETE — tool call limit reached]")
                        break

                    self._add_trace("ACTION", step_id=step_id, cycle=cycle,
                                    tool_name=tc.tool_name, tool_args=tc.arguments,
                                    content=f"Calling {tc}")
                    log_agent_step("ACTION", f"Calling {tc}",
                                   session_id=self.session_id)

                    # Execute tool with Circuit Breaker, Exponential Retry, & Fallback Chain
                    obs_start = time.time()
                    tool_name = tc.tool_name
                    tool_args = tc.arguments

                    # 1. Check Circuit Breaker
                    if self.circuit_breaker.is_open(tool_name):
                        logger.warning(
                            f"[Circuit Breaker OPEN] Bypassing primary tool '{tool_name}' and routing directly to fallback chain."
                        )
                        fb_success, fb_result = self.fallback_manager.execute_fallback_chain(
                            self.registry, tool_name, tool_args, self.circuit_breaker
                        )
                        result = fb_result
                        success = fb_success
                        error = None if fb_success else "Circuit Breaker OPEN & Fallbacks Exhausted"
                    else:
                        # 2. Execute Primary Tool with Retry Handler
                        def _tool_fn():
                            return self.registry.execute_tool(
                                tool_name, tool_args, simulate_failure_rate=self.config.simulate_tool_failure_rate
                            )

                        success, result, err_category = self.error_handler.execute_with_retry(
                            _tool_fn, tool_name=tool_name
                        )

                        if success and isinstance(result, dict) and not result.get("error"):
                            self.circuit_breaker.record_success(tool_name)
                            error = None
                        else:
                            error_msg = str(result.get("error", "Tool execution failed")) if isinstance(result, dict) else str(result)
                            self.circuit_breaker.record_failure(tool_name, error_detail=error_msg)

                            # Trigger Fallback Chain
                            logger.info(f"[Primary Tool Failed] Triggering Fallback Chain for '{tool_name}'.")
                            fb_success, fb_result = self.fallback_manager.execute_fallback_chain(
                                self.registry, tool_name, tool_args, self.circuit_breaker
                            )
                            if fb_success:
                                result = fb_result
                                success = True
                                error = None
                            else:
                                success = False
                                error = error_msg
                                sec_name = description or "Financial Analysis"
                                self.degraded_sections[sec_name] = {
                                    "cause": f"Primary tool '{tool_name}' failed ({error_msg}) and fallback chain was exhausted.",
                                    "tools_attempted": [tool_name] + self.fallback_manager.get_fallbacks(tool_name),
                                    "user_mitigation": f"Manually verify {tool_name} data via SEC EDGAR 10-K or check API key status.",
                                }

                    if isinstance(result, dict):
                        self.tool_results_history.append(result)
                    obs_str = json.dumps(result, indent=2, default=str)

                    obs_latency = (time.time() - obs_start) * 1000
                    self.total_tool_calls += 1
                    step_tool_calls += 1

                    log_tool_call(
                        tool_name=tc.tool_name,
                        success=success,
                        latency_ms=obs_latency,
                        session_id=self.session_id,
                        error=error,
                    )

                    self._add_trace("OBSERVATION", step_id=step_id, cycle=cycle,
                                    tool_name=tc.tool_name, tool_result=obs_str,
                                    content=f"Result from {tc.tool_name}")
                    log_agent_step("OBSERVATION", f"{tc.tool_name}: {obs_str[:200]}",
                                   session_id=self.session_id)

                    findings_parts.append(
                        f"[{tc.tool_name}({json.dumps(tc.arguments)})]: {obs_str}"
                    )

                    # Add to conversation for next cycle
                    conversation.append({"role": "assistant", "content": parsed.raw_content,
                                         "tool_calls_data": str(tc)})
                    conversation.append({"role": "user",
                                         "content": f"Tool result from {tc.tool_name}: {obs_str}"})

            # ── Check for step completion ─────────────────────────────
            if parsed.step_complete or is_synthesis_step:
                answer = parsed.final_answer or parsed.raw_content
                findings_parts.append(f"[Summary]: {answer}")
                self._add_trace("THOUGHT", step_id=step_id, cycle=cycle,
                                content=f"Step complete: {answer[:200]}")
                break

            # ── Check for plan revision trigger ──────────────────────
            if parsed.revision_needed:
                self._add_trace("REVISION", step_id=step_id, cycle=cycle,
                                content=f"Revision needed: {parsed.revision_reason}")
                return StepResult(
                    step_id=step_id, description=description,
                    status="revision_needed",
                    findings=parsed.revision_reason,
                    tool_calls_made=step_tool_calls,
                    cycles_used=cycles_used,
                )

            # If no tool calls and not complete, mark as done
            if not parsed.has_tool_calls:
                findings_parts.append(f"[Response]: {parsed.raw_content}")
                break

        return StepResult(
            step_id=step_id,
            description=description,
            status="completed",
            findings="\n".join(findings_parts),
            tool_calls_made=step_tool_calls,
            cycles_used=cycles_used,
        )

    # ── Phase 3: Plan Revision ───────────────────────────────────────
    def _revise_plan(self, trigger_result: StepResult) -> dict | None:
        """Re-invoke the planner to revise remaining steps."""
        if not self.plan:
            return None

        self._add_trace("REVISION",
                        content=f"Revising plan due to: {trigger_result.findings}")

        tool_schemas = self.registry.get_all_schemas()
        remaining_budget = self.config.max_tool_calls - self.total_tool_calls
        completed_results = self._format_previous_results()

        system_prompt = build_plan_revision_prompt(
            tool_schemas=tool_schemas,
            original_plan=json.dumps(self.plan, indent=2),
            completed_results=completed_results,
            revision_reason=trigger_result.findings,
            remaining_budget=remaining_budget,
            max_tool_calls=self.config.max_tool_calls,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Revise the plan based on the new information."},
        ]

        response = self.llm.invoke(
            messages=messages,
            role=self.config.planning_model_role,
            session_id=self.session_id,
        )

        content = response.get("content", "")
        revised = parse_plan_response(content)

        if revised:
            self._add_trace("REVISION",
                            content=f"Plan revised: {len(revised.get('steps', []))} steps")
        else:
            self._add_trace("REVISION", content="Plan revision failed, continuing with original")

        return revised

    # ── Phase 4: Synthesis ───────────────────────────────────────────
    def _synthesize_report(self) -> str:
        """Compile all gathered data into the final report."""
        all_results = self._format_previous_results()

        # If we have no results, return a minimal report
        if not self.step_results:
            return self._build_partial_report("No data gathered — all steps skipped or failed.")

        self._add_trace("SYNTHESIS", content="Generating final report...")

        system_prompt = build_synthesis_prompt(
            all_results=all_results,
            max_tool_calls=self.config.max_tool_calls,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Synthesize the final research report from all gathered data."},
        ]

        response = self.llm.invoke(
            messages=messages,
            role=self.config.synthesis_model_role,
            session_id=self.session_id,
        )

        report = response.get("content", "")

        # Check for rate-of-change triggers across gathered data
        self.rate_of_change_res = self.disambiguator.detect_rate_of_change(all_results)

        # Build Header Disclosures Block
        header_disclosures = []

        if self.rate_of_change_res and self.rate_of_change_res.get("banner_markdown"):
            header_disclosures.append(self.rate_of_change_res["banner_markdown"])

        if self.disambiguation_res and self.disambiguation_res.get("disclosure_markdown"):
            header_disclosures.append(self.disambiguation_res["disclosure_markdown"])

        if self.query_analysis.get("is_private_company_query"):
            priv_disc = self.disambiguator.format_private_company_disclosure("Target Entity")
            header_disclosures.append(priv_disc["disclosure_markdown"])
        elif self.query_analysis.get("is_recent_ipo_query"):
            ipo_disc = self.disambiguator.format_recent_ipo_disclosure("Target Entity")
            header_disclosures.append(ipo_disc["disclosure_markdown"])

        if header_disclosures:
            header_block = "\n".join(header_disclosures) + "\n\n"
            # Prepend after H1 header if present, or at top
            if report.startswith("# "):
                h1_end = report.find("\n")
                if h1_end != -1:
                    report = report[:h1_end+1] + "\n" + header_block + report[h1_end+1:]
                else:
                    report = header_block + report
            else:
                report = header_block + report

        # Append graceful degradation warnings if any sections were degraded
        if self.degraded_sections:
            from tools.report_generator import format_degradation_notice
            report += "\n\n## Section Degradation Disclosures\n"
            for sec, deg in self.degraded_sections.items():
                report += "\n" + format_degradation_notice(sec, deg)

        self._add_trace("SYNTHESIS", content=f"Report generated ({len(report)} chars)")

        # Append metadata footer
        metadata_footer = self._build_metadata_footer()
        report = report + "\n\n" + metadata_footer

        return report

    # ── Helpers ───────────────────────────────────────────────────────
    def _check_limits(self) -> str | None:
        """Check if any termination limit has been reached."""
        if self.total_tool_calls >= self.config.max_tool_calls:
            return TerminationReason.TOOL_LIMIT

        elapsed = time.time() - self.start_time
        if elapsed > self.config.max_wall_clock_seconds:
            return TerminationReason.TIME_LIMIT

        if len(self.step_results) >= self.config.max_plan_steps:
            return TerminationReason.STEP_LIMIT

        return None

    def _format_previous_results(self) -> str:
        """Format all completed step results for prompt injection."""
        if not self.step_results:
            return "No previous results."

        parts = []
        for sr in self.step_results:
            status_icon = "✅" if sr.status == "completed" else "⚠️"
            parts.append(
                f"{status_icon} Step {sr.step_id}: {sr.description}\n"
                f"   Status: {sr.status}\n"
                f"   Findings:\n{sr.findings}\n"
            )
        return "\n".join(parts)

    def _build_metadata_footer(self) -> str:
        """Build the metadata footer for the report."""
        elapsed = time.time() - self.start_time
        return (
            "---\n"
            "## Research Metadata\n"
            f"- **Session ID**: {self.session_id}\n"
            f"- **Termination**: {self.termination_reason}\n"
            f"- **Tool calls used**: {self.total_tool_calls}/{self.config.max_tool_calls}\n"
            f"- **Steps completed**: {sum(1 for sr in self.step_results if sr.status == 'completed')}"
            f"/{len(self.plan.get('steps', [])) if self.plan else 0}\n"
            f"- **Wall-clock time**: {elapsed:.1f}s\n"
        )

    def _build_partial_report(self, reason: str) -> str:
        """Build a partial report when limits are hit or errors occur."""
        parts = [
            "# Partial Research Report",
            f"\n> ⚠️ **This report is incomplete.** Reason: {reason}\n",
        ]

        if self.step_results:
            parts.append("## Data Gathered\n")
            for sr in self.step_results:
                parts.append(f"### Step {sr.step_id}: {sr.description}")
                parts.append(f"Status: {sr.status}")
                if sr.findings:
                    parts.append(sr.findings)
                parts.append("")

        parts.append(self._build_metadata_footer())
        return "\n".join(parts)

    def _build_error_result(self, error_msg: str) -> dict:
        """Build a result dict for error cases."""
        return {
            "report": self._build_partial_report(error_msg),
            "trace": [str(t) for t in self.trace],
            "plan": self.plan,
            "step_results": [],
            "metadata": {
                "session_id": self.session_id,
                "termination_reason": TerminationReason.ERROR,
                "total_tool_calls": self.total_tool_calls,
                "elapsed_seconds": round(time.time() - self.start_time, 2),
                "steps_completed": 0,
                "steps_total": 0,
            },
        }

    def _add_trace(self, phase: str, **kwargs) -> None:
        """Add an entry to the execution trace."""
        entry = TraceEntry(
            timestamp=time.time() - self.start_time,
            phase=phase,
            **kwargs,
        )
        self.trace.append(entry)
        logger.debug(str(entry))
