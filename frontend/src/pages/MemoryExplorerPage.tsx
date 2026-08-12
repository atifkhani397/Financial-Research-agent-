import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Database, Search, Tag, Calendar, CheckCircle } from 'lucide-react';
import { api, MemorySearchResponse } from '../lib/api';

export const MemoryExplorerPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('cloud revenue');
  const [activeQuery, setActiveQuery] = useState('cloud revenue');

  const { data, isLoading, isError } = useQuery<MemorySearchResponse>({
    queryKey: ['memory', activeQuery],
    queryFn: () => api.searchMemory(activeQuery, 5),
    enabled: !!activeQuery,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) setActiveQuery(searchTerm.trim());
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-2">
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <Database className="w-6 h-6 text-blue-400" /> Long-Term Vector Memory Explorer (ChromaDB)
        </h1>
        <p className="text-slate-400 text-xs leading-relaxed">
          Perform semantic similarity vector searches across 800–900 character structural chunks of SEC filings, earnings call transcripts, and news articles stored in ChromaDB.
        </p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search semantic memory (e.g. AWS Intelligent Cloud revenue)..."
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-10 pr-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <button
          type="submit"
          className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg text-xs shadow-md"
        >
          Search Memory
        </button>
      </form>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-28 bg-slate-900/50 border border-slate-800 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : isError ? (
        <div className="p-4 bg-red-950/30 border border-red-800 text-red-400 text-xs rounded-xl">
          Failed to search vector memory.
        </div>
      ) : (
        <div className="space-y-4">
          <div className="text-xs text-slate-400 flex items-center justify-between">
            <span>Query: <code className="text-blue-400">{data?.query}</code></span>
            <span>{data?.count || 0} Chunks Retrieved</span>
          </div>

          {data?.results.length === 0 ? (
            <div className="p-8 text-center bg-slate-900 border border-slate-800 rounded-xl text-slate-500 text-xs">
              No matching vector chunks found in ChromaDB store for this query.
            </div>
          ) : (
            data?.results.map((item, idx) => (
              <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {item.metadata.ticker && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-bold">
                        {item.metadata.ticker}
                      </span>
                    )}
                    {item.metadata.source_type && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        {item.metadata.source_type}
                      </span>
                    )}
                  </div>
                  {item.metadata.confidence && (
                    <span className="text-[10px] text-emerald-400 font-semibold flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" /> Score: {(item.metadata.confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>

                <p className="text-xs text-slate-300 font-mono bg-slate-950 p-3 rounded-lg border border-slate-800 leading-relaxed whitespace-pre-wrap">
                  {item.content}
                </p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
