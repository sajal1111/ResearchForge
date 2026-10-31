import { ExternalLink, Globe } from "lucide-react";
import { cn, domainFromUrl } from "../lib/utils";
import type { SourceItem } from "../types/research";

interface SourceCardProps {
  source: SourceItem;
  index: number;
}

export function SourceCard({ source, index }: SourceCardProps) {
  const domain = domainFromUrl(source.url);

  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(
        "group flex flex-col gap-2 p-4 rounded-xl border border-white/10",
        "bg-white/5 hover:bg-white/10 transition-all duration-200",
        "hover:border-violet-500/50 hover:shadow-lg hover:shadow-violet-500/10",
        "cursor-pointer"
      )}
      id={`source-card-${index}`}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="flex-shrink-0 w-7 h-7 rounded-md bg-violet-500/20 border border-violet-500/30 flex items-center justify-center">
            <Globe className="w-3.5 h-3.5 text-violet-400" />
          </div>
          <span className="font-semibold text-sm text-violet-300 truncate">
            {domain}
          </span>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {source.score != null && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-slate-400 font-mono">
              {(source.score * 100).toFixed(0)}%
            </span>
          )}
          <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-violet-400 transition-colors" />
        </div>
      </div>

      {/* Title */}
      {source.title && (
        <p className="text-sm text-slate-200 line-clamp-2 leading-snug">
          {source.title}
        </p>
      )}

      {/* Snippet */}
      {source.snippet && (
        <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
          {source.snippet}
        </p>
      )}

      {/* Full URL */}
      <p className="text-xs text-slate-600 truncate mt-auto pt-1 border-t border-white/5">
        {source.url}
      </p>
    </a>
  );
}
