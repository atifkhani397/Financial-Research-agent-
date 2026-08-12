import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Layers, ChevronDown, ChevronUp, CheckCircle, AlertTriangle, Sparkles } from 'lucide-react';
import { api, TraceGalleryItem } from '../lib/api';

export const TraceGalleryPage: React.FC = () => {
  const [expandedId, setExpandedId] = useState<string | null>('trace-1-tsla-dcf');

  const { data: traces, isLoading, isError } = useQuery<TraceGalleryItem[]>({
    queryKey: ['traces'],
    queryFn: api.getTraces,
  });

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-2">
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <Layers className="w-6 h-6 text-blue-400" /> Curated Reasoning Trace Gallery (Section A8)
        </h1>
        <p className="text-slate-400 text-xs leading-relaxed">
          Inspect 6 annotated agent reasoning traces demonstrating clean DCF calculation, error-recovery fallback hops, source conflict resolution, 100% outage degradation, and vector memory recall.
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-32 bg-slate-900/50 border border-slate-800 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : isError ? (
        <div className="p-4 bg-red-950/30 border border-red-800 text-red-400 text-xs rounded-xl">
          Failed to load trace gallery.
        </div>
      ) : (
        <div className="space-y-4">
          {traces?.map((trace) => {
            const isExpanded = expandedId === trace.trace_id;
            return (
              <div key={trace.trace_id} className="bg-slate-900 border border-slate-800 rounded-xl shadow-xl overflow-hidden transition-all">
                <div
                  onClick={() => toggleExpand(trace.trace_id)}
                  className="p-5 cursor-pointer hover:bg-slate-800/50 flex items-center justify-between transition-colors"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-bold">
                        {trace.trace_id}
                      </span>
                      <h3 className="font-semibold text-slate-100 text-sm">{trace.title}</h3>
                    </div>
                    <p className="text-xs text-slate-400 line-clamp-1">{trace.highlights}</p>
                  </div>
                  {isExpanded ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                </div>

                {isExpanded && (
                  <div className="p-5 border-t border-slate-800 bg-slate-950 space-y-4 text-xs font-sans">
                    <div className="space-y-1">
                      <span className="text-[10px] uppercase font-bold text-slate-500">Query</span>
                      <p className="font-mono text-slate-300 bg-slate-900 p-2.5 rounded border border-slate-800">{trace.query}</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-3 bg-emerald-950/20 border border-emerald-800/40 rounded-lg space-y-1">
                        <span className="text-[11px] font-bold text-emerald-400 flex items-center gap-1">
                          <CheckCircle className="w-3.5 h-3.5" /> What Agent Did Well
                        </span>
                        <p className="text-slate-300 text-[11px] leading-relaxed">{trace.annotations.what_agent_did_well}</p>
                      </div>
                      <div className="p-3 bg-amber-950/20 border border-amber-800/40 rounded-lg space-y-1">
                        <span className="text-[11px] font-bold text-amber-400 flex items-center gap-1">
                          <AlertTriangle className="w-3.5 h-3.5" /> What Could Still Improve
                        </span>
                        <p className="text-slate-300 text-[11px] leading-relaxed">{trace.annotations.what_could_improve}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
