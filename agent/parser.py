"""
ARA-1 LLM Response Parser

Parses LLM responses into structured tool calls + reasoning traces.

Strategy:
  - Primary: Use Groq's native tool-calling / function-calling format
    (OpenAI-compatible `tools` / `tool_calls` schema). Groq's qwen3-32b and
    compatible models support function calling natively.
  - Fallback: If the model returns content-only (no tool_calls), attempt to
    parse structured JSON from the text body with strict validation.

This module never uses regex to extract free-text tool calls — it relies
entirely on the API's structured output or validated JSON parsing.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("ara1.parser")


@dataclass
class ToolCall:
    """A parsed tool call with its arguments."""
    tool_name: str
    arguments: dict
    call_id: str = ""

    def __repr__(self) -> str:
        args_str = ", ".join(f"{k}={v!r}" for k, v in self.arguments.items())
        return f"{self.tool_name}({args_str})"


@dataclass
class ParsedResponse:
    """The full parsed result from an LLM response."""
    # Reasoning / thinking content from the model
    reasoning: str = ""
    # Extracted tool calls (may be empty for synthesis steps)
    tool_calls: list[ToolCall] = field(default_factory=list)
    # Final answer content (when no more tool calls needed)
    final_answer: str = ""
    # Whether this response indicates the step is complete
    step_complete: bool = False
    # Any plan revision signals detected
    revision_needed: bool = False
    revision_reason: str = ""
    # Raw content for trace logging
    raw_content: str = ""

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


def parse_llm_response(response: dict, available_tools: list[str] | None = None) -> ParsedResponse:
    """
    Parse an LLM response dict (from LLMWrapper.invoke) into a structured
    ParsedResponse.

    Args:
        response: Dict with keys: content, tool_calls, usage, model, latency_ms
        available_tools: Optional list of valid tool names for validation.

    Returns:
        ParsedResponse with extracted tool calls and reasoning.
    """
    content = response.get("content", "") or ""
    raw_tool_calls = response.get("tool_calls", [])
    parsed = ParsedResponse(raw_content=content)

    # ── Strategy 1: Native tool-calling (OpenAI-compatible) ──────────
    if raw_tool_calls:
        parsed = _parse_native_tool_calls(raw_tool_calls, content, available_tools)
        logger.debug(f"Parsed {len(parsed.tool_calls)} native tool calls")
        return parsed

    # ── Strategy 2: JSON fallback from content body ──────────────────
    if content:
        json_parsed = _try_parse_json_tool_calls(content, available_tools)
        if json_parsed and json_parsed.has_tool_calls:
            logger.debug(f"Parsed {len(json_parsed.tool_calls)} tool calls from JSON fallback")
            return json_parsed

    # ── No tool calls — treat as reasoning / final answer ────────────
    parsed.reasoning = content
    if "STEP_COMPLETE:" in content:
        parsed.step_complete = True
        idx = content.index("STEP_COMPLETE:")
        parsed.final_answer = content[idx + len("STEP_COMPLETE:"):].strip()
        parsed.reasoning = content[:idx].strip()
    elif "REVISION_NEEDED:" in content:
        parsed.revision_needed = True
        idx = content.index("REVISION_NEEDED:")
        parsed.revision_reason = content[idx + len("REVISION_NEEDED:"):].strip()
        parsed.reasoning = content[:idx].strip()
    else:
        parsed.final_answer = content

    return parsed


def _parse_native_tool_calls(
    raw_tool_calls: list,
    content: str,
    available_tools: list[str] | None,
) -> ParsedResponse:
    """Parse tool calls from Groq/OpenAI native function-calling format."""
    parsed = ParsedResponse(raw_content=content, reasoning=content)
    
    for tc in raw_tool_calls:
        # LangChain tool call format: dict with 'name', 'args', 'id'
        if isinstance(tc, dict):
            name = tc.get("name", "")
            args = tc.get("args", {})
            call_id = tc.get("id", "")
        else:
            # Object-style (LangChain ToolCall dataclass)
            name = getattr(tc, "name", "") or getattr(tc, "function", {}).get("name", "")
            args = getattr(tc, "args", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse tool call args as JSON: {args}")
                    args = {}
            call_id = getattr(tc, "id", "")

        # Validate tool name
        if available_tools and name not in available_tools:
            logger.warning(f"Tool call to unknown tool '{name}', skipping")
            continue

        if name:
            parsed.tool_calls.append(ToolCall(
                tool_name=name,
                arguments=args if isinstance(args, dict) else {},
                call_id=call_id or "",
            ))

    return parsed


def _try_parse_json_tool_calls(
    content: str,
    available_tools: list[str] | None,
) -> ParsedResponse | None:
    """
    Fallback: attempt to extract tool calls from a JSON block in the
    LLM's content output.

    Expected format (single call):
    {
        "tool_name": "company_profile",
        "arguments": {"ticker": "MSFT"}
    }

    Or (multiple calls):
    {
        "tool_calls": [
            {"tool_name": "company_profile", "arguments": {"ticker": "MSFT"}},
            ...
        ]
    }
    """
    # Try to find JSON in the content
    json_str = _extract_json_block(content)
    if not json_str:
        return None

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        logger.debug("JSON fallback: content did not contain valid JSON")
        return None

    parsed = ParsedResponse(raw_content=content)

    # Extract reasoning text before the JSON block
    json_start = content.find(json_str)
    if json_start > 0:
        parsed.reasoning = content[:json_start].strip()

    if isinstance(data, dict):
        # Single tool call format
        if "tool_name" in data:
            tc = _validate_json_tool_call(data, available_tools)
            if tc:
                parsed.tool_calls.append(tc)
        # Multiple tool calls format
        elif "tool_calls" in data and isinstance(data["tool_calls"], list):
            for call_data in data["tool_calls"]:
                tc = _validate_json_tool_call(call_data, available_tools)
                if tc:
                    parsed.tool_calls.append(tc)
    elif isinstance(data, list):
        for call_data in data:
            tc = _validate_json_tool_call(call_data, available_tools)
            if tc:
                parsed.tool_calls.append(tc)

    return parsed if parsed.has_tool_calls else None


def _validate_json_tool_call(
    data: dict,
    available_tools: list[str] | None,
) -> ToolCall | None:
    """Validate and create a ToolCall from a JSON dict."""
    if not isinstance(data, dict):
        return None

    name = data.get("tool_name", "") or data.get("name", "")
    args = data.get("arguments", {}) or data.get("args", {})

    if not name:
        return None

    if available_tools and name not in available_tools:
        logger.warning(f"JSON fallback: unknown tool '{name}'")
        return None

    if not isinstance(args, dict):
        logger.warning(f"JSON fallback: arguments for '{name}' is not a dict")
        return None

    return ToolCall(tool_name=name, arguments=args)


def _extract_json_block(text: str) -> str | None:
    """Extract a JSON object or array from text, handling markdown fences."""
    # Try markdown-fenced JSON first
    fence_pattern = r"```(?:json)?\s*\n?([\s\S]*?)\n?```"
    match = re.search(fence_pattern, text)
    if match:
        return match.group(1).strip()

    # Try to find bare JSON object
    brace_start = text.find("{")
    bracket_start = text.find("[")

    if brace_start == -1 and bracket_start == -1:
        return None

    # Pick the earlier one
    if brace_start == -1:
        start = bracket_start
        end_char = "]"
    elif bracket_start == -1:
        start = brace_start
        end_char = "}"
    else:
        start = min(brace_start, bracket_start)
        end_char = "}" if start == brace_start else "]"

    # Find matching close
    depth = 0
    for i in range(start, len(text)):
        c = text[i]
        if c in "{[":
            depth += 1
        elif c in "}]":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    return None


def parse_plan_response(content: str) -> dict | None:
    """
    Parse the Planner's response into a structured plan dict.

    Returns None if parsing fails.
    """
    json_str = _extract_json_block(content)
    if not json_str:
        # Try the whole content as JSON
        json_str = content.strip()

    try:
        plan = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse plan JSON: {e}")
        return None

    # Validate plan structure
    if not isinstance(plan, dict):
        logger.error("Plan is not a JSON object")
        return None

    if "steps" not in plan:
        logger.error("Plan is missing 'steps' key")
        return None

    if not isinstance(plan["steps"], list) or len(plan["steps"]) == 0:
        logger.error("Plan 'steps' must be a non-empty list")
        return None

    # Validate each step
    for i, step in enumerate(plan["steps"]):
        if not isinstance(step, dict):
            logger.error(f"Step {i} is not a dict")
            return None
        if "step_id" not in step or "description" not in step:
            logger.error(f"Step {i} missing required fields (step_id, description)")
            return None

    return plan
