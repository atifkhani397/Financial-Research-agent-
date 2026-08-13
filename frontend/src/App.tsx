import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { 
  Terminal, Cpu, Wrench, Database, BarChart3, Layers, Sparkles, Activity, 
  ShieldCheck, TrendingUp, Zap, FileText, ChevronRight, Compass, Shield
} from 'lucide-react';

import { QueryConsolePage } from './pages/QueryConsolePage';
import { LiveTraceView } from './pages/LiveTraceView';
import { ReportViewerPage } from './pages/ReportViewerPage';
import { ToolRegistryPage } from './pages/ToolRegistryPage';
import { MemoryExplorerPage } from './pages/MemoryExplorerPage';
import { EvaluationDashboardPage } from './pages/EvaluationDashboardPage';
import { TraceGalleryPage } from './pages/TraceGalleryPage';
import { api } from './lib/api';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 10000,
    },
  },
});

const TickerMarquee: React.FC = () => {
  const tickerItems = [
    { symbol: 'ARA-1 ENGINE', val: 'OPERATIONAL', change: '100%', up: true },
    { symbol: 'SEC EDGAR TIER 1', val: 'CONNECTED', change: '0ms', up: true },
    { symbol: 'ALPHA VANTAGE', val: 'LIVE API', change: '100req/m', up: true },
    { symbol: 'NVDA', val: '$128.45', change: '+3.42%', up: true },
    { symbol: 'TSLA', val: '$218.80', change: '+2.15%', up: true },
    { symbol: 'MSFT', val: '$448.90', change: '+0.88%', up: true },
    { symbol: 'AAPL', val: '$224.20', change: '-0.35%', up: false },
    { symbol: 'HALLUCINATION FILTER', val: 'ACTIVE', change: '99.4%', up: true },
    { symbol: 'BENCHMARKS', val: '8/8 PASSED', change: '100%', up: true },
  ];

  return (
    <div className="bg-slate-950/90 border-b border-white/10 py-1.5 overflow-hidden backdrop-blur-md">
      <div className="flex whitespace-nowrap animate-marquee">
        {[...tickerItems, ...tickerItems].map((item, idx) => (
          <div key={idx} className="inline-flex items-center gap-2 mx-5 text-[11px] font-mono">
            <span className="text-slate-400 font-semibold">{item.symbol}</span>
            <span className="text-slate-200">{item.val}</span>
            <span className={`flex items-center gap-0.5 ${item.up ? 'text-emerald-400' : 'text-red-400'}`}>
              <TrendingUp className={`w-3 h-3 ${!item.up ? 'rotate-180' : ''}`} />
              {item.change}
            </span>
            <span className="text-slate-800 mx-2">•</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const SidebarNav: React.FC = () => {
  const location = useLocation();

  const { data: healthData, isError } = useQuery({
    queryKey: ['health'],
    queryFn: api.getHealth,
    refetchInterval: 15000,
  });

  const isOnline = !isError && healthData?.status === 'ok';

  const researchCoreItems = [
    { path: '/', label: 'Research Console', icon: Terminal, count: 'Main' },
    { path: '/trace', label: 'Live Trace Stream', icon: Activity, count: 'Live' },
    { path: '/report', label: 'Report Viewer', icon: FileText, count: 'PDF' },
  ];

  const intelligenceItems = [
    { path: '/tools', label: 'Tool Capability Registry', icon: Wrench, count: '12' },
    { path: '/memory', label: 'Vector Memory Store', icon: Database, count: 'Chroma' },
    { path: '/evaluation', label: 'Benchmarks & Eval', icon: BarChart3, count: '8/8' },
    { path: '/traces', label: 'Trace Gallery', icon: Layers, count: '6' },
  ];

  return (
    <aside className="w-64 sidebar-panel h-screen sticky top-0 flex flex-col justify-between p-4 z-40 shrink-0">
      <div className="space-y-6">
        {/* Brand Header */}
        <Link to="/" className="flex items-center gap-3 px-2 py-2 group border-b border-white/10 pb-4">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 via-teal-400 to-emerald-400 p-[1px] shadow-glow-cyan group-hover:scale-105 transition-transform duration-300">
              <div className="w-full h-full bg-slate-950 rounded-[11px] flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-cyan-400 animate-pulse" />
              </div>
            </div>
            <div className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-400 border-2 border-slate-950 animate-ping" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-base tracking-tight text-white group-hover:text-cyan-400 transition-colors">
                ARA-1
              </span>
              <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold">
                PRO
              </span>
            </div>
            <span className="text-[10px] text-slate-400 font-medium block truncate max-w-[140px]">
              Autonomous Financial Agent
            </span>
          </div>
        </Link>

        {/* Navigation Group 1: Research Core */}
        <div className="space-y-1.5">
          <span className="px-3 text-[10px] font-mono font-bold uppercase tracking-wider text-slate-500 block">
            Research Engine
          </span>
          {researchCoreItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path.split('/')[1]));
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
                  isActive
                    ? 'nav-item-active'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-white/5'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                  <span>{item.label}</span>
                </div>
                <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                  isActive ? 'bg-cyan-500/20 text-cyan-300 font-bold' : 'bg-slate-900 text-slate-500'
                }`}>
                  {item.count}
                </span>
              </Link>
            );
          })}
        </div>

        {/* Navigation Group 2: Intelligence & System */}
        <div className="space-y-1.5">
          <span className="px-3 text-[10px] font-mono font-bold uppercase tracking-wider text-slate-500 block">
            Intelligence Platform
          </span>
          {intelligenceItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
                  isActive
                    ? 'nav-item-active'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-white/5'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                  <span>{item.label}</span>
                </div>
                <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                  isActive ? 'bg-cyan-500/20 text-cyan-300 font-bold' : 'bg-slate-900 text-slate-500'
                }`}>
                  {item.count}
                </span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Bottom Sidebar Status */}
      <div className="space-y-3 pt-4 border-t border-white/10">
        <div className={`p-3 rounded-xl border font-mono text-xs flex items-center justify-between ${
          isOnline 
            ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300 shadow-glow-emerald' 
            : 'bg-red-950/40 border-red-500/30 text-red-300'
        }`}>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-400 animate-ping' : 'bg-red-400'}`} />
            <span className="text-[11px] font-bold">{isOnline ? 'FastAPI :8000' : 'API Offline'}</span>
          </div>
          <span className="text-[10px] text-slate-400">v2.4</span>
        </div>

        <Link
          to="/"
          className="w-full py-2.5 px-3 bg-gradient-to-r from-cyan-600 via-teal-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white font-bold rounded-xl text-xs shadow-glow-cyan flex items-center justify-center gap-2 transition-all"
        >
          <Zap className="w-3.5 h-3.5 fill-current" /> New Research Query
        </Link>
      </div>
    </aside>
  );
};

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-[#060911] text-slate-100 font-sans flex relative ambient-mesh grid-pattern overflow-x-hidden">
          {/* Left Sidebar Menu */}
          <SidebarNav />

          {/* Main Layout Container */}
          <div className="flex-1 flex flex-col min-w-0">
            {/* Top Market Ticker Marquee Bar */}
            <TickerMarquee />

            {/* Main View Area */}
            <main className="flex-1 px-6 lg:px-10 py-8 relative z-10 max-w-7xl mx-auto w-full">
              <Routes>
                <Route path="/" element={<QueryConsolePage />} />
                <Route path="/trace" element={<LiveTraceView />} />
                <Route path="/trace/:sessionId" element={<LiveTraceView />} />
                <Route path="/report" element={<ReportViewerPage />} />
                <Route path="/report/:sessionId" element={<ReportViewerPage />} />
                <Route path="/tools" element={<ToolRegistryPage />} />
                <Route path="/memory" element={<MemoryExplorerPage />} />
                <Route path="/evaluation" element={<EvaluationDashboardPage />} />
                <Route path="/traces" element={<TraceGalleryPage />} />
              </Routes>
            </main>

            {/* Footer */}
            <footer className="border-t border-white/10 bg-slate-950/80 backdrop-blur-md py-4 px-8 text-xs text-slate-500 relative z-10 flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                ARA-1 Financial Agent &bull; QuantumEdge Institutional Platform
              </div>
              <p className="text-[11px] text-slate-500 font-mono">
                Tier 1-5 Certified Sources &bull; Vector Memory Verified &bull; Multi-Agent LLMs
              </p>
              <div className="text-[11px] text-slate-400 font-mono">
                &copy; 2026 Atif Khan
              </div>
            </footer>
          </div>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
