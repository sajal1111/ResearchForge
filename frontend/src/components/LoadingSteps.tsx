import { useEffect, useRef, useState } from "react";
import { cn } from "../lib/utils";

const STEPS = [
  { id: "planning",    label: "Planning Subtopics",     icon: "🧠", description: "Breaking topic into focused research angles..." },
  { id: "searching",  label: "Searching the Web",       icon: "🔍", description: "Running parallel searches across subtopics..." },
  { id: "ranking",    label: "Ranking Sources",         icon: "📊", description: "Scoring and deduplicating search results..." },
  { id: "scraping",   label: "Scraping Sources",        icon: "📥", description: "Reading top-ranked pages in parallel..." },
  { id: "summarizing",label: "Summarizing Content",     icon: "✍️", description: "Distilling key facts from each source..." },
  { id: "writing",    label: "Writing Report",          icon: "📝", description: "Drafting the full research report..." },
  { id: "reviewing",  label: "Reviewing Report",        icon: "🔬", description: "Critic agent evaluating quality..." },
];

const STEP_INTERVAL_MS = 5500; // advance every ~5.5 s

interface LoadingStepsProps {
  isPending: boolean;
}

export function LoadingSteps({ isPending }: LoadingStepsProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!isPending) {
      // Request completed — clear timer but keep state (parent will unmount)
      if (intervalRef.current) clearInterval(intervalRef.current);
      return;
    }

    // Reset when a new request starts
    setCurrentStep(0);

    intervalRef.current = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < STEPS.length - 1) return prev + 1;
        return prev; // cap at last step, hold until real response arrives
      });
    }, STEP_INTERVAL_MS);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isPending]);

  const activeStep = STEPS[currentStep];
  const isAtLastStep = currentStep === STEPS.length - 1;

  return (
    <div className="w-full max-w-2xl mx-auto px-4">
      {/* Main status card */}
      <div className="relative rounded-2xl border border-violet-500/30 bg-gradient-to-b from-violet-950/60 to-slate-900/60 backdrop-blur-sm p-8 shadow-xl shadow-violet-500/10 overflow-hidden">
        {/* Animated background pulse */}
        <div className="absolute inset-0 bg-gradient-to-r from-violet-600/5 via-transparent to-blue-600/5 animate-pulse" />

        {/* Current step icon + label */}
        <div className="relative flex flex-col items-center gap-4 mb-8">
          <div className="relative">
            <div className="w-16 h-16 rounded-2xl bg-violet-500/20 border border-violet-500/40 flex items-center justify-center text-3xl shadow-lg shadow-violet-500/20">
              {activeStep.icon}
            </div>
            {/* Spinning ring */}
            <div className="absolute -inset-1 rounded-2xl border-2 border-transparent border-t-violet-500 animate-spin opacity-60" />
          </div>
          <div className="text-center">
            <h3 className="text-lg font-semibold text-white">{activeStep.label}</h3>
            <p className="text-sm text-slate-400 mt-1">{activeStep.description}</p>
            {isAtLastStep && isPending && (
              <p className="text-xs text-violet-400 mt-2 animate-pulse">
                Waiting for response… this may take a moment
              </p>
            )}
          </div>
        </div>

        {/* Step progress dots */}
        <div className="relative flex items-center justify-center gap-2 flex-wrap">
          {STEPS.map((step, i) => (
            <div key={step.id} className="flex items-center gap-2">
              <div
                className={cn(
                  "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium transition-all duration-500",
                  i < currentStep
                    ? "bg-violet-600/40 text-violet-300 border border-violet-500/40"
                    : i === currentStep
                    ? "bg-violet-500 text-white border border-violet-400 shadow-md shadow-violet-500/40 scale-105"
                    : "bg-white/5 text-slate-600 border border-white/10"
                )}
              >
                <span>{step.icon}</span>
                <span className="hidden sm:inline">{step.label}</span>
              </div>
              {i < STEPS.length - 1 && (
                <div
                  className={cn(
                    "w-3 h-px transition-colors duration-500",
                    i < currentStep ? "bg-violet-500" : "bg-white/10"
                  )}
                />
              )}
            </div>
          ))}
        </div>

        {/* Progress bar */}
        <div className="relative mt-6 h-1 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-violet-500 to-blue-500 rounded-full transition-all duration-1000 ease-out"
            style={{ width: `${((currentStep + 1) / STEPS.length) * 100}%` }}
          />
        </div>

        <p className="relative text-center text-xs text-slate-500 mt-3">
          Step {currentStep + 1} of {STEPS.length} — typical runtime 20–60 seconds
        </p>
      </div>
    </div>
  );
}
