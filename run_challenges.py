"""
ARA-1 Financial Research Benchmark Challenges Runner
Runs the agent against financial research benchmarks, edge cases, and cross-company synthesis tasks.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import run_day10_challenges

if __name__ == "__main__":
    run_day10_challenges.main()
