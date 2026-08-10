# ARA-1 (Autonomous Financial Research Agent) Project Ground Truth

## PROJECT IDENTITY
- Codename: ARA-1 (Autonomous Research Agent)
- Simulated employer: QuantumEdge Research (fictional quant research firm)
- My role: Lead AI Agent Architect
- Owner: Atif Khan (COMSATS University Islamabad, Software Engineering, FA24-BSE-011)
- Hardware constraint: CPU-only laptop (Intel i7 8th gen, 16GB RAM, no GPU). Prefer free-tier / local-first tools (Chroma over managed Pinecone during development; small/cheap LLM models during dev, better models only for final challenge runs) exactly as Section E of the brief recommends.

## CORE DELIVERABLE
An agent that: receives a financial research query -> autonomously plans -> calls tools across SEC EDGAR, a financial data API, earnings transcripts, news/web search, and its own vector memory -> resolves conflicting data via a source-reliability hierarchy -> produces a structured, cited investment research report -> degrades gracefully instead of hallucinating when tools fail. It must be validated against 8 progressive challenges.

## ARCHITECTURE REQUIREMENTS
1. **Reasoning loop**: ReAct (Thought/Action/Observation) or Plan-and-Execute, or a documented hybrid. Pick one explicitly on Day 1 and justify it in `architecture_specification.md` — don't leave it implicit in code.
2. **Tool registry**: minimum 10 tools, each with an OpenAI-function-calling-style JSON schema. Required tools at minimum: `sec_filing_search`, `web_search`, `earnings_transcript`, `financial_data_api`, `news_sentiment`, `vector_db_search`, `vector_db_store`, `company_profile`, `peer_comparison`, `report_generator`, `fact_checker`, `calculation_engine`.
3. **Memory**: three layers —
   (a) short-term = the live context window for one research session, with explicit summarization/compaction when it grows large;
   (b) long-term = a vector database (Chroma for dev; document a migration path to Pinecone/Weaviate/Qdrant) storing chunked findings with metadata: ticker, source_type, date, confidence, verified, researcher_session;
   (c) episodic = a log of which strategies/tools worked well for which query types, used to improve future planning.
4. **Multi-source synthesis**: implement the 5-tier source reliability hierarchy (SEC filings > financial data APIs > earnings transcripts > news outlets > social/forum content) and a conflict-resolution protocol. Always document the conflict and its resolution in the report output.
5. **Error handling**: retry with exponential backoff + jitter (start 1s, max 5 retries) for transient errors; a fallback chain of at least 2 alternate tools per primary tool; a circuit breaker so repeated failures on one tool don't cascade; graceful degradation that clearly states in the final report which sections are incomplete and why — NEVER fabricate data to fill a gap.
6. **Evaluation**: implement the 20+ metric framework across 5 categories exactly as specified. For any metric definition in the brief that looks self-contradictory, implement the version that is mathematically sensible and note in your evaluation report that you resolved an apparent contradiction in the source spec.
7. **8 progressive challenges** (Section B2) must all be runnable end-to-end against the final agent, from a 1/5-difficulty single company profile up to a 5/5-difficulty full report under a simulated 50% tool-failure rate.

## TECH STACK DEFAULTS
- **Language**: Python 3.11+, LangChain + LangGraph for orchestration
- **LLM**: **Groq API only** — no OpenAI or Anthropic key for the agent's reasoning engine. Use the official `groq` Python SDK or LangChain's wrapper pointing to Groq's base URL.
  - Planning / synthesis / final report generation: a larger reasoning model such as `qwen3-32b` or `llama-3.3-70b-versatile`.
  - Cheap/fast sub-tasks: a smaller/faster model such as `llama-3.1-8b-instant` or `compound-mini`.
  - Evaluation LLM-as-judge (Day 11): use a DIFFERENT Groq model than the one that generated the report being judged.
  - Respect Groq's published rate limits.
- **Vector DB**: Chroma locally during dev
- **Embeddings**: Default to a **free local model**, `sentence-transformers/all-MiniLM-L6-v2`.
- **Free-tier data sources**: SEC EDGAR full-text search API (no key), Financial Modeling Prep or Alpha Vantage or yfinance for financial data, Tavily or SerpAPI for web search, NewsAPI.org or scored sentiment on search results for news
- **Libraries**: `pydantic` for schema validation, `tenacity` for retry logic, `pytest` for tests
- **Web layer (additive, built Days 16-18):** FastAPI service in `api/` that wraps the agent, React 18+ / TypeScript / Vite / TailwindCSS frontend in `frontend/`. Do not touch the required Section D3 folders to build this.

## REQUIRED REPOSITORY LAYOUT
```text
Project1A-AtifKhan-AutonomousFinancialResearchAgent/
├── README.md
├── .zetheta-project.json
├── .env.example
├── requirements.txt
├── setup.py (or pyproject.toml)
├── ERROR_LOG.md
├── agent/
│   ├── __init__.py, core.py, prompts.py, parser.py, error_handler.py,
│   ├── fallback_chains.py, circuit_breaker.py, query_analyzer.py,
│   └── disambiguation.py
├── tools/
│   ├── __init__.py, tool_registry.py, schemas/, sec_edgar.py,
│   ├── financial_api.py, web_search.py, news_sentiment.py, earnings.py,
│   ├── company_profile.py, peer_comparison.py, calculator.py,
│   └── fact_checker.py, report_gen.py
├── memory/
│   └── __init__.py, vector_store.py, context_manager.py, episodic.py
├── synthesis/
│   └── __init__.py, engine.py, conflict_resolver.py, narrative.py
├── evaluation/
│   └── __init__.py, metrics.py, benchmarks/, dashboard.py
├── results/
│   ├── challenge_1.md ... challenge_8.md, evaluation_report.md,
│   └── stress_test_report.md, token_usage_analysis.md
├── docs/
│   └── architecture_specification_final.md, trace_gallery.md, optimization_log.md
└── tests/
    └── test_tools.py, test_memory.py, test_agent.py, test_synthesis.py
```

## ADDITIVE WEB LAYER (Days 16-18)
```text
Project1A-AtifKhan-AutonomousFinancialResearchAgent/
├── (everything above, unchanged)
├── api/
│   ├── __init__.py, main.py, schemas.py, websocket.py,
│   └── routes/
│       └── research.py, challenges.py, evaluation.py, memory.py, traces.py, tools.py
├── frontend/
│   ├── package.json, vite.config.ts, tailwind.config.ts, index.html,
│   ├── src/
│   │   └── main.tsx, App.tsx, pages/, components/, hooks/, lib/, styles/
│   └── public/
└── docker-compose.yml (optional)
```

## WORKING RULES
- Never fabricate financial data, citations, or API behavior in code comments or docstrings.
- Every tool must have a mock/stub mode.
- After each day's work, give: (1) short summary, (2) the exact commit message, WITHOUT the "Day-XX:" prefix (e.g. "Agent Architecture Specification - Atif Khan"), (3) uncertainties/assumptions.
- **CRITICAL COMMIT RULE**: Do NOT add day numbers in the commit message. Use only the exact message text required without the day prefix.
- Flag, don't silently resolve, any place where the brief's own spec is ambiguous or internally inconsistent.
- Do not start Day N+1 work until Day N is confirmed.
