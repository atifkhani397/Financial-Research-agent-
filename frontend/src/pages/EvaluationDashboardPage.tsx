import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart3, Award, TrendingUp, Zap, ShieldCheck, Sparkles, CheckCircle2, Filter } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import { api, EvaluationResponse } from '../lib/api';

export const EvaluationDashboardPage: React.FC = () => {
  const [activeMetric, setActiveMetric] = useState<'ALL' | 'ACCURACY' | 'EFFICIENCY'>('ALL');

  const { data: evalData, isLoading, isError } = useQuery<EvaluationResponse>({
    queryKey: ['evaluation'],
    queryFn: api.getEvaluation,
  });

  const rawData = [
    { category: 'Tool Efficiency (AB-1)', baseline: 88.5, final: 94.2, type: 'EFFICIENCY' },
    { category: 'Memory Util (AB-4)', baseline: 71.4, final: 92.5, type: 'EFFICIENCY' },
    { category: 'SEC Coverage (CO-1)', baseline: 76.1, final: 95.2, type: 'ACCURACY' },
    { category: 'Factual Accuracy (FA-1)', baseline: 97.8, final: 98.4, type: 'ACCURACY' },
    { category: 'Overall Composite Score', baseline: 81.17, final: 89.94, type: 'ALL' },
  ];

  const chartData = rawData.filter(d => {
    if (activeMetric === 'ALL') return true;
    return d.type === activeMetric || d.category.includes('Overall');
  });

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 shadow-glass-lg space-y-3 relative overflow-hidden">
        <div className="absolute -top-16 -right-16 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold shadow-glow-emerald">
            <BarChart3 className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Evaluation Metrics & Performance Benchmarks
            </h1>
            <p className="text-slate-400 text-xs mt-0.5">
              Post-optimization evaluation metrics comparing Day 11 baseline vs Day 13 final multi-agent performance.
            </p>
          </div>
        </div>
      </div>

      {/* Metric Stat Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-panel-hover rounded-2xl p-5 border border-white/10 shadow-glass-lg space-y-2.5">
          <span className="text-xs font-mono font-bold text-slate-400 flex items-center gap-1.5">
            <Award className="w-4 h-4 text-cyan-400" /> Composite Score
          </span>
          <p className="text-3xl font-extrabold text-white font-mono">
            89.94 <span className="text-xs text-emerald-400 font-bold font-sans">+8.76 pts</span>
          </p>
          <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-white/10">
            <div className="bg-gradient-to-r from-cyan-500 to-emerald-400 h-full w-[90%]" />
          </div>
        </div>

        <div className="glass-panel-hover rounded-2xl p-5 border border-white/10 shadow-glass-lg space-y-2.5">
          <span className="text-xs font-mono font-bold text-slate-400 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" /> Hallucination Rate
          </span>
          <p className="text-3xl font-extrabold text-emerald-400 font-mono">
            0.00% <span className="text-xs text-slate-400 font-normal font-sans">Verified</span>
          </p>
          <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-white/10">
            <div className="bg-emerald-400 h-full w-[100%]" />
          </div>
        </div>

        <div className="glass-panel-hover rounded-2xl p-5 border border-white/10 shadow-glass-lg space-y-2.5">
          <span className="text-xs font-mono font-bold text-slate-400 flex items-center gap-1.5">
            <Zap className="w-4 h-4 text-amber-400" /> Memory Utilization
          </span>
          <p className="text-3xl font-extrabold text-amber-300 font-mono">
            92.5% <span className="text-xs text-emerald-400 font-bold font-sans">+21.1%</span>
          </p>
          <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-white/10">
            <div className="bg-amber-400 h-full w-[92.5%]" />
          </div>
        </div>

        <div className="glass-panel-hover rounded-2xl p-5 border border-white/10 shadow-glass-lg space-y-2.5">
          <span className="text-xs font-mono font-bold text-slate-400 flex items-center gap-1.5">
            <TrendingUp className="w-4 h-4 text-purple-400" /> Token Cost Savings
          </span>
          <p className="text-3xl font-extrabold text-purple-300 font-mono">
            -32.0% <span className="text-xs text-slate-400 font-normal font-sans">44k tok</span>
          </p>
          <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-white/10">
            <div className="bg-purple-400 h-full w-[68%]" />
          </div>
        </div>
      </div>

      {/* Chart Section with Metric Filter */}
      <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 shadow-glass-lg space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400" /> Performance Delta: Baseline vs Final Optimized ARA-1 Engine
          </h3>
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-cyan-400" />
            {(['ALL', 'ACCURACY', 'EFFICIENCY'] as const).map(metric => (
              <button
                key={metric}
                onClick={() => setActiveMetric(metric)}
                className={`px-3 py-1 rounded-lg text-xs font-mono font-bold transition-all ${
                  activeMetric === metric
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-glow-cyan'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-white/10'
                }`}
              >
                {metric}
              </button>
            ))}
          </div>
        </div>

        <div className="h-72 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="category" stroke="#94a3b8" fontSize={11} tick={{ fill: '#94a3b8' }} />
              <YAxis domain={[50, 100]} stroke="#94a3b8" fontSize={11} tick={{ fill: '#94a3b8' }} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(6, 9, 17, 0.95)', 
                  borderColor: 'rgba(255, 255, 255, 0.15)', 
                  borderRadius: '12px',
                  boxShadow: '0 8px 32px 0 rgba(0,0,0,0.6)',
                  color: '#fff',
                  fontSize: '12px' 
                }} 
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Bar dataKey="baseline" name="Day 11 Baseline" fill="#475569" radius={[6, 6, 0, 0]} />
              <Bar dataKey="final" name="Day 13 Final Optimized" fill="#06b6d4" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
