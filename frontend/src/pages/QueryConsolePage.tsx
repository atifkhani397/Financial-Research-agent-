import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Search, Play, ShieldAlert, Cpu, Sparkles, CheckCircle } from 'lucide-react';
import { api, ChallengeItem } from '../lib/api';

export const QueryConsolePage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const { data: challenges, isLoading: isChallengesLoading, isError } = useQuery<ChallengeItem[]>({
    queryKey: ['challenges'],
    queryFn: api.getChallenges,
  });

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
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 border border-slate-800 rounded-xl p-8 shadow-2xl relative overflow-hidden">
        <div className="relative z-10 space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full text-blue-400 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" /> ARA-1 Production Research Engine
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Autonomous Financial Research Query Console</h1>
          <p className="text-slate-400 max-w-2xl text-sm leading-relaxed">
            Enter a natural language financial query or select from the 8 progressive benchmark challenges below. ARA-1 plans a multi-step roadmap, queries Tier 1–5 authoritative sources, resolves conflicting figures, and outputs publication-grade markdown investment reports.
          </p>
        </div>
      </div>

      {/* Query Submission Box */}
      <form onSubmit={handleSubmit} className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl flex flex-col md:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-3.5 w-5 h-5 text-slate-500" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. Produce a complete investment research report on NVIDIA Corporation (NVDA)..."
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-12 pr-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors text-sm"
          />
        </div>
        <button
          type="submit"
          disabled={isSubmitting || !query.trim()}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg shadow-lg flex items-center justify-center gap-2 transition-all text-sm shrink-0"
        >
          <Play className="w-4 h-4 fill-current" />
          {isSubmitting ? 'Initiating Agent...' : 'Launch Agent Research'}
        </button>
      </form>

      {/* 8 Predefined Challenges Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-blue-400" /> Section B2 Benchmark Challenges
          </h2>
          <span className="text-xs text-slate-400 font-mono">8 Predefined Research Tasks</span>
        </div>

        {isChallengesLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((n) => (
              <div key={n} className="h-32 bg-slate-900/50 border border-slate-800 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : isError ? (
          <div className="p-4 bg-red-950/30 border border-red-800/50 rounded-xl text-red-400 text-sm flex items-center gap-2">
            <ShieldAlert className="w-5 h-5" /> Failed to load benchmark challenges. Ensure FastAPI server is running on http://localhost:8000.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {challenges?.map((c) => (
              <div
                key={c.challenge_id}
                onClick={() => handleRunChallenge(c)}
                className="group bg-slate-900/80 border border-slate-800 hover:border-blue-500/50 rounded-xl p-5 transition-all hover:shadow-xl cursor-pointer flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 text-blue-400 border border-slate-700">
                      Challenge {c.challenge_id}
                    </span>
                    <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${
                      c.difficulty.startsWith('5') ? 'bg-red-950 text-red-400 border border-red-800' :
                      c.difficulty.startsWith('4') ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                      'bg-emerald-950 text-emerald-400 border border-emerald-800'
                    }`}>
                      Difficulty: {c.difficulty}
                    </span>
                  </div>
                  <h3 className="font-semibold text-slate-200 group-hover:text-blue-400 transition-colors text-sm">
                    {c.title}
                  </h3>
                  <p className="text-slate-400 text-xs line-clamp-2 leading-relaxed">
                    {c.query}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between">
                  <div className="flex flex-wrap gap-1">
                    {c.expected_tools.slice(0, 3).map((tool) => (
                      <span key={tool} className="text-[10px] font-mono bg-slate-950 px-2 py-0.5 rounded border border-slate-800 text-slate-400">
                        {tool}
                      </span>
                    ))}
                  </div>
                  <span className="text-xs text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity font-medium flex items-center gap-1">
                    Run <Play className="w-3 h-3 fill-current" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
