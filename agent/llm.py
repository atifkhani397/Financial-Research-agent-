"""
ARA-1 LLM Wrapper

Thin wrapper around the Groq chat-completions API using LangChain's
ChatOpenAI pointed at Groq's OpenAI-compatible base URL.

Design decision: We use langchain_groq.ChatGroq (which wraps the Groq
OpenAI-compatible endpoint) rather than the raw groq SDK because:
  1. It integrates directly with LangGraph's tool-calling and agent APIs.
  2. It handles streaming, structured output, and tool schemas natively.
  3. Model switching (planning / fast / judge) is just a constructor arg.
The raw groq SDK would require us to build all of that integration ourselves.
"""

import time
import logging
from typing import Optional, Literal

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
    before_sleep_log,
)
from langchain_groq import ChatGroq

from config import get_settings

logger = logging.getLogger("ara1.llm")


class TokenTracker:
    """Tracks cumulative token usage across all LLM calls in a session."""

    def __init__(self):
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_calls: int = 0
        self.calls_by_model: dict[str, int] = {}

    def record(self, model: str, prompt_tokens: int, completion_tokens: int):
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_calls += 1
        self.calls_by_model[model] = self.calls_by_model.get(model, 0) + 1

    @property
    def total_tokens(self) -> int:
        return self.total_prompt_tokens + self.total_completion_tokens

    def summary(self) -> dict:
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens,
            "total_calls": self.total_calls,
            "calls_by_model": self.calls_by_model,
        }


# Global token tracker for the session
token_tracker = TokenTracker()


class RateLimitError(Exception):
    """Raised when Groq returns a 429 rate-limit response."""
    pass


class LLMWrapper:
    """
    Provides three-way model switching (planning / fast / judge)
    with tenacity-based retry on Groq 429 rate-limit errors and
    per-call token tracking.
    """

    def __init__(self):
        self.settings = get_settings()
        self._models: dict[str, ChatGroq] = {}

    def _get_model(self, role: Literal["planning", "fast", "judge"]) -> ChatGroq:
        """Get or create a ChatGroq instance for the given role."""
        if role not in self._models:
            model_map = {
                "planning": self.settings.planning_model,
                "fast": self.settings.fast_model,
                "judge": self.settings.judge_model,
            }
            model_id = model_map[role]
            self._models[role] = ChatGroq(
                model=model_id,
                api_key=self.settings.groq_api_key,
                temperature=0.1 if role == "planning" else 0.0,
                max_retries=0,  # We handle retries ourselves via tenacity
            )
            logger.info(f"Initialized ChatGroq for role={role} model={model_id}")
        return self._models[role]

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential_jitter(initial=1, max=32, jitter=2),
        stop=stop_after_attempt(5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def invoke(
        self,
        messages: list,
        role: Literal["planning", "fast", "judge"] = "planning",
        tools: Optional[list] = None,
        session_id: str = "",
    ) -> dict:
        """
        Send a chat completion request to Groq.

        Args:
            messages: List of message dicts (role/content).
            role: Which model to use — "planning", "fast", or "judge".
            tools: Optional list of tool schemas for function calling.
            session_id: Research session ID for logging.

        Returns:
            dict with keys: content, tool_calls, usage, model, latency_ms
        """
        model = self._get_model(role)
        model_id = model.model_name
        start = time.time()

        try:
            kwargs = {}
            if tools:
                kwargs["tools"] = tools

            response = model.invoke(messages, **kwargs)
            latency_ms = (time.time() - start) * 1000

            # Extract token usage if available
            prompt_tokens = 0
            completion_tokens = 0
            if hasattr(response, "response_metadata"):
                usage = response.response_metadata.get("token_usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)

            token_tracker.record(model_id, prompt_tokens, completion_tokens)

            # Extract tool calls if any
            tool_calls = []
            if hasattr(response, "tool_calls") and response.tool_calls:
                tool_calls = response.tool_calls

            result = {
                "content": response.content if hasattr(response, "content") else str(response),
                "tool_calls": tool_calls,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                },
                "model": model_id,
                "latency_ms": round(latency_ms, 2),
            }

            logger.info(
                f"LLM call completed | role={role} model={model_id} "
                f"latency={result['latency_ms']}ms "
                f"tokens={prompt_tokens}+{completion_tokens} "
                f"session={session_id}"
            )
            return result

        except Exception as e:
            error_str = str(e).lower()
            # Detect Groq 429 rate limit and raise our custom error for tenacity
            if "429" in error_str or "rate_limit" in error_str or "rate limit" in error_str:
                logger.warning(f"Rate limited by Groq on model={model_id}. Retrying...")
                raise RateLimitError(f"Groq rate limit hit: {e}") from e
            # All other errors propagate immediately
            raise

    def get_planning_model(self) -> ChatGroq:
        """Get the ChatGroq instance for planning/synthesis tasks."""
        return self._get_model("planning")

    def get_fast_model(self) -> ChatGroq:
        """Get the ChatGroq instance for fast sub-tasks."""
        return self._get_model("fast")

    def get_judge_model(self) -> ChatGroq:
        """Get the ChatGroq instance for evaluation/judging."""
        return self._get_model("judge")


# Convenience singleton
_llm_instance = None


def get_llm() -> LLMWrapper:
    """Get or create the global LLMWrapper singleton."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMWrapper()
    return _llm_instance
