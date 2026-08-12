"""
Evaluation Benchmarks Package
Contains reference analyst summaries for MSFT, AAPL, TSLA.
"""
from pathlib import Path

BENCHMARK_DIR = Path(__file__).parent

def load_reference_summary(ticker: str) -> str:
    """Load reference summary markdown for a ticker (e.g. 'msft', 'aapl', 'tsla')."""
    file_path = BENCHMARK_DIR / f"{ticker.lower()}_reference.md"
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    return ""
