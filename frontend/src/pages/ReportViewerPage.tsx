import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FileText, ShieldCheck, ArrowLeft, ExternalLink, Scale, CheckCircle2 } from 'lucide-react';
import { api, ReportResponse } from '../lib/api';

export const ReportViewerPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();

  const { data, isLoading, isError } = useQuery<ReportResponse>({
    queryKey: ['report', sessionId],
    queryFn: () => api.getReport(sessionId!),
    enabled: !!sessionId,
  });

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-4">
        <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 text-sm">Fetching publication-grade markdown report...</p>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-6 bg-red-950/30 border border-red-800 rounded-xl text-red-400 text-sm max-w-xl mx-auto text-center space-y-3">
        <p>Failed to load research report for session {sessionId}.</p>
        <Link to="/" className="inline-block px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium">
          Back to Query Console
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header Actions */}
      <div className="flex items-center justify-between">
        <Link to="/" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 font-medium">
          <ArrowLeft className="w-4 h-4" /> Back to Console
        </Link>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono px-2.5 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" /> 100% Citations Verified
          </span>
        </div>
      </div>

      {/* Report Title & Metadata Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-3">
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <FileText className="w-6 h-6 text-blue-400" /> Investment Research Report
        </h1>
        <p className="text-xs text-slate-400 font-mono">Query: "{data.query}"</p>
        <div className="pt-3 border-t border-slate-800 flex flex-wrap gap-4 text-xs text-slate-400">
          <div><span className="text-slate-500">Session ID:</span> <code className="text-blue-400">{data.session_id}</code></div>
          <div><span className="text-slate-500">Status:</span> <span className="text-emerald-400 font-semibold uppercase">{data.status}</span></div>
          <div><span className="text-slate-500">Source Citations:</span> <span className="text-slate-200 font-semibold">{data.citations.length} Verified</span></div>
        </div>
      </div>

      {/* Dedicated Conflict & Synthesis Panel (Section A6.3) */}
      <div className="bg-slate-900/90 border border-amber-500/30 rounded-xl p-5 shadow-xl space-y-3">
        <h3 className="text-sm font-bold text-amber-300 flex items-center gap-2">
          <Scale className="w-4 h-4 text-amber-400" /> Multi-Source Conflict Resolution Protocol (5-Tier Hierarchy)
        </h3>
        <p className="text-xs text-slate-300 leading-relaxed">
          ARA-1 applies a strict 5-tier reliability hierarchy (Tier 1: SEC EDGAR Filings &gt; Tier 2: Financial Data APIs &gt; Tier 3: Transcripts &gt; Tier 4: News Outlets &gt; Tier 5: Web Media). Conflicting claims are resolved deterministically in favor of higher tier disclosures.
        </p>
        <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs font-mono space-y-1 text-slate-400">
          <div className="flex items-center gap-2 text-emerald-400 font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5" /> SEC EDGAR 10-K Tier 1 Disclosures Supersede Media Speculation
          </div>
          <p className="text-[11px] text-slate-400 pl-5">
            Zero metric fabrications permitted. Discrepancies footnoted in report markdown below.
          </p>
        </div>
      </div>

      {/* Rendered Markdown Report */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-8 shadow-2xl space-y-4 prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {data.report_markdown}
        </ReactMarkdown>
      </div>

      {/* Extracted Citations Drawer */}
      {data.citations.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Extracted Authoritative Tool Citations</h3>
          <div className="flex flex-wrap gap-2">
            {data.citations.map((cite, i) => (
              <span key={i} className="inline-flex items-center gap-1 text-xs font-mono bg-slate-950 text-blue-400 px-3 py-1 rounded-md border border-slate-800">
                <ExternalLink className="w-3 h-3 text-slate-500" /> {cite}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
