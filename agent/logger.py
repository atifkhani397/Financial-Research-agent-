"""
ARA-1 Structured Logging

Provides:
  - Rich console output for human-readable dev logs
  - JSON-lines file logging for structured trace analysis
  - All logs keyed by research session ID
  - Captures every Thought/Action/Observation, tool call with latency, and errors
"""

import os
import json
import logging
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

from config import get_settings


console = Console()

_initialized = False


def setup_logging(session_id: str = "default") -> logging.Logger:
    """
    Initialize the ARA-1 logging system.

    Args:
        session_id: Unique ID for the current research session.

    Returns:
        The root 'ara1' logger.
    """
    global _initialized
    if _initialized:
        return logging.getLogger("ara1")

    settings = get_settings()

    # Ensure log directory exists
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Root logger for the project
    root_logger = logging.getLogger("ara1")
    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # --- Rich console handler (human-readable) ---
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )
    rich_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(rich_handler)

    # --- JSON-lines file handler (structured, machine-readable) ---
    jsonl_handler = JSONLinesHandler(str(log_path), session_id=session_id)
    jsonl_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(jsonl_handler)

    _initialized = True
    root_logger.info(f"Logging initialized | session={session_id} | file={settings.log_file}")
    return root_logger


class JSONLinesHandler(logging.Handler):
    """Writes each log record as a single JSON object per line."""

    def __init__(self, filepath: str, session_id: str = "default"):
        super().__init__()
        self.filepath = filepath
        self.session_id = session_id
        # Open file in append mode
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.file = open(filepath, "a", encoding="utf-8")

    def emit(self, record: logging.LogRecord):
        try:
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": self.session_id,
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            # Attach any extra structured data
            for key in ("event_type", "tool_name", "latency_ms", "success", "error"):
                if hasattr(record, key):
                    entry[key] = getattr(record, key)

            self.file.write(json.dumps(entry) + "\n")
            self.file.flush()
        except Exception:
            self.handleError(record)

    def close(self):
        self.file.close()
        super().close()


def log_tool_call(
    tool_name: str,
    success: bool,
    latency_ms: float,
    session_id: str = "",
    error: Optional[str] = None,
):
    """Convenience function to log a tool call with structured fields."""
    logger = logging.getLogger("ara1.tools")
    extra = {
        "event_type": "tool_call",
        "tool_name": tool_name,
        "latency_ms": round(latency_ms, 2),
        "success": success,
    }
    if error:
        extra["error"] = error

    if success:
        logger.info(
            f"Tool call: {tool_name} | {latency_ms:.0f}ms | session={session_id}",
            extra=extra,
        )
    else:
        logger.error(
            f"Tool FAILED: {tool_name} | {latency_ms:.0f}ms | error={error} | session={session_id}",
            extra=extra,
        )


def log_agent_step(
    step_type: str,
    content: str,
    session_id: str = "",
):
    """Log a Thought/Action/Observation step."""
    logger = logging.getLogger("ara1.agent")
    logger.info(
        f"[{step_type}] {content[:200]}{'...' if len(content) > 200 else ''}",
        extra={"event_type": step_type.lower(), "session_id": session_id},
    )
