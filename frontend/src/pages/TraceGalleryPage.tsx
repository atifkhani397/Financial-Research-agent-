import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Layers, ChevronDown, ChevronUp, CheckCircle, AlertTriangle, Sparkles, Terminal, Activity, Filter } from 'lucide-react';
import { api, TraceGalleryItem } from '../lib/api';

export const TraceGalleryPage: React.FC = () => {
  const [expandedId, setExpandedId] = useState<string | null>('trace-1-tsla-dcf');
  const [filterTag, setFilterTag] = useState<string>('ALL');

  const { data: traces, isLoading, isError } = useQuery<TraceGalleryItem[]>({
    queryKey: ['traces'],
    queryFn: api.getTraces,
  });

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const filteredTraces = traces?.filter(t => {
    if (filterTag === 'ALL') return true;
    return t.trace_id.includes(filterTag.toLowerCase()) || t.title.toLowerCase().includes(filterTag.toLowerCase());
  });

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 shadow-glass-lg space-y-3 relative overflow-hidden">
        <div className="absolute -top-16 -right-16 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 font-bold shadow-glow-cyan">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Curated Reasoning Trace Gallery
            </h1>
            <p className="text-slate-400 text-xs mt-0.5">
              Inspect annotated reasoning traces showcasing DCF modeling, circuit breaker hops, and 100% outage fallback recovery.
            </p>
          </div>
        </div>
      </div>

      {/* Filter Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        <span className="text-xs font-mono text-slate-400 flex items-center gap-1.5 mr-2 font-semibold">
          <Filter className="w-3.5 h-3.5 text-cyan-400" /> Filter Traces:
        </span>
        {['ALL', 'DCF', 'Fallback', 'Outage', 'Conflict'].map(tag => (
          <button
            key={tag}
            onClick={() => setFilterTag(tag)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all ${
              filterTag === tag
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-glow-cyan'
                : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-white/10'
            }`}
          >
            {tag}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-32 glass-panel rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : isError ? (
        <div className="p-6 glass-panel rounded-2xl border border-red-500/30 text-red-300 text-sm">
          Failed to fetch trace gallery items from API.
        </div>
      ) : (
        <div className="space-y-4">
          {filteredTraces?.map((trace) => {
            const isExpanded = expandedId === trace.trace_id;
            return (
              <div 
                key={trace.trace_id} 
                className="glass-panel-hover rounded-2xl overflow-hidden transition-all duration-300"
              >
                <div
                  onClick={() => toggleExpand(trace.trace_id)}
                  className="p-6 cursor-pointer flex items-center justify-between transition-colors"
                >
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-lg bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                        {trace.trace_id}
                      </span>
                      <h3 className="font-bold text-slate-100 text-base">{trace.title}</h3>
                    </div>
                    <p className="text-xs text-slate-400 font-sans line-clamp-1">{trace.highlights}</p>
                  </div>
                  <div className="p-2 rounded-xl bg-slate-900 border border-white/10 text-slate-400">
                    {isExpanded ? <ChevronUp className="w-5 h-5 text-cyan-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                  </div>
                </div>

                {isExpanded && (
                  <div className="p-6 border-t border-white/10 bg-slate-950/90 space-y-5 text-xs">
                    <div className="space-y-1.5">
                      <span className="text-[10px] uppercase font-bold font-mono text-slate-500">Query Hypothesis</span>
                      <p className="font-mono text-slate-200 bg-slate-900/90 p-3.5 rounded-xl border border-white/10 leading-relaxed">
                        {trace.query}
                      </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-4 bg-emerald-950/40 border border-emerald-500/30 rounded-xl space-y-1.5">
                        <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                          <CheckCircle className="w-4 h-4" /> Agent Strength Highlights
                        </span>
                        <p className="text-slate-300 text-xs leading-relaxed font-sans">{trace.annotations.what_agent_did_well}</p>
                      </div>
                      <div className="p-4 bg-amber-950/40 border border-amber-500/30 rounded-xl space-y-1.5">
                        <span className="text-xs font-bold text-amber-300 flex items-center gap-1.5">
                          <AlertTriangle className="w-4 h-4 text-amber-400" /> Optimization Hops
                        </span>
                        <p className="text-slate-300 text-xs leading-relaxed font-sans">{trace.annotations.what_could_improve}</p>
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
