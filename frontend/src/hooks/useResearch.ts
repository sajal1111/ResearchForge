import { useMutation } from "@tanstack/react-query";
import { generateReport } from "../services/api";
import type { ResearchResponse } from "../types/research";

/**
 * TanStack Query mutation wrapper for the research pipeline.
 *
 * Exposes:
 *   mutate(vars)  — trigger the research call
 *   data          — ResearchResponse on success
 *   isPending     — true while the pipeline is running
 *   isError       — true if the request failed
 *   error         — Error object
 *   reset         — clear state (use for "Generate New Report")
 */
export function useResearch() {
  const mutation = useMutation<
    ResearchResponse,
    Error,
    { topic: string; mode: string }
  >({
    mutationFn: ({ topic, mode }) => generateReport(topic, mode),
  });

  return {
    mutate: mutation.mutate,
    data: mutation.data,
    isPending: mutation.isPending,
    isSuccess: mutation.isSuccess,
    isError: mutation.isError,
    error: mutation.error,
    reset: mutation.reset,
  };
}
