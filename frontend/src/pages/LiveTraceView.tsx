import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  Terminal, Activity, AlertTriangle, CheckCircle, RefreshCw, AlertOctagon, 
  FileText, ArrowRight, ShieldCheck, Sparkles, Cpu, Layers, Zap, Filter, Play
} from 'lucide-react';
import { useWebSocketTrace } from '../hooks/useWebSocketTrace';
import { api, ReportResponse, TraceEvent } from '../lib/api';

const MOCK_DEMO_TRACES: TraceEvent[] = [
  {
    timestamp: Date.now() - 12000,
    phase: 'PLAN',
    step_id: 1,
    cycle: 1,
    content: "Decomposing natural language query: 'NVIDIA (NVDA) FY24 10-K & CapEx ROI'. Formulating 4-step multi-agent roadmap:\n1. Execute Tier 1 SEC Edgar Filing Search (Form 10-K CIK 0001045810)\n2. Retrieve Income Statement & Balance Sheet metrics from Financial Modeling Prep API\n3. Execute ChromaDB vector memory query for AI GPU CapEx ROI disclosures\n4. Synthesize final valuation report with 100% verified citations."
  },
  {
    timestamp: Date.now() - 9000,
    phase: 'ACTION',
    step_id: 2,
    cycle: 1,
    tool_name: 'sec_filing_search',
    content: "Executing Tool: `sec_filing_search` with parameters: {\"ticker\": \"NVDA\", \"form_type\": \"10-K\", \"year\": 2024}\nStatus: HTTP 200 OK. Retrieved 10-K filing document (Item 7. MD&A). Total revenue: $60.92B (+126% YoY). Data Center revenue: $47.50B."
  },
  {
    timestamp: Date.now() - 6000,
    phase: 'OBSERVATION',
    step_id: 3,
    cycle: 2,
    tool_name: 'vector_db_search',
    content: "Executing Tool: `vector_db_search` with parameters: {\"query\": \"NVDA Blackwell GPU CapEx ROI\", \"top_k\": 3}\nMatched 3 structural chunks in ChromaDB vector store. Similarity confidence score: 94.2%. Statutory disclosures confirm zero supply bottleneck for Q4 FY25."
  },
  {
    timestamp: Date.now() - 3000,
    phase: 'SYNTHESIS',
    step_id: 4,
    cycle: 2,
    tool_name: 'report_generator',
    content: "Executing Tool: `report_generator`. Synthesizing executive report markdown. Verifying 5-tier source hierarchy: Tier 1 SEC disclosures supercede Tier 4 media speculation. Hallucination Guardrails: 100% Enforced."
  }
];

export const LiveTraceView: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const traceEndRef = useRef<HTMLDivElement | null>(null);
  const [filterPhase, setFilterPhase] = useState<string>('ALL');

  const isRealSession = !!sessionId && sessionId !== 'live-active-session' && sessionId !== 'demo';

  const { traceEvents: liveEvents, isConnected, error: wsError } = useWebSocketTrace(isRealSession ? sessionId : null);

  // Use live WebSocket events for real sessions (never show mock data for real sessions)
  const traceEvents = isRealSession ? liveEvents : MOCK_DEMO_TRACES;
  const isWaitingForEvents = isRealSession && liveEvents.length === 0;

  // Poll report status every 3 seconds
  const { data: reportData } = useQuery<ReportResponse>({
    queryKey: ['report', sessionId],
    queryFn: () => api.getReport(sessionId!),
    enabled: isRealSession,
    refetchInterval: (query) => (query.state.data?.status === 'completed' ? false : 3000),
  });

  const isCompleted = reportData?.status === 'completed' || !isRealSession;

  // Auto-scroll to bottom of trace stream
  useEffect(() => {
    traceEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [traceEvents]);

  // Calculate live progress steps
  const steps = [
    { label: 'Decompose Intent', done: traceEvents.length > 0 },
    { label: 'Tier 1 SEC Routing', done: traceEvents.some(e => e.phase === 'ACTION') },
    { label: 'Fact Verification', done: traceEvents.some(e => e.phase === 'OBSERVATION') },
    { label: 'Synthesize Report', done: isCompleted },
  ];

  const filteredEvents = traceEvents.filter(ev => {
    if (filterPhase === 'ALL') return true;
    if (filterPhase === 'FALLBACK') return ev.content.includes("Fallback") || ev.content.includes("confidence");
    return ev.phase === filterPhase;
  });

  return (
    <div className="space-y-6">
      {/* Session Header Status */}
      <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-glass-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="space-y-2 relative z-10">
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-xs font-mono font-bold px-3 py-1 rounded-lg bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-glow-cyan">
              Session: {isRealSession ? sessionId : 'demo-live-preview'}
            </span>
            <span className={`inline-flex items-center gap-2 text-xs font-mono font-semibold px-3 py-1 rounded-full border ${
              isRealSession && isConnected ? 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40 shadow-glow-emerald' : 'bg-cyan-950/80 text-cyan-300 border-cyan-500/40'
            }`}>
              <span className={`w-2 h-2 rounded-full ${isRealSession && isConnected ? 'bg-emerald-400 animate-ping' : 'bg-cyan-400'}`} />
              {isRealSession ? (isConnected ? 'Live WebSocket Active' : 'Connecting Stream...') : 'Live Demo Trace Stream'}
            </span>
            <span className="inline-flex items-center gap-1.5 text-xs font-mono font-semibold px-3 py-1 rounded-full bg-slate-900/80 text-amber-300 border border-amber-500/30">
              <Activity className="w-3.5 h-3.5 text-amber-400 animate-pulse" /> Est. Time: 3–6 mins (20m Max Timeout)
            </span>
          </div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2.5">
            <Terminal className="w-5 h-5 text-cyan-400" /> Live Cognitive Reasoning & Tool Execution Stream
          </h2>
        </div>

        <button
          onClick={() => navigate(isRealSession ? `/report/${sessionId}` : '/report')}
          className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-white font-bold rounded-xl shadow-glow-emerald flex items-center gap-2.5 text-sm transition-all duration-300 animate-bounce hover:scale-105 shrink-0 relative z-10"
        >
          <FileText className="w-4 h-4" /> View Finished Report <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Explanation Banner */}
      {!isRealSession && (
        <div className="p-4 bg-cyan-950/40 border border-cyan-500/30 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 text-cyan-300 font-medium">
            <Sparkles className="w-4 h-4 text-cyan-400 shrink-0" />
            <span>Showing interactive demonstration trace stream. Launch a query from the <strong>Console</strong> to stream live WebSocket execution events in real time.</span>
          </div>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-teal-500 text-white font-bold rounded-xl shadow-glow-cyan flex items-center gap-1.5 shrink-0"
          >
            <Play className="w-3.5 h-3.5 fill-current" /> Launch Real Query
          </button>
        </div>
      )}

      {/* Progress Step Pipeline */}
      <div className="glass-panel p-4 rounded-2xl border border-white/10 flex flex-col sm:flex-row items-center justify-between gap-3">
        {steps.map((step, idx) => (
          <React.Fragment key={idx}>
            <div className="flex items-center gap-2.5">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-mono font-bold transition-all ${
                step.done 
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 shadow-glow-emerald' 
                  : idx === 0 || steps[idx-1]?.done 
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 animate-pulse' 
                  : 'bg-slate-900 text-slate-600 border border-white/5'
              }`}>
                {step.done ? <CheckCircle className="w-4 h-4 text-emerald-400" /> : idx + 1}
              </div>
              <span className={`text-xs font-semibold ${step.done ? 'text-emerald-300' : 'text-slate-400'}`}>
                {step.label}
              </span>
            </div>
            {idx < steps.length - 1 && (
              <div className="hidden sm:block flex-1 h-[1px] bg-white/10 mx-2" />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Interactive Phase Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        <span className="text-xs font-mono text-slate-400 flex items-center gap-1.5 mr-2 font-semibold">
          <Filter className="w-3.5 h-3.5 text-cyan-400" /> Filter Stream:
        </span>
        {['ALL', 'PLAN', 'ACTION', 'OBSERVATION', 'SYNTHESIS'].map(phase => (
          <button
            key={phase}
            onClick={() => setFilterPhase(phase)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all ${
              filterPhase === phase
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-glow-cyan'
                : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-white/10'
            }`}
          >
            {phase}
          </button>
        ))}
      </div>

      {/* Trace Stream Container */}
      <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-glass-lg space-y-4 min-h-[450px] max-h-[650px] overflow-y-auto font-mono text-xs">
        {wsError && isRealSession && (
          <div className="p-4 bg-red-950/40 border border-red-500/40 rounded-xl text-red-300 flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 shrink-0 text-red-400" /> {wsError}
          </div>
        )}

        {isWaitingForEvents && !wsError && (
          <div className="flex flex-col items-center justify-center py-16 space-y-4">
            <div className="relative">
              <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin" />
              <Cpu className="w-5 h-5 text-cyan-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
            </div>
            <p className="text-sm text-slate-400 font-medium">Agent is initializing research pipeline...</p>
            <p className="text-xs text-slate-500">Live trace events will appear here as the agent reasons, executes tools, and synthesizes data.</p>
          </div>
        )}

        {filteredEvents.map((ev, idx) => {
          const isFallback = ev.content.includes("Fallback") || ev.content.includes("confidence");
          const isCircuitOpen = ev.content.includes("OPEN") || ev.content.includes("Circuit Breaker");
          const isAction = ev.phase === 'ACTION';

          return (
            <div
              key={idx}
              className={`p-4 rounded-xl border transition-all ${
                isCircuitOpen
                  ? 'bg-red-950/30 border-red-500/40 text-red-200'
                  : isFallback
                  ? 'bg-amber-950/30 border-amber-500/40 text-amber-200'
                  : isAction
                  ? 'bg-slate-900/90 border-cyan-500/40 text-slate-200 shadow-glow-cyan'
                  : 'bg-slate-950/60 border-white/10 text-slate-300'
              }`}
            >
              <div className="flex flex-wrap items-center justify-between pb-2.5 border-b border-white/10 mb-3 gap-2">
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`px-2.5 py-0.5 rounded-md text-[10px] font-bold ${
                    ev.phase === 'PLAN' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40' :
                    ev.phase === 'ACTION' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' :
                    ev.phase === 'OBSERVATION' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' :
                    'bg-slate-800 text-slate-300'
                  }`}>
                    {ev.phase}
                  </span>
                  {ev.tool_name && (
                    <span className="text-slate-300 font-bold text-xs flex items-center gap-1">
                      Tool: <code className="text-cyan-300 bg-slate-900 px-2 py-0.5 rounded border border-white/10">{ev.tool_name}</code>
                    </span>
                  )}
                  {isFallback && (
                    <span className="inline-flex items-center gap-1 text-[10px] bg-amber-950 text-amber-300 px-2 py-0.5 rounded border border-amber-800 font-bold">
                      <RefreshCw className="w-3 h-3 animate-spin" /> Fallback Hop (-0.15 Conf)
                    </span>
                  )}
                  {isCircuitOpen && (
                    <span className="inline-flex items-center gap-1 text-[10px] bg-red-950 text-red-300 px-2 py-0.5 rounded border border-red-800 font-bold">
                      <AlertOctagon className="w-3 h-3" /> Circuit Breaker OPEN
                    </span>
                  )}
                </div>
                <span className="text-[10px] text-slate-500 font-mono">
                  Step {ev.step_id} &bull; Cycle {ev.cycle}
                </span>
              </div>

              <div className="whitespace-pre-wrap leading-relaxed font-sans text-xs">
                {ev.content}
              </div>
            </div>
          );
        })}

        <div ref={traceEndRef} />
      </div>
    </div>
  );
};
