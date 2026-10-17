import React from "react";
import { Award, Clock, Globe2, TrendingUp } from "lucide-react";
import { Competition, CompetitionsMetadata } from "../types";
import { formatUsd } from "../utils/format";

interface StatCardsProps {
  competitions: Competition[];
  filtered: Competition[];
  metadata: CompetitionsMetadata | null;
}

export const StatCards: React.FC<StatCardsProps> = ({ competitions, filtered, metadata }) => {
  const activeCount = filtered.length;
  const totalCount = competitions.length;
  const totalPrizeUsd = filtered.reduce((acc, c) => acc + (c.prize_usd || 0), 0);
  const endingSoonCount = filtered.filter((c) => c.status === "ending_soon").length;
  const tournamentsCount = filtered.filter((c) => c.competition_type === "tournament").length;
  const uniquePlatforms = new Set(filtered.map((c) => c.platform)).size;

  const cards = [
    {
      label: "Active Quant Arenas",
      value: activeCount.toLocaleString("en-US"),
      subtext:
        activeCount === totalCount
          ? `Across ${uniquePlatforms} global platforms (${tournamentsCount} rolling tournaments)`
          : `Filtered from ${totalCount} total indexed quant arenas`,
      icon: TrendingUp,
      accent: "from-emerald-500/20 to-teal-500/5 border-emerald-500/30 text-emerald-300",
      iconBg: "bg-emerald-500/15 text-emerald-300",
    },
    {
      label: "Liquid Prize & Staking Pool",
      value: formatUsd(totalPrizeUsd),
      subtext: `${filtered.filter((c) => c.prize_usd > 0).length} cash / USDC / NMR backed arenas`,
      icon: Award,
      accent: "from-indigo-500/20 to-cyan-500/5 border-indigo-500/30 text-indigo-300",
      iconBg: "bg-indigo-500/15 text-indigo-300",
    },
    {
      label: "Closing Within 7 Days",
      value: endingSoonCount.toLocaleString("en-US"),
      subtext:
        endingSoonCount > 0
          ? "Final submission & walk-forward lock window"
          : "No immediate 7-day settlement cliffs",
      icon: Clock,
      accent: "from-amber-500/20 to-orange-500/5 border-amber-500/30 text-amber-300",
      iconBg: "bg-amber-500/15 text-amber-300",
    },
    {
      label: "Quant Venues & Feeds",
      value: `${uniquePlatforms} Venues`,
      subtext: `${metadata?.sources?.filter((s) => s.status === "ok" || s.status === "cached").length ?? 13} automated daily scrapers`,
      icon: Globe2,
      accent: "from-purple-500/20 to-pink-500/5 border-purple-500/30 text-purple-300",
      iconBg: "bg-purple-500/15 text-purple-300",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={card.label}
            className="group relative overflow-hidden rounded-xl border border-slate-800/80 bg-slate-900/60 backdrop-blur-md p-4 transition-all duration-200 hover:border-slate-700/80 hover:bg-slate-900/80"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-[10px] uppercase tracking-widest text-slate-500">
                0{idx + 1} // {card.label}
              </span>
              <div className={`p-1.5 rounded-lg border border-white/5 ${card.iconBg}`}>
                <Icon className="w-3.5 h-3.5" />
              </div>
            </div>
            <div className="font-display text-2xl sm:text-3xl font-bold tracking-tight text-white tabular-nums">
              {card.value}
            </div>
            <div className="mt-1 text-xs text-slate-400 truncate">{card.subtext}</div>
          </div>
        );
      })}
    </div>
  );
};

