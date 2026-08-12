/**
 * ARA-1 Frontend API Client (Day 17)
 * Connects to Day 16 FastAPI backend server at http://localhost:8000
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface ChallengeItem {
  challenge_id: number;
  title: string;
  difficulty: string;
  query: string;
  expected_tools: string[];
}

export interface ToolItem {
  name: string;
  description: string;
  parameters: Record<string, any>;
  source_tier: string;
  usage_count: number;
}

export interface TraceEvent {
  timestamp: number;
  phase: 'PLAN' | 'THOUGHT' | 'ACTION' | 'OBSERVATION' | 'LIMIT' | 'SYNTHESIS' | 'COMPLETE' | string;
  step_id: number;
  cycle: number;
  tool_name?: string;
  content: string;
}

export interface ReportResponse {
  session_id: string;
  query: string;
  status: string;
  report_markdown: string;
  citations: string[];
  metadata: Record<string, any>;
}

export interface MemorySearchResponse {
  query: string;
  results: Array<{
    id: string;
    content: string;
    metadata: {
      ticker?: string;
      source_type?: string;
      date?: string;
      confidence?: number;
      verified?: boolean;
    };
  }>;
  count: number;
}

export interface EvaluationResponse {
  framework_version: string;
  composite_score: number;
  metrics_summary: Record<string, any>;
  challenge_scores: Array<{
    challenge_name: string;
    description: string;
    composite_score: number;
    factual_accuracy: Record<string, any>;
    completeness: Record<string, any>;
    agent_behaviour: Record<string, any>;
  }>;
}

export interface TraceGalleryItem {
  trace_id: string;
  title: string;
  query: string;
  session_id: string;
  highlights: string;
  annotations: {
    what_agent_did_well: string;
    what_could_improve: string;
  };
}

export const api = {
  async getHealth() {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error("API Offline");
    return res.json();
  },

  async getChallenges(): Promise<ChallengeItem[]> {
    const res = await fetch(`${API_BASE_URL}/api/challenges`);
    if (!res.ok) throw new Error("Failed to fetch challenges");
    return res.json();
  },

  async runChallenge(challengeId: number) {
    const res = await fetch(`${API_BASE_URL}/api/challenges/${challengeId}/run`, { method: 'POST' });
    if (!res.ok) throw new Error("Failed to run challenge");
    return res.json();
  },

  async submitQuery(query: string, customSessionId?: string) {
    const res = await fetch(`${API_BASE_URL}/api/research`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: customSessionId })
    });
    if (!res.ok) throw new Error("Failed to submit research query");
    return res.json();
  },

  async getReport(sessionId: string): Promise<ReportResponse> {
    const res = await fetch(`${API_BASE_URL}/api/research/${sessionId}/report`);
    if (!res.ok) throw new Error("Failed to fetch research report");
    return res.json();
  },

  async getTools(): Promise<ToolItem[]> {
    const res = await fetch(`${API_BASE_URL}/api/tools`);
    if (!res.ok) throw new Error("Failed to fetch tool registry");
    return res.json();
  },

  async searchMemory(query: string, topK: number = 5): Promise<MemorySearchResponse> {
    const res = await fetch(`${API_BASE_URL}/api/memory/search?q=${encodeURIComponent(query)}&top_k=${topK}`);
    if (!res.ok) throw new Error("Failed to search vector memory");
    return res.json();
  },

  async getEvaluation(): Promise<EvaluationResponse> {
    const res = await fetch(`${API_BASE_URL}/api/evaluation`);
    if (!res.ok) throw new Error("Failed to fetch evaluation metrics");
    return res.json();
  },

  async getTraces(): Promise<TraceGalleryItem[]> {
    const res = await fetch(`${API_BASE_URL}/api/traces`);
    if (!res.ok) throw new Error("Failed to fetch trace gallery");
    return res.json();
  }
};
