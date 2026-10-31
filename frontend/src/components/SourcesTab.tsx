import { SourceCard } from "./SourceCard";
import type { SourceItem } from "../types/research";
import { Globe } from "lucide-react";

interface SourcesTabProps {
  sources: SourceItem[];
}

export function SourcesTab({ sources }: SourcesTabProps) {
  if (!sources.length) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-3 text-slate-500">
        <Globe className="w-10 h-10 opacity-30" />
        <p className="text-sm">No sources were returned for this report.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4" id="sources-list">
      <p className="text-xs text-slate-500 uppercase tracking-wider font-medium">
        {sources.length} ranked source{sources.length !== 1 ? "s" : ""} — sorted by relevance score
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
        {sources.map((source, i) => (
          <SourceCard key={source.url + i} source={source} index={i} />
        ))}
      </div>
      <p className="text-xs text-slate-600 mt-2">
        Scores are a weighted heuristic blend of domain quality, keyword overlap, and freshness — use for sort order only, not as absolute quality signals.
      </p>
    </div>
  );
}
