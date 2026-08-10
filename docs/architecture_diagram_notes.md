# ARA-1 Architecture Diagram Notes

*Note: These notes are formatted as a node/edge list for easy import into Excalidraw, draw.io, or Mermaid.*

## Nodes (Components)
- `N_User`: User Input (Query)
- `N_Analyzer`: Query Analyzer & Disambiguation (llama-3.1-8b-instant)
- `N_Planner`: Global Planner (qwen3-32b or llama-3.3-70b-versatile)
- `N_Executor`: ReAct Step Executor (Inner Loop)
- `N_ToolReg`: Tool Registry (12+ API/Mock Tools)
- `N_MemShort`: Short-Term Memory (Context & Compaction)
- `N_MemLong`: Long-Term Memory (Chroma Vector DB)
- `N_MemEpi`: Episodic Memory (Strategy Log)
- `N_Synth`: Synthesis & Conflict Resolution Engine
- `N_FactCheck`: Fact Checker & Verifier
- `N_ReportGen`: Report Generator
- `N_Output`: Final Research Report

## Edges (Flow & Interactions)
- `N_User` -> `N_Analyzer`: Submits natural language query
- `N_Analyzer` -> `N_Planner`: Passes parsed entities and retrieval strategy (Precision/Breadth)
- `N_Analyzer` <-> `N_MemEpi`: Queries past successful strategies for similar query types
- `N_Planner` -> `N_Executor`: Sends discrete execution step
- `N_Executor` -> `N_ToolReg`: Invokes specific tool via JSON schema
- `N_ToolReg` -> `N_Executor`: Returns raw observation/data (or triggers fallback/circuit breaker on error)
- `N_Executor` <-> `N_MemShort`: Reads/writes intermediate step context
- `N_Executor` <-> `N_MemLong`: Queries past findings / stores new embeddings
- `N_Executor` -> `N_Planner`: Reports step completion; asks for next step
- `N_Planner` -> `N_Synth`: Sends all aggregated step data once plan is complete
- `N_Synth` -> `N_FactCheck`: Sends synthesized draft for verification (applies 5-tier hierarchy)
- `N_FactCheck` -> `N_ReportGen`: Approves verified facts
- `N_ReportGen` -> `N_Output`: Emits final markdown with citations
- `N_Output` -> `N_MemEpi`: Logs successful session strategy

## Description of the Flow (for diagram caption)
**Plan-and-Execute with ReAct Inner Loop:**
The user's query is first parsed and disambiguated. A high-level Plan is generated based on historical success logs (Episodic Memory). The Executor takes one step of the plan at a time, entering a ReAct loop to interact with the Tool Registry. Tools have built-in retry and circuit-breaker logic. All intermediate states are stored in Short-Term Memory, while important factual chunks are embedded into the Chroma Long-Term Memory. Once the plan is fully executed, the Synthesis engine resolves conflicts using the 5-tier source hierarchy. A Fact Checker verifies the output before the Report Generator formats the final response.
