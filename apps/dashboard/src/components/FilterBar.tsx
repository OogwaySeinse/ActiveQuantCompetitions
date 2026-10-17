import React from "react";
import {
  Activity,
  Bookmark,
  Download,
  Flame,
  GraduationCap,
  Layers,
  RotateCcw,
  Search,
  Sparkles,
  Trophy,
  Zap,
} from "lucide-react";
import { CompetitionStatus, DifficultyLevel, FilterState, QuickPreset } from "../types";
import { MultiSelect } from "./MultiSelect";

interface FilterBarProps {
  filters: FilterState;
  setFilters: React.Dispatch<React.SetStateAction<FilterState>>;
  platformOptions: { value: string; count: number }[];
  categoryOptions: { value: string; count: number }[];
  conferenceOptions: { value: string; count: number }[];
  savedCount: number;
  newCount: number;
  researchCount: number;
  practiceCount: number;
  tournamentsCount: number;
  orderBookCount: number;
  onExportCsv: () => void;
  searchInputRef: React.RefObject<HTMLInputElement>;
}

const DIFFICULTIES: DifficultyLevel[] = ["Beginner", "Intermediate", "Advanced", "Research"];
const STATUSES: { value: CompetitionStatus; label: string }[] = [
  { value: "active", label: "Live Market" },
  { value: "ending_soon", label: "Closing ≤ 7d" },
  { value: "upcoming", label: "Upcoming" },
];

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  setFilters,
  platformOptions,
  categoryOptions,
  conferenceOptions,
  savedCount,
  newCount,
  researchCount,
  practiceCount,
  tournamentsCount,
  orderBookCount,
  onExportCsv,
  searchInputRef,
}) => {
  const applyPreset = (preset: QuickPreset) => {
    setFilters((prev) => {
      if (preset === "all") {
        return {
          ...prev,
          preset: "all",
          statuses: [],
          minPrizeUsd: 0,
          maxDaysRemaining: null,
        };
      }
      if (preset === "ending_soon") {
        return {
          ...prev,
          preset,
          statuses: ["ending_soon"],
          minPrizeUsd: 0,
          maxDaysRemaining: 7,
        };
      }
      if (preset === "high_prize") {
        return {
          ...prev,
          preset,
          statuses: [],
          minPrizeUsd: 25000,
          maxDaysRemaining: null,
        };
      }
      return {
        ...prev,
        preset,
        statuses: [],
        minPrizeUsd: 0,
        maxDaysRemaining: null,
      };
    });
  };

  const resetAll = () => {
    setFilters((prev) => ({
      search: "",
      platforms: [],
      categories: [],
      statuses: [],
      difficulties: [],
      conferences: [],
      minPrizeUsd: 0,
      maxDaysRemaining: null,
      preset: "all",
      includePractice: prev.includePractice,
    }));
  };

  const hasActiveFilters =
    filters.search.trim().length > 0 ||
    filters.platforms.length > 0 ||
    filters.categories.length > 0 ||
    filters.statuses.length > 0 ||
    filters.difficulties.length > 0 ||
    filters.conferences.length > 0 ||
    filters.minPrizeUsd > 0 ||
    filters.maxDaysRemaining !== null ||
    filters.preset !== "all";

  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 backdrop-blur-md p-4 space-y-3.5">
      {/* Row 1: Quick Quant Presets + Search + CSV Export */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-1.5">
          <button
            type="button"
            onClick={() => applyPreset("all")}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              filters.preset === "all"
                ? "bg-emerald-500 text-slate-950 font-semibold shadow-sm shadow-emerald-500/30"
                : "bg-slate-800/80 text-slate-300 hover:bg-slate-800"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            All Quant Arenas
          </button>

          <button
            type="button"
            onClick={() => applyPreset("tournaments")}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              filters.preset === "tournaments"
                ? "bg-cyan-500 text-slate-950 font-semibold shadow-sm shadow-cyan-500/30"
                : "bg-slate-800/80 text-slate-300 hover:bg-slate-800"
            }`}
          >
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            Rolling Alpha Tournaments ({tournamentsCount})
          </button>

          <button
            type="button"
            onClick={() => applyPreset("order_book")}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              filters.preset === "order_book"
                ? "bg-indigo-500 text-white shadow-sm shadow-indigo-500/30"
                : "bg-slate-800/80 text-slate-300 hover:bg-slate-800"
            }`}
          >
            <Zap className="w-3.5 h-3.5 text-indigo-400" />
            HFT / Order Book & Algo ({orderBookCount})
          </button>

          <button
            type="button"
            onClick={() => applyPreset("high_prize")}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              filters.preset === "high_prize"
                ? "bg-emerald-600 text-white shadow-sm shadow-emerald-500/30"
                : "bg-slate-800/80 text-slate-300 hover:bg-slate-800"
            }`}
          >
            <Trophy className="w-3.5 h-3.5 text-emerald-400" />
            Prize ≥ $25K
          </button>

          <button
            type="button"
            onClick={() => applyPreset("ending_soon")}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              filters.preset === "ending_soon"
                ? "bg-amber-500 text-slate-950 font-semibold shadow-sm shadow-amber-500/30"
                : "bg-slate-800/80 text-slate-300 hover:bg-slate-800"
            }`}
          >
            <Flame className="w-3.5 h-3.5" />
            Closing ≤ 7d
          </button>

          <button
            type="button"
            onClick={() => applyPreset("research")}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              filters.preset === "research"
                ? "bg-purple-600 text-white shadow-sm shadow-purple-500/30"
                : "bg-slate-800/80 text-slate-300 hover:bg-slate-800"
            }`}
          >
            <GraduationCap className="w-3.5 h-3.5 text-purple-400" />
            Quant Labs & Conferences ({researchCount})
          </button>

          {newCount > 0 && (
            <button
              type="button"
              onClick={() => applyPreset("new")}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                filters.preset === "new"
                  ? "bg-teal-500 text-slate-950 font-semibold"
                  : "bg-slate-800/80 text-slate-300 hover:bg-slate-800"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-teal-300" />
              New ({newCount})
            </button>
          )}

          <button
            type="button"
            onClick={() => applyPreset("saved")}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              filters.preset === "saved"
                ? "bg-pink-600 text-white shadow-sm shadow-pink-500/30"
                : "bg-slate-800/80 text-slate-300 hover:bg-slate-800"
            }`}
          >
            <Bookmark className="w-3.5 h-3.5 text-pink-400" />
            Saved ({savedCount})
          </button>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative flex-1 sm:w-72">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              ref={searchInputRef}
              type="text"
              value={filters.search}
              onChange={(e) => setFilters((prev) => ({ ...prev, search: e.target.value }))}
              placeholder="Search alpha, LOB, options, QRT, Numerai... (/)"
              className="w-full pl-8 pr-8 py-1.5 rounded-lg border border-slate-800 bg-slate-950/90 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500/60"
            />
            {filters.search && (
              <button
                type="button"
                onClick={() => setFilters((prev) => ({ ...prev, search: "" }))}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[11px] text-slate-500 hover:text-slate-300"
              >
                ✕
              </button>
            )}
          </div>

          <button
            type="button"
            onClick={onExportCsv}
            title="Export filtered quant competitions to CSV"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-xs font-medium text-slate-300 hover:border-slate-700 hover:text-white transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Export CSV</span>
          </button>
        </div>
      </div>

      {/* Row 2: Multi-select dropdowns, Difficulty, Status, Min Prize, Archive Benchmark Toggle */}
      <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/60">
        <MultiSelect
          label="Quant Venues"
          options={platformOptions}
          selected={filters.platforms}
          onChange={(platforms) => setFilters((prev) => ({ ...prev, platforms }))}
        />

        <MultiSelect
          label="Quant Domains"
          options={categoryOptions}
          selected={filters.categories}
          onChange={(categories) => setFilters((prev) => ({ ...prev, categories }))}
        />

        {conferenceOptions.length > 0 && (
          <MultiSelect
            label="Labs & Tracks"
            options={conferenceOptions}
            selected={filters.conferences}
            onChange={(conferences) => setFilters((prev) => ({ ...prev, conferences }))}
          />
        )}

        {/* Status pills */}
        <div className="flex items-center gap-1 rounded-lg border border-slate-800 bg-slate-950/60 p-0.5">
          {STATUSES.map((st) => {
            const active = filters.statuses.includes(st.value);
            return (
              <button
                key={st.value}
                type="button"
                onClick={() =>
                  setFilters((prev) => ({
                    ...prev,
                    statuses: active
                      ? prev.statuses.filter((x) => x !== st.value)
                      : [...prev.statuses, st.value],
                  }))
                }
                className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors ${
                  active
                    ? "bg-emerald-500/20 text-emerald-200 border border-emerald-500/40"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {st.label}
              </button>
            );
          })}
        </div>

        {/* Difficulty pills */}
        <div className="flex items-center gap-1 rounded-lg border border-slate-800 bg-slate-950/60 p-0.5">
          {DIFFICULTIES.map((diff) => {
            const active = filters.difficulties.includes(diff);
            return (
              <button
                key={diff}
                type="button"
                onClick={() =>
                  setFilters((prev) => ({
                    ...prev,
                    difficulties: active
                      ? prev.difficulties.filter((x) => x !== diff)
                      : [...prev.difficulties, diff],
                  }))
                }
                className={`px-2 py-1 rounded-md text-[11px] font-medium transition-colors ${
                  active
                    ? "bg-indigo-500/20 text-indigo-200 border border-indigo-500/40"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {diff}
              </button>
            );
          })}
        </div>

        {/* Min Prize selector */}
        <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg border border-slate-800 bg-slate-950/60 text-xs text-slate-300">
          <span className="text-slate-400 text-[11px]">Min Pool:</span>
          <select
            value={filters.minPrizeUsd}
            onChange={(e) =>
              setFilters((prev) => ({ ...prev, minPrizeUsd: Number(e.target.value) }))
            }
            className="bg-transparent text-xs text-slate-200 focus:outline-none cursor-pointer"
          >
            <option value={0} className="bg-slate-900">Any</option>
            <option value={1000} className="bg-slate-900">$1K+</option>
            <option value={10000} className="bg-slate-900">$10K+</option>
            <option value={25000} className="bg-slate-900">$25K+</option>
            <option value={50000} className="bg-slate-900">$50K+</option>
            <option value={100000} className="bg-slate-900">$100K+</option>
          </select>
        </div>

        {/* Archive Benchmarks toggle */}
        <button
          type="button"
          onClick={() =>
            setFilters((prev) => ({ ...prev, includePractice: !prev.includePractice }))
          }
          title="Include historical ENS Challenge Data benchmarks (QRT, CFM, AMF, Natixis, BNP Paribas) and Kaggle Getting Started playgrounds"
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-[11px] font-medium transition-colors ${
            filters.includePractice
              ? "border-cyan-500/40 bg-cyan-500/15 text-cyan-200"
              : "border-slate-800 bg-slate-950/60 text-slate-400 hover:text-slate-200"
          }`}
        >
          <span>♾️ Archive Benchmarks ({practiceCount})</span>
          <span
            className={`px-1.5 py-0.2 rounded text-[10px] font-semibold ${
              filters.includePractice
                ? "bg-cyan-500 text-slate-950"
                : "bg-slate-800 text-slate-400"
            }`}
          >
            {filters.includePractice ? "Shown" : "Hidden"}
          </span>
        </button>

        {hasActiveFilters && (
          <button
            type="button"
            onClick={resetAll}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs text-rose-400 hover:bg-rose-500/10 transition-colors ml-auto"
          >
            <RotateCcw className="w-3 h-3" />
            Reset Filters
          </button>
        )}
      </div>
    </div>
  );
};

