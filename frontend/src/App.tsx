import { useState, useEffect, useRef } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { TopNav } from "./layouts/TopNav";
import { HomePage } from "./pages/HomePage";
import { ResultsView } from "./pages/ResultsView";
import { LoadingSteps } from "./components/LoadingSteps";
import { useResearch } from "./hooks/useResearch";
import type { ReportMode } from "./types/research";
import "./styles/globals.css";

const queryClient = new QueryClient();

function AppInner() {
  const [isDark, setIsDark] = useState(true);
  const { mutate, data, isPending, isError, error, reset } = useResearch();
  const resultsRef = useRef<HTMLDivElement>(null);

  // Apply dark class to document root
  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDark);
  }, [isDark]);

  // Scroll to results when they arrive
  useEffect(() => {
    if (data && resultsRef.current) {
      resultsRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [data]);

  function handleSubmit(topic: string, mode: ReportMode) {
    mutate({ topic, mode });
    // Scroll to loading area
    window.scrollTo({ top: 500, behavior: "smooth" });
  }

  function handleReset() {
    reset();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col">
      <TopNav isDark={isDark} onToggleDark={() => setIsDark((d) => !d)} />

      {/* Show HomePage only when no result and not pending */}
      {!data && !isPending && (
        <HomePage onSubmit={handleSubmit} isPending={isPending} />
      )}

      {/* Loading state */}
      {isPending && (
        <div className="flex flex-col items-center justify-center flex-1 py-20 px-4">
          <LoadingSteps isPending={isPending} />
        </div>
      )}

      {/* Error state */}
      {isError && !isPending && (
        <div className="flex flex-col items-center justify-center flex-1 py-20 px-4 gap-4">
          <div className="max-w-md w-full rounded-2xl border border-red-500/30 bg-red-950/20 p-6 text-center">
            <p className="text-2xl mb-2">⚠️</p>
            <h3 className="text-lg font-semibold text-red-400 mb-2">Request Failed</h3>
            <p className="text-sm text-slate-400 mb-5">
              {error?.message || "An unexpected error occurred. Please try again."}
            </p>
            <button
              id="error-retry-btn"
              onClick={handleReset}
              className="px-5 py-2.5 rounded-xl bg-red-500/20 border border-red-500/30 text-red-300 hover:bg-red-500/30 text-sm font-medium transition-all"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Results */}
      {data && !isPending && (
        <div ref={resultsRef}>
          <ResultsView data={data} onReset={handleReset} />
        </div>
      )}

      {/* Footer */}
      <footer className="mt-auto border-t border-white/5 py-6 text-center">
        <p className="text-xs text-slate-700">
          ResearchForge · Built with LangChain, FastAPI & React
        </p>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppInner />
    </QueryClientProvider>
  );
}
