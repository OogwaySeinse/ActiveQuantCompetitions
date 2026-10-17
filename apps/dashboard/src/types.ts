export type CompetitionStatus = "active" | "ending_soon" | "upcoming" | "ended";

export type DifficultyLevel = "Beginner" | "Intermediate" | "Advanced" | "Research";

export type CompetitionType = "competition" | "tournament" | "benchmark" | "practice" | "hackathon";

export interface Competition {
  id: string;
  title: string;
  platform: string;
  source: string;
  url: string;
  prize: string;
  prize_usd: number;
  prize_currency: string;
  prize_raw: string;
  start_date: string | null;
  end_date: string | null;
  days_remaining: number | null;
  status: CompetitionStatus;
  category: string;
  tags: string[];
  description: string;
  organizer: string;
  evaluation_metric: string;
  teams_count: number | null;
  competitors_count: number | null;
  entries_count: number | null;
  difficulty: DifficultyLevel;
  competition_type?: CompetitionType;
  conference?: string | null;
  conference_year?: number | null;
  paper_url?: string | null;
  first_seen_at?: string | null;
  is_new?: boolean;
  prize_delta_usd?: number;
  days_Shift?: number;
  scraped_at: string;
}

export interface SourceStatusItem {
  name: string;
  status: "ok" | "cached" | "degraded" | "error";
  count: number;
  duration_ms: number;
  error: string | null;
  updated_at: string;
}

export interface HistoryMeta {
  new_competitions: number;
  prize_changes: number;
  deadline_changes: number;
  tracked_total: number;
}

export interface CompetitionsMetadata {
  generated_at: string;
  total_active: number;
  total_prize_usd: number;
  ending_soon_count: number;
  platforms_count: number;
  platforms: Record<string, number>;
  categories: Record<string, number>;
  history?: HistoryMeta;
  sources: SourceStatusItem[];
}

export interface CompetitionsPayload {
  metadata: CompetitionsMetadata;
  competitions: Competition[];
}

export type QuickPreset =
  | "all"
  | "ending_soon"
  | "high_prize"
  | "tournaments"
  | "order_book"
  | "student_prop"
  | "new"
  | "research"
  | "saved";

export interface FilterState {
  search: string;
  platforms: string[];
  categories: string[];
  statuses: CompetitionStatus[];
  difficulties: DifficultyLevel[];
  conferences: string[];
  minPrizeUsd: number;
  maxDaysRemaining: number | null;
  preset: QuickPreset;
  includePractice: boolean;
}

