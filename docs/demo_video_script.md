# ARA-1 Comprehensive Demo Video Walkthrough Script (CLI + Web UI)

> **Demo Objective**: Walk a technical reviewer or non-technical stakeholder through the end-to-end execution of **Challenge 4: Cloud Infrastructure Triopoly (AWS vs Azure vs GCP)** using both the graded Section D3 CLI engine and the additive React/FastAPI Web UI.

---

## 🎬 Section 1: Graded Section D3 CLI Engine Walkthrough (0:00 - 10:00)

| Timestamp | Video Section | Primary Demonstration | Narration Focus |
| :--- | :--- | :--- | :--- |
| **0:00 - 1:30** | System Introduction | Architecture Spec & Layout | Plan-and-Execute + Bounded ReAct engine, 3-layer memory, 12 tools |
| **1:30 - 3:00** | CLI Execution & Intake | Query Submission | `QueryAnalyzer` entity extraction (`AMZN`, `MSFT`, `GOOGL`) |
| **3:00 - 5:00** | Plan Generation | Planner Roadmap JSON | Dependency-ordered step decomposition via `llama-3.3-70b-versatile` |
| **5:00 - 7:30** | Live ReAct Execution | Tool Call Highlights | Fast executor ReAct loop (`financial_data_api`, `calculation_engine`) |
| **7:30 - 8:30** | Conflict Resolution | 5-Tier Hierarchy Pass | SEC 10-K Tier 1 overriding news claims |
| **8:30 - 10:00**| Final Report & Metrics | Final Cited Output | Publication report (`results/challenge_4.md`), 0% hallucinations |

---

### CLI Script Breakdown

#### 1. Introduction & System Architecture (0:00 - 1:30)
- **Visual**: Screen showing project root, `docs/architecture_specification_final.md`, and terminal.
- **Exact Narration**:
  > *"Hello, my name is Atif Khan, Lead AI Agent Architect for ARA-1. Today we are demonstrating ARA-1, an autonomous multi-source financial research agent built for QuantumEdge Research. ARA-1 combines a Plan-and-Execute global strategy with a bounded ReAct inner loop per step, powered by Groq's cloud models, a 3-layer memory system, and a 12-tool registry."*

#### 2. CLI Execution & Query Intake (1:30 - 3:00)
- **Visual**: Terminal executing the run command.
- **Exact Command**:
  ```bash
  python run_day7_challenges.py
  ```
- **Exact Narration**:
  > *"We initiate Challenge 4. Immediately, the QueryAnalyzer evaluates the query structure. It identifies target entities—AMZN, MSFT, and GOOGL—classifies query type as ANALYTICAL_BREADTH, and sets ambiguity to LOW because explicit tickers and sub-segments are defined."*

#### 3. Plan Generation & Execution (3:00 - 7:30)
- **Visual**: Live logs showing Thought → Action → Observation ReAct cycles.
- **Exact Narration**:
  > *"The Planner LLM drafts a 6-step roadmap. On Step 2, the fast model calls financial_data_api for Microsoft. Payload returns $24.5B in Intelligent Cloud revenue. On Step 5, the agent invokes calculation_engine to compute market shares deterministically in Python, proving AWS holds 31%, Azure 24%, and GCP 11%."*

#### 4. Conflict Resolution & Report Output (7:30 - 10:00)
- **Visual**: Final report rendered in terminal and saved to `results/challenge_4.md`.
- **Exact Narration**:
  > *"During data aggregation, SEC EDGAR 10-K disclosures (Tier 1) superseded media margin compression rumors (Tier 4). ARA-1 achieved a 97.0 / 100 evaluation score on Challenge 4 with 0.00% hallucination rate and 100% citation resolution in just 4.4 seconds."*

---

## 🌐 Section 2: Interactive Web UI Walkthrough (Additive Layer, 10:00 - 15:00)

| Timestamp | Web UI Section | Feature Visualized | Key Visual Highlights |
| :--- | :--- | :--- | :--- |
| **10:00 - 11:00**| Web Launch & Console | Query Console Page (`http://localhost:5173`) | 8 Predefined Challenge Cards, Live API Online badge |
| **11:00 - 12:30**| Real-Time Trace Streaming| Live Trace View (`/trace/:sessionId`) | WebSocket stream, color-coded tool cards (clean vs fallback vs circuit breaker) |
| **12:30 - 13:30**| Report & Conflict Panel | Report Viewer Page (`/report/:sessionId`) | Interactive citations, 5-Tier Conflict Resolution Panel |
| **13:30 - 15:00**| Analytics & Gallery | Evaluation Dashboard & Trace Gallery | Recharts score gains, expandable curated reasoning traces |

---

### Web UI Script Breakdown

#### 1. Web Launch & Query Console (10:00 - 11:00)
- **Visual**: Browser displaying `http://localhost:5173` (React 18 / Tailwind UI).
- **Exact Command**:
  ```bash
  docker compose up  # OR uvicorn api.main:app + npm run dev
  ```
- **Exact Narration**:
  > *"Now we transition to the Web Layer. Here on the Query Console home page, users can submit free-text queries or click any of the 8 Section B2 benchmark challenge cards. We click Challenge 4 (Cloud Triopoly)."*

#### 2. Real-Time WebSocket Trace Streaming (11:00 - 12:30)
- **Visual**: Navigating to `/trace/challenge-4` showing real-time streaming cards.
- **Exact Narration**:
  > *"As the agent executes, the Live Trace View streams Thought/Action/Observation events in real time over WebSockets. Clean tool calls display in blue, Day 9 Fallback hops highlight in amber with confidence penalties (-0.15), and tripped circuit breakers display in red."*

#### 3. Report Viewer & Conflict Panel (12:30 - 13:30)
- **Visual**: Viewing finished report page `/report/challenge-4`.
- **Exact Narration**:
  > *"Once complete, the Report Viewer renders the publication report with interactive citation badges. Above the report is the dedicated Multi-Source Conflict Resolution Panel, explicitly showing how SEC EDGAR 10-K Tier 1 disclosures superseded news media claims."*

#### 4. Evaluation Dashboard & Trace Gallery (13:30 - 15:00)
- **Visual**: Switching tabs to `/evaluation` and `/traces`.
- **Exact Narration**:
  > *"Finally, the Evaluation Dashboard renders Recharts score trends (+8.76 composite score gain, 32% token savings, 0% hallucinations), while the Trace Gallery allows reviewers to expand and annotate curated agent reasoning traces."*

---

## Script Metadata
- **Total Video Duration**: 15 Minutes (10-Min CLI + 5-Min Web UI)
- **Author**: Atif Khan
- **Status**: Production Final Script
