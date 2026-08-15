"""
ARA-1 System Stress & Resilience Testing Suite
Executes failure injection tests, concurrency tests, context compaction stress tests,
and total outage fallback verification.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import run_day12_challenges_and_stress_tests

if __name__ == "__main__":
    run_day12_challenges_and_stress_tests.main()
