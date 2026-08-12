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
| **Day 14** | Final Documentation & Trace Gallery | ✅ Complete | `docs/architecture_specification_final.md`, `docs/trace_gallery.md`, `docs/evaluation_report_final.md`, `ERROR_LOG.md` |
| **Day 15** | Code Cleanup & Final Audit | ✅ Complete | `.zetheta-project.json`, `docs/demo_video_script.md`, repo layout verification |
| **Day 16** | FastAPI Service Layer Over Agent Engine | ✅ Complete | REST & WebSocket API (`api/main.py`, `api/routes/`, `api/schemas.py`, `api/websocket.py`, `tests/test_api.py`) |
| **Day 17** | Modern React 18 Frontend UI | ✅ Complete | React 18 / Vite / Tailwind UI (`frontend/`, `QueryConsolePage`, `LiveTraceView`, `ReportViewerPage`, `ToolRegistryPage`, `MemoryExplorerPage`, `EvaluationDashboardPage`, `TraceGalleryPage`) |
| **Day 18** | Full-Stack Integration Audit & Release | ✅ Complete | Web layer integration audit, full test suite validation, full release packaging |

---

## 🚀 Overview & Key Architectural Layers

ARA-1 receives a natural language financial research query, autonomously plans a multi-step roadmap, calls tools across SEC EDGAR, financial data APIs, earnings call transcripts, news/web search, and its own 3-layer vector memory, resolves conflicting data via a 5-tier source reliability hierarchy, and produces structured, cited investment research reports with DCF valuation models.

### Key Production Architecture:

```
                      ┌─────────────────────────────────────────┐
                      │            User Research Query           │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │  Query Analyzer (Disambiguation & Type)  │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │    Planner LLM (llama-3.3-70b-versatile) │
                      │  Creates Multi-Step Execution Plan JSON │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
            ┌───────────────────────────────────────────────────────────┐
            │               Step Execution Loop (ReAct Inner)            │
            │               Fast LLM (llama-3.1-8b-instant)             │
            │                                                           │
            │  THOUGHT ──► ACTION (Tool Call) ──► CIRCUIT BREAKER /      │
            │                                     FALLBACK CHAIN         │
            │                                            │              │
            │  STEP_COMPLETE ◄── OBSERVATION ◄───────────┘              │
            └──────────────────────────────┬────────────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │ Multi-Source Synthesis & Fact Checker   │
                      │  5-Tier Source Reliability Hierarchy    │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │ Final Report Generator (Cited Markdown) │
                      │  Section A8.2 Stage 4 Token Budgeting   │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
            ┌───────────────────────────────────────────────────────────┐
            │                     ADDITIVE WEB LAYER                    │
            │                                                           │
            │  FastAPI Server (8000)  ◄──►  React 18 / Vite UI (5173)   │
            │  REST + WebSockets            TanStack Query + Tailwind   │
            └───────────────────────────────────────────────────────────┘
```

1. **Agent Pattern:** Plan-and-Execute global strategy with a bounded ReAct inner loop per step.
2. **LLM Engine:** Groq API (`llama-3.3-70b-versatile` for planning/synthesis; `llama-3.1-8b-instant` for fast execution; `llama-3.3-70b-versatile` for LLM-as-Judge).
3. **Three-Layer Memory Architecture:**
   - **Short-Term Memory:** Live context manager tracking token usage with 70% threshold trace compaction.
   - **Long-Term Memory:** Local ChromaDB with structural chunking (SEC Filings by Item, Transcripts by speaker-turn, News by paragraph carrying headline context, Financial Statements as metadata).
   - **Episodic Memory:** Task episode strategy log for past strategy recall.
4. **12 Live Tools:** `sec_filing_search`, `financial_data_api`, `earnings_transcript`, `news_sentiment`, `web_search`, `vector_db_search`, `vector_db_store`, `company_profile`, `peer_comparison`, `calculation_engine` (with DCF model), `fact_checker`, `report_generator`.
5. **Web Layer:** FastAPI service (`api/`) with REST & WebSockets + React 18 / Vite / Tailwind UI (`frontend/`).

---

## 💻 Full-Stack Quick-Start & Installation

### 1. System Requirements
- **OS**: Windows, macOS, or Linux
- **Python**: Version 3.10, 3.11, or 3.12 recommended
- **Node.js**: Version 18+ or 20+
- **Hardware**: CPU-only supported (16GB RAM recommended; no local GPU required)

### 2. Clone the Repository

```bash
git clone https://github.com/atifkhani397/Financial-Research-agent-.git
cd Financial-Research-agent-
```

### 3. Setup Python Backend Environment

```bash
# Windows (PowerShell)
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Setup Environment Variables

Create `.env` in the root directory:

```bash
cp .env.example .env
```

Fill in `.env`:

```env
GROQ_API_KEY=gsk_your_groq_key_here
SEC_EDGAR_USER_AGENT=QuantumEdge Research atif.khan@example.com
FMP_API_KEY=your_fmp_key_here
TAVILY_API_KEY=tvly-your_tavily_key_here
NEWS_API_KEY=your_news_key_here
```

### 5. Launch FastAPI Backend Server

```bash
# Serves REST API endpoints & WebSockets at http://localhost:8000
uvicorn api.main:app --reload --port 8000
```

### 6. Launch React Frontend Application

```bash
# In a new terminal tab
cd frontend
npm run dev
# Opens web app UI at http://localhost:5173
```

---

## 🔑 Required API Keys & Acquisition Guide

| API Key / Setting | Mandatory? | Free Tier Available? | Acquisition URL & Registration Instructions |
| :--- | :---: | :---: | :--- |
| `GROQ_API_KEY` | **Yes** | **Yes** (Free) | Register at [console.groq.com](https://console.groq.com). Create an API key under **API Keys**. Powers planning, execution, synthesis, and judge passes. |
| `SEC_EDGAR_USER_AGENT` | **Yes** | **Yes** (Free) | SEC EDGAR requires a custom User-Agent header (format: `CompanyName AdminEmail`, e.g. `QuantumEdge Research admin@quantumedge.com`). No API key needed. |
| `FMP_API_KEY` | Optional | **Yes** (Free) | Register at [financialmodelingprep.com/developer](https://financialmodelingprep.com/developer). Free tier provides company profiles, income statements, balance sheets. |
| `TAVILY_API_KEY` | Optional | **Yes** (Free) | Register at [tavily.com](https://tavily.com). Free tier provides 1,000 search queries/month for web search fallbacks. |
| `NEWS_API_KEY` | Optional | **Yes** (Free) | Register at [newsapi.org](https://newsapi.org). Free tier provides 100 requests/day for news sentiment aggregation. |

---

## 📈 Measured System Improvements (Day 11 vs Day 13)

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

## 🤖 AI Assistance Disclosure (Section E5.3)

In compliance with **Section E5.3 of the Zetheta Algorithms Project Brief**, below is the specific disclosure detailing which AI tools were used during development and for what tasks:

1. **Antigravity AI (Google DeepMind)**:
   - **Usage**: Primary agentic pair programming assistant.
   - **Specific Tasks**: Architected the hybrid Plan-and-Execute reasoning engine, wrote Tenacity retry wrappers, developed vector store chunking logic (`memory/vector_store.py`), created 20+ metric evaluation scripts (`run_day11_evaluation.py`, `run_day13_evaluation.py`), formatted markdown artifacts, and scaffolded the FastAPI + React web layer.

2. **Groq Cloud API Models (`llama-3.3-70b-versatile` & `llama-3.1-8b-instant`)**:
   - **Usage**: Runtime LLM inference engine powering the agent at runtime.
   - **Specific Tasks**: `llama-3.3-70b-versatile` executed step planning, plan revisions, multi-source synthesis, and qualitative LLM-as-Judge evaluation passes. `llama-3.1-8b-instant` executed fast ReAct Thought-Action tool selection cycles.

3. **Sentence Transformers (`sentence-transformers/all-MiniLM-L6-v2`)**:
   - **Usage**: Local HuggingFace embedding model.
   - **Specific Tasks**: Embedded SEC filing chunks, earnings transcripts, and news articles into 384-dimensional dense vectors for ChromaDB long-term memory retrieval.

---

## 📂 Full Repository Structure

```text
├── agent/                         # Core agent logic (reasoning loop, LLM wrapper, prompts, parser)
├── api/                           # FastAPI REST & WebSocket web service (main.py, schemas.py, routes/)
├── tools/                         # 12 live tool implementations & JSON schemas
├── memory/                        # Vector store (Chroma), context manager, episodic memory
├── synthesis/                     # Multi-source synthesis and conflict resolution
├── evaluation/                    # Metrics framework, benchmarks, dashboard
├── config/                        # Environment and model configuration
├── frontend/                      # React 18 / Vite / Tailwind UI application
│   ├── src/
│   │   ├── lib/api.ts             # Type-safe API client
│   │   ├── hooks/                 # Custom WebSocket stream hook
│   │   └── pages/                 # Console, Trace, Report, Tools, Memory, Eval, Gallery
├── scripts/                       # Utility & API smoke test scripts (api_smoke_test.py)
├── tests/                         # Unit & integration test suite (test_memory.py, test_tools.py, test_api.py)
├── results/                       # Generated reports (challenge_1.md ... challenge_8.md, evaluation_report_v2.md)
└── docs/                          # Architecture spec, trace gallery, optimization log, demo_video_script.md
```

---

## 📄 License

MIT
