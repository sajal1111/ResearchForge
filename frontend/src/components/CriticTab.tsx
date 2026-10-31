import { CheckCircle, AlertCircle, Star, MessageSquare } from "lucide-react";
import { cn } from "../lib/utils";
import type { CriticReview } from "../types/research";

interface CriticTabProps {
  critic: CriticReview;
}

function ScoreDisplay({ score }: { score: string | null | undefined }) {
  if (!score) return null;

  // Extract numeric value for colour coding
  const numMatch = score.match(/(\d+)/);
  const num = numMatch ? parseInt(numMatch[1], 10) : null;
  const colour =
    num == null
      ? "text-slate-300"
      : num >= 8
      ? "text-emerald-400"
      : num >= 6
      ? "text-yellow-400"
      : "text-red-400";

  return (
    <div className="flex flex-col items-center gap-1">
      <div className={cn("text-6xl font-black tabular-nums tracking-tight", colour)}>
        {score}
      </div>
      <p className="text-sm text-slate-500 font-medium">Critic Score</p>
    </div>
  );
}

function BulletList({
  items,
  icon: Icon,
  colour,
  label,
}: {
  items: string[];
  icon: React.ElementType;
  colour: string;
  label: string;
}) {
  if (!items.length) return null;
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-2 mb-1">
        <Icon className={cn("w-4 h-4", colour)} />
        <h4 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
          {label}
        </h4>
      </div>
      <ul className="flex flex-col gap-2">
        {items.map((item, i) => (
          <li
            key={i}
            className={cn(
              "flex gap-2.5 text-sm text-slate-300 leading-relaxed",
              "p-2.5 rounded-lg border border-white/5 bg-white/3"
            )}
          >
            <span className={cn("mt-0.5 flex-shrink-0 w-1.5 h-1.5 rounded-full mt-1.5", colour.replace("text-", "bg-"))} />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function CriticTab({ critic }: CriticTabProps) {
  const hasStructured =
    critic.score || critic.strengths.length || critic.weaknesses.length || critic.verdict;

  // Fallback: render raw text if structured parsing yielded nothing
  if (!hasStructured) {
    return (
      <div className="rounded-xl border border-white/10 bg-white/3 p-6">
        <p className="text-xs text-slate-500 uppercase tracking-wider mb-3 font-medium">
          Raw Critic Output
        </p>
        <pre className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed font-mono">
          {critic.raw || "No critic feedback available."}
        </pre>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6" id="critic-review">
      {/* Score card */}
      {critic.score && (
        <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-slate-800/60 to-slate-900/60 p-8 flex flex-col items-center gap-4 shadow-inner">
          <ScoreDisplay score={critic.score} />
          {critic.verdict && (
            <div className="mt-2 px-4 py-2.5 rounded-xl bg-violet-500/10 border border-violet-500/30 text-center max-w-md">
              <p className="text-sm text-violet-300 italic leading-relaxed">
                "{critic.verdict}"
              </p>
            </div>
          )}
        </div>
      )}

      {/* Strengths + Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-950/20 p-5">
          <BulletList
            items={critic.strengths}
            icon={CheckCircle}
            colour="text-emerald-400"
            label="Strengths"
          />
          {!critic.strengths.length && (
            <p className="text-sm text-slate-500 italic">No strengths listed.</p>
          )}
        </div>
        <div className="rounded-xl border border-amber-500/20 bg-amber-950/20 p-5">
          <BulletList
            items={critic.weaknesses}
            icon={AlertCircle}
            colour="text-amber-400"
            label="Areas to Improve"
          />
          {!critic.weaknesses.length && (
            <p className="text-sm text-slate-500 italic">No weaknesses listed.</p>
          )}
        </div>
      </div>

      {/* Verdict (if not already shown above) */}
      {critic.verdict && !critic.score && (
        <div className="rounded-xl border border-violet-500/30 bg-violet-950/20 p-5">
          <div className="flex items-center gap-2 mb-2">
            <MessageSquare className="w-4 h-4 text-violet-400" />
            <span className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
              Verdict
            </span>
          </div>
          <p className="text-slate-300 italic">"{critic.verdict}"</p>
        </div>
      )}

      {/* Raw fallback accordion */}
      <details className="rounded-xl border border-white/5 bg-white/3">
        <summary className="cursor-pointer px-4 py-3 text-xs text-slate-500 hover:text-slate-400 flex items-center gap-2 select-none">
          <Star className="w-3.5 h-3.5" />
          View raw critic output
        </summary>
        <pre className="px-4 pb-4 text-xs text-slate-500 whitespace-pre-wrap font-mono leading-relaxed">
          {critic.raw}
        </pre>
      </details>
    </div>
  );
}
