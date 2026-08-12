import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Wrench, Shield, CheckCircle, Database } from 'lucide-react';
import { api, ToolItem } from '../lib/api';

export const ToolRegistryPage: React.FC = () => {
  const { data: tools, isLoading, isError } = useQuery<ToolItem[]>({
    queryKey: ['tools'],
    queryFn: api.getTools,
  });

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-2">
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <Wrench className="w-6 h-6 text-blue-400" /> Production 12-Tool Registry Explorer
        </h1>
        <p className="text-slate-400 text-xs leading-relaxed">
          Inspect ARA-1's 12 registered tools, OpenAI JSON Schemas, parameter validation constraints, and 5-tier authoritative source classifications.
        </p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((n) => (
            <div key={n} className="h-40 bg-slate-900/50 border border-slate-800 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : isError ? (
        <div className="p-4 bg-red-950/30 border border-red-800 text-red-400 text-sm rounded-xl">
          Failed to load tool registry from backend API.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {tools?.map((tool) => (
            <div key={tool.name} className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <code className="text-sm font-bold text-blue-400 font-mono">{tool.name}</code>
                </div>
                <span className="text-[10px] font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  {tool.source_tier}
                </span>
              </div>

              <p className="text-slate-300 text-xs leading-relaxed">
                {tool.description}
              </p>

              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">JSON Schema Parameters</span>
                <pre className="text-[11px] font-mono text-emerald-400 overflow-x-auto">
                  {JSON.stringify(tool.parameters.properties || {}, null, 2)}
                </pre>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
