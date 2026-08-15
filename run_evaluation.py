"""
ARA-1 Comprehensive Evaluation Execution Script
Runs the 20+ metric evaluation suite across all financial research benchmarks
and generates the evaluation report in results/evaluation_report_v2.md.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import run_day13_evaluation

if __name__ == "__main__":
    run_day13_evaluation.main()
