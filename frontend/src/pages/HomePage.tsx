import { useRef, useState } from "react";
import { Send, X, ChevronDown, Sparkles } from "lucide-react";
import { cn } from "../lib/utils";
import { REPORT_MODE_LABELS, REPORT_MODE_DESCRIPTIONS } from "../types/research";
import type { ReportMode } from "../types/research";

const MODES = Object.keys(REPORT_MODE_LABELS) as ReportMode[];
const MAX_CHARS = 300;
const MIN_CHARS = 3;

interface HomePageProps {
  onSubmit: (topic: string, mode: ReportMode) => void;
  isPending: boolean;
}

export function HomePage({ onSubmit, isPending }: HomePageProps) {
  const [topic, setTopic] = useState("");
  const [mode, setMode] = useState<ReportMode>("deep_research");
  const [modeOpen, setModeOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const canSubmit = topic.trim().length >= MIN_CHARS && !isPending;

  function handleSubmit() {
    if (!canSubmit) return;
    onSubmit(topic.trim(), mode);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  }

  function handleClear() {
    setTopic("");
    textareaRef.current?.focus();
  }

  const remaining = MAX_CHARS - topic.length;

  return (
    <main className="flex flex-col items-center w-full px-4 py-16 sm:py-24 gap-12">
      {/* Hero */}
      <section className="flex flex-col items-center gap-5 text-center max-w-3xl">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-violet-500/40 bg-violet-500/10 text-violet-300 text-xs font-medium">
          <Sparkles className="w-3.5 h-3.5" />
          Powered by Intelligent AI Agents
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight leading-tight">
          Research
          <span className="bg-gradient-to-r from-violet-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent">
            Forge
          </span>
        </h1>

        <p className="text-lg text-slate-400 leading-relaxed max-w-xl">
          Forge reliable research from the web using intelligent AI agents.
          Plan → Search → Rank → Scrape → Summarize → Write → Review.
        </p>
      </section>

      {/* Input card */}
      <section
        id="input-card"
        className="w-full max-w-2xl rounded-2xl border border-white/10 bg-gradient-to-b from-slate-800/60 to-slate-900/60 backdrop-blur-sm p-6 shadow-2xl shadow-black/40"
      >
        {/* Textarea */}
        <div className="relative mb-5">
          <textarea
            ref={textareaRef}
            id="topic-textarea"
            value={topic}
            onChange={(e) => setTopic(e.target.value.slice(0, MAX_CHARS))}
            onKeyDown={handleKeyDown}
            disabled={isPending}
            placeholder="Enter a research topic… e.g. 'The impact of quantum computing on cryptography'"
            rows={4}
            className={cn(
              "w-full resize-none rounded-xl border bg-white/5 px-4 py-3.5 text-sm text-slate-200",
              "placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-violet-500/60",
              "transition-colors leading-relaxed",
              topic.length >= MIN_CHARS
                ? "border-white/15 focus:border-violet-500/50"
                : "border-white/10",
              isPending && "opacity-50 cursor-not-allowed"
            )}
          />
          {/* Char count */}
          <div className="absolute bottom-2.5 right-3 flex items-center gap-2">
            {topic.length > 0 && (
              <button
                onClick={handleClear}
                disabled={isPending}
                className="text-slate-600 hover:text-slate-400 transition-colors"
                aria-label="Clear topic"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
            <span
              className={cn(
                "text-xs font-mono tabular-nums",
                remaining < 30 ? "text-amber-500" : "text-slate-600"
              )}
            >
              {remaining}
            </span>
          </div>
        </div>

        {/* Mode selector */}
        <div className="mb-5 relative">
          <label className="block text-xs text-slate-500 uppercase tracking-wider font-medium mb-2">
            Report Mode
          </label>
          <button
            id="mode-select"
            onClick={() => setModeOpen((o) => !o)}
            disabled={isPending}
            className={cn(
              "w-full flex items-center justify-between px-4 py-3 rounded-xl border",
              "bg-white/5 text-sm text-slate-200 transition-all text-left",
              modeOpen
                ? "border-violet-500/50 ring-2 ring-violet-500/20"
                : "border-white/10 hover:border-white/20",
              isPending && "opacity-50 cursor-not-allowed"
            )}
          >
            <div className="flex flex-col gap-0.5">
              <span className="font-medium">{REPORT_MODE_LABELS[mode]}</span>
              <span className="text-xs text-slate-500">
                {REPORT_MODE_DESCRIPTIONS[mode]}
              </span>
            </div>
            <ChevronDown
              className={cn(
                "w-4 h-4 text-slate-500 flex-shrink-0 ml-2 transition-transform duration-200",
                modeOpen && "rotate-180"
              )}
            />
          </button>

          {/* Dropdown */}
          {modeOpen && (
            <div className="absolute top-full mt-1 left-0 right-0 z-10 rounded-xl border border-white/15 bg-slate-800/95 backdrop-blur-sm shadow-xl overflow-hidden">
              {MODES.map((m) => (
                <button
                  key={m}
                  id={`mode-option-${m}`}
                  onClick={() => { setMode(m); setModeOpen(false); }}
                  className={cn(
                    "w-full flex flex-col gap-0.5 px-4 py-3 text-left transition-colors",
                    m === mode
                      ? "bg-violet-500/20 text-violet-300"
                      : "text-slate-300 hover:bg-white/5"
                  )}
                >
                  <span className="text-sm font-medium">{REPORT_MODE_LABELS[m]}</span>
                  <span className="text-xs text-slate-500">{REPORT_MODE_DESCRIPTIONS[m]}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Submit row */}
        <div className="flex items-center gap-3">
          <button
            id="generate-btn"
            onClick={handleSubmit}
            disabled={!canSubmit}
            className={cn(
              "flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold transition-all",
              canSubmit
                ? "bg-gradient-to-r from-violet-600 to-blue-600 text-white hover:from-violet-500 hover:to-blue-500 shadow-lg shadow-violet-500/30 hover:shadow-violet-500/50 hover:scale-[1.02] active:scale-[0.98]"
                : "bg-white/5 text-slate-600 cursor-not-allowed"
            )}
          >
            <Send className="w-4 h-4" />
            Generate Report
          </button>
          <p className="hidden sm:block text-xs text-slate-600 flex-shrink-0">
            Ctrl+Enter
          </p>
        </div>

        {topic.length > 0 && topic.length < MIN_CHARS && (
          <p className="text-xs text-amber-500/80 mt-2 text-center">
            Topic must be at least {MIN_CHARS} characters.
          </p>
        )}
      </section>

      {/* Feature grid */}
      <section className="w-full max-w-2xl grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
        {[
          { icon: "🧠", label: "AI Planning" },
          { icon: "🔍", label: "Web Search" },
          { icon: "📊", label: "Source Ranking" },
          { icon: "✍️", label: "Report Writing" },
        ].map((f) => (
          <div
            key={f.label}
            className="flex flex-col items-center gap-1.5 p-3 rounded-xl bg-white/3 border border-white/8"
          >
            <span className="text-xl">{f.icon}</span>
            <span className="text-xs text-slate-400 font-medium">{f.label}</span>
          </div>
        ))}
      </section>
    </main>
  );
}
