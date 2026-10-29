"use client";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
} from "recharts";

interface OperatorScore {
  operator: string;
  score: number;
  files?: number;
  wells?: number;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    name?: string;
    value?: number | string;
    payload?: Record<string, unknown>;
  }>;
  label?: string;
}

function CustomBarTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload || !payload.length) return null;
  const data = payload[0].payload as OperatorScore | undefined;
  return (
    <div className="bg-[#0f172a]/95 border border-cyan-500/30 rounded-xl p-3 shadow-xl backdrop-blur-md text-xs font-mono text-slate-200 min-w-44">
      <p className="font-bold text-white mb-1">{label || data?.operator}</p>
      <div className="space-y-1">
        <div className="flex justify-between items-center text-cyan-300">
          <span>Avg Quality Score:</span>
          <span className="font-bold">{data?.score ?? payload[0].value}%</span>
        </div>
        {data?.wells !== undefined && (
          <div className="flex justify-between items-center text-slate-400">
            <span>Wells:</span>
            <span>{data.wells}</span>
          </div>
        )}
        {data?.files !== undefined && (
          <div className="flex justify-between items-center text-slate-400">
            <span>LAS Files:</span>
            <span>{data.files}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export function OperatorScoreChart({ data }: { data: OperatorScore[] }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 10, right: 15, left: -10, bottom: 25 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
        <XAxis
          dataKey="operator"
          stroke="#94a3b8"
          tick={{ fontSize: 11, fill: "#94a3b8" }}
          angle={-20}
          textAnchor="end"
          height={40}
        />
        <YAxis stroke="#94a3b8" tick={{ fontSize: 11, fill: "#94a3b8" }} domain={[0, 100]} />
        <Tooltip content={<CustomBarTooltip />} cursor={{ fill: "rgba(6, 182, 212, 0.08)" }} />
        <Bar dataKey="score" fill="#06b6d4" radius={[6, 6, 0, 0]} maxBarSize={45} />
      </BarChart>
    </ResponsiveContainer>
  );
}

interface BasinScore {
  basin: string;
  score: number;
  wells?: number;
  files?: number;
}

export function BasinScoreChart({ data }: { data: BasinScore[] }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 10, right: 15, left: -10, bottom: 25 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
        <XAxis
          dataKey="basin"
          stroke="#94a3b8"
          tick={{ fontSize: 11, fill: "#94a3b8" }}
          angle={-20}
          textAnchor="end"
          height={40}
        />
        <YAxis stroke="#94a3b8" tick={{ fontSize: 11, fill: "#94a3b8" }} domain={[0, 100]} />
        <Tooltip
          contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
          cursor={{ fill: "rgba(59, 130, 246, 0.08)" }}
        />
        <Bar dataKey="score" fill="#3b82f6" radius={[6, 6, 0, 0]} maxBarSize={45} />
      </BarChart>
    </ResponsiveContainer>
  );
}

interface AnomalySlice {
  name?: string;
  value: number;
  color: string;
  percentage?: number;
  [key: string]: unknown;
}

function CustomPieTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload || !payload.length) return null;
  const data = payload[0].payload as AnomalySlice | undefined;
  return (
    <div className="bg-[#0f172a]/95 border border-slate-700 rounded-xl p-3 shadow-xl backdrop-blur-md text-xs font-mono text-slate-200">
      <div className="flex items-center space-x-2 mb-1">
        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: data?.color || "#06b6d4" }} />
        <span className="font-bold text-white">{data?.name || "Anomaly"}</span>
      </div>
      <div className="flex items-center justify-between space-x-4 text-slate-300">
        <span>Occurrences:</span>
        <span className="font-bold text-white">{data?.value}</span>
      </div>
      {data?.percentage !== undefined && (
        <div className="flex items-center justify-between space-x-4 text-slate-400">
          <span>Proportion:</span>
          <span>{data.percentage}%</span>
        </div>
      )}
    </div>
  );
}

export function AnomalyPieChart({ data }: { data: AnomalySlice[] }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={55}
          outerRadius={85}
          paddingAngle={3}
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} stroke="#0b1120" strokeWidth={2} />
          ))}
        </Pie>
        <Tooltip content={<CustomPieTooltip />} />
      </PieChart>
    </ResponsiveContainer>
  );
}

interface SeveritySlice {
  severity: string;
  count: number;
  color: string;
}

export function SeverityBarChart({ data }: { data: SeveritySlice[] }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} layout="vertical" margin={{ top: 10, right: 20, left: 30, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
        <XAxis type="number" stroke="#94a3b8" tick={{ fontSize: 11 }} />
        <YAxis dataKey="severity" type="category" stroke="#94a3b8" tick={{ fontSize: 11 }} width={75} />
        <Tooltip contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }} />
        <Bar dataKey="count" radius={[0, 4, 4, 0]} maxBarSize={25}>
          {data.map((entry, index) => (
            <Cell key={`sev-cell-${index}`} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

interface CurveAnomaly {
  curve: string;
  count: number;
}

export function CurveAnomalyChart({ data }: { data: CurveAnomaly[] }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 10, right: 15, left: -10, bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
        <XAxis dataKey="curve" stroke="#94a3b8" tick={{ fontSize: 11 }} />
        <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
        <Tooltip contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }} />
        <Bar dataKey="count" fill="#f59e0b" radius={[6, 6, 0, 0]} maxBarSize={38} />
      </BarChart>
    </ResponsiveContainer>
  );
}

interface GradeSlice {
  grade: string;
  count: number;
  color: string;
}

export function QualityGradeDonut({ data }: { data: GradeSlice[] }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={45}
          outerRadius={75}
          paddingAngle={4}
          dataKey="count"
          nameKey="grade"
        >
          {data.map((entry, index) => (
            <Cell key={`grade-cell-${index}`} fill={entry.color} stroke="#0b1120" strokeWidth={2} />
          ))}
        </Pie>
        <Tooltip contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }} />
      </PieChart>
    </ResponsiveContainer>
  );
}