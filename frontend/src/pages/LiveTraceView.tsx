import React, { useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  Terminal, Activity, AlertTriangle, CheckCircle, RefreshCw, AlertOctagon, 
  FileText, ArrowRight, ShieldCheck, Sparkles 
} from 'lucide-react';
import { useWebSocketTrace } from '../hooks/useWebSocketTrace';
import { api, ReportResponse } from '../lib/api';

export const LiveTraceView: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const traceEndRef = useRef<HTMLDivElement | null>(null);

  const { traceEvents, isConnected, error: wsError } = useWebSocketTrace(sessionId || null);

  // Poll report status every 3 seconds
  const { data: reportData } = useQuery<ReportResponse>({
    queryKey: ['report', sessionId],
    queryFn: () => api.getReport(sessionId!),
    enabled: !!sessionId,
    refetchInterval: (query) => (query.state.data?.status === 'completed' ? false : 3000),
  });

  const isCompleted = reportData?.status === 'completed';

  // Auto-scroll to bottom of trace stream
  useEffect(() => {
    traceEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [traceEvents]);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Session Header Status */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono px-2.5 py-0.5 rounded-full bg-slate-800 text-blue-400 border border-slate-700">
              Session: {sessionId}
            </span>
            <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-0.5 rounded-full ${
              isConnected ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-amber-950 text-amber-400 border border-amber-800'
            }`}>
              <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
              {isConnected ? 'Live WebSocket Active' : 'Connecting Stream...'}
            </span>
          </div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Terminal className="w-5 h-5 text-blue-400" /> Live Cognitive Reasoning & Tool Execution Stream
          </h2>
        </div>

        {isCompleted && (
          <button
            onClick={() => navigate(`/report/${sessionId}`)}
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-medium rounded-lg shadow-lg flex items-center gap-2 text-sm transition-all animate-bounce"
          >
            <FileText className="w-4 h-4" /> View Finished Report <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Trace Stream Container */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-2xl space-y-4 min-h-[500px] max-h-[700px] overflow-y-auto font-mono text-xs">
        {wsError && (
          <div className="p-4 bg-red-950/40 border border-red-800/60 rounded-lg text-red-300 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-red-400" /> {wsError}
          </div>
        )}

        {traceEvents.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500 space-y-3">
            <Activity className="w-8 h-8 animate-spin text-blue-500" />
            <p className="text-sm">Initiating ARA-1 cognitive reasoning loop...</p>
            <p className="text-xs text-slate-600 font-sans">Awaiting initial step decomposition from Planner (llama-3.3-70b-versatile)</p>
          </div>
        )}

        {traceEvents.map((ev, idx) => {
          const isFallback = ev.content.includes("Fallback") || ev.content.includes("confidence");
          const isCircuitOpen = ev.content.includes("OPEN") || ev.content.includes("Circuit Breaker");
          const isAction = ev.phase === 'ACTION';

          return (
            <div
              key={idx}
              className={`p-4 rounded-lg border transition-all ${
                isCircuitOpen
                  ? 'bg-red-950/20 border-red-800/60 text-red-200'
                  : isFallback
                  ? 'bg-amber-950/20 border-amber-800/60 text-amber-200'
                  : isAction
                  ? 'bg-slate-900 border-blue-500/30 text-slate-200'
                  : 'bg-slate-900/60 border-slate-800 text-slate-300'
              }`}
            >
              <div className="flex items-center justify-between pb-2 border-b border-slate-800/60 mb-2">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    ev.phase === 'PLAN' ? 'bg-purple-950 text-purple-300 border border-purple-800' :
                    ev.phase === 'ACTION' ? 'bg-blue-950 text-blue-300 border border-blue-800' :
                    ev.phase === 'OBSERVATION' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' :
                    'bg-slate-800 text-slate-300'
                  }`}>
                    {ev.phase}
                  </span>
                  {ev.tool_name && (
                    <span className="text-slate-400 font-bold text-xs">
                      Tool: <code className="text-blue-400">{ev.tool_name}</code>
                    </span>
                  )}
                  {isFallback && (
                    <span className="inline-flex items-center gap-1 text-[10px] bg-amber-950 text-amber-300 px-2 py-0.5 rounded border border-amber-800 font-bold">
                      <RefreshCw className="w-3 h-3 animate-spin" /> Day 9 Fallback Triggered (-0.15 Conf)
                    </span>
                  )}
                  {isCircuitOpen && (
                    <span className="inline-flex items-center gap-1 text-[10px] bg-red-950 text-red-300 px-2 py-0.5 rounded border border-red-800 font-bold">
                      <AlertOctagon className="w-3 h-3" /> Circuit Breaker OPEN
                    </span>
                  )}
                </div>
                <span className="text-[10px] text-slate-500">
                  Step {ev.step_id} | Cycle {ev.cycle}
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
