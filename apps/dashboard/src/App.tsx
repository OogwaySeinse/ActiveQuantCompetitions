import React, { useEffect, useMemo, useRef, useState } from "react";
import { BookOpen, Clock, Github, RefreshCw, TrendingUp } from "lucide-react";
import { AiRecommender } from "./components/AiRecommender";
import { AsciiBackdrop } from "./components/AsciiBackdrop";
import { Charts } from "./components/Charts";
import { CompetitionTable } from "./components/CompetitionTable";
import { FilterBar } from "./components/FilterBar";
import { SourceStatus } from "./components/SourceStatus";
import { StatCards } from "./components/StatCards";
import { Competition, CompetitionsMetadata, CompetitionsPayload, FilterState } from "./types";
import { formatRelativeTimestamp } from "./utils/format";
import {
  exportCompetitionsToCsv,
  readFiltersFromUrl,
  useBookmarks,
  useSyncFiltersToUrl,
} from "./utils/hooks";

const DEFAULT_FILTERS: FilterState = {
  search: "",
  platforms: [],
  categories: [],
  statuses: [],
  difficulties: [],
  conferences: [],
  minPrizeUsd: 0,
  maxDaysRemaining: null,
  preset: "all",
  includePractice: false,
};

export const App: React.FC = () => {
  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [metadata, setMetadata] = useState<CompetitionsMetadata | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterState>(() => readFiltersFromUrl(DEFAULT_FILTERS));
  const { bookmarks, toggleBookmark } = useBookmarks();
  const searchInputRef = useRef<HTMLInputElement>(null);

  useSyncFiltersToUrl(filters);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (
        e.key === "/" &&
        document.activeElement?.tagName !== "INPUT" &&
        document.activeElement?.tagName !== "TEXTAREA" &&
        document.activeElement?.tagName !== "SELECT"
      ) {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`./data/competitions.json?t=${Date.now()}`);
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: Failed to load competitions.json`);
      }
      const payload: CompetitionsPayload = await res.json();
      setCompetitions(payload.competitions ?? []);
      setMetadata(payload.metadata ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load quant competitions data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const isPracticeOrBenchmark = (c: Competition) =>
    c.competition_type === "practice" || c.competition_type === "benchmark";

  // Active live quant pool (excludes historical archive benchmarks unless toggled)
  const visiblePool = useMemo(() => {
    if (filters.includePractice) return competitions;
    return competitions.filter((c) => !isPracticeOrBenchmark(c));
  }, [competitions, filters.includePractice]);

  const practiceCount = useMemo(
    () => competitions.filter((c) => isPracticeOrBenchmark(c)).length,
    [competitions],
  );

  const tournamentsCount = useMemo(
    () => visiblePool.filter((c) => c.competition_type === "tournament").length,
    [visiblePool],
  );

  const orderBookCount = useMemo(
    () =>
      visiblePool.filter(
        (c) =>
          c.category === "Market Microstructure & HFT" ||
          c.category === "Algorithmic & Prop Trading",
      ).length,
    [visiblePool],
  );

  const platformOptions = useMemo(() => {
    const map: Record<string, number> = {};
    for (const c of visiblePool) {
      map[c.platform] = (map[c.platform] ?? 0) + 1;
    }
    return Object.entries(map)
      .map(([value, count]) => ({ value, count }))
      .sort((a, b) => b.count - a.count || a.value.localeCompare(b.value));
  }, [visiblePool]);

  const categoryOptions = useMemo(() => {
    const map: Record<string, number> = {};
    for (const c of visiblePool) {
      map[c.category] = (map[c.category] ?? 0) + 1;
    }
    return Object.entries(map)
      .map(([value, count]) => ({ value, count }))
      .sort((a, b) => b.count - a.count || a.value.localeCompare(b.value));
  }, [visiblePool]);

  const conferenceOptions = useMemo(() => {
    const map: Record<string, number> = {};
    for (const c of visiblePool) {
      if (c.conference) {
        map[c.conference] = (map[c.conference] ?? 0) + 1;
      }
    }
    return Object.entries(map)
      .map(([value, count]) => ({ value, count }))
      .sort((a, b) => b.count - a.count || a.value.localeCompare(b.value));
  }, [visiblePool]);

  const newCount = useMemo(
    () => visiblePool.filter((c) => c.is_new).length,
    [visiblePool],
  );

  const researchCount = useMemo(
    () =>
      visiblePool.filter(
        (c) => Boolean(c.conference) || Boolean(c.paper_url) || c.difficulty === "Research",
      ).length,
    [visiblePool],
  );

  const filteredCompetitions = useMemo(() => {
    const q = filters.search.trim().toLowerCase();
    return visiblePool.filter((c) => {
      if (filters.preset === "saved" && !bookmarks.has(c.id)) return false;
      if (filters.preset === "new" && !c.is_new) return false;
      if (filters.preset === "tournaments" && c.competition_type !== "tournament") return false;
      if (
        filters.preset === "order_book" &&
        c.category !== "Market Microstructure & HFT" &&
        c.category !== "Algorithmic & Prop Trading"
      ) {
        return false;
      }
      if (
        filters.preset === "research" &&
        !c.conference &&
        !c.paper_url &&
        c.difficulty !== "Research"
      ) {
        return false;
      }

      if (filters.platforms.length > 0 && !filters.platforms.includes(c.platform)) {
        return false;
      }
      if (filters.categories.length > 0 && !filters.categories.includes(c.category)) {
        return false;
      }
      if (
        filters.conferences.length > 0 &&
        (!c.conference || !filters.conferences.includes(c.conference))
      ) {
        return false;
      }
      if (filters.statuses.length > 0 && !filters.statuses.includes(c.status)) {
        return false;
      }
      if (filters.difficulties.length > 0 && !filters.difficulties.includes(c.difficulty)) {
        return false;
      }
      if (filters.minPrizeUsd > 0 && (c.prize_usd || 0) < filters.minPrizeUsd) {
        return false;
      }
      if (
        filters.maxDaysRemaining !== null &&
        (c.days_remaining === null || c.days_remaining > filters.maxDaysRemaining)
      ) {
        return false;
      }

      if (q) {
        const hay = [
          c.title,
          c.platform,
          c.category,
          c.organizer,
          c.description,
          c.evaluation_metric,
          c.conference ?? "",
          ...c.tags,
        ]
          .join(" ")
          .toLowerCase();
        if (!hay.includes(q)) return false;
      }

      return true;
    });
  }, [visiblePool, filters, bookmarks]);

  const handleTogglePlatformFromChart = (platform: string) => {
    setFilters((prev) => ({
      ...prev,
      platforms: prev.platforms.includes(platform)
        ? prev.platforms.filter((p) => p !== platform)
        : [platform],
    }));
  };

  const handleToggleCategoryFromChart = (category: string) => {
    setFilters((prev) => ({
      ...prev,
      categories: prev.categories.includes(category)
        ? prev.categories.filter((c) => c !== category)
        : [category],
    }));
  };

  const handleSelectTag = (tag: string) => {
    setFilters((prev) => ({ ...prev, search: tag }));
  };

  return (
    <div className="relative min-h-screen flex flex-col overflow-x-hidden">
      {/* Drifting stochastic calculus & limit order book ASCII background */}
      <AsciiBackdrop />

      {/* Top Navigation / Header */}
      <header className="sticky top-0 z-20 border-b border-slate-800/80 bg-[#090b10]/85 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 shadow-lg shadow-emerald-500/10">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] uppercase tracking-widest text-emerald-400">
                  WUNDERQUANT // QUANT ARENA
                </span>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono uppercase tracking-wider bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Daily Sync · 06:00 UTC
                </span>
              </div>
              <h1 className="font-display text-lg sm:text-xl font-bold tracking-tight text-white">
                Active Quant & Algorithmic Trading Competitions
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-2.5 text-xs text-slate-400">
            {metadata?.generated_at && (
              <div
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80"
                title={`Snapshot generated at ${metadata.generated_at}`}
              >
                <Clock className="w-3.5 h-3.5 text-emerald-400" />
                <span>Updated {formatRelativeTimestamp(metadata.generated_at)}</span>
              </div>
            )}

            <button
              type="button"
              onClick={fetchData}
              title="Refresh competition data"
              className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:border-slate-700 text-slate-300 hover:text-white transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-emerald-400" : ""}`} />
            </button>

            <a
              href="https://quantbender.github.io/quant-contests/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:border-emerald-500/40 text-slate-300 hover:text-emerald-300 transition-colors"
              title="Inspired by QuantBender Quant Contests"
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span className="hidden md:inline">QuantContests</span>
            </a>

            <a
              href="https://github.com/OogwaySeinse/ActiveQuantCompetitions"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:border-slate-700 text-slate-200 hover:text-white transition-colors"
            >
              <Github className="w-4 h-4" />
              <span className="hidden sm:inline">GitHub</span>
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-5">
        {error && (
          <div className="rounded-xl border border-rose-500/40 bg-rose-500/10 p-4 text-xs text-rose-200">
            {error}
          </div>
        )}

        {/* KPI Cards */}
        <StatCards
          competitions={visiblePool}
          filtered={filteredCompetitions}
          metadata={metadata}
        />

        {/* AI Quant Strategy & Competition Matchmaker */}
        <AiRecommender
          competitions={visiblePool}
          categories={categoryOptions.map((c) => c.value)}
        />

        {/* Analytics Charts */}
        <Charts
          competitions={filteredCompetitions}
          onSelectPlatform={handleTogglePlatformFromChart}
          onSelectCategory={handleToggleCategoryFromChart}
        />

        {/* Filter Bar */}
        <FilterBar
          filters={filters}
          setFilters={setFilters}
          platformOptions={platformOptions}
          categoryOptions={categoryOptions}
          conferenceOptions={conferenceOptions}
          savedCount={bookmarks.size}
          newCount={newCount}
          researchCount={researchCount}
          practiceCount={practiceCount}
          tournamentsCount={tournamentsCount}
          orderBookCount={orderBookCount}
          onExportCsv={() => exportCompetitionsToCsv(filteredCompetitions)}
          searchInputRef={searchInputRef}
        />

        {/* Competitions Table */}
        {loading && competitions.length === 0 ? (
          <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 p-12 text-center text-sm text-slate-400">
            Loading active quant competitions & alpha tournaments...
          </div>
        ) : (
          <CompetitionTable
            competitions={filteredCompetitions}
            bookmarks={bookmarks}
            onToggleBookmark={toggleBookmark}
            onSelectTag={handleSelectTag}
          />
        )}

        {/* Scraper Feed Health */}
        {metadata?.sources && <SourceStatus sources={metadata.sources} />}
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-800/80 bg-[#090b10]/90 py-5 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-500">
          <div>
            Automated daily aggregation across Numerai, CrunchDAO, WorldQuant BRAIN, ENS Challenge Data, Jane Street, Wunder Fund, QuantConnect, Algogene, Kaggle, Rotman RITC, UChicago, CME Group, Bloomberg, IMC, Citadel, Optiver, and QuantContests.
          </div>
          <div>
            Press <kbd className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">/</kbd> to search · Raw data in{" "}
            <a
              href="./data/competitions.json"
              target="_blank"
              rel="noopener noreferrer"
              className="text-emerald-400 hover:underline"
            >
              competitions.json
            </a>{" "}
            &{" "}
            <a
              href="./data/competitions.csv"
              target="_blank"
              rel="noopener noreferrer"
              className="text-emerald-400 hover:underline"
            >
              competitions.csv
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;

