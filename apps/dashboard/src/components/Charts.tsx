import React, { useMemo } from "react";
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Competition } from "../types";
import { getPlatformStyle } from "../utils/format";

interface ChartsProps {
  competitions: Competition[];
  onSelectPlatform: (platform: string) => void;
  onSelectCategory: (category: string) => void;
}

const CATEGORY_PALETTE = [
  "#34d399",
  "#818cf8",
  "#22d3ee",
  "#fbbf24",
  "#c084fc",
  "#f472b6",
  "#fb923c",
  "#38bdf8",
  "#a3e635",
];

export const Charts: React.FC<ChartsProps> = ({
  competitions,
  onSelectPlatform,
  onSelectCategory,
}) => {
  const platformData = useMemo(() => {
    const counts: Record<string, { count: number; prize: number }> = {};
    for (const c of competitions) {
      if (!counts[c.platform]) counts[c.platform] = { count: 0, prize: 0 };
      counts[c.platform].count += 1;
      counts[c.platform].prize += c.prize_usd || 0;
    }
    return Object.entries(counts)
      .map(([name, v]) => ({
        name,
        count: v.count,
        prize: v.prize,
        color: getPlatformStyle(name).dot,
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
  }, [competitions]);

  const categoryData = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const c of competitions) {
      counts[c.category] = (counts[c.category] ?? 0) + 1;
    }
    return Object.entries(counts)
      .map(([name, value], idx) => ({
        name,
        value,
        color: CATEGORY_PALETTE[idx % CATEGORY_PALETTE.length],
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 9);
  }, [competitions]);

  if (competitions.length === 0) return null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-3.5">
      {/* Platform Distribution */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 backdrop-blur-md p-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Active Quant Arenas by Venue
            </h3>
            <p className="text-[11px] text-slate-500">Click any bar to filter by quant platform</p>
          </div>
        </div>
        <div className="h-52">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={platformData} layout="vertical" margin={{ left: 12, right: 18, top: 4, bottom: 4 }}>
              <XAxis type="number" hide />
              <YAxis
                type="category"
                dataKey="name"
                width={135}
                tick={{ fill: "#cbd5e1", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                cursor={{ fill: "rgba(148, 163, 184, 0.08)" }}
                contentStyle={{
                  backgroundColor: "#0f172a",
                  borderColor: "#1e293b",
                  borderRadius: "0.5rem",
                  fontSize: "12px",
                  color: "#f8fafc",
                }}
              />
              <Bar
                dataKey="count"
                radius={[0, 6, 6, 0]}
                className="cursor-pointer"
                onClick={(entry) => {
                  if (entry?.name) onSelectPlatform(String(entry.name));
                }}
              >
                {platformData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Category Distribution */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 backdrop-blur-md p-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Quantitative Domain Taxonomy
            </h3>
            <p className="text-[11px] text-slate-500">Click a slice or legend item to filter by domain</p>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 items-center gap-2 h-52">
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categoryData}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={44}
                  outerRadius={72}
                  paddingAngle={3}
                  className="cursor-pointer"
                  onClick={(entry) => {
                    if (entry?.name) onSelectCategory(String(entry.name));
                  }}
                >
                  {categoryData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} stroke="rgba(15,23,42,0.8)" />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#1e293b",
                    borderRadius: "0.5rem",
                    fontSize: "12px",
                    color: "#f8fafc",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-1.5 overflow-y-auto max-h-48 pr-1">
            {categoryData.map((cat) => (
              <button
                key={cat.name}
                type="button"
                onClick={() => onSelectCategory(cat.name)}
                className="w-full flex items-center justify-between px-2 py-1 rounded-md text-xs text-slate-300 hover:bg-slate-800/70 transition-colors"
              >
                <div className="flex items-center gap-2 truncate">
                  <span
                    className="w-2.5 h-2.5 rounded-full shrink-0"
                    style={{ backgroundColor: cat.color }}
                  />
                  <span className="truncate">{cat.name}</span>
                </div>
                <span className="text-slate-400 font-medium tabular-nums ml-2">{cat.value}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

