# ARA-1: Autonomous Financial Research Agent

> An autonomous, multi-source financial research agent built for QuantumEdge Research.
> Project 1A — Zetheta Algorithms challenge brief.

**Author:** Atif Khan (COMSATS University Islamabad, FA24-BSE-011)

---

## Overview

ARA-1 receives a financial research query, autonomously plans a research strategy,
calls tools across SEC EDGAR, financial data APIs, earnings transcripts, news/web
search, and its own vector memory, resolves conflicting data via a 5-tier source
reliability hierarchy, and produces a structured, cited investment research report.
It degrades gracefully instead of hallucinating when tools fail.

## Architecture

- **Agent Pattern:** Plan-and-Execute with ReAct inner loop
- **LLM:** Groq API only (no OpenAI/Anthropic)
  - Planning/synthesis: `qwen/qwen3-32b`
  - Fast sub-tasks: `openai/gpt-oss-20b`
  - Evaluation judge: `openai/gpt-oss-120b`
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (local, CPU-only)
- **Vector DB:** ChromaDB (local)
- **12 tools** with JSON schemas, fallback chains, and circuit breakers

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/atifkhani397/Financial-Research-agent-.git
cd Financial-Research-agent-
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
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

### 6. Run the test suite

```bash
pytest tests/ -v
```

### 7. Run a sample query (available after Day 7+)

```bash
python -m agent.core --query "What is Apple's current P/E ratio compared to industry peers?"
```

## Environment Variables

| Variable | Required | Description |
| :--- | :---: | :--- |
| `GROQ_API_KEY` | **Yes** | Groq API key from console.groq.com |
| `GROQ_PLANNING_MODEL` | No | Model for planning/synthesis (default: `qwen/qwen3-32b`) |
| `GROQ_FAST_MODEL` | No | Model for fast sub-tasks (default: `openai/gpt-oss-20b`) |
| `GROQ_JUDGE_MODEL` | No | Model for evaluation (default: `openai/gpt-oss-120b`) |
| `SEC_EDGAR_USER_AGENT` | No | Required by SEC.gov (format: "Company email") |
| `FMP_API_KEY` | No | Financial Modeling Prep API key |
| `TAVILY_API_KEY` | No | Tavily web search API key |
| `NEWS_API_KEY` | No | NewsAPI.org key |

See [.env.example](.env.example) for the full list with comments.

## Project Structure

```
├── agent/          # Core agent logic (reasoning loop, LLM wrapper, prompts)
├── tools/          # 12 tool implementations with JSON schemas
├── memory/         # Vector store, context manager, episodic memory
├── synthesis/      # Multi-source synthesis and conflict resolution
├── evaluation/     # Metrics framework, benchmarks, dashboard
├── config/         # Environment and model configuration
├── tests/          # Unit and integration tests
├── results/        # Challenge outputs and evaluation reports
└── docs/           # Architecture spec, trace gallery, optimization log
```

## Hardware Requirements

- **CPU-only laptop** (Intel i7 8th gen, 16GB RAM — no GPU required)
- All inference runs on Groq's cloud API
- Embeddings run locally via sentence-transformers

## License

MIT
