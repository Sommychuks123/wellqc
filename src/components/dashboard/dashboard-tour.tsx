"use client";

import { useState, useEffect, useCallback, useRef, useSyncExternalStore } from "react";
import Link from "next/link";
import {
  Sparkles,
  ChevronRight,
  ChevronLeft,
  X,
  Compass,
  CheckCircle2,
  ArrowRight,
  Sliders,
  Filter,
  BarChart3,
  TrendingUp,
  PlusCircle,
} from "lucide-react";

export interface TourStep {
  id: string;
  targetId?: string; // HTML element ID to spotlight; if omitted, modal is centered
  title: string;
  badge?: string;
  description: string;
  icon?: React.ReactNode;
  tips?: string;
  preferredPlacement?: "bottom" | "top" | "center";
}

const TOUR_STEPS: TourStep[] = [
  {
    id: "welcome",
    title: "Welcome to WellQC Asset Platform",
    badge: "Getting Started",
    icon: <Sparkles className="w-5 h-5 text-cyan-400" />,
    description:
      "WellQC automates petrophysical LAS log quality assurance, standardises curve mnemonics, detects sensor anomalies, and produces interpretation-ready well datasets. Let's take a quick 1-minute tour of your dashboard!",
    preferredPlacement: "center",
  },
  {
    id: "dashboard-mode",
    targetId: "tour-dashboard-mode",
    title: "1. Tailor Your Telemetry View",
    badge: "Display Themes",
    icon: <Sliders className="w-5 h-5 text-cyan-400" />,
    description:
      "Switch between 3 specialised operational views: Executive (Calm) for C-suite KPIs and risk summaries, Operational for fleet distributions, and Full Telemetry for all 18 engineering metrics and scan tables.",
    tips: "Your preferred mode is automatically remembered on your device.",
    preferredPlacement: "bottom",
  },
  {
    id: "scope-filter",
    targetId: "tour-scope-filter",
    title: "2. Filter Assets By Verification Health",
    badge: "Asset Scopes",
    icon: <Filter className="w-5 h-5 text-cyan-400" />,
    description:
      "Filter your subsurface portfolio in one click: All Wells for the entire catalog, Uploaded for verified production-ready logs, and Flagged for assets requiring automated remediation.",
    preferredPlacement: "bottom",
  },
  {
    id: "kpi-grid",
    targetId: "tour-kpi-grid",
    title: "3. Fleet Health & QA Index Cards",
    badge: "Quality Index",
    icon: <BarChart3 className="w-5 h-5 text-cyan-400" />,
    description:
      "Review your corporate Composite Quality Score, verified LAS volumes, and high-impact severity alert cards highlighting critical vs moderate faults.",
    preferredPlacement: "bottom",
  },
  {
    id: "trend-section",
    targetId: "tour-trend-section",
    title: "4. Composite Dial & Ingestion Trends",
    badge: "Analytics Engine",
    icon: <TrendingUp className="w-5 h-5 text-cyan-400" />,
    description:
      "Track your API RP 66 benchmark quality gauge alongside 7-day ingestion volume trajectories and active ML auto-clean engine throughput.",
    preferredPlacement: "top",
  },
  {
    id: "actions",
    targetId: "tour-actions",
    title: "5. Ingest New Logs & Well Registry",
    badge: "Actions & Tools",
    icon: <PlusCircle className="w-5 h-5 text-cyan-400" />,
    description:
      "Click '+' to upload and inspect raw LAS files, test curves against physical limits, preview wireline tracks, and upload validated datasets into your database.",
    preferredPlacement: "bottom",
  },
  {
    id: "completed",
    title: "You're Ready to Explore WellQC!",
    badge: "Tour Complete",
    icon: <CheckCircle2 className="w-5 h-5 text-emerald-400" />,
    description:
      "You now know your way around the platform. You can relaunch this tour at any time by clicking the 'Tour Guide' button in the dashboard header.",
    preferredPlacement: "center",
  },
];

const TOUR_STORAGE_KEY = "wellqc_dashboard_tour_completed_v1";

function subscribeToTourStorage(callback: () => void) {
  if (typeof window === "undefined") return () => {};
  window.addEventListener("storage", callback);
  window.addEventListener("wellqc_tour_updated", callback);
  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener("wellqc_tour_updated", callback);
  };
}

function getTourStorageSnapshot(): boolean {
  if (typeof window === "undefined") return true;
  try {
    return Boolean(localStorage.getItem(TOUR_STORAGE_KEY));
  } catch {
    return false;
  }
}

function getTourStorageServerSnapshot(): boolean {
  return true;
}

export function useIsTourCompleted(): boolean {
  return useSyncExternalStore(
    subscribeToTourStorage,
    getTourStorageSnapshot,
    getTourStorageServerSnapshot
  );
}

interface DashboardTourProps {
  isOpen: boolean;
  onClose: () => void;
  onStart?: () => void;
}

export function DashboardTour({ isOpen, onClose }: DashboardTourProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);
  const cardRef = useRef<HTMLDivElement>(null);

  const currentStep = TOUR_STEPS[currentStepIndex] || TOUR_STEPS[0];
  const isFirstStep = currentStepIndex === 0;
  const isLastStep = currentStepIndex === TOUR_STEPS.length - 1;

  // Measure and scroll target element into view
  const updateTargetRect = useCallback(() => {
    if (!currentStep.targetId) {
      setTargetRect(null);
      return;
    }

    const el =
      document.getElementById(currentStep.targetId) ||
      (currentStep.targetId === "tour-trend-section"
        ? document.getElementById("tour-trend-section-alt")
        : null);
    if (el) {
      const rect = el.getBoundingClientRect();
      setTargetRect(rect);
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    } else {
      setTargetRect(null);
    }
  }, [currentStep.targetId]);

  useEffect(() => {
    if (!isOpen) return;

    // Small delay to allow scroll and rendering
    const timer = setTimeout(() => {
      updateTargetRect();
    }, 150);

    const handleResize = () => updateTargetRect();
    window.addEventListener("resize", handleResize);
    window.addEventListener("scroll", handleResize, { passive: true });

    return () => {
      clearTimeout(timer);
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("scroll", handleResize);
    };
  }, [isOpen, currentStepIndex, updateTargetRect]);

  const handleComplete = useCallback(() => {
    try {
      localStorage.setItem(TOUR_STORAGE_KEY, "true");
      window.dispatchEvent(new Event("wellqc_tour_updated"));
    } catch {}
    onClose();
  }, [onClose]);

  const handleDismiss = useCallback(() => {
    try {
      localStorage.setItem(TOUR_STORAGE_KEY, "true");
      window.dispatchEvent(new Event("wellqc_tour_updated"));
    } catch {}
    onClose();
  }, [onClose]);

  const handleNext = useCallback(() => {
    if (isLastStep) {
      handleComplete();
    } else {
      setCurrentStepIndex((prev) => prev + 1);
    }
  }, [isLastStep, handleComplete]);

  const handlePrev = useCallback(() => {
    if (!isFirstStep) {
      setCurrentStepIndex((prev) => prev - 1);
    }
  }, [isFirstStep]);

  // Keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        handleDismiss();
      } else if (e.key === "ArrowRight") {
        if (!isLastStep) setCurrentStepIndex((prev) => prev + 1);
      } else if (e.key === "ArrowLeft") {
        if (!isFirstStep) setCurrentStepIndex((prev) => prev - 1);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, isFirstStep, isLastStep, handleDismiss]);

  if (!isOpen) return null;

  // Compute tooltip card position relative to target or viewport center
  const getCardPositionStyle = (): React.CSSProperties => {
    if (!targetRect || currentStep.preferredPlacement === "center") {
      return {
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        position: "fixed",
      };
    }

    const cardWidth = 420;
    const padding = 16;
    const viewportWidth = typeof window !== "undefined" ? window.innerWidth : 1200;
    const viewportHeight = typeof window !== "undefined" ? window.innerHeight : 800;

    let left = targetRect.left + targetRect.width / 2 - cardWidth / 2;
    // Keep inside horizontal viewport
    left = Math.max(padding, Math.min(left, viewportWidth - cardWidth - padding));

    let top = 0;
    if (currentStep.preferredPlacement === "top") {
      top = Math.max(padding, targetRect.top - 240);
    } else {
      top = Math.min(viewportHeight - 260, targetRect.bottom + 16);
    }

    return {
      top: `${Math.round(top)}px`,
      left: `${Math.round(left)}px`,
      position: "fixed",
    };
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden font-sans select-none pointer-events-auto">
      {/* Dark backdrop with blur */}
      <div
        onClick={handleDismiss}
        className="absolute inset-0 bg-slate-950/75 backdrop-blur-[2px] transition-opacity duration-300"
      />

      {/* Target Element Spotlight Cutout Ring */}
      {targetRect && (
        <div
          className="fixed rounded-2xl border-2 border-cyan-400 pointer-events-none transition-all duration-300 z-50 shadow-[0_0_0_9999px_rgba(2,6,23,0.7),0_0_25px_rgba(6,182,212,0.4)]"
          style={{
            top: `${Math.max(0, targetRect.top - 6)}px`,
            left: `${Math.max(0, targetRect.left - 6)}px`,
            width: `${targetRect.width + 12}px`,
            height: `${targetRect.height + 12}px`,
          }}
        />
      )}

      {/* Floating Tour Guide Dialog Card */}
      <div
        ref={cardRef}
        style={getCardPositionStyle()}
        className="w-[92vw] sm:w-[420px] bg-slate-900/95 dark:bg-slate-900/95 border border-cyan-500/40 rounded-3xl shadow-2xl z-[60] overflow-hidden text-slate-100 backdrop-blur-xl animate-in fade-in zoom-in-95 duration-200"
      >
        {/* Top Header Strip */}
        <div className="p-4 bg-gradient-to-r from-cyan-950/40 via-slate-900 to-slate-900 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="p-1.5 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              {currentStep.icon || <Compass className="w-4 h-4" />}
            </span>
            <div>
              <span className="text-[10px] font-mono uppercase font-bold tracking-wider text-cyan-400 block">
                {currentStep.badge || "WellQC Walkthrough"}
              </span>
              <span className="text-xs font-mono text-slate-400">
                Step {currentStepIndex + 1} of {TOUR_STEPS.length}
              </span>
            </div>
          </div>

          <button
            onClick={handleDismiss}
            className="p-1.5 rounded-full text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            title="Exit Tour (Esc)"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-5 space-y-3.5">
          <h3 className="text-base font-extrabold text-white tracking-tight leading-snug">
            {currentStep.title}
          </h3>

          <p className="text-xs text-slate-300 leading-relaxed">
            {currentStep.description}
          </p>

          {currentStep.tips && (
            <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-[11px] text-cyan-300 font-mono flex items-start space-x-2">
              <span className="font-bold shrink-0">💡 Tip:</span>
              <span>{currentStep.tips}</span>
            </div>
          )}

          {/* Quick links on completion step */}
          {isLastStep && (
            <div className="grid grid-cols-2 gap-2 pt-2">
              <Link
                href="/upload"
                onClick={handleComplete}
                className="p-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs flex items-center justify-center space-x-1.5 transition-all shadow-md active:scale-95"
              >
                <span>Ingest First Log</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
              <Link
                href="/wells"
                onClick={handleComplete}
                className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs flex items-center justify-center space-x-1.5 transition-colors border border-slate-700"
              >
                <span>Well Registry</span>
              </Link>
            </div>
          )}
        </div>

        {/* Navigation Controls Footer */}
        <div className="p-4 bg-slate-950/60 border-t border-slate-800/80 flex items-center justify-between">
          {/* Progress Dots */}
          <div className="flex items-center space-x-1.5">
            {TOUR_STEPS.map((step, idx) => (
              <button
                key={step.id}
                onClick={() => setCurrentStepIndex(idx)}
                className={`w-2 h-2 rounded-full transition-all ${
                  idx === currentStepIndex
                    ? "w-5 bg-cyan-400"
                    : idx < currentStepIndex
                    ? "bg-cyan-700"
                    : "bg-slate-700 hover:bg-slate-600"
                }`}
                title={`Go to Step ${idx + 1}: ${step.title}`}
              />
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            {!isFirstStep && (
              <button
                type="button"
                onClick={handlePrev}
                className="px-3 py-1.5 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 text-xs font-mono font-bold transition-colors flex items-center space-x-1"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                <span>Back</span>
              </button>
            )}

            <button
              type="button"
              onClick={handleNext}
              className="px-4 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-slate-950 font-mono font-extrabold text-xs transition-all shadow-md flex items-center space-x-1 active:scale-95"
            >
              <span>{isLastStep ? "Finish" : isFirstStep ? "Start Tour" : "Next"}</span>
              {!isLastStep && <ChevronRight className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Welcoming Onboarding Banner shown for users who have not taken or completed the tour yet.
 */
export function OnboardingWelcomeBanner({ onStartTour }: { onStartTour: () => void }) {
  const isCompleted = useIsTourCompleted();
  const [isLocallyDismissed, setIsLocallyDismissed] = useState(false);

  const handleDismiss = () => {
    setIsLocallyDismissed(true);
    try {
      localStorage.setItem(TOUR_STORAGE_KEY, "dismissed");
      window.dispatchEvent(new Event("wellqc_tour_updated"));
    } catch {}
  };

  if (isCompleted || isLocallyDismissed) return null;

  return (
    <div className="bg-gradient-to-r from-cyan-950/80 via-slate-900/90 to-blue-950/80 border border-cyan-500/30 rounded-2xl p-3.5 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs font-mono shadow-lg backdrop-blur-md animate-in fade-in slide-in-from-top-2 duration-300">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center shrink-0 border border-cyan-500/30">
          <Sparkles className="w-4 h-4 animate-pulse" />
        </div>
        <div>
          <span className="font-bold text-white text-xs block font-sans">
            Welcome to WellQC! New here?
          </span>
          <span className="text-slate-300 text-[11px] leading-tight">
            Take a quick 1-minute guided tour to explore automated QA diagnostics, multi-track wireline views, and fleet verification.
          </span>
        </div>
      </div>

      <div className="flex items-center space-x-2 shrink-0 w-full sm:w-auto justify-end">
        <button
          onClick={onStartTour}
          className="px-4 py-1.5 rounded-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition-all shadow-md active:scale-95 flex items-center space-x-1.5"
        >
          <Compass className="w-3.5 h-3.5" />
          <span>Start Tour</span>
        </button>
        <button
          onClick={handleDismiss}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          title="Dismiss Banner"
          aria-label="Dismiss banner"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}

/**
 * Compact "Tour Guide" button to be placed in top headers or toolbars.
 */
export function TourGuideButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 border border-slate-300 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-all shadow-sm font-mono text-[11px] font-bold active:scale-95 group"
      title="Launch Interactive Dashboard Tour"
    >
      <Compass className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 group-hover:rotate-45 transition-transform" />
      <span>Tour Guide</span>
    </button>
  );
}
