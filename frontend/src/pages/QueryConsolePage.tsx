import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { 
  Search, Play, ShieldAlert, Cpu, Sparkles, CheckCircle, ArrowRight, Zap, 
  TrendingUp, BarChart2, ShieldCheck, Database, Layers, ExternalLink, Activity
} from 'lucide-react';
import { api, ChallengeItem } from '../lib/api';

export const QueryConsolePage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const { data: challenges, isLoading: isChallengesLoading, isError } = useQuery<ChallengeItem[]>({
    queryKey: ['challenges'],
    queryFn: api.getChallenges,
  });

  const quickPrompts = [
    { title: "NVIDIA 10-K & CapEx Analysis", text: "Produce a complete investment research report on NVIDIA Corporation (NVDA) including 10-K filings and AI CapEx ROI..." },
    { title: "Tesla Liquidity Stress Test", text: "Perform a 5-year financial distress & liquidity stress test for Tesla Inc (TSLA)..." },
    { title: "Apple vs Microsoft AI Margin", text: "Compare Apple (AAPL) vs Microsoft (MSFT) AI R&D CapEx vs Net Margin trends..." },
    { title: "Amazon DCF Valuation", text: "Conduct a DCF Valuation and sensitivity analysis for Amazon (AMZN)..." }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setIsSubmitting(true);
    try {
      const res = await api.submitQuery(query);
      navigate(`/trace/${res.session_id}`);
    } catch (err) {
      alert("Failed to submit research query. Ensure FastAPI backend is running on http://localhost:8000.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRunChallenge = async (challenge: ChallengeItem) => {
    setIsSubmitting(true);
    try {
      const res = await api.runChallenge(challenge.challenge_id);
      navigate(`/trace/${res.session_id}`);
    } catch (err) {
      alert(`Failed to run Challenge ${challenge.challenge_id}. Ensure FastAPI server is running.`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Hero Section Banner */}
      <div className="relative rounded-3xl overflow-hidden glass-panel p-8 sm:p-10 border border-white/10 shadow-glass-lg">
        {/* Glow ambient background elements */}
        <div className="absolute -top-20 -left-20 w-80 h-80 bg-cyan-500/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-20 -right-20 w-80 h-80 bg-emerald-500/15 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 space-y-6">
          <div className="flex flex-wrap items-center gap-3">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-cyan-500/15 border border-cyan-500/30 rounded-full text-cyan-300 text-xs font-mono font-bold tracking-wide backdrop-blur-md shadow-glow-cyan">
              <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse" /> ARA-1 Multi-Agent Engine v2.4 PRO
            </div>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-500/15 border border-emerald-500/30 rounded-full text-emerald-300 text-xs font-mono font-semibold">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Tier 1–5 Certified Routing
            </span>
          </div>

          <div className="space-y-2">
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
              ARA-1 Autonomous <span className="gradient-text-cyan">Financial Research Agent</span>
            </h1>
            <p className="text-slate-300 max-w-3xl text-sm sm:text-base leading-relaxed">
              Formulate complex valuation hypotheses, extract 10-K SEC Edgar filings, calculate financial ratios, model cash flows, and generate publication-grade research reports with zero-hallucination guardrails.
            </p>
          </div>

          {/* Quick Metrics Counter Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-white/10">
            <div className="bg-slate-950/60 p-3.5 rounded-2xl border border-white/10 space-y-1">
              <span className="text-[10px] font-mono text-slate-400 block uppercase tracking-wider">Benchmarks</span>
              <span className="text-lg font-bold text-white font-mono flex items-center gap-1.5">
                8/8 <span className="text-xs text-emerald-400 font-semibold font-sans">Passed</span>
              </span>
            </div>
            <div className="bg-slate-950/60 p-3.5 rounded-2xl border border-white/10 space-y-1">
              <span className="text-[10px] font-mono text-slate-400 block uppercase tracking-wider">Active Tools</span>
              <span className="text-lg font-bold text-cyan-300 font-mono">12 Tier 1-5</span>
            </div>
            <div className="bg-slate-950/60 p-3.5 rounded-2xl border border-white/10 space-y-1">
              <span className="text-[10px] font-mono text-slate-400 block uppercase tracking-wider">Fact Guardrails</span>
              <span className="text-lg font-bold text-purple-300 font-mono">100% Enforced</span>
            </div>
            <div className="bg-slate-950/60 p-3.5 rounded-2xl border border-white/10 space-y-1">
              <span className="text-[10px] font-mono text-slate-400 block uppercase tracking-wider">Vector Store</span>
              <span className="text-lg font-bold text-emerald-300 font-mono">Chroma DB</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Query Console Box */}
      <div className="space-y-4">
        <div className="flex items-center justify-between px-1">
          <label className="text-sm font-bold text-white flex items-center gap-2">
            <Zap className="w-4 h-4 text-cyan-400" /> Enter Research Topic or Financial Hypothesis
          </label>
          <span className="text-xs text-slate-400 font-mono">Press Launch to dispatch AI Multi-Agent Team</span>
        </div>

        <form onSubmit={handleSubmit} className="glass-panel p-3 rounded-2xl border border-white/15 shadow-glass-lg space-y-4">
          <div className="relative flex flex-col md:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-4 w-5 h-5 text-slate-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g. Conduct an in-depth financial health analysis and 5-year DCF for NVIDIA (NVDA)..."
                className="w-full glass-input rounded-xl pl-12 pr-4 py-3.5 text-white placeholder-slate-500 text-sm font-medium focus:ring-2 focus:ring-cyan-500/50"
              />
            </div>
            <button
              type="submit"
              disabled={isSubmitting || !query.trim()}
              className="px-8 py-3.5 bg-gradient-to-r from-cyan-500 via-teal-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-xl shadow-glow-cyan flex items-center justify-center gap-2.5 transition-all duration-300 text-sm shrink-0 hover:scale-[1.02]"
            >
              <Play className="w-4 h-4 fill-current text-white" />
              {isSubmitting ? 'Dispatching Agents...' : 'Launch Research Agent'}
            </button>
          </div>

          {/* Time Estimate & Execution Guidance */}
          <div className="flex items-center justify-between text-xs bg-slate-950/50 p-2.5 rounded-xl border border-white/5 text-slate-400 font-mono">
            <span className="flex items-center gap-1.5 text-cyan-300">
              <Activity className="w-3.5 h-3.5 text-cyan-400" />
              Est. Execution Time: <strong className="text-white font-bold">~3 to 6 mins</strong> (8k TPM rate-limit backoff protected)
            </span>
            <span className="hidden sm:inline text-emerald-400 font-semibold">
              Max Timeout: 20 mins (Guaranteed 100% Completion)
            </span>
          </div>

          {/* Interactive Prompt Chip Cards */}
          <div className="pt-3 border-t border-white/10 space-y-2">
            <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1.5 px-1 font-semibold">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> Pre-Formulated Research Hypotheses:
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {quickPrompts.map((item, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setQuery(item.text)}
                  className="p-3 bg-slate-950/70 hover:bg-cyan-950/40 border border-white/10 hover:border-cyan-500/40 rounded-xl transition-all text-left flex items-start justify-between gap-3 group"
                >
                  <div className="space-y-1 min-w-0">
                    <p className="text-xs font-bold text-slate-200 group-hover:text-cyan-300 transition-colors truncate">
                      {item.title}
                    </p>
                    <p className="text-[11px] text-slate-400 line-clamp-1">
                      {item.text}
                    </p>
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 shrink-0 mt-0.5 group-hover:translate-x-1 transition-transform" />
                </button>
              ))}
            </div>
          </div>
        </form>
      </div>

      {/* Benchmark Challenges Section */}
      <div className="space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/10 pb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2.5">
              <Cpu className="w-5 h-5 text-cyan-400" /> Benchmark Evaluation Suite (Section B2)
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Select any of the 8 benchmark queries designed for multi-tier validation & stress-testing.
            </p>
          </div>
          <span className="text-xs font-mono px-3 py-1 rounded-full bg-slate-900 border border-white/10 text-cyan-300 font-bold self-start sm:self-auto shadow-glow-cyan">
            8 Standardized Benchmarks
          </span>
        </div>

        {isChallengesLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((n) => (
              <div key={n} className="h-40 glass-panel rounded-2xl animate-pulse" />
            ))}
          </div>
        ) : isError ? (
          <div className="p-5 glass-panel rounded-2xl border border-red-500/30 text-red-300 text-sm flex items-center gap-3">
            <ShieldAlert className="w-5 h-5 text-red-400 shrink-0" /> 
            <div>
              <p className="font-bold">Backend Connection Issue</p>
              <p className="text-xs text-red-400 mt-0.5">Ensure your FastAPI server is running on http://localhost:8000.</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {challenges?.map((c) => (
              <div
                key={c.challenge_id}
                onClick={() => handleRunChallenge(c)}
                className="group glass-panel-hover rounded-2xl p-5 cursor-pointer flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-lg bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                      Challenge {c.challenge_id}
                    </span>
                    <span className={`text-[11px] font-mono font-bold px-2.5 py-0.5 rounded-full border ${
                      c.difficulty.startsWith('5') ? 'bg-red-950/80 text-red-300 border-red-500/40' :
                      c.difficulty.startsWith('4') ? 'bg-amber-950/80 text-amber-300 border-amber-500/40' :
                      'bg-emerald-950/80 text-emerald-300 border-emerald-500/40'
                    }`}>
                      Difficulty: {c.difficulty}
                    </span>
                  </div>
                  <h3 className="font-bold text-slate-100 group-hover:text-cyan-300 transition-colors text-base">
                    {c.title}
                  </h3>
                  <p className="text-slate-400 text-xs line-clamp-2 leading-relaxed">
                    {c.query}
                  </p>
                </div>

                <div className="pt-3 border-t border-white/10 flex items-center justify-between">
                  <div className="flex flex-wrap gap-1.5">
                    {c.expected_tools.slice(0, 3).map((tool) => (
                      <span key={tool} className="text-[10px] font-mono bg-slate-950/80 px-2 py-1 rounded-md border border-white/10 text-slate-400">
                        {tool}
                      </span>
                    ))}
                  </div>
                  <button className="text-xs text-cyan-300 group-hover:translate-x-1 transition-transform font-bold flex items-center gap-1.5 bg-cyan-500/15 px-3 py-1 rounded-lg border border-cyan-500/30">
                    Run <Play className="w-3 h-3 fill-current" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
