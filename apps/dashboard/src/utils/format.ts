import { CompetitionStatus, DifficultyLevel } from "../types";

export const PLATFORM_COLORS: Record<
  string,
  { bg: string; text: string; border: string; dot: string }
> = {
  Numerai: {
    bg: "bg-amber-500/10",
    text: "text-amber-300",
    border: "border-amber-500/30",
    dot: "#fbbf24",
  },
  CrunchDAO: {
    bg: "bg-indigo-500/10",
    text: "text-indigo-300",
    border: "border-indigo-500/30",
    dot: "#818cf8",
  },
  "WorldQuant BRAIN": {
    bg: "bg-cyan-500/10",
    text: "text-cyan-300",
    border: "border-cyan-500/30",
    dot: "#22d3ee",
  },
  "Wunder Fund": {
    bg: "bg-emerald-500/10",
    text: "text-emerald-300",
    border: "border-emerald-500/30",
    dot: "#34d399",
  },
  "ENS Challenge Data": {
    bg: "bg-purple-500/10",
    text: "text-purple-300",
    border: "border-purple-500/30",
    dot: "#c084fc",
  },
  "Jane Street": {
    bg: "bg-teal-500/10",
    text: "text-teal-300",
    border: "border-teal-500/30",
    dot: "#2dd4bf",
  },
  QuantConnect: {
    bg: "bg-orange-500/10",
    text: "text-orange-300",
    border: "border-orange-500/30",
    dot: "#fb923c",
  },
  Algogene: {
    bg: "bg-sky-500/10",
    text: "text-sky-300",
    border: "border-sky-500/30",
    dot: "#38bdf8",
  },
  "IMC Trading": {
    bg: "bg-blue-500/10",
    text: "text-blue-300",
    border: "border-blue-500/30",
    dot: "#60a5fa",
  },
  "Citadel / Correlation One": {
    bg: "bg-violet-500/10",
    text: "text-violet-300",
    border: "border-violet-500/30",
    dot: "#a78bfa",
  },
  Optiver: {
    bg: "bg-rose-500/10",
    text: "text-rose-300",
    border: "border-rose-500/30",
    dot: "#fb7185",
  },
  "G-Research": {
    bg: "bg-fuchsia-500/10",
    text: "text-fuchsia-300",
    border: "border-fuchsia-500/30",
    dot: "#e879f9",
  },
  Bloomberg: {
    bg: "bg-amber-500/10",
    text: "text-amber-300",
    border: "border-amber-500/30",
    dot: "#f59e0b",
  },
  "CME Group": {
    bg: "bg-sky-500/10",
    text: "text-sky-300",
    border: "border-sky-500/30",
    dot: "#0ea5e9",
  },
  "Rotman RITC": {
    bg: "bg-pink-500/10",
    text: "text-pink-300",
    border: "border-pink-500/30",
    dot: "#f472b6",
  },
  "UChicago Trading": {
    bg: "bg-red-500/10",
    text: "text-red-300",
    border: "border-red-500/30",
    dot: "#f87171",
  },
  "CMU MSCF": {
    bg: "bg-rose-500/10",
    text: "text-rose-300",
    border: "border-rose-500/30",
    dot: "#fb7185",
  },
  "CFA Institute": {
    bg: "bg-indigo-500/10",
    text: "text-indigo-300",
    border: "border-indigo-500/30",
    dot: "#6366f1",
  },
  Kaggle: {
    bg: "bg-sky-500/10",
    text: "text-sky-300",
    border: "border-sky-500/30",
    dot: "#38bdf8",
  },
  Zindi: {
    bg: "bg-amber-500/10",
    text: "text-amber-300",
    border: "border-amber-500/30",
    dot: "#fbbf24",
  },
  DrivenData: {
    bg: "bg-emerald-500/10",
    text: "text-emerald-300",
    border: "border-emerald-500/30",
    dot: "#34d399",
  },
  Devpost: {
    bg: "bg-teal-500/10",
    text: "text-teal-300",
    border: "border-teal-500/30",
    dot: "#2dd4bf",
  },
};

export function getPlatformStyle(platform: string) {
  return (
    PLATFORM_COLORS[platform] ?? {
      bg: "bg-slate-800/80",
      text: "text-slate-300",
      border: "border-slate-700",
      dot: "#94a3b8",
    }
  );
}

export const STATUS_STYLES: Record<
  CompetitionStatus,
  { label: string; bg: string; text: string; border: string; dot: string }
> = {
  active: {
    label: "Live Market",
    bg: "bg-emerald-500/10",
    text: "text-emerald-300",
    border: "border-emerald-500/30",
    dot: "bg-emerald-400",
  },
  ending_soon: {
    label: "Closing ≤ 7d",
    bg: "bg-amber-500/15",
    text: "text-amber-300",
    border: "border-amber-500/40",
    dot: "bg-amber-400",
  },
  upcoming: {
    label: "Upcoming Season",
    bg: "bg-sky-500/10",
    text: "text-sky-300",
    border: "border-sky-500/30",
    dot: "bg-sky-400",
  },
  ended: {
    label: "Settled",
    bg: "bg-slate-800",
    text: "text-slate-400",
    border: "border-slate-700",
    dot: "bg-slate-500",
  },
};

export const DIFFICULTY_STYLES: Record<DifficultyLevel, string> = {
  Beginner: "bg-emerald-500/10 text-emerald-300 border-emerald-500/25",
  Intermediate: "bg-sky-500/10 text-sky-300 border-sky-500/25",
  Advanced: "bg-purple-500/10 text-purple-300 border-purple-500/25",
  Research: "bg-rose-500/10 text-rose-300 border-rose-500/30",
};

export function formatUsd(amount: number): string {
  if (!amount || amount <= 0) return "Knowledge / Non-Cash";
  if (amount >= 1_000_000) {
    return `$${(amount / 1_000_000).toFixed(amount % 1_000_000 === 0 ? 0 : 2)}M`;
  }
  if (amount >= 1_000) {
    return `$${(amount / 1_000).toFixed(amount % 1_000 === 0 ? 0 : 1)}K`;
  }
  return `$${amount.toLocaleString("en-US")}`;
}

export function formatDeadlineCountdown(daysRemaining: number | null, endDate: string | null): string {
  if (daysRemaining === null || !endDate) return "Continuous / Rolling";
  if (daysRemaining === 0) return "Closes today";
  if (daysRemaining === 1) return "1 day left";
  if (daysRemaining < 0) return "Settled";
  if (daysRemaining <= 30) return `${daysRemaining}d left`;
  const months = Math.floor(daysRemaining / 30);
  const remDays = daysRemaining % 30;
  return remDays > 0 ? `${months}mo ${remDays}d left` : `${months}mo left`;
}

export function formatRelativeTimestamp(iso: string): string {
  if (!iso) return "Unknown";
  const dt = new Date(iso);
  if (Number.isNaN(dt.getTime())) return iso;
  const diffSec = Math.round((Date.now() - dt.getTime()) / 1000);
  if (diffSec < 60) return "just now";
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  return `${diffDay}d ago`;
}

