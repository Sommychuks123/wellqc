"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import {
  BarChart3,
  PieChart as PieIcon,
  Building2,
  RefreshCw,
  Layers,
  AlertTriangle,
  ShieldCheck,
  Search,
  ArrowUpRight,
  UploadCloud,
  Compass,
  FileCode2,
} from "lucide-react";
import dynamic from "next/dynamic";
import { safeReadJson } from "@/lib/http-client";
import type { AnalyticsResponse } from "@/lib/api-types";

const OperatorScoreChart = dynamic(
  () => import("@/components/analytics/charts").then((m) => m.OperatorScoreChart),
  { ssr: false }
);
const BasinScoreChart = dynamic(
  () => import("@/components/analytics/charts").then((m) => m.BasinScoreChart),
  { ssr: false }
);
const AnomalyPieChart = dynamic(
  () => import("@/components/analytics/charts").then((m) => m.AnomalyPieChart),
  { ssr: false }
);
const SeverityBarChart = dynamic(
  () => import("@/components/analytics/charts").then((m) => m.SeverityBarChart),
  { ssr: false }
);
const CurveAnomalyChart = dynamic(
  () => import("@/components/analytics/charts").then((m) => m.CurveAnomalyChart),
  { ssr: false }
);
const QualityGradeDonut = dynamic(
  () => import("@/components/analytics/charts").then((m) => m.QualityGradeDonut),
  { ssr: false }
);

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [selectedBasin, setSelectedBasin] = useState("ALL");
  const [selectedOperator, setSelectedOperator] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [reloadTrigger, setReloadTrigger] = useState(0);

  const handleRefresh = useCallback(() => {
    setIsRefreshing(true);
    setReloadTrigger((prev) => prev + 1);
  }, []);

  const handleRetry = useCallback(() => {
    setIsLoading(true);
    setReloadTrigger((prev) => prev + 1);
  }, []);

  const handleBasinChange = useCallback((basin: string) => {
    setSelectedBasin(basin);
    setIsLoading(true);
  }, []);

  const handleOperatorChange = useCallback((operator: string) => {
    setSelectedOperator(operator);
    setIsLoading(true);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function fetchAnalytics() {
      try {
        const params = new URLSearchParams();
        if (selectedBasin !== "ALL") params.set("basin", selectedBasin);
        if (selectedOperator !== "ALL") params.set("operator", selectedOperator);

        const url = `/api/analytics${params.toString() ? `?${params.toString()}` : ""}`;
        const response = await fetch(url, { cache: "no-store" });
        const res = await safeReadJson<AnalyticsResponse>(response, "Unable to load analytics.");

        if (cancelled) return;

        if (!res.ok || !res.data) {
          setError(res.error || "Unable to load analytics.");
        } else {
          setData(res.data);
          setError("");
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unable to load analytics.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
          setIsRefreshing(false);
        }
      }
    }

    fetchAnalytics();

    return () => {
      cancelled = true;
    };
  }, [selectedBasin, selectedOperator, reloadTrigger]);

  const summary = data?.summary;
  const operatorScores = data?.operatorScores || [];
  const basinScores = data?.basinScores || [];
  const anomalyDistribution = data?.anomalyDistribution || [];
  const severityDistribution = data?.severityDistribution || [];
  const curveAnomalyDistribution = data?.curveAnomalyDistribution || [];
  const gradeDistribution = data?.gradeDistribution || [];
  const wells = data?.wells || [];
  const availableBasins = data?.availableBasins || [];
  const availableOperators = data?.availableOperators || [];

  const filteredWells = wells.filter((w) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      w.name.toLowerCase().includes(q) ||
      w.apiNo.toLowerCase().includes(q) ||
      w.operator.toLowerCase().includes(q) ||
      w.field.toLowerCase().includes(q) ||
      w.basin.toLowerCase().includes(q)
    );
  });

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-wellqc-panel/70 border border-wellqc-border p-5 rounded-2xl backdrop-blur-md shadow-lg">
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-blue-500/20 text-cyan-300 border border-cyan-500/40">
                Module 08 - Basin & Operator Analytics
              </span>
              {summary && summary.totalWells > 0 && (
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  {summary.totalWells} Well{summary.totalWells !== 1 ? "s" : ""} Online
                </span>
              )}
            </div>
            <h1 className="text-2xl font-black text-white tracking-tight mt-1">
              Petrophysical Analytics & Subsurface Quality Benchmarks
            </h1>
            <p className="text-xs text-wellqc-muted font-mono mt-0.5">
              Live intelligence aggregated across all uploaded LAS wireline log files, downsampled curves, and quality reports.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            {/* Filter by Basin */}
            <div className="flex items-center space-x-1.5 bg-wellqc-dark/80 border border-wellqc-border rounded-xl px-3 py-1.5 text-xs font-mono">
              <Compass className="w-3.5 h-3.5 text-cyan-400" />
              <select
                aria-label="Filter by basin"
                value={selectedBasin}
                onChange={(e) => handleBasinChange(e.target.value)}
                className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
              >
                <option value="ALL" className="bg-[#0f172a] text-slate-300">All Basins</option>
                {availableBasins.map((b) => (
                  <option key={b} value={b} className="bg-[#0f172a] text-slate-300">{b}</option>
                ))}
              </select>
            </div>

            {/* Filter by Operator */}
            <div className="flex items-center space-x-1.5 bg-wellqc-dark/80 border border-wellqc-border rounded-xl px-3 py-1.5 text-xs font-mono">
              <Building2 className="w-3.5 h-3.5 text-blue-400" />
              <select
                aria-label="Filter by operator"
                value={selectedOperator}
                onChange={(e) => handleOperatorChange(e.target.value)}
                className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
              >
                <option value="ALL" className="bg-[#0f172a] text-slate-300">All Operators</option>
                {availableOperators.map((op) => (
                  <option key={op} value={op} className="bg-[#0f172a] text-slate-300">{op}</option>
                ))}
              </select>
            </div>

            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={isLoading || isRefreshing}
              className="flex items-center space-x-1.5 bg-wellqc-card hover:bg-wellqc-card/80 border border-wellqc-border text-slate-300 hover:text-white px-3 py-1.5 rounded-xl text-xs font-mono transition-colors disabled:opacity-50"
              title="Refresh telemetry"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin text-cyan-400" : ""}`} />
              <span>{isRefreshing ? "Syncing..." : "Refresh"}</span>
            </button>

            {/* Direct Upload Shortcut */}
            <Link
              href="/upload"
              className="flex items-center space-x-1.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold px-3.5 py-1.5 rounded-xl text-xs font-mono shadow-md transition-all"
            >
              <UploadCloud className="w-3.5 h-3.5" />
              <span>Upload LAS</span>
            </Link>
          </div>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-200 rounded-xl px-4 py-3 text-xs font-mono flex items-center justify-between">
            <span>{error}</span>
            <button onClick={handleRetry} className="text-cyan-300 hover:underline">Retry</button>
          </div>
        )}

        {/* 4 Summary Telemetry KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* Card 1: Total Wells */}
          <div className="bg-wellqc-panel/80 border border-wellqc-border p-4 rounded-2xl relative overflow-hidden group">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono text-wellqc-muted uppercase tracking-wider">Total Wells</span>
              <Layers className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="mt-2 flex items-baseline space-x-2">
              <span className="text-3xl font-black text-white font-mono">
                {isLoading ? "..." : summary?.totalWells ?? 0}
              </span>
              <span className="text-xs text-wellqc-muted font-mono">
                ({summary?.totalFiles ?? 0} files)
              </span>
            </div>
            <div className="mt-1 text-[11px] text-cyan-400/80 font-mono">
              Top: {summary?.topOperator || "None"}
            </div>
          </div>

          {/* Card 2: Fleet Quality Score */}
          <div className="bg-wellqc-panel/80 border border-wellqc-border p-4 rounded-2xl relative overflow-hidden group">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono text-wellqc-muted uppercase tracking-wider">Fleet Avg Score</span>
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="mt-2 flex items-baseline space-x-2">
              <span className={`text-3xl font-black font-mono ${
                (summary?.avgQualityScore ?? 0) >= 80 ? "text-emerald-400" :
                (summary?.avgQualityScore ?? 0) >= 60 ? "text-cyan-400" :
                (summary?.avgQualityScore ?? 0) >= 50 ? "text-amber-400" : "text-rose-400"
              }`}>
                {isLoading ? "..." : `${summary?.avgQualityScore ?? 0}%`}
              </span>
              <span className="text-xs text-emerald-400 font-mono">
                {isLoading ? "" : (summary?.avgQualityScore ?? 0) >= 75 ? "HEALTHY" : "NEEDS REVIEW"}
              </span>
            </div>
            <div className="mt-1 text-[11px] text-wellqc-muted font-mono">
              {summary?.cleanWellsCount ?? 0} passing · {summary?.flaggedWellsCount ?? 0} flagged
            </div>
          </div>

          {/* Card 3: Detected Anomalies */}
          <div className="bg-wellqc-panel/80 border border-wellqc-border p-4 rounded-2xl relative overflow-hidden group">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono text-wellqc-muted uppercase tracking-wider">Quality Anomalies</span>
              <AlertTriangle className="w-4 h-4 text-amber-400" />
            </div>
            <div className="mt-2 flex items-baseline space-x-2">
              <span className="text-3xl font-black text-amber-400 font-mono">
                {isLoading ? "..." : summary?.totalAnomalies ?? 0}
              </span>
              {summary && summary.criticalAnomalies > 0 && (
                <span className="text-xs px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 font-mono">
                  {summary.criticalAnomalies} Critical
                </span>
              )}
            </div>
            <div className="mt-1 text-[11px] text-wellqc-muted font-mono">
              Across all ingested wireline logs
            </div>
          </div>

          {/* Card 4: Dominant Basin */}
          <div className="bg-wellqc-panel/80 border border-wellqc-border p-4 rounded-2xl relative overflow-hidden group">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono text-wellqc-muted uppercase tracking-wider">Active Basin</span>
              <Compass className="w-4 h-4 text-purple-400" />
            </div>
            <div className="mt-2 flex items-baseline space-x-2">
              <span className="text-lg font-bold text-white font-mono truncate" title={summary?.topBasin}>
                {isLoading ? "..." : summary?.topBasin || "N/A"}
              </span>
            </div>
            <div className="mt-1 text-[11px] text-purple-400/80 font-mono">
              {basinScores.length} basin region{basinScores.length !== 1 ? "s" : ""} indexed
            </div>
          </div>
        </div>

        {/* Charts Row 1: Operator Benchmark & Basin Benchmark */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Operator Scores */}
          <div className="bg-wellqc-panel border border-wellqc-border p-5 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white font-mono flex items-center space-x-2">
                <Building2 className="w-4 h-4 text-cyan-400" />
                <span>Operator Quality Score Benchmark</span>
              </h3>
              <span className="text-[11px] text-wellqc-muted font-mono">0-100% Avg Score</span>
            </div>
            <div className="h-72 w-full">
              {isLoading ? (
                <LoadingPanel label="Computing operator benchmarks..." />
              ) : operatorScores.length === 0 ? (
                <EmptyPanel label="No uploaded wells found for this filter" />
              ) : (
                <OperatorScoreChart data={operatorScores} />
              )}
            </div>
          </div>

          {/* Basin Regional Benchmark */}
          <div className="bg-wellqc-panel border border-wellqc-border p-5 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white font-mono flex items-center space-x-2">
                <Compass className="w-4 h-4 text-blue-400" />
                <span>Basin & Regional Log Quality</span>
              </h3>
              <span className="text-[11px] text-wellqc-muted font-mono">Stratigraphic Averages</span>
            </div>
            <div className="h-72 w-full">
              {isLoading ? (
                <LoadingPanel label="Calculating regional basin averages..." />
              ) : basinScores.length === 0 ? (
                <EmptyPanel label="No basin records found" />
              ) : (
                <BasinScoreChart data={basinScores} />
              )}
            </div>
          </div>
        </div>

        {/* Charts Row 2: Anomaly Category Distribution & Severity / Curve Impact */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Donut Chart: Anomaly Types */}
          <div className="lg:col-span-2 bg-wellqc-panel border border-wellqc-border p-5 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white font-mono flex items-center space-x-2">
                <PieIcon className="w-4 h-4 text-amber-400" />
                <span>Petrophysical Anomaly Breakdown</span>
              </h3>
              <span className="text-[11px] text-wellqc-muted font-mono">
                {summary?.totalAnomalies ?? 0} flags total
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
              <div className="md:col-span-6 h-64 w-full flex items-center justify-center">
                {isLoading ? (
                  <LoadingPanel label="Analyzing anomaly distribution..." />
                ) : anomalyDistribution.length === 0 ? (
                  <EmptyPanel label="No anomalies recorded" />
                ) : (
                  <AnomalyPieChart data={anomalyDistribution} />
                )}
              </div>

              {/* Dynamic Legend */}
              <div className="md:col-span-6 space-y-1.5 max-h-64 overflow-y-auto pr-1">
                {anomalyDistribution.length === 0 ? (
                  <p className="text-xs text-wellqc-muted font-mono italic">Zero anomalies across selected wells.</p>
                ) : (
                  anomalyDistribution.map((entry) => (
                    <div
                      key={entry.name}
                      className="flex items-center justify-between text-xs font-mono p-1.5 rounded-lg hover:bg-wellqc-dark/50 transition-colors"
                    >
                      <div className="flex items-center space-x-2 truncate">
                        <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: entry.color }} />
                        <span className="text-slate-300 truncate" title={entry.name}>{entry.name}</span>
                      </div>
                      <div className="flex items-center space-x-2 ml-2 flex-shrink-0">
                        <span className="text-white font-bold">{entry.value}</span>
                        {entry.percentage !== undefined && (
                          <span className="text-slate-400 text-[10px]">({entry.percentage}%)</span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Anomaly Severity Breakdown */}
          <div className="bg-wellqc-panel border border-wellqc-border p-5 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white font-mono flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <span>Severity Distribution</span>
              </h3>
              <span className="text-[11px] text-wellqc-muted font-mono">Risk Profile</span>
            </div>
            <div className="h-64 w-full">
              {isLoading ? (
                <LoadingPanel label="Classifying severity..." />
              ) : severityDistribution.length === 0 ? (
                <EmptyPanel label="No severity flags recorded" />
              ) : (
                <SeverityBarChart data={severityDistribution} />
              )}
            </div>
          </div>
        </div>

        {/* Charts Row 3: Curve-Level Anomaly Impact & Grade Tiers */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Impacted Curves */}
          <div className="bg-wellqc-panel border border-wellqc-border p-5 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white font-mono flex items-center space-x-2">
                <FileCode2 className="w-4 h-4 text-cyan-400" />
                <span>Most Impacted Logging Curve Channels</span>
              </h3>
              <span className="text-[11px] text-wellqc-muted font-mono">Top Anomaly Frequencies</span>
            </div>
            <div className="h-64 w-full">
              {isLoading ? (
                <LoadingPanel label="Auditing curve channels..." />
              ) : curveAnomalyDistribution.length === 0 ? (
                <EmptyPanel label="No curve-level anomalies detected" />
              ) : (
                <CurveAnomalyChart data={curveAnomalyDistribution} />
              )}
            </div>
          </div>

          {/* Well Quality Grade Tiers */}
          <div className="bg-wellqc-panel border border-wellqc-border p-5 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white font-mono flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Well Quality Grade Distribution</span>
              </h3>
              <span className="text-[11px] text-wellqc-muted font-mono">Certification Tiers</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
              <div className="md:col-span-7 h-64 w-full flex items-center justify-center">
                {isLoading ? (
                  <LoadingPanel label="Calculating grade tiers..." />
                ) : gradeDistribution.length === 0 ? (
                  <EmptyPanel label="No grade distribution data" />
                ) : (
                  <QualityGradeDonut data={gradeDistribution} />
                )}
              </div>

              <div className="md:col-span-5 space-y-2">
                {gradeDistribution.map((entry) => (
                  <div key={entry.grade} className="flex items-center justify-between p-2 rounded-xl bg-wellqc-dark/50 border border-wellqc-border text-xs font-mono">
                    <div className="flex items-center space-x-2">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
                      <span className="text-slate-200 font-bold">{entry.grade}</span>
                    </div>
                    <span className="text-white font-mono font-bold">{entry.count} well{entry.count !== 1 ? "s" : ""}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Uploaded Wells Subsurface Scorecard Table */}
        <div className="bg-wellqc-panel border border-wellqc-border rounded-2xl overflow-hidden shadow-lg space-y-4 p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-base font-bold text-white font-mono flex items-center space-x-2">
                <Layers className="w-4 h-4 text-cyan-400" />
                <span>Uploaded Wells Subsurface Scorecard</span>
              </h3>
              <p className="text-xs text-wellqc-muted font-mono mt-0.5">
                Audit summary and quality scores for all wells currently stored in your workspace.
              </p>
            </div>

            {/* Search Input */}
            <div className="relative w-full sm:w-64">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-wellqc-muted" />
              <input
                type="text"
                placeholder="Search well, API, operator..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-wellqc-dark/80 border border-wellqc-border rounded-xl pl-8 pr-3 py-1.5 text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs font-mono">
              <thead>
                <tr className="border-b border-wellqc-border text-slate-400 bg-wellqc-dark/40">
                  <th className="py-2.5 px-3 font-bold">Well Name & API</th>
                  <th className="py-2.5 px-3 font-bold">Operator</th>
                  <th className="py-2.5 px-3 font-bold">Basin & Field</th>
                  <th className="py-2.5 px-3 font-bold text-center">LAS Files</th>
                  <th className="py-2.5 px-3 font-bold text-center">Anomalies</th>
                  <th className="py-2.5 px-3 font-bold text-right">Quality Score</th>
                  <th className="py-2.5 px-3 font-bold text-center">Grade</th>
                  <th className="py-2.5 px-3 font-bold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-wellqc-border/40 text-slate-300">
                {isLoading ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-cyan-300 font-mono">
                      <RefreshCw className="w-4 h-4 animate-spin inline-block mr-2" />
                      Loading uploaded well telemetry...
                    </td>
                  </tr>
                ) : filteredWells.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-wellqc-muted font-mono">
                      {wells.length === 0 ? (
                        <div className="space-y-2">
                          <p>No uploaded wells found in this workspace.</p>
                          <Link href="/upload" className="text-cyan-400 hover:underline inline-flex items-center space-x-1">
                            <span>Upload a LAS file to view analytics</span>
                            <ArrowUpRight className="w-3.5 h-3.5" />
                          </Link>
                        </div>
                      ) : (
                        "No wells match your search query."
                      )}
                    </td>
                  </tr>
                ) : (
                  filteredWells.map((well) => (
                    <tr key={well.id} className="hover:bg-wellqc-dark/40 transition-colors">
                      <td className="py-3 px-3">
                        <div className="font-bold text-white">{well.name}</div>
                        <div className="text-[10px] text-wellqc-muted">{well.apiNo}</div>
                      </td>
                      <td className="py-3 px-3 text-slate-300 font-medium">{well.operator}</td>
                      <td className="py-3 px-3">
                        <div className="text-slate-200">{well.basin}</div>
                        <div className="text-[10px] text-wellqc-muted">{well.field}</div>
                      </td>
                      <td className="py-3 px-3 text-center text-slate-300 font-bold">{well.filesCount}</td>
                      <td className="py-3 px-3 text-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          well.anomalyCount > 0 ? "bg-amber-500/20 text-amber-300 border border-amber-500/30" : "bg-emerald-500/20 text-emerald-300"
                        }`}>
                          {well.anomalyCount}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-right">
                        <span className={`text-sm font-bold ${
                          well.qualityScore >= 80 ? "text-emerald-400" :
                          well.qualityScore >= 60 ? "text-cyan-400" :
                          well.qualityScore >= 50 ? "text-amber-400" : "text-rose-400"
                        }`}>
                          {well.qualityScore}%
                        </span>
                      </td>
                      <td className="py-3 px-3 text-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          well.qualityGrade === "EXCELLENT" ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30" :
                          well.qualityGrade === "GOOD" ? "bg-blue-500/20 text-blue-300 border border-blue-500/30" :
                          well.qualityGrade === "POOR" ? "bg-amber-500/20 text-amber-300 border border-amber-500/30" :
                          "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                        }`}>
                          {well.qualityGrade}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-right">
                        <Link
                          href={`/wells/${well.id}`}
                          className="inline-flex items-center space-x-1 text-cyan-400 hover:text-cyan-300 font-bold text-xs"
                        >
                          <span>Log Viewer</span>
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

function LoadingPanel({ label }: { label: string }) {
  return (
    <div className="h-full rounded-xl bg-wellqc-card/60 border border-wellqc-border flex items-center justify-center text-xs text-cyan-300 font-mono">
      <RefreshCw className="w-4 h-4 animate-spin mr-2" />
      {label}
    </div>
  );
}

function EmptyPanel({ label }: { label: string }) {
  return (
    <div className="h-full rounded-xl bg-wellqc-card/60 border border-wellqc-border flex flex-col items-center justify-center text-xs text-wellqc-muted font-mono">
      <BarChart3 className="w-5 h-5 text-cyan-400 mb-2" />
      {label}
    </div>
  );
}