import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ResearchResponse } from "../types/research";

interface ReportTabProps {
  data: ResearchResponse;
}

export function ReportTab({ data }: ReportTabProps) {
  return (
    <div
      className="prose prose-invert prose-slate max-w-none
        prose-headings:font-bold prose-headings:text-white
        prose-h1:text-2xl prose-h1:border-b prose-h1:border-white/10 prose-h1:pb-3 prose-h1:mb-6
        prose-h2:text-xl prose-h2:text-violet-300 prose-h2:mt-8 prose-h2:mb-4
        prose-h3:text-lg prose-h3:text-slate-200 prose-h3:mt-6
        prose-p:text-slate-300 prose-p:leading-relaxed prose-p:my-3
        prose-a:text-violet-400 prose-a:no-underline hover:prose-a:underline
        prose-strong:text-white prose-strong:font-semibold
        prose-em:text-slate-200
        prose-ul:text-slate-300 prose-ol:text-slate-300
        prose-li:my-1 prose-li:leading-relaxed
        prose-blockquote:border-l-violet-500 prose-blockquote:text-slate-400 prose-blockquote:italic
        prose-code:text-violet-300 prose-code:bg-violet-950/60 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-code:font-mono
        prose-pre:bg-slate-900/80 prose-pre:border prose-pre:border-white/10 prose-pre:rounded-xl
        prose-table:text-sm prose-table:text-slate-300
        prose-th:text-slate-200 prose-th:font-semibold prose-th:border prose-th:border-white/10 prose-th:bg-white/5 prose-th:px-3 prose-th:py-2
        prose-td:border prose-td:border-white/10 prose-td:px-3 prose-td:py-2
        prose-hr:border-white/10"
      id="report-content"
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {data.report}
      </ReactMarkdown>
    </div>
  );
}
