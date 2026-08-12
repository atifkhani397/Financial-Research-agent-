# ARA-1: Autonomous Financial Research Agent

> An autonomous, multi-source financial research agent built for QuantumEdge Research.
> Project 1A — Zetheta Algorithms challenge brief.

**Author:** Atif Khan (COMSATS University Islamabad, FA24-BSE-011)

---

## 📊 Development Progress Tracker (Days 1–18 Roadmap)

| Phase | Milestone | Status | Details / Deliverables |
| :--- | :--- | :---: | :--- |
| **Day 1** | Architecture Specification & Foundation | ✅ Complete | `docs/architecture_specification.md`, project layout |
| **Day 2** | Tool Registry & JSON Schemas | ✅ Complete | 12 tool schemas, `ToolRegistry` with validation |
| **Day 3** | LLM Integration & Rate Limiting | ✅ Complete | Groq API wrapper (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`), token bucket limiter |
| **Day 4** | Plan-and-Execute Agent Core Loop | ✅ Complete | Hybrid Planner + ReAct executor loop, plan revisions, limits |
| **Day 5** | Live API Data Sources | ✅ Complete | Real SEC EDGAR, Financial Modeling Prep (FMP), Tavily, NewsAPI |
| **Day 6** | Three-Layer Memory Architecture | ✅ Complete | Short-term context compaction, Chroma long-term vector store with structural chunking, Episodic memory |
| **Day 7** | 12-Tool Registry Live & Challenges 3–4 | ✅ Complete | All 12 tools functional (`dcf`, `fact_checker`, `peer_comparison`, `earnings_transcript`, `report_generator`) |
| **Day 8** | Multi-Source Synthesis & Source Hierarchy | ✅ Complete | Conflict resolution protocol, 5-tier reliability hierarchy, sentiment-fact alignment |
| **Day 9** | Fallback Chains & Circuit Breakers | ✅ Complete | Resilience under simulated 50% API failure rate, exponential backoff, circuit breaker |
| **Day 10** | Query Disambiguation & Edge Cases | ✅ Complete | Section A8.3 query classification, stated assumptions, private company non-fabrication |
| **Day 11** | Evaluation Framework & LLM-as-Judge | ✅ Complete | 20+ Metric Evaluation Framework (`run_day11_evaluation.py`, `results/evaluation_report.md`, `evaluation_dashboard.html`) |
| **Day 12** | Challenge 8 & System Stress Testing | ✅ Complete | Challenge 8 NVDA 50% failure report (`results/challenge_8.md`), 3 stress tests (`results/stress_test_report.md`), token usage analysis |
| **Day 13** | Measurable Optimization & Evaluation V2 | ✅ Complete | +8.76 pt score gain, 32.0% token reduction, +21.1% memory utilization (`docs/optimization_log.md`, `results/evaluation_report_v2.md`) |
| **Day 14** | End-to-End Benchmark Run | 📅 Upcoming | Full test suite against all progressive challenges |
| **Day 15** | Code Cleanup & Final Audit | 📅 Upcoming | Final repository audit and release |
| **Days 16–18** | Additive Web Layer | 📅 Upcoming | FastAPI backend (`api/`) & React 18 / Vite / Tailwind UI (`frontend/`) |

---

## 🚀 Overview & Key Features

ARA-1 receives a natural language financial research query, autonomously plans a multi-step roadmap, calls tools across SEC EDGAR, financial data APIs, earnings call transcripts, news/web search, and its own 3-layer vector memory, resolves conflicting data via a 5-tier source reliability hierarchy, and produces a structured, cited investment research report with DCF valuation models.

### Key Architectural Layers

1. **Agent Pattern:** Plan-and-Execute global strategy with a bounded ReAct inner loop per step.
2. **LLM Engine:** Groq API (`llama-3.3-70b-versatile` for planning/synthesis; `llama-3.1-8b-instant` for fast execution; `llama-3.3-70b-versatile` for LLM-as-Judge).
3. **Three-Layer Memory Architecture:**
   - **Short-Term Memory:** Live context manager tracking token usage with 70% threshold trace compaction.
   - **Long-Term Memory:** Local ChromaDB with structural chunking (SEC Filings by Item, Transcripts by speaker-turn, News by paragraph carrying headline context, Financial Statements as metadata).
   - **Episodic Memory:** Task episode strategy log for past strategy recall.
4. **12 Live Tools:** `sec_filing_search`, `financial_data_api`, `earnings_transcript`, `news_sentiment`, `web_search`, `vector_db_search`, `vector_db_store`, `company_profile`, `peer_comparison`, `calculation_engine` (with DCF model), `fact_checker`, `report_generator`.

---

## 📈 Quantified Optimization & Evaluation Benchmarks (Day 11 vs Day 13)

| Performance Metric | Day 11 Baseline | Day 13 Optimized | Verified Metric Improvement |
| :--- | :--- | :--- | :--- |
| **Composite Evaluation Score** | **81.17 / 100** | **89.94 / 100** | **+8.76 Points Gain** |
| **Tool Efficiency (AB-1)** | 88.5% | 94.2% | **+5.7% Improvement** |
| **Memory Utilization (AB-4)** | 71.4% | 92.5% | **+21.1% Increase** |
| **Section Coverage (CO-1)** | 76.1% | 95.2% | **+19.1% Gain** |
| **Total Prompt Tokens** | 64,820 tokens | 44,077 tokens | **32.0% Token Cost Reduction** |
| **Average Query Latency (AB-5)** | 38.2s avg | 21.4s avg | **44.0% Faster Execution** |
| **Hallucination Rate (FA-5)** | 0.00% | 0.00% | **Sustained 0.00% (Zero Hallucinations)** |

---

## 💻 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/atifkhani397/Financial-Research-agent-.git
cd Financial-Research-agent-
```

### 2. Create a dedicated virtual environment (`.venv`)

```bash
# Windows
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt tavily-python
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (required)
# Get your key at: https://console.groq.com
```

### 5. Run Evaluation Suites & Stress Tests

```bash
# Day 11 Full 20+ Metric Evaluation Suite
python run_day11_evaluation.py

# Day 12 Challenge 8 & Stress Tests
python run_day12_challenges_and_stress_tests.py

# Day 13 Measurable Optimization Evaluation V2
python run_day13_evaluation.py
```

---

## 🛠️ Environment Variables

| Variable | Required | Description |
| :--- | :---: | :--- |
| `GROQ_API_KEY` | **Yes** | Groq API key from [console.groq.com](https://console.groq.com) |
| `GROQ_PLANNING_MODEL` | No | Model for planning/synthesis (default: `llama-3.3-70b-versatile`) |
| `GROQ_FAST_MODEL` | No | Model for fast sub-tasks (default: `llama-3.1-8b-instant`) |
| `GROQ_JUDGE_MODEL` | No | Model for evaluation (default: `llama-3.3-70b-versatile`) |
| `SEC_EDGAR_USER_AGENT` | No | Required by SEC.gov (format: `QuantumEdge Research email@domain.com`) |
| `FMP_API_KEY` | No | Financial Modeling Prep API key |
| `TAVILY_API_KEY` | No | Tavily web search API key |
| `NEWS_API_KEY` | No | NewsAPI.org key |

See [.env.example](.env.example) for details.

---

## 📂 Project Structure

```text
├── agent/          # Core agent logic (reasoning loop, LLM wrapper, prompts, parser)
├── tools/          # 12 live tool implementations & JSON schemas
├── memory/         # Vector store (Chroma), context manager, episodic memory
├── synthesis/      # Multi-source synthesis and conflict resolution
├── evaluation/     # Metrics framework, benchmarks, dashboard
├── config/         # Environment and model configuration
├── tests/          # Unit and integration test suite
├── results/        # Generated reports (challenge_1.md ... challenge_8.md, evaluation_report_v2.md)
└── docs/           # Architecture spec, trace gallery, optimization log
```

---

## 💻 Hardware Requirements

- **CPU-only laptop** (Intel i7 8th gen, 16GB RAM — no GPU required)
- All LLM inference runs on Groq's cloud API
- Embeddings run locally via `sentence-transformers/all-MiniLM-L6-v2` or in-memory fallback

---

## 📄 License

MIT
