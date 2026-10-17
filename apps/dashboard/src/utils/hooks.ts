import { useCallback, useEffect, useState } from "react";
import { Competition, FilterState, QuickPreset } from "../types";

const BOOKMARKS_KEY = "active_quant_competitions_bookmarks_v1";

export function useBookmarks() {
  const [bookmarks, setBookmarks] = useState<Set<string>>(() => {
    try {
      const raw = localStorage.getItem(BOOKMARKS_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) return new Set(parsed);
      }
    } catch {
      // ignore localStorage errors
    }
    return new Set();
  });

  const toggleBookmark = useCallback((id: string) => {
    setBookmarks((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      try {
        localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(Array.from(next)));
      } catch {
        // ignore
      }
      return next;
    });
  }, []);

  return { bookmarks, toggleBookmark };
}

export function readFiltersFromUrl(defaultState: FilterState): FilterState {
  if (typeof window === "undefined") return defaultState;
  const params = new URLSearchParams(window.location.search);
  const search = params.get("q") ?? defaultState.search;
  const platforms = params.get("platforms")?.split(",").filter(Boolean) ?? defaultState.platforms;
  const categories = params.get("categories")?.split(",").filter(Boolean) ?? defaultState.categories;
  const conferences = params.get("conferences")?.split(",").filter(Boolean) ?? defaultState.conferences;
  const minPrize = Number(params.get("minPrize") ?? defaultState.minPrizeUsd);
  const maxDaysRaw = params.get("maxDays");
  const maxDaysRemaining = maxDaysRaw ? Number(maxDaysRaw) : defaultState.maxDaysRemaining;
  const preset = (params.get("preset") as QuickPreset) ?? defaultState.preset;
  const includePractice = params.get("practice") === "1" ? true : defaultState.includePractice;

  return {
    ...defaultState,
    search,
    platforms,
    categories,
    conferences,
    minPrizeUsd: Number.isFinite(minPrize) ? minPrize : 0,
    maxDaysRemaining: maxDaysRemaining && Number.isFinite(maxDaysRemaining) ? maxDaysRemaining : null,
    preset: [
      "all",
      "ending_soon",
      "high_prize",
      "tournaments",
      "order_book",
      "student_prop",
      "new",
      "research",
      "saved",
    ].includes(preset)
      ? preset
      : "all",
    includePractice,
  };
}

export function useSyncFiltersToUrl(filters: FilterState) {
  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams();
    if (filters.search.trim()) params.set("q", filters.search.trim());
    if (filters.platforms.length > 0) params.set("platforms", filters.platforms.join(","));
    if (filters.categories.length > 0) params.set("categories", filters.categories.join(","));
    if (filters.conferences.length > 0) params.set("conferences", filters.conferences.join(","));
    if (filters.minPrizeUsd > 0) params.set("minPrize", String(filters.minPrizeUsd));
    if (filters.maxDaysRemaining !== null) params.set("maxDays", String(filters.maxDaysRemaining));
    if (filters.preset !== "all") params.set("preset", filters.preset);
    if (filters.includePractice) params.set("practice", "1");

    const qs = params.toString();
    const newUrl = qs ? `${window.location.pathname}?${qs}` : window.location.pathname;
    window.history.replaceState(null, "", newUrl);
  }, [filters]);
}

export function exportCompetitionsToCsv(competitions: Competition[], filename = "active-quant-competitions.csv") {
  const headers = [
    "Title",
    "Platform",
    "Organizer",
    "Category",
    "Type",
    "Prize",
    "Prize USD",
    "Status",
    "Start Date",
    "End Date",
    "Days Remaining",
    "Difficulty",
    "Evaluation Metric",
    "Research / Sponsor Track",
    "Paper URL",
    "URL",
  ];
  const rows = competitions.map((c) => [
    c.title,
    c.platform,
    c.organizer,
    c.category,
    c.competition_type ?? "competition",
    c.prize,
    String(c.prize_usd),
    c.status,
    c.start_date ?? "",
    c.end_date ?? "Continuous",
    c.days_remaining !== null ? String(c.days_remaining) : "",
    c.difficulty,
    c.evaluation_metric,
    c.conference ? `${c.conference}${c.conference_year ? ` ${c.conference_year}` : ""}` : "",
    c.paper_url ?? "",
    c.url,
  ]);

  const escapeCell = (val: string) => `"${String(val ?? "").replace(/"/g, '""')}"`;
  const csvContent = [headers.map(escapeCell).join(","), ...rows.map((r) => r.map(escapeCell).join(","))].join("\n");

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

