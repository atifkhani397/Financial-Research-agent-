# ARA-1 Architecture Specification

**Project Codename:** ARA-1 (Autonomous Research Agent)
**Role:** Lead AI Agent Architect
**Owner:** Atif Khan (QuantumEdge Research)

---

## 1. Executive Summary & Primary Agent Pattern

ARA-1 is designed to be an autonomous, highly reliable financial research agent capable of answering complex financial queries, synthesizing data from multiple authoritative sources, and gracefully handling API and tool failures.

### Primary Agent Pattern: Plan-and-Execute with ReAct Inner Loop
We have selected a **hybrid Plan-and-Execute architecture** with a **ReAct-style inner loop**. 

**Rationale:**
- **Why not pure ReAct?** Pure ReAct agents tend to get lost in long horizons, frequently making redundant tool calls or losing track of the original objective when distracted by intermediate findings. This violates the goal of high reliability and predictable token usage.
- **Why Plan-and-Execute?** A Plan-and-Execute pattern explicitly separates the *planning* phase (breaking a complex financial query into discrete, sequential steps) from the *execution* phase (running the steps). 
- **The Hybrid Advantage:** By combining Plan-and-Execute for the global strategy with a ReAct inner loop for the execution of individual steps, we get the best of both worlds. The Planner creates a deterministic roadmap (e.g., Step 1: Get SEC 10-K, Step 2: Get Earnings Transcript, Step 3: Compare). The Executor tackles each step using a ReAct loop to handle dynamic sub-tasks (e.g., retrieving, dealing with an API error, retrying, extracting data). This reduces redundant tool calls (aligning with Case Study 3's successful redesign) and makes error recovery highly localized and manageable.

---

## 2. Cognitive Loop & Flow Architecture

The cognitive loop dictates how a query traverses the ARA-1 system from intake to final report.

### Process Flow
1.  **Query Intake:** The user submits a natural language financial query.
2.  **Query Analysis & Disambiguation:** A fast LLM model (`llama-3.1-8b-instant`) analyzes the query to extract entities (tickers, dates, metrics) and disambiguates vague terms.
3.  **Retrieval-Strategy Classification:** The analyzer determines if the query requires *Precision* (e.g., "What was AAPL's Q3 revenue?") or *Breadth* (e.g., "Summarize market sentiment on AI stocks").
4.  **Planning Phase:** The larger reasoning model (`qwen3-32b` or `llama-3.3-70b-versatile`) drafts a step-by-step execution plan based on the classified strategy.
5.  **Execution (ReAct Inner Loop):** The executor processes each step, calling tools from the Tool Registry.
    -   *Resilience:* Incorporates exponential backoff and fallback chains.
6.  **Multi-Source Synthesis:** Data extracted from tools is aggregated. The 5-tier reliability hierarchy resolves conflicting data points.
7.  **Fact Verification Pass:** The `fact_checker` tool cross-references synthesized data against the highest-tier source available.
8.  **Report Generation:** The final markdown report is generated, complete with explicit citations.
9.  **Self-Reflection (Episodic Memory):** The system evaluates the session's success and logs successful strategies into episodic memory.

---

## 3. Tool Registry

ARA-1 features a robust registry of at least 12 tools, each strictly defined via an OpenAI-style JSON schema.

| Tool Name | Description | Source Tier |
| :--- | :--- | :--- |
| `sec_filing_search` | Searches SEC EDGAR for official filings (10-K, 10-Q). | Tier 1 |
| `financial_data_api` | Retrieves structured financial metrics (FMP / Alpha Vantage). | Tier 2 |
| `earnings_transcript`| Fetches management commentary from earnings calls. | Tier 3 |
| `news_sentiment` | Aggregates and scores sentiment from financial news. | Tier 4 |
| `web_search` | General search for macro trends (Tavily/SerpAPI). | Tier 5 |
| `vector_db_search` | Semantic search across previously chunked/stored findings. | Internal |
| `vector_db_store` | Embeds and stores new findings into Chroma. | Internal |
| `company_profile` | Retrieves static metadata about a company. | Tier 2 |
| `peer_comparison` | Fetches industry peers for relative valuation. | Tier 2 |
| `report_generator` | Formats verified data into the final structured report. | Internal |
| `fact_checker` | Verifies claims against the memory/source context. | Internal |
| `calculation_engine` | Performs safe math operations (ratios, growth rates). | Internal |

*(All external API tools implement a mock/stub mode for testing without keys).*

---

## 4. Memory Architecture

The memory system comprises three distinct layers, ensuring both context limits and long-term recall are managed efficiently.

### 4.1 Short-Term Memory (Context Window)
- **Function:** Tracks the live state of the current research session.
- **Compaction Strategy:** Once the token count approaches 70% of the model's limit, a background summarization agent compresses intermediate steps while retaining hard data and citations.

### 4.2 Long-Term Memory (Vector Database)
- **Technology:** Chroma (Local during dev, with documented migration to Pinecone/Qdrant).
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`.
- **Schema:** 
  - `id`: UUID
  - `content`: Chunked text
  - `embedding`: Float vector
  - `ticker`: e.g., "AAPL"
  - `source_type`: e.g., "SEC_10K"
  - `date`: ISO-8601
  - `confidence`: Float (0.0-1.0)
  - `verified`: Boolean
  - `researcher_session`: Session ID

### 4.3 Episodic Memory
- **Function:** A reflective log storing metadata on *how* queries were successfully solved. If a specific tool chain successfully answers a "merger arbitrage" query, this strategy is saved and retrieved for similar future queries, improving planning efficiency over time.

---

## 5. Multi-Source Synthesis & Conflict Resolution

In financial research, sources often disagree (e.g., a news article misquoting an earnings transcript). ARA-1 resolves this deterministically.

### 5-Tier Source Reliability Hierarchy
1.  **Tier 1:** SEC Filings (EDGAR) - *Highest Authority*
2.  **Tier 2:** Financial Data APIs
3.  **Tier 3:** Earnings Transcripts
4.  **Tier 4:** News Outlets
5.  **Tier 5:** Social/Forum Content - *Lowest Authority*

### Conflict Resolution Protocol
1.  **Detect:** The synthesis engine identifies disparate figures for the same metric.
2.  **Tier Check:** Compare the source tiers. 
3.  **Temporal/Restatement Check:** If tiers are equal, check dates (e.g., a restated 10-K supersedes the original).
4.  **Resolution:** Prefer the highest tier. If unresolved, the conflict is explicitly documented in the report, allowing the human to review it.
5.  **Transparency:** NEVER fabricate data. The final report must state: *"Source A claimed X, Source B claimed Y. Resolved to X due to Source A being an SEC filing."*

---

## 6. Error Handling Strategy

ARA-1 is designed for a simulated 50% tool-failure rate. It must degrade gracefully.

- **Exponential Backoff + Jitter:** For transient API errors (e.g., HTTP 429, 500). Wait time = `min(max_delay, base_delay * 2^attempt) + jitter`. Start at 1s, max 5 retries, max delay capped at 32s.
- **Fallback Chains:** Every primary tool has a fallback. 
  - *Example:* If `financial_data_api` fails after 5 retries, fallback to `sec_filing_search` to extract the metric manually. If that fails, fallback to `web_search`.
- **Circuit Breaker:** If a tool fails 3 consecutive times across different steps, it is marked as "OPEN" (unavailable) for the remainder of the session to prevent cascading timeouts.
- **Graceful Degradation:** If a mandatory data point cannot be retrieved, the report generator leaves a structured gap: *"Data unavailable due to API failure. Proceeding with qualitative analysis."*

---

## 7. Evaluation Framework

The agent will be scored using a 20+ metric framework across 5 categories.

1.  **Factual Accuracy (FA):** e.g., FA-1 (Zero hallucinations).
2.  **Completeness (CO):** Did the report address all parts of the query?
3.  **Analytical Depth (AD):** Quality of synthesis, not just regurgitation.
4.  **Coherence & Structure (CS):** Markdown validity, citation formatting.
5.  **Agent Behaviour (AB):** Efficiency. 
    - *Correction Note:* Metric AB-4 "Memory Utilization" will be explicitly implemented as a mathematically sound **ratio** (`memory_hits / total_api_calls`), overriding the brief's contradictory instruction to calculate it as a product.

*Evaluation LLM:* We will use an LLM-as-a-judge approach on Day 11, utilizing a different model than the generator (e.g., if generator is `qwen3-32b`, judge is `llama-3.3-70b-versatile`) to prevent self-grading bias.

---

## 8. Validation Plan (The 8 Progressive Challenges)

ARA-1 will be validated against 8 progressive challenges (Section B2) to prove end-to-end reliability.

- **Challenge 1 (1/5 difficulty):** Single company profile retrieval.
- **Challenge 2-3:** Time-series data and peer comparison.
- **Challenge 4-5:** Conflicting data resolution and multi-source synthesis.
- **Challenge 6-7:** Handling transient errors and invoking fallback chains.
- **Challenge 8 (5/5 difficulty):** Full investment report generation under a simulated 50% permanent tool-failure rate. Success requires the circuit breaker to activate and the report to degrade gracefully without hallucination.
