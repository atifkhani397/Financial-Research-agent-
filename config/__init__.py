"""
ARA-1 Configuration Module

Loads all configuration from environment variables via python-dotenv.
Fails fast with a clear message if GROQ_API_KEY is missing.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_project_root = Path(__file__).resolve().parent.parent
_env_path = _project_root / ".env"
load_dotenv(dotenv_path=_env_path)


class ConfigError(Exception):
    """Raised when a required configuration value is missing."""
    pass


class Settings:
    """Central configuration for ARA-1. All values come from environment variables."""

    def __init__(self):
        # --- Groq / Primary API (REQUIRED) ---
        self.groq_api_key: str = self._require("GROQ_API_KEY")
        self.groq_api_base: str = os.getenv("GROQ_API_BASE", "")

        # --- TokenRouter / Secondary API (FALLBACK) ---
        self.tokenrouter_api_key: str = os.getenv("TOKENROUTER_API_KEY", "")
        self.tokenrouter_api_base: str = os.getenv("TOKENROUTER_API_BASE", "https://api.tokenrouter.com/v1")

        # --- Model IDs (configurable, not hardcoded in agent logic) ---
        self.planning_model: str = os.getenv("GROQ_PLANNING_MODEL", "llama-3.3-70b-versatile")
        self.fast_model: str = os.getenv("GROQ_FAST_MODEL", "llama-3.1-8b-instant")
        self.judge_model: str = os.getenv("GROQ_JUDGE_MODEL", "llama-3.3-70b-versatile")

        # --- Groq Rate Limits ---
        self.groq_rpm: int = int(os.getenv("GROQ_REQUESTS_PER_MINUTE", "30"))
        self.groq_tpm: int = int(os.getenv("GROQ_TOKENS_PER_MINUTE", "14400"))

        # --- SEC EDGAR ---
        self.sec_user_agent: str = os.getenv(
            "SEC_EDGAR_USER_AGENT",
            "QuantumEdge Research atif.khan@example.com"
        )

        # --- Financial Data APIs ---
        self.fmp_api_key: str = os.getenv("FMP_API_KEY", "")
        self.alpha_vantage_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")

        # --- Web Search ---
        self.tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")

        # --- News ---
        self.news_api_key: str = os.getenv("NEWS_API_KEY", "")

        # --- Vector DB ---
        self.chroma_persist_dir: str = os.getenv(
            "CHROMA_PERSIST_DIR",
            str(_project_root / "data" / "chroma_db")
        )

        # --- Embeddings ---
        self.embedding_model: str = os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        # --- Logging ---
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_file: str = os.getenv(
            "LOG_FILE",
            str(_project_root / "logs" / "ara1.jsonl")
        )

    @staticmethod
    def _require(var_name: str) -> str:
        """Get a required environment variable or fail fast with a clear message."""
        value = os.getenv(var_name)
        if not value:
            print(
                f"\n{'=' * 60}\n"
                f"  FATAL: Required environment variable '{var_name}' is not set.\n"
                f"  1. Copy .env.example to .env\n"
                f"  2. Fill in your {var_name}\n"
                f"  3. Get your Groq API key at: https://console.groq.com\n"
                f"{'=' * 60}\n",
                file=sys.stderr
            )
            raise ConfigError(f"Missing required environment variable: {var_name}")
        return value

    def __repr__(self) -> str:
        return (
            f"Settings(\n"
            f"  planning_model={self.planning_model!r},\n"
            f"  fast_model={self.fast_model!r},\n"
            f"  judge_model={self.judge_model!r},\n"
            f"  groq_rpm={self.groq_rpm},\n"
            f"  groq_tpm={self.groq_tpm},\n"
            f"  embedding_model={self.embedding_model!r},\n"
            f"  chroma_persist_dir={self.chroma_persist_dir!r}\n"
            f")"
        )


# Singleton instance — import this from anywhere
# Wrapped in a function so tests can mock the env before calling it.
_settings_instance = None


def get_settings() -> Settings:
    """Get (or create) the global Settings singleton."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


def reset_settings():
    """Reset the singleton (used in tests to force re-read of env vars)."""
    global _settings_instance
    _settings_instance = None
