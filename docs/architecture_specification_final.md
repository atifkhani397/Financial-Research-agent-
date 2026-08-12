# ARA-1 Final Architecture Specification (As-Built)

**Project Codename:** ARA-1 (Autonomous Research Agent)  
**Role:** Lead AI Agent Architect  
**Author:** Atif Khan (QuantumEdge Research / COMSATS University Islamabad)  
**Specification Version:** Final As-Built Architecture (Days 1–14)

---

## 1. Executive Summary & Core Agent Pattern

ARA-1 is an autonomous, multi-source financial research agent engineered for QuantumEdge Research to execute complex financial analyses, synthesize quantitative and qualitative data across Tier 1–5 authoritative sources, and maintain publication-grade reliability under extreme API outage conditions.

### Implemented Agent Pattern: Plan-and-Execute with Bounded ReAct Inner Loop

The production system implements a **hybrid Plan-and-Execute architecture** combined with a **bounded ReAct (Thought → Action → Observation) inner loop** for step execution.

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
                      └─────────────────────────────────────────┘
```

**Why this pattern succeeded:**
- **Global Strategic Coherence**: The Planner (`llama-3.3-70b-versatile`) creates an explicit, dependency-ordered roadmap, eliminating wandering and infinite reasoning loops.
- **Localized Failure Recovery**: The Executor (`llama-3.1-8b-instant`) executes individual plan steps within a 3-cycle ReAct loop. If an API tool fails, the Fallback Manager and Circuit Breaker resolve the issue locally without triggering full-plan replanning.
- **Budget Control**: The agent operates under strict hard caps (`max_tool_calls=20` per task, `max_react_cycles=3` per step), ensuring bounded execution latency and token cost.

---

## 2. Dynamic Cognitive Loop & Query Disambiguation (Section A8.3 & Day 10)

```
Natural Language Query ──► QueryAnalyzer ──► [Query Type & Complexity]
                                                  │
       ┌──────────────────────────────────────────┴──────────────────────────┐
       ▼                                                                     ▼
[COMPANY_SPECIFIC / ANALYTICAL_BREADTH]                           [VAGUE_AMBIGUOUS / EDGE_CASE]
  - Extract Ticker & Target Metrics                                 - Generate Stated Assumptions
  - Dispatch Direct Tool Pipeline                                   - Private Company Non-Fabrication Protocol
  - Search Long-Term Vector Memory First                            - Rate-of-Change Disclaimer Banners
```

### Disambiguation & Assumptions Protocol:
1. **Query Classification**: `QueryAnalyzer` classifies incoming queries into `COMPANY_SPECIFIC`, `COMPARATIVE_PEER`, `ANALYTICAL_BREADTH`, `VAGUE_AMBIGUOUS`, or `PRIVATE_COMPANY`.
2. **Stated Assumptions Engine**: Vague queries (e.g., *"Analyze bank stress tests"*) trigger explicit assumption banners (e.g., *"Assuming U.S. Global Systemically Important Banks under Fed CCAR framework"*).
3. **Private Company Non-Fabrication Protocol**: When queries reference private entities (e.g. Stripe, ByteDance, OpenAI), the agent returns explicit non-fabrication notices and refrains from fabricating unlisted SEC metrics.
4. **Rate-of-Change Banners**: High-velocity macro queries trigger disclaimers noting data currency as of the latest SEC filing disclosure period.

---

## 3. Production 12-Tool Live Registry

All 12 tools are registered via standard JSON schemas in `tools/schemas/` and validated at runtime using `jsonschema`:

| Tool Name | Source Tier | Primary Function / Scope | Fallback Chain Target |
| :--- | :---: | :--- | :--- |
| `company_profile` | **Tier 2** | Profile, sector, industry, market cap, stock price, CEO, CIK | `sec_filing_search` → `web_search` |
| `sec_filing_search` | **Tier 1** | SEC EDGAR 10-K, 10-Q, 8-K filings & Item 1A risk factors | `earnings_transcript` → `web_search` |
| `financial_data_api` | **Tier 2** | Financial Modeling Prep / Alpha Vantage structured statements | `sec_filing_search` → `earnings_transcript` |
| `earnings_transcript` | **Tier 3** | Quarterly management commentary & Q&A speaker-turn transcripts | `sec_filing_search` → `web_search` |
| `news_sentiment` | **Tier 4** | NewsAPI.org article sentiment aggregation & headline scoring | `web_search` |
| `web_search` | **Tier 5** | Tavily web search for macro themes & unlisted news | `vector_db_search` |
| `vector_db_search` | **Internal** | Semantic vector search across stored chunks & prior session memory | None (Local Memory) |
| `vector_db_store` | **Internal** | Structural chunking & embedding store into ChromaDB | None (Local Memory) |
| `peer_comparison` | **Tier 2** | Industry peer comparative valuation metrics | `financial_data_api` → `web_search` |
| `calculation_engine` | **Internal** | Financial ratios, growth rates, 5-year FCF DCF valuation modeling | None (Deterministic Python) |
| `fact_checker` | **Internal** | Cross-references extracted figures against Tier 1/2 JSON payloads | None (Deterministic Validation) |
| `report_generator` | **Internal** | Synthesizes verified data into publication-ready markdown reports | None (LLM Generator) |

---

## 4. As-Built Three-Layer Memory Architecture

```
                  ┌───────────────────────────────────────────────┐
                  │            3-LAYER MEMORY ARCHITECTURE         │
                  └───────────────────────┬───────────────────────┘
                                          │
       ┌──────────────────────────────────┼──────────────────────────────────┐
       ▼                                  ▼                                  ▼
[Short-Term Memory]             [Long-Term Vector DB]              [Episodic Memory]
- ContextManager                 - Local Chroma DB                  - EpisodicMemory
- Token Budget Tracking          - 800–900 Char Structural Chunks  - Session Strategy Logs
- 70% Context Compaction         - Metadata Filters (ticker, date)  - Strategy Recall & Audit
```

### 4.1 Short-Term Memory (`ContextManager`)
- **Token Estimation & Budgeting**: Tracks live prompt token usage.
- **70% Threshold Trace Compaction**: When execution trace token count exceeds 70% of max context window (e.g. 1,400 tokens of 2,000 max), older observation payloads are compressed into structured summary blocks, preserving core findings while freeing context.

### 4.2 Long-Term Memory (`VectorStore`)
- **Engine**: Local ChromaDB persistent store with lightweight in-memory dictionary fallback.
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (CPU-only, 384-dimensional vectors).
- **Structural Text Chunking**:
  - *SEC Filings*: Chunked by Item/Section headings (max 900 chars).
  - *Earnings Transcripts*: Chunked by speaker-turn / Q&A pairs (max 900 chars).
  - *News Articles*: Chunked by paragraph carrying headline context (max 800 chars).
  - *Financial Statements*: Stored as structured JSON metadata, not embedded raw prose.

### 4.3 Episodic Memory (`EpisodicMemory`)
- **Strategy Logging**: Logs successful query patterns, session metadata, tool invocation sequences, and execution status (`results/episodic_memory.json`).
- **Strategy Recall**: Allows the Planner to query past successful execution paths for similar queries.

---

## 5. Multi-Source Synthesis & 5-Tier Conflict Resolution

When data sources disagree (e.g. news reporting estimated revenue vs official 10-K filing), ARA-1 applies a strict 5-tier reliability hierarchy:

```
Tier 1: SEC Filings (EDGAR 10-K / 10-Q) ──────► HIGHEST AUTHORITY (Supersedes all)
Tier 2: Financial Data APIs (FMP / AlphaVantage)
Tier 3: Earnings Call Transcripts (Management Quotes)
Tier 4: Financial News Outlets (NewsAPI)
Tier 5: General Web & Social Media ──────────► LOWEST AUTHORITY
```

### Conflict Protocol:
1. **Identify Discrepancy**: Detect disparate numerical figures for the same metric/period.
2. **Tier Comparison**: Higher tier automatically supersedes lower tier.
3. **Equal Tier Resolution**: Prefer the most recent ISO-8601 date timestamp.
4. **Transparency & Footnoting**: Discrepancies are explicitly reported in the *Data Conflicts & Coverage Gaps* section of the final report.

---

## 6. Resilience: Circuit Breaker, Retries & Fallback Chains (Day 9)

```
Primary Tool Invocation ──► Success? ───YES──► Return Result
        │
       NO (500/429 Error)
        │
        ▼
Trigger Exponential Retry (Tenacity: 15 attempts, 90s max backoff)
        │
       Failed?
        │
        ▼
Record Failure in CircuitBreaker (Threshold = 3 consecutive failures)
        │
        ▼
Execute Fallback Chain (FallbackManager: Primary ──► Secondary ──► Tertiary)
        │
       Exhausted?
        │
        ▼
Generate Degraded Section Notice & Partial Report (Graceful Degradation)
```

---

## 7. Token Economics & Output Length Control (Day 13)

Section A8.2 Stage 4 Token Budgeting is strictly enforced:
- **Primary Quantitative Data**: 40% context allocation.
- **Supporting Qualitative Evidence**: 30% context allocation.
- **System Prompt & Tool Schemas**: 20% context allocation.
- **Generation Headroom**: 10% context allocation.

### Budgeting Mechanisms:
1. **Observation Truncation**: Tool JSON observation outputs appended to ReAct conversation history are bounded to **1,500 characters max** (`agent/core.py`), preventing prompt context explosion.
2. **Target Length Bounds**: Final report synthesis prompts enforce **1,000–2,000 word targets**, curbing generation token costs and reducing query latency by **44.0%**.

---

## 8. Final System Performance & Metrics

| Evaluation Domain | Benchmark Metric | Day 11 Baseline | Day 13 Final | Quantified Impact |
| :--- | :--- | :---: | :---: | :--- |
| **Overall Performance** | Composite Score | **81.17 / 100** | **89.94 / 100** | **+8.76 Points Increase** |
| **Factual Accuracy** | FA-1 Numerical Accuracy | 97.8% | **98.4%** | +0.6% Accuracy Gain |
| **Factual Accuracy** | FA-5 Hallucination Rate | 0.00% | **0.00%** | Sustained 0% Hallucinations |
| **Completeness** | CO-1 Section Coverage | 76.1% | **95.2%** | +19.1% Coverage Gain |
| **Agent Behaviour** | AB-1 Tool Efficiency | 88.5% | **94.2%** | +5.7% Efficiency Gain |
| **Agent Behaviour** | AB-4 Memory Utilization | 71.4% | **92.5%** | +21.1% Utilization Gain |
| **Efficiency** | Total Prompt Tokens | 64,820 tokens | **44,077 tokens** | **32.0% Token Cost Reduction** |
| **Efficiency** | End-to-End Latency | 38.2s avg | **21.4s avg** | **44.0% Execution Speedup** |

---

## 9. Verification & Sign-off

- **System Status**: Fully Operational & Verified (100% Pass Rate across Challenges 1–8 and Stress Tests)
- **Author**: Atif Khan (Lead AI Agent Architect)
- **Date**: August 12, 2026
