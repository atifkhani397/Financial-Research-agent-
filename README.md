# ARA-1: Autonomous Financial Research Agent

> An autonomous, multi-source financial research AI agent engine with real-time tool execution, multi-tier memory compaction, automated source conflict resolution, and a full-stack interactive interface.

**Author:** Atif Khan (COMSATS University Islamabad)

---

## 📌 Architecture & System Capabilities Matrix

| Architecture Layer | Core Focus | Status | Key Features & Deliverables |
| :--- | :--- | :---: | :--- |
| **Foundation & Design** | Architecture Specification | ✅ Complete | Modular decoupling, async design (`docs/architecture_specification.md`) |
| **Tool Infrastructure** | Schema Validation & Registry | ✅ Complete | 12 financial tool schemas, strict JSON validation (`ToolRegistry`) |
| **LLM & Rate Control** | Orchestration & Throttling | ✅ Complete | Dual-tier LLM integration (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`), token bucket limiter |
| **Reasoning Engine** | Plan-and-Execute Loop | ✅ Complete | Hybrid Planner + ReAct executor loop, dynamic plan revision |
| **Data Connectors** | Financial API Integrations | ✅ Complete | Live SEC EDGAR, Financial Modeling Prep (FMP), Tavily Search, NewsAPI |
| **Memory Management** | Multi-Tier Context Memory | ✅ Complete | Context compaction, ChromaDB vector store, episodic memory |
| **Financial Analysis** | Quantitative Tool Suite | ✅ Complete | DCF valuation, peer analysis, earnings transcript parser, fact checker |
| **Data Synthesis** | Multi-Source Hierarchy | ✅ Complete | 5-tier source reliability hierarchy, sentiment-fact alignment |
| **Report PDF Engine** | `rules.md` Strict Typography | ✅ Complete | Real-time `xhtml2pdf` generation, strict ASCII rules (zero unicode hyphens/dots) |
| **System Resilience** | Circuit Breakers & Retries | ✅ Complete | Exponential backoff, 50% API failure resilience, circuit breaker pattern |
| **Query Intelligence** | Disambiguation & Edge Cases | ✅ Complete | Entity classification, stated assumption resolution, non-fabrication guarantees |
| **Evaluation Suite** | Quantitative Benchmarks | ✅ Complete | 20+ metric evaluation framework (`evaluation/metrics.py`, interactive HTML dashboard) |
| **Stress Testing** | Concurrency & Fault Recovery | ✅ Complete | System concurrency tests, memory stress tests, full outage fallbacks |
| **Performance Tuning** | Token & Latency Optimization | ✅ Complete | +8.76 pt evaluation score gain, 32.0% token cost reduction, +21.1% memory utilization |
| **Observability** | Trace Gallery & Diagnostics | ✅ Complete | Reasoning trace gallery (`docs/trace_gallery.md`), system audit logs |
| **Quality Audit** | Security & Code Refactoring | ✅ Complete | Codebase modularization, clean type annotations, test suite coverage |
| **API Service Layer** | REST & WebSocket Server | ✅ Complete | FastAPI REST endpoints, WebSocket streaming, `/pdf` REST export (`api/`) |
| **Interactive Frontend** | Web Console & Dashboards | ✅ Complete | React 18 / Vite UI, All Generated Reports directory grid with direct PDF downloads |
| **Deployment** | Full-Stack Containerization | ✅ Complete | Single-command Docker Compose orchestration (`docker-compose.yml`) |

---

## 🏗 System Architecture Overview

ARA-1 features a decoupled architecture designed for high throughput, data integrity, and real-time observability.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      CORE REASONING ENGINE (CLI)                         │
│                                                                          │
│  agent/  tools/  memory/  synthesis/  evaluation/  config/  tests/       │
│  - Python 3.11 Execution Engine                                          │
│  - Automated Pytest integration test suite (100% pass rate)              │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ (Modular Execution Interface)
┌──────────────────────────────────────────────────────────────────────────┐
│                      INTERACTIVE FULL-STACK WEB LAYER                    │
│                                                                          │
│  api/                     FastAPI Backend (REST & WebSocket Streaming)   │
│  frontend/                React 18 / Vite / Tailwind Dashboard           │
│  docker-compose.yml       Single-Command Deployment Container            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 💻 CLI Quick Start Guide

### 1. System Requirements
- **OS**: Windows, macOS, or Linux
- **Python**: Version 3.10, 3.11, or 3.12 recommended
- **Hardware**: CPU-only supported (16GB RAM recommended)

### 2. Virtual Environment Setup

```bash
# Clone Repository
git clone https://github.com/atifkhani397/Financial-Research-agent-.git
cd Financial-Research-agent-

# Windows (PowerShell)
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Install Dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Environment Variable Configuration

Create `.env` in the root directory:

```bash
cp .env.example .env
```

Configure `.env`:
```env
GROQ_API_KEY=gsk_your_groq_key_here
SEC_EDGAR_USER_AGENT=QuantumEdge Research atif.khan@example.com
FMP_API_KEY=your_fmp_key_here
TAVILY_API_KEY=tvly-your_tavily_key_here
NEWS_API_KEY=your_news_key_here
```

### 4. Run Core Verification & Benchmark Suites

```bash
# Run Integration Test Suite (100% pass rate)
pytest tests/ -v

# Run Comprehensive 20+ Metric Evaluation Framework
python run_evaluation.py

# Run System Stress & Resilience Tests
python run_stress_tests.py

# Run Benchmark Research Challenges
python run_challenges.py
```

---

## 🌐 Web UI & API Application Quick Start

### Option A: Single-Command Docker Deployment (Recommended)

```bash
# Build and launch FastAPI backend + React frontend with one command
docker compose up --build

# Backend API: http://localhost:8000
# Frontend Web App: http://localhost:5173
```

### Option B: Local Development Execution

```bash
# Terminal 1: Launch FastAPI Service
uvicorn api.main:app --reload --port 8000

# Terminal 2: Launch React Frontend Application
cd frontend
npm run dev
# Opens web application at http://localhost:5173
```

### Web Interface Capabilities:
1. **Query Console (`http://localhost:5173`)**: Direct financial query input and benchmark scenario cards.
2. **Live Trace Stream (`/trace/:sessionId`)**: Real-time WebSocket execution feed displaying active step plans, tool execution parameters, fallback hops, and circuit breaker status.
3. **Report Viewer & Conflict Panel (`/report/:sessionId`)**: Rendered markdown reports with citations and an interactive **5-Tier Conflict Resolution Panel**.
4. **Tool Registry Explorer (`/tools`)**: Interactive inspection of all 12 registered tools with schema specifications.
5. **Memory Explorer (`/memory`)**: Vector store search across ChromaDB dense embeddings.
6. **Evaluation Dashboard (`/evaluation`)**: Visual analytics comparing baseline performance metrics against optimized benchmarks.
7. **Trace Gallery (`/traces`)**: Curated set of annotated execution traces demonstrating reasoning pathways.

---

## 🔑 Required API Keys & Acquisition Guide

| API Key / Parameter | Mandatory? | Free Tier Available? | Acquisition & Setup Guide |
| :--- | :---: | :---: | :--- |
| `GROQ_API_KEY` | **Yes** | **Yes** | Register at [console.groq.com](https://console.groq.com). Create an API key under **API Keys**. Powers reasoning, tool selection, synthesis, and judge passes. |
| `SEC_EDGAR_USER_AGENT` | **Yes** | **Yes** | Mandatory User-Agent header required by SEC EDGAR (Format: `Organization Email`, e.g. `QuantumEdge Research admin@quantumedge.com`). No API key needed. |
| `FMP_API_KEY` | Optional | **Yes** | Register at [financialmodelingprep.com](https://financialmodelingprep.com/developer). Free tier provides company profiles, income statements, balance sheets. |
| `TAVILY_API_KEY` | Optional | **Yes** | Register at [tavily.com](https://tavily.com). Free tier provides web search capabilities for fallbacks. |
| `NEWS_API_KEY` | Optional | **Yes** | Register at [newsapi.org](https://newsapi.org). Free tier provides news sentiment aggregation. |

---

## 📈 Quantified System Performance & Optimization Metrics

| Performance Metric | Initial Baseline | Production Optimized | Quantified Gain / Optimization |
| :--- | :--- | :--- | :--- |
| **Composite Evaluation Score** | **81.17 / 100** | **89.94 / 100** | **+8.76 Points Gain** |
| **Tool Efficiency (AB-1)** | 88.5% | 94.2% | **+5.7% Improvement** |
| **Memory Utilization (AB-4)** | 71.4% | 92.5% | **+21.1% Increase** |
| **Section Coverage (CO-1)** | 76.1% | 95.2% | **+19.1% Gain** |
| **Total Prompt Tokens** | 64,820 tokens | 44,077 tokens | **32.0% Token Cost Reduction** |
| **Average Query Latency (AB-5)** | 38.2s avg | 21.4s avg | **44.0% Faster Execution** |
| **Hallucination Rate (FA-5)** | 0.00% | 0.00% | **Sustained 0.00% (Zero Hallucinations)** |

---

## 🤖 Technology Stack & Component Disclosures

The implementation leverages modern open-source models, libraries, and frameworks:

1. **Antigravity AI (Google DeepMind)**:
   - **Role**: Intelligent coding assistant utilized during development.
   - **Scope**: Assisted with architecture design, vector store chunking logic (`memory/vector_store.py`), evaluation framework integration (`evaluation/metrics.py`), and full-stack REST/WebSocket API and React UI creation.

2. **Groq Cloud API Infrastructure (`openai/gpt-oss-120b` & `openai/gpt-oss-20b`)**:
   - **Role**: High-speed LLM inference engine powering the agent at runtime.
   - **Scope**: `openai/gpt-oss-120b` manages step planning, plan revisions, multi-source synthesis, and quantitative evaluation judging. `openai/gpt-oss-20b` handles fast ReAct tool selection loops.

3. **Sentence Transformers (`sentence-transformers/all-MiniLM-L6-v2`)**:
   - **Role**: Dense embedding generation.
   - **Scope**: Generates 384-dimensional vector embeddings for SEC filings, earnings transcripts, and web search results for semantic retrieval in ChromaDB.

---

## 📂 Repository Layout

```text
├── rules.md                        # Mandatory report formatting & ASCII typography specification
├── .agents/AGENTS.md              # Project agent rules configuration
├── agent/                         # Core reasoning engine (planner, ReAct loop, LLM wrapper, prompts)
├── api/                           # FastAPI REST & WebSocket server (main.py, schemas.py, routes/)
├── tools/                         # 12 financial tool implementations & JSON validation schemas
├── memory/                        # Vector store (ChromaDB), context compaction manager, episodic memory
├── synthesis/                     # Multi-source synthesis and 5-tier conflict resolution engine
├── evaluation/                    # Metric evaluation framework, benchmark runner, HTML dashboard generator
├── config/                        # Environment, logging, and model parameter configuration
├── frontend/                      # React 18 / Vite / Tailwind Web UI Application
│   ├── src/
│   │   ├── lib/api.ts             # Type-safe REST API client
│   │   ├── hooks/                 # WebSocket streaming hook
│   │   └── pages/                 # Console, Trace, Report (Directory Grid & PDF), Tools, Memory, Eval, Gallery views
├── scripts/                       # Diagnostic & smoke test scripts
├── tests/                         # Automated Pytest suite (unit, integration, and API tests)
├── results/                       # Generated research reports (.md and .pdf binary files), stress test reports
├── docs/                          # Architecture specs, trace gallery, optimization logs, QA logs
├── Dockerfile                     # FastAPI backend container manifest
├── docker-compose.yml             # Full-stack Docker Compose configuration
├── run_evaluation.py              # CLI runner for comprehensive evaluation framework
├── run_stress_tests.py            # CLI runner for system stress testing
└── run_challenges.py              # CLI runner for research benchmark challenges
```

---

## 📄 License

MIT
