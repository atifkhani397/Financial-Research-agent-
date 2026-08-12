import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { 
  Terminal, Cpu, Wrench, Database, BarChart3, Layers, Sparkles, Activity, ShieldCheck 
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

const NavigationHeader: React.FC = () => {
  const location = useLocation();

  const { data: healthData, isError } = useQuery({
    queryKey: ['health'],
    queryFn: api.getHealth,
    refetchInterval: 15000,
  });

  const isOnline = !isError && healthData?.status === 'ok';

  const navItems = [
    { path: '/', label: 'Console', icon: Terminal },
    { path: '/tools', label: 'Tools (12)', icon: Wrench },
    { path: '/memory', label: 'Memory', icon: Database },
    { path: '/evaluation', label: 'Evaluation', icon: BarChart3 },
    { path: '/traces', label: 'Traces', icon: Layers },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/20 font-bold group-hover:scale-105 transition-transform">
            A
          </div>
          <div>
            <span className="font-bold text-slate-100 tracking-tight text-sm block">ARA-1 Financial Agent</span>
            <span className="text-[10px] text-slate-400 font-mono block">QuantumEdge Research</span>
          </div>
        </Link>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Icon className="w-4 h-4" /> {item.label}
              </Link>
            );
          })}
        </nav>

        {/* API Connection Indicator */}
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono border ${
            isOnline ? 'bg-emerald-950 text-emerald-400 border-emerald-800' : 'bg-red-950 text-red-400 border-red-800'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${isOnline ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
            {isOnline ? 'FastAPI Online (8000)' : 'API Offline'}
          </span>
        </div>
      </div>
    </header>
  );
};

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-[#0b0f19] text-slate-100 font-sans flex flex-col justify-between">
          <div>
            <NavigationHeader />
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <Routes>
                <Route path="/" element={<QueryConsolePage />} />
                <Route path="/trace/:sessionId" element={<LiveTraceView />} />
                <Route path="/report/:sessionId" element={<ReportViewerPage />} />
                <Route path="/tools" element={<ToolRegistryPage />} />
                <Route path="/memory" element={<MemoryExplorerPage />} />
                <Route path="/evaluation" element={<EvaluationDashboardPage />} />
                <Route path="/traces" element={<TraceGalleryPage />} />
              </Routes>
            </main>
          </div>

          <footer className="border-t border-slate-800 py-4 text-center text-xs text-slate-500 font-mono">
            ARA-1 Autonomous Financial Research Agent &copy; 2026 Atif Khan | QuantumEdge Research
          </footer>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
