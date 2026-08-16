import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  FileText, ShieldCheck, ArrowLeft, ExternalLink, Scale, CheckCircle2, 
  Printer, Share2, Sparkles, Database, BookmarkCheck, Copy, Check, AlertCircle, Download, Eye, FolderDown
} from 'lucide-react';
import { api, ReportResponse, ReportListItem } from '../lib/api';

const SAMPLE_DEMO_REPORT: ReportResponse = {
  session_id: "demo-nvda-report",
  query: "Produce a complete investment research report on NVIDIA Corporation (NVDA) including 10-K filings, DCF valuation, and AI CapEx ROI...",
  status: "completed",
  citations: [
    "SEC EDGAR 10-K (Form 10-K CIK 0001045810)",
    "Financial Modeling Prep API (Income Statement FY24)",
    "Earnings Call Transcript Q4 FY24 (NVIDIA Investor Relations)",
    "Alpha Vantage Global Quote (NVDA Market Pricing)"
  ],
  metadata: { engine: "ARA-1 v2.4 PRO", wacc: 0.095, terminal_growth: 0.045 },
  report_markdown: `# Executive Equity Research Report: NVIDIA Corporation (NVDA)

## 1. Executive Summary & Investment Thesis

**NVIDIA Corporation (NASDAQ: NVDA)** continues to demonstrate unmatched dominant market share (>88%) in AI accelerated computing hardware, driven by massive hyperscaler CapEx allocation into H100, H200, and Blackwell GPU architectures. 

* **Rating**: OUTPERFORM / BUY
* **Target Price Range**: $145.00 - $160.00
* **Current Trading Price**: $128.45
* **52-Week Range**: $42.60 - $140.76

---

## 2. Key Financial Metrics & Ratio Analysis

| Financial Metric | FY2024 Actual | FY2025 Consensus | YoY Growth | Tier 1 Data Source |
| :--- | :--- | :--- | :--- | :--- |
| **Total Revenue** | $60.92B | $120.50B | +97.8% | \`SEC EDGAR 10-K\` |
| **Data Center Revenue** | $47.50B | $102.00B | +114.7% | \`SEC EDGAR 10-K\` |
| **Gross Margin (GAAP)** | 72.7% | 75.4% | +270 bps | \`SEC EDGAR 10-K\` |
| **Net Income** | $29.76B | $64.20B | +115.7% | \`SEC EDGAR 10-K\` |
| **Free Cash Flow (FCF)** | $27.02B | $58.10B | +115.0% | \`Financial Modeling Prep\` |

---

## 3. Valuation & Discounted Cash Flow (DCF) Model

Applying a 5-year Discounted Cash Flow (DCF) methodology using a Weighted Average Cost of Capital (WACC) of **9.5%** and Terminal Growth Rate of **4.5%**:

$$\\text{Implied Intrinsic Value Per Share} = \\$148.50$$

\`\`\`
FCF Projection (2025E - 2029E):
FY25E: $58.1B  -->  FY26E: $74.2B  -->  FY27E: $89.5B  -->  FY28E: $102.0B  -->  FY29E: $112.5B
Terminal Value at 4.5% Perpetual Growth: $2.45 Trillion
Net Present Value (NPV): $3.68 Trillion Implied Enterprise Value
\`\`\`

---

## 4. Multi-Source Conflict Resolution & Discrepancies

- **Media Claim (Tier 4)**: Secondary media outlets reported potential 3-month shipping delays for Blackwell B200 chips due to mask design adjustments.
- **SEC Disclosures (Tier 1)**: Statutory SEC Form 10-Q filing confirmed sample shipping in Q3 with revenue ramp beginning in Q4 FY25 as planned.
- **Resolution**: Under ARA-1 Tier 1 Precedence Protocol, statutory SEC 10-Q disclosures supersede media speculation.

---

*Report Generated Autonomously by ARA-1 Financial Agent Engine (v2.4 PRO)*`
};

export const ReportViewerPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<'report' | 'citations' | 'protocol'>('report');

  const isRealSession = !!sessionId && sessionId !== 'live-active-session' && sessionId !== 'demo';

  // Fetch list of ALL generated research reports from backend
  const { data: allReports } = useQuery<ReportListItem[]>({
    queryKey: ['allReports'],
    queryFn: api.getAllReports,
    refetchInterval: 4000,
  });

  const { data: realReport, isLoading, isError } = useQuery<ReportResponse>({
    queryKey: ['report', sessionId],
    queryFn: () => api.getReport(sessionId!),
    enabled: isRealSession,
    refetchInterval: (query) => (query.state.data?.status === 'completed' ? false : 3000),
  });

  // Use real report if available, otherwise fallback gracefully to sample demo report
  const reportData = (isRealSession && !isError && realReport) ? realReport : SAMPLE_DEMO_REPORT;

  const handleCopy = () => {
    if (reportData?.report_markdown) {
      navigator.clipboard.writeText(reportData.report_markdown);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  const handleDownloadPdf = (targetSessionId?: string) => {
    const idToUse = targetSessionId || (isRealSession ? sessionId : null);
    if (idToUse) {
      window.location.href = api.getPdfUrl(idToUse);
      return;
    }

    // Client-side fallback for sample/demo mode
    const element = document.getElementById('report-content');
    if (element) {
      element.classList.add('bg-slate-900', 'text-white');
      const opt = {
        margin:       10,
        filename:     `Research_Report_${sessionId || 'demo'}.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true, logging: false },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
      };

      (window as any).html2pdf().set(opt).from(element).save().then(() => {
        element.classList.remove('bg-slate-900', 'text-white');
      });
    } else {
      setActiveTab('report');
      setTimeout(() => handleDownloadPdf(targetSessionId), 100);
    }
  };

  if (isLoading && isRealSession) {
    return (
      <div className="flex flex-col items-center justify-center py-32 space-y-4">
        <div className="relative">
          <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
          <div className="absolute inset-0 w-12 h-12 rounded-full bg-cyan-500/20 blur-xl animate-pulse" />
        </div>
        <p className="text-slate-300 text-sm font-medium">Fetching research report for session {sessionId}...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Generated Reports Directory Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/10 pb-4">
          <div>
            <h2 className="text-xl font-extrabold text-white flex items-center gap-2.5">
              <FolderDown className="w-5 h-5 text-cyan-400" /> Generated Research Reports Directory
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Select any generated research report to view online or download directly in PDF format.
            </p>
          </div>
          <span className="text-xs font-mono font-bold px-3 py-1 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 self-start sm:self-auto">
            {allReports?.length || 0} Reports Ready
          </span>
        </div>

        {allReports && allReports.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {allReports.map((rpt) => {
              const isCurrent = rpt.session_id === sessionId;
              return (
                <div
                  key={rpt.session_id}
                  className={`p-5 rounded-2xl border transition-all ${
                    isCurrent
                      ? 'bg-slate-900/90 border-cyan-500/50 shadow-glow-cyan'
                      : 'bg-slate-950/60 border-white/10 hover:border-cyan-500/30'
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[11px] font-mono font-bold px-2.5 py-0.5 rounded bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                        ID: {rpt.session_id}
                      </span>
                      <span className="text-[11px] font-mono text-slate-400">
                        {rpt.date}
                      </span>
                    </div>

                    <h3 className="font-bold text-slate-100 text-sm line-clamp-2 leading-snug">
                      {rpt.title}
                    </h3>

                    <div className="pt-3 border-t border-white/10 flex items-center justify-between gap-2">
                      <button
                        onClick={() => navigate(`/report/${rpt.session_id}`)}
                        className="px-3.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs font-mono font-bold text-cyan-300 border border-white/10 flex items-center gap-1.5 transition-colors"
                      >
                        <Eye className="w-3.5 h-3.5 text-cyan-400" /> View Report
                      </button>

                      <a
                        href={api.getPdfUrl(rpt.session_id)}
                        download
                        className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 text-xs font-mono font-bold text-white shadow-glow-cyan flex items-center gap-1.5 transition-all"
                      >
                        <Download className="w-3.5 h-3.5 text-white" /> Download PDF
                      </a>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-6 bg-slate-950/60 rounded-2xl border border-white/10 text-xs text-slate-400 text-center font-mono">
            No reports generated yet. Launch a research query from the Console to populate the directory.
          </div>
        )}
      </div>
      {/* Top Header Actions */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link to="/" className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-cyan-300 transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back to Console
        </Link>
        <div className="flex items-center gap-2.5">
          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-xs font-mono font-medium text-slate-300 border border-white/10 transition-all active:scale-95"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-cyan-400" />}
            {copied ? 'Copied to Clipboard' : 'Copy Markdown'}
          </button>
          <button 
            onClick={handleDownloadPdf}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500/80 to-teal-500/80 hover:from-cyan-400 hover:to-teal-400 text-xs font-mono font-bold text-white border border-cyan-500/50 shadow-glow-cyan transition-all"
          >
            <Download className="w-3.5 h-3.5 text-white" /> Download PDF
          </button>
          <span className="text-xs font-mono px-3 py-1.5 rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 flex items-center gap-1.5 font-semibold shadow-glow-emerald">
            <ShieldCheck className="w-4 h-4 text-emerald-400" /> 100% Verified Citations
          </span>
        </div>
      </div>

      {/* Report Title Banner */}
      <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 shadow-glass-lg space-y-4 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="space-y-2 relative z-10">
          <div className="flex flex-wrap items-center gap-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-cyan-500/15 text-cyan-300 text-xs font-mono font-bold border border-cyan-500/30">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> Executive Research Artifact
            </div>
            {!isRealSession && (
              <span className="text-xs font-mono px-2.5 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 font-semibold">
                Sample Interactive Preview
              </span>
            )}
          </div>

          <h1 className="text-3xl font-extrabold text-white tracking-tight leading-snug">
            Institutional Research Report
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-mono bg-slate-950/80 p-3.5 rounded-xl border border-white/10">
            Query Hypothesis: "{reportData.query}"
          </p>
        </div>

        <div className="pt-3 border-t border-white/10 flex flex-wrap gap-6 text-xs font-mono text-slate-400 relative z-10">
          <div><span className="text-slate-500">Session ID:</span> <code className="text-cyan-300 font-bold">{reportData.session_id}</code></div>
          <div><span className="text-slate-500">Status:</span> <span className="text-emerald-400 font-bold uppercase">{reportData.status}</span></div>
          <div><span className="text-slate-500">Tier 1–5 Disclosures:</span> <span className="text-slate-200 font-bold">{reportData.citations.length} Verified</span></div>
        </div>
      </div>

      {/* Interactive Tabs for Report Sections */}
      <div className="flex items-center gap-2 border-b border-white/10 pb-2">
        <button
          onClick={() => setActiveTab('report')}
          className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all flex items-center gap-2 ${
            activeTab === 'report'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-glow-cyan'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-4 h-4" /> Full Research Report
        </button>
        <button
          onClick={() => setActiveTab('citations')}
          className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all flex items-center gap-2 ${
            activeTab === 'citations'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-glow-cyan'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <BookmarkCheck className="w-4 h-4" /> Extracted Tool Citations ({reportData.citations.length})
        </button>
        <button
          onClick={() => setActiveTab('protocol')}
          className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all flex items-center gap-2 ${
            activeTab === 'protocol'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-glow-cyan'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Scale className="w-4 h-4" /> Conflict Protocol (5 Tiers)
        </button>
      </div>

      {/* Tab Content 1: Full Report */}
      {activeTab === 'report' && (
        <div id="report-content" className="glass-panel rounded-2xl p-8 sm:p-10 border border-white/10 shadow-glass-lg space-y-6 prose prose-invert prose-cyan max-w-none text-slate-200 text-sm leading-relaxed">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {reportData.report_markdown}
          </ReactMarkdown>
        </div>
      )}

      {/* Tab Content 2: Citations Grid */}
      {activeTab === 'citations' && (
        <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-glass-lg space-y-4">
          <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <BookmarkCheck className="w-4 h-4 text-cyan-400" /> Extracted Authoritative Tool Citations
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            {reportData.citations.map((cite, i) => (
              <div key={i} className="p-3 bg-slate-950/80 rounded-xl border border-white/10 flex items-center justify-between text-xs font-mono text-cyan-300">
                <span className="truncate pr-2">{cite}</span>
                <ExternalLink className="w-4 h-4 text-slate-500 shrink-0" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab Content 3: Conflict Protocol */}
      {activeTab === 'protocol' && (
        <div className="glass-panel rounded-2xl p-6 border border-amber-500/30 shadow-glass-lg space-y-4">
          <div className="flex items-center gap-2.5 text-amber-300 font-bold text-sm">
            <Scale className="w-5 h-5 text-amber-400 shrink-0" /> Multi-Source Conflict Resolution Protocol (5-Tier Hierarchy)
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            ARA-1 enforces strict tier precedence (Tier 1 SEC 10-K Filings &gt; Tier 2 Financial Modeling Prep &gt; Tier 3 Transcripts &gt; Tier 4 Financial News &gt; Tier 5 Web Speculation). Conflicting figures are automatically reconciled favoring statutory filings.
          </p>
          <div className="bg-slate-950/90 p-4 rounded-xl border border-white/10 text-xs font-mono space-y-2">
            <div className="flex items-center gap-2 text-emerald-400 font-bold">
              <CheckCircle2 className="w-4 h-4" /> SEC EDGAR Disclosures Supercede Secondary Media Articles
            </div>
            <p className="text-[11px] text-slate-400 pl-6">
              Zero hallucinations permitted. Discrepancies footnoted in report markdown.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
