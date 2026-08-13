import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Wrench, Shield, CheckCircle, Database, Sparkles, Cpu, Layers, Filter, Copy, Check } from 'lucide-react';
import { api, ToolItem } from '../lib/api';

export const ToolRegistryPage: React.FC = () => {
  const [selectedTier, setSelectedTier] = useState<string>('ALL');
  const [copiedTool, setCopiedTool] = useState<string | null>(null);

  const { data: tools, isLoading, isError } = useQuery<ToolItem[]>({
    queryKey: ['tools'],
    queryFn: api.getTools,
  });

  const handleCopySchema = (toolName: string, schema: any) => {
    navigator.clipboard.writeText(JSON.stringify(schema, null, 2));
    setCopiedTool(toolName);
    setTimeout(() => setCopiedTool(null), 2500);
  };

  const filteredTools = tools?.filter(t => {
    if (selectedTier === 'ALL') return true;
    return t.source_tier?.includes(selectedTier);
  });

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 shadow-glass-lg space-y-3 relative overflow-hidden">
        <div className="absolute -top-16 -right-16 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 font-bold shadow-glow-cyan">
            <Wrench className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Production 12-Tool Capability Registry
            </h1>
            <p className="text-slate-400 text-xs mt-0.5">
              Inspect registered multi-agent tools, OpenAI JSON schemas, parameter constraints, and 5-tier routing rules.
            </p>
          </div>
        </div>
      </div>

      {/* Tier Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        <span className="text-xs font-mono text-slate-400 flex items-center gap-1.5 mr-2 font-semibold">
          <Filter className="w-3.5 h-3.5 text-cyan-400" /> Source Tier:
        </span>
        {['ALL', 'Tier 1', 'Tier 2', 'Tier 3', 'Tier 4'].map(tier => (
          <button
            key={tier}
            onClick={() => setSelectedTier(tier)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all ${
              selectedTier === tier
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-glow-cyan'
                : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-white/10'
            }`}
          >
            {tier}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((n) => (
            <div key={n} className="h-48 glass-panel rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : isError ? (
        <div className="p-6 glass-panel rounded-2xl border border-red-500/30 text-red-300 text-sm">
          Failed to fetch tool registry from backend server.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredTools?.map((tool) => (
            <div key={tool.name} className="glass-panel-hover rounded-2xl p-6 space-y-4 flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <code className="text-sm font-bold text-cyan-300 font-mono bg-cyan-500/10 px-2.5 py-1 rounded-lg border border-cyan-500/30">
                    {tool.name}
                  </code>
                  <span className={`text-[10px] font-mono font-bold px-3 py-1 rounded-full border ${
                    tool.source_tier?.includes('1') ? 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40 shadow-glow-emerald' :
                    tool.source_tier?.includes('2') ? 'bg-cyan-950/80 text-cyan-300 border-cyan-500/40' :
                    'bg-slate-900 text-slate-300 border-white/10'
                  }`}>
                    {tool.source_tier}
                  </span>
                </div>

                <p className="text-slate-300 text-xs leading-relaxed font-sans">
                  {tool.description}
                </p>
              </div>

              <div className="bg-slate-950/90 p-3.5 rounded-xl border border-white/10 font-mono space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold text-slate-500">JSON Schema Signature</span>
                  <button
                    onClick={() => handleCopySchema(tool.name, tool.parameters)}
                    className="text-[10px] text-cyan-300 hover:text-cyan-200 flex items-center gap-1 font-bold bg-slate-900 px-2 py-0.5 rounded border border-white/10"
                  >
                    {copiedTool === tool.name ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    {copiedTool === tool.name ? 'Copied' : 'Copy Schema'}
                  </button>
                </div>
                <pre className="text-[11px] text-cyan-300 max-h-36 overflow-y-auto font-mono">
                  {JSON.stringify(tool.parameters?.properties || {}, null, 2)}
                </pre>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
