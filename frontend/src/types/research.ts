/**
 * TypeScript types mirroring backend Pydantic schemas exactly.
 * Keep in sync with backend/app/schemas/research.py.
 */

export type ReportMode =
  | "quick_summary"
  | "deep_research"
  | "technical"
  | "business"
  | "interview_prep";

export interface ResearchRequest {
  topic: string;
  mode: ReportMode;
}

export interface SourceItem {
  url: string;
  title?: string | null;
  snippet?: string | null;
  score?: number | null;
}

export interface CriticReview {
  score?: string | null;       // e.g. "7/10" — string, not number
  strengths: string[];
  weaknesses: string[];
  verdict?: string | null;
  raw: string;                 // always present — full raw critic text
}

export interface ResearchResponse {
  report: string;
  critic: CriticReview;
  sources: SourceItem[];
  mode: ReportMode;
  topic: string;
}

export interface ApiError {
  error: string;
  message: string;
}

export const REPORT_MODE_LABELS: Record<ReportMode, string> = {
  quick_summary: "Quick Summary",
  deep_research: "Deep Research",
  technical: "Technical",
  business: "Business",
  interview_prep: "Interview Prep",
};

export const REPORT_MODE_DESCRIPTIONS: Record<ReportMode, string> = {
  quick_summary: "150–250 word concise overview of key points",
  deep_research: "500–800 word thorough report with key findings",
  technical: "400–700 word technical report for engineering audiences",
  business: "400–700 word report focused on business implications",
  interview_prep: "300–600 word Q&A preparation with key facts",
};
