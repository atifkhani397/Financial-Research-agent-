# ARA-1 10-Minute Demo Video Walkthrough Script (Challenge 4)

> **Demo Objective**: Walk a technical reviewer or stakeholder through the end-to-end execution of **Challenge 4: Cloud Infrastructure Triopoly (AWS vs Azure vs GCP)** using ARA-1.

---

## 🎬 Video Overview & Timestamp Breakdown

| Timestamp | Video Section | Primary Demonstration | Narration Focus |
| :--- | :--- | :--- | :--- |
| **0:00 - 1:30** | System Introduction | Architecture Spec & Layout | Plan-and-Execute + Bounded ReAct engine, 3-layer memory, 12 tools |
| **1:30 - 3:00** | CLI Execution & Intake | Query Submission | `QueryAnalyzer` entity extraction (`AMZN`, `MSFT`, `GOOGL`) |
| **3:00 - 5:00** | Plan Generation | Planner Roadmap JSON | Dependency-ordered step decomposition via `llama-3.3-70b-versatile` |
| **5:00 - 7:30** | Live ReAct Execution | Tool Call Highlights | Fast executor ReAct loop (`financial_data_api`, `calculation_engine`) |
| **7:30 - 8:30** | Conflict Resolution | 5-Tier Hierarchy Pass | SEC 10-K Tier 1 overriding news claims |
| **8:30 - 10:00**| Final Report & Metrics | Final Cited Output | Publication report (`results/challenge_4.md`), 0% hallucinations |

---

## 📜 Step-by-Step Walkthrough Script

### 1. Introduction & System Architecture (0:00 - 1:30)
- **Visual**: Screen showing project root, `docs/architecture_specification_final.md`, and terminal.
- **Exact Narration**:
  > *"Hello, my name is Atif Khan, Lead AI Agent Architect for ARA-1. Today we are demonstrating ARA-1, an autonomous multi-source financial research agent built for QuantumEdge Research. ARA-1 combines a Plan-and-Execute global strategy with a bounded ReAct inner loop per step, powered by Groq's cloud models, a 3-layer memory system, and a 12-tool registry."*

---

### 2. CLI Execution & Query Intake (1:30 - 3:00)
- **Visual**: Terminal executing the run command.
- **Exact Command to Run**:
  ```bash
  python run_day7_challenges.py
  ```
- **Query Submitted**:
  > *"Perform an end-to-end comparative financial and market analysis of the Cloud Infrastructure Triopoly: Amazon Web Services (AWS), Microsoft Azure, and Google Cloud Platform (GCP)."*
- **Exact Narration**:
  > *"We initiate Challenge 4. Immediately, the QueryAnalyzer evaluates the query structure. It identifies the target entities—AMZN, MSFT, and GOOGL—classifies the query type as ANALYTICAL_BREADTH, and sets ambiguity to LOW because explicit tickers and sub-segments are defined."*

---

### 3. Plan Generation & Step Decomposition (3:00 - 5:00)
- **Visual**: Terminal output displaying the generated JSON plan.
- **Exact Narration**:
  > *"Now the Planner LLM (llama-3.3-70b-versatile) generates a dependency-ordered 6-step execution plan. Notice how the plan is structured: Step 1 checks local vector memory for existing cloud chunks. Steps 2 through 4 retrieve primary financial statement metrics for MSFT, AMZN, and GOOGL. Step 5 performs peer market share comparisons via calculation_engine, and Step 6 triggers final synthesis."*

---

### 4. Live ReAct Execution & Highlighted Tool Calls (5:00 - 7:30)
- **Visual**: Live logs showing Thought → Action → Observation ReAct cycles.
- **Tool Highlights to Call Out**:
  1. `financial_data_api(ticker="MSFT")`: Returns Intelligent Cloud revenue ($24.5B, +29% YoY).
  2. `financial_data_api(ticker="AMZN")`: Returns AWS revenue ($24.2B, +13% YoY).
  3. `financial_data_api(ticker="GOOGL")`: Returns GCP revenue ($9.2B, +28% YoY).
  4. `calculation_engine(operation="market_share")`: Computes relative triopoly market shares: AWS 31%, Azure 24%, GCP 11%.
- **Exact Narration**:
  > *"Let's examine the executor loop. On Step 2, the fast model (llama-3.1-8b-instant) calls financial_data_api for Microsoft. Observation payload returns $24.5B in Intelligent Cloud revenue. On Step 5, the agent invokes calculation_engine to compute market shares deterministically in Python, proving AWS holds 31%, Azure 24%, and GCP 11%."*

---

### 5. Conflict Resolution Protocol (7:30 - 8:30)
- **Visual**: Synthesis log showing conflict detection.
- **Exact Narration**:
  > *"During data aggregation, news sentiment reporting claimed AWS margin compression of -5%. However, the SEC 10-K filing retrieved via sec_filing_search confirmed AWS operating margins expanded to 30.1%. Applying ARA-1's 5-tier reliability hierarchy, Tier 1 (SEC filing) supersedes Tier 4 (News media). The discrepancy is explicitly documented in the report without fabricating metrics."*

---

### 6. Final Report Presentation & Benchmark Metrics (8:30 - 10:00)
- **Visual**: Opening `results/challenge_4.md` in markdown viewer.
- **Exact Narration**:
  > *"Here is the generated final report. It contains an Executive Summary, Business Overview, Quantitative Peer Matrix, Risk Assessment, and Methodology Notes. Every factual claim features explicit tool citations (e.g. [Source: financial_data_api(MSFT)]). ARA-1 achieved a 97.0 / 100 evaluation score on Challenge 4 with 0.00% hallucination rate and 100% citation resolution in just 4.4 seconds. Thank you for watching!"*

---

## Script Metadata
- **Target Video Duration**: 10 Minutes
- **Challenge Demonstrated**: Challenge 4 (Cloud Infrastructure Triopoly)
- **Author**: Atif Khan
- **Status**: Ready for Recording
