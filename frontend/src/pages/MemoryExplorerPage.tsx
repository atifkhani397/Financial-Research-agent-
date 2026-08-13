import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Database, Search, Tag, Calendar, CheckCircle, Sparkles, Layers, Sliders } from 'lucide-react';
import { api, MemorySearchResponse } from '../lib/api';

export const MemoryExplorerPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('cloud revenue');
  const [activeQuery, setActiveQuery] = useState('cloud revenue');
  const [minScore, setMinScore] = useState<number>(0.60);

  const { data, isLoading, isError } = useQuery<MemorySearchResponse>({
    queryKey: ['memory', activeQuery],
    queryFn: () => api.searchMemory(activeQuery, 6),
    enabled: !!activeQuery,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) setActiveQuery(searchTerm.trim());
  };

  const filteredResults = data?.results.filter(item => {
    const score = item.metadata?.confidence || 0.85;
    return score >= minScore;
  });

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 shadow-glass-lg space-y-3 relative overflow-hidden">
        <div className="absolute -top-16 -right-16 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400 font-bold shadow-glow-purple">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Long-Term Vector Memory Store (ChromaDB)
            </h1>
            <p className="text-slate-400 text-xs mt-0.5">
              Execute vector similarity searches over 800–900 character structural chunks of SEC filings and earnings transcripts.
            </p>
          </div>
        </div>
      </div>

      {/* Search Input Box & Slider Controls */}
      <div className="glass-panel p-4 rounded-2xl border border-white/15 shadow-glass-lg space-y-4">
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-3.5 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search semantic memory (e.g. AWS Intelligent Cloud revenue)..."
              className="w-full glass-input rounded-xl pl-11 pr-4 py-3 text-white text-xs font-medium focus:ring-2 focus:ring-cyan-500/50"
            />
          </div>
          <button
            type="submit"
            className="px-6 py-3 bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white font-bold rounded-xl text-xs shadow-glow-purple shrink-0 transition-all"
          >
            Search Vector Store
          </button>
        </form>

        {/* Interactive Threshold Slider */}
        <div className="pt-3 border-t border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 text-slate-300 font-semibold">
            <Sliders className="w-4 h-4 text-cyan-400" /> Minimum Similarity Threshold:
            <span className="font-mono text-cyan-300 bg-cyan-950 px-2 py-0.5 rounded border border-cyan-500/30">
              {(minScore * 100).toFixed(0)}%
            </span>
          </div>
          <input
            type="range"
            min="0.50"
            max="0.95"
            step="0.05"
            value={minScore}
            onChange={(e) => setMinScore(parseFloat(e.target.value))}
            className="w-full sm:w-48 accent-cyan-400 cursor-pointer"
          />
        </div>
      </div>

      {/* Search Results Display */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-36 glass-panel rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : isError ? (
        <div className="p-6 glass-panel rounded-2xl border border-red-500/30 text-red-300 text-sm">
          Failed to query ChromaDB vector store.
        </div>
      ) : (
        <div className="space-y-4">
          <div className="text-xs font-mono text-slate-400 flex items-center justify-between px-1">
            <span>Query Vector: <code className="text-cyan-300 font-bold">{data?.query}</code></span>
            <span className="bg-slate-900 px-3 py-1 rounded-full border border-white/10 text-emerald-400 font-bold">
              {filteredResults?.length || 0} Chunks Matched
            </span>
          </div>

          {!filteredResults || filteredResults.length === 0 ? (
            <div className="p-12 text-center glass-panel rounded-2xl border border-white/10 text-slate-400 text-xs">
              No vector chunks met the selected {(minScore * 100).toFixed(0)}% similarity threshold for this query.
            </div>
          ) : (
            filteredResults.map((item, idx) => {
              const score = item.metadata?.confidence || 0.88;
              return (
                <div key={idx} className="glass-panel-hover rounded-2xl p-6 space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      {item.metadata?.ticker && (
                        <span className="text-[10px] font-mono px-2.5 py-1 rounded-lg bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 font-bold">
                          {item.metadata.ticker}
                        </span>
                      )}
                      {item.metadata?.source_type && (
                        <span className="text-[10px] font-mono px-2.5 py-1 rounded-lg bg-slate-900 text-slate-300 border border-white/10">
                          {item.metadata.source_type}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="w-32 bg-slate-950 h-2 rounded-full overflow-hidden border border-white/10">
                        <div 
                          className="bg-gradient-to-r from-cyan-400 to-emerald-400 h-full" 
                          style={{ width: `${(score * 100).toFixed(0)}%` }}
                        />
                      </div>
                      <span className="text-[11px] font-mono text-emerald-400 font-bold bg-emerald-950/80 px-2.5 py-1 rounded-md border border-emerald-500/30">
                        {(score * 100).toFixed(1)}% Match
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-200 font-mono bg-slate-950/90 p-4 rounded-xl border border-white/10 leading-relaxed whitespace-pre-wrap">
                    {item.content}
                  </p>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
};
