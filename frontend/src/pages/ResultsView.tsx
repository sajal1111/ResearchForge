import { useState } from "react";
import { Copy, Download, RefreshCw, Check, FileText, Star, Globe } from "lucide-react";
import { cn, copyToClipboard, downloadMarkdown } from "../lib/utils";
import { REPORT_MODE_LABELS } from "../types/research";
import type { ResearchResponse } from "../types/research";
import { ReportTab } from "../components/ReportTab";
import { CriticTab } from "../components/CriticTab";
import { SourcesTab } from "../components/SourcesTab";

type TabId = "report" | "critic" | "sources";

interface ResultsViewProps {
  data: ResearchResponse;
  onReset: () => void;
}

export function ResultsView({ data, onReset }: ResultsViewProps) {
  const [activeTab, setActiveTab] = useState<TabId>("report");
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    const ok = await copyToClipboard(data.report);
    if (ok) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  function handleDownload() {
    downloadMarkdown(data.report, data.topic);
  }

  const TABS: { id: TabId; label: string; icon: React.ElementType; count?: number }[] = [
    { id: "report",  label: "Research Report",  icon: FileText },
    { id: "critic",  label: "Critic Review",    icon: Star },
    { id: "sources", label: "Sources",          icon: Globe, count: data.sources.length },
  ];

  return (
    <main className="w-full max-w-5xl mx-auto px-4 sm:px-6 py-8 flex flex-col gap-6">
      {/* Result header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <span className="text-xs px-2 py-0.5 rounded-md bg-violet-500/20 text-violet-400 border border-violet-500/30 font-medium uppercase tracking-wider">
              {REPORT_MODE_LABELS[data.mode]}
            </span>
            {data.critic.score && (
              <span className="text-xs px-2 py-0.5 rounded-md bg-white/10 text-slate-400 font-mono">
                Critic: {data.critic.score}
              </span>
            )}
          </div>
          <h2 className="text-xl font-bold text-white leading-tight mt-1">
            {data.topic}
          </h2>
        </div>
      </div>

      {/* Tabs */}
      <div className="rounded-2xl border border-white/10 bg-slate-900/60 backdrop-blur-sm overflow-hidden">
        {/* Tab bar */}
        <div className="flex border-b border-white/10 overflow-x-auto">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                id={`tab-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center gap-2 px-5 py-3.5 text-sm font-medium whitespace-nowrap",
                  "transition-all border-b-2 -mb-px",
                  activeTab === tab.id
                    ? "border-violet-500 text-white bg-violet-500/10"
                    : "border-transparent text-slate-500 hover:text-slate-300 hover:bg-white/5"
                )}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
                {tab.count != null && (
                  <span className="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-white/10 text-slate-400 font-mono">
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Tab content */}
        <div className="p-6">
          {activeTab === "report"  && <ReportTab data={data} />}
          {activeTab === "critic"  && <CriticTab critic={data.critic} />}
          {activeTab === "sources" && <SourcesTab sources={data.sources} />}
        </div>
      </div>

      {/* Bottom action bar */}
      <div className="flex flex-wrap items-center gap-3 pt-2">
        <button
          id="copy-report-btn"
          onClick={handleCopy}
          className={cn(
            "flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all border",
            copied
              ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-400"
              : "bg-white/5 border-white/10 text-slate-300 hover:bg-white/10 hover:border-white/20"
          )}
        >
          {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
          {copied ? "Copied!" : "Copy Report"}
        </button>

        <button
          id="download-md-btn"
          onClick={handleDownload}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium bg-white/5 border border-white/10 text-slate-300 hover:bg-white/10 hover:border-white/20 transition-all"
        >
          <Download className="w-4 h-4" />
          Download Markdown
        </button>

        <button
          id="new-report-btn"
          onClick={onReset}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium bg-gradient-to-r from-violet-600/20 to-blue-600/20 border border-violet-500/30 text-violet-300 hover:from-violet-600/30 hover:to-blue-600/30 transition-all ml-auto"
        >
          <RefreshCw className="w-4 h-4" />
          Generate New Report
        </button>
      </div>
    </main>
  );
}
