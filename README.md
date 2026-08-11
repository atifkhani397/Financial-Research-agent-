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
| **Day 3** | LLM Integration & Rate Limiting | ✅ Complete | Groq API wrapper (`qwen3-32b`, `gpt-oss-20b`), token bucket limiter |
| **Day 4** | Plan-and-Execute Agent Core Loop | ✅ Complete | Hybrid Planner + ReAct executor loop, plan revisions, limits |
| **Day 5** | Live API Data Sources | ✅ Complete | Real SEC EDGAR, Financial Modeling Prep (FMP), Tavily, NewsAPI |
| **Day 6** | Three-Layer Memory Architecture | ✅ Complete | Short-term context compaction, Chroma long-term vector store with structural chunking, Episodic memory |
| **Day 7** | 12-Tool Registry Live & Challenges 3–4 | ✅ Complete | All 12 tools functional (`dcf`, `fact_checker`, `peer_comparison`, `earnings_transcript`, `report_generator`) |
| **Day 8** | Multi-Source Synthesis & Source Hierarchy | ✅ Complete | Conflict resolution protocol, 5-tier reliability hierarchy, sentiment-fact alignment |
| **Day 9** | Fallback Chains & Circuit Breakers | ✅ Complete | Resilience under simulated 50% API failure rate, exponential backoff, circuit breaker |
| **Day 10** | Error Recovery & Stress Testing | ⏳ Next | Challenge 8 (5/5 difficulty) graceful degradation |
| **Day 11** | Evaluation Framework & LLM-as-Judge | 📅 Upcoming | 20+ metrics evaluation engine |
| **Day 12** | Token Usage Analysis & Optimization | 📅 Upcoming | Efficiency benchmarks & optimization logs |
| **Day 13** | Documentation & Trace Gallery | 📅 Upcoming | Full architectural documentation & trace gallery |
| **Day 14** | End-to-End Benchmark Run | 📅 Upcoming | Full test suite against all 8 progressive challenges |
| **Day 15** | Code Cleanup & Final Audit | 📅 Upcoming | Final repository audit and release |
| **Days 16–18** | Additive Web Layer | 📅 Upcoming | FastAPI backend (`api/`) & React 18 / Vite / Tailwind UI (`frontend/`) |

---

## 🚀 Overview & Key Features

ARA-1 receives a natural language financial research query, autonomously plans a multi-step roadmap, calls tools across SEC EDGAR, financial data APIs, earnings call transcripts, news/web search, and its own 3-layer vector memory, resolves conflicting data via a 5-tier source reliability hierarchy, and produces a structured, cited investment research report with DCF valuation models.

### Key Architectural Layers

1. **Agent Pattern:** Plan-and-Execute global strategy with a bounded ReAct inner loop per step.
2. **LLM Engine:** Groq API (`qwen/qwen3-32b` for planning/synthesis; `openai/gpt-oss-20b` for fast execution).
3. **Three-Layer Memory Architecture:**
   - **Short-Term Memory:** Live context manager tracking token usage with 70% threshold trace compaction.
   - **Long-Term Memory:** Local ChromaDB with structural chunking (SEC Filings by Item, Transcripts by speaker-turn, News by paragraph carrying headline context, Financial Statements as metadata).
   - **Episodic Memory:** Task episode strategy log for past strategy recall.
4. **12 Live Tools:** `sec_filing_search`, `financial_data_api`, `earnings_transcript`, `news_sentiment`, `web_search`, `vector_db_search`, `vector_db_store`, `company_profile`, `peer_comparison`, `calculation_engine` (with DCF model), `fact_checker`, `report_generator`.

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

### 5. Initialize the vector database

```bash
python init_vector_db.py
```

### 6. Run the full test suite

```bash
pytest tests/test_memory.py tests/test_tools.py -v
```

### 7. Run Challenge Execution Scripts

```bash
# Day 5 Challenges (1 & 2)
python run_day5_challenges.py

# Day 6 Challenges (1 & 7 Memory Recall)
python run_day6_challenges.py

# Day 7 Challenges (3 & 4: Tesla Risk & DCF, Cloud Hyperscalers)
python run_day7_challenges.py
```

---

## 🛠️ Environment Variables

| Variable | Required | Description |
| :--- | :---: | :--- |
| `GROQ_API_KEY` | **Yes** | Groq API key from [console.groq.com](https://console.groq.com) |
| `GROQ_PLANNING_MODEL` | No | Model for planning/synthesis (default: `qwen/qwen3-32b`) |
| `GROQ_FAST_MODEL` | No | Model for fast sub-tasks (default: `openai/gpt-oss-20b`) |
| `GROQ_JUDGE_MODEL` | No | Model for evaluation (default: `openai/gpt-oss-120b`) |
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
├── tests/          # Unit and integration test suite (test_memory.py, test_tools.py)
├── results/        # Generated reports (challenge_1.md ... challenge_7.md)
└── docs/           # Architecture spec, trace gallery, optimization log
```

---

## 💻 Hardware Requirements

- **CPU-only laptop** (Intel i7 8th gen, 16GB RAM — no GPU required)
- All LLM inference runs on Groq's cloud API
- Embeddings run locally via `sentence-transformers/all-MiniLM-L6-v2`

---

## 📄 License

MIT
