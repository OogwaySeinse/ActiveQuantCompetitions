import React, { useState } from "react";
import {
  Bot,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Cpu,
  ExternalLink,
  KeyRound,
  Layers,
  MapPin,
  Sparkles,
  Target,
  Trophy,
  Wand2,
} from "lucide-react";
import { Competition } from "../types";
import { formatDeadlineCountdown, getPlatformStyle } from "../utils/format";
import {
  RecommendationResult,
  UserProfile,
  generateAiRecommendations,
  generateLocalRecommendations,
  getSavedApiKey,
  saveApiKey,
} from "../utils/recommender";

interface AiRecommenderProps {
  competitions: Competition[];
  categories: string[];
}

const ARCHETYPES: Array<{
  label: string;
  tagline: string;
  profile: UserProfile;
}> = [
  {
    label: "📈 Cross-Sectional Equity Alpha",
    tagline: "LightGBM/CatBoost, factor neutralization, Sharpe & IC optimization",
    profile: {
      skills: "Python, LightGBM, CatBoost, Polars, Cross-Sectional Equities, Factor Neutralization, Sharpe Ratio",
      preferredCategories: ["Alpha & Equity Prediction", "Time Series & Econometrics"],
      difficulty: "Advanced",
      computeTier: "Laptop / CPU (Tabular & Factor)",
      goal: "Win Cash / USDC / NMR",
      hoursPerWeek: 12,
    },
  },
  {
    label: "⚡ HFT & Limit Order Book Modeler",
    tagline: "Tick data, L2/L3 order flow imbalance, sequence encoders, market making",
    profile: {
      skills: "Python, C++, PyTorch, Limit Order Book, Market Microstructure, Hawkes Processes, Market Making",
      preferredCategories: ["Market Microstructure & HFT", "Algorithmic & Prop Trading"],
      difficulty: "Research",
      computeTier: "Single GPU (LOB & Sequence)",
      goal: "Prop Trading & Hedge Fund Recruiting",
      hoursPerWeek: 18,
    },
  },
  {
    label: "🪙 Crypto, Volatility & Derivatives",
    tagline: "Perp funding rates, Deribit DVOL, implied volatility surfaces, Solana/BTC",
    profile: {
      skills: "Crypto, Implied Volatility, Options, Deribit, Bitcoin, Solana, GARCH, HAR-RV, Time Series",
      preferredCategories: ["Crypto, DeFi & Digital Assets", "Macro, Commodities & Derivatives"],
      difficulty: "Intermediate",
      computeTier: "Laptop / CPU (Tabular & Factor)",
      goal: "Build Live Algo Track Record",
      hoursPerWeek: 10,
    },
  },
  {
    label: "🎓 University Trading & Valuation League",
    tagline: "Rotman RITC, UChicago, CME Futures, CFA Research, McGill MIPC",
    profile: {
      skills: "Portfolio Optimization, Options & Futures, Valuation, DCF, Python Backtesting, Bloomberg",
      preferredCategories: ["Algorithmic & Prop Trading", "Valuation, Portfolio & Case Arenas"],
      difficulty: "Intermediate",
      computeTier: "Laptop / CPU (Tabular & Factor)",
      goal: "Prop Trading & Hedge Fund Recruiting",
      hoursPerWeek: 8,
    },
  },
];

export const AiRecommender: React.FC<AiRecommenderProps> = ({ competitions, categories }) => {
  const [expanded, setExpanded] = useState(false);
  const [apiKey, setApiKey] = useState<string>(() => getSavedApiKey());
  const [showKeyInput, setShowKeyInput] = useState(false);
  const [loading, setLoading] = useState(false);
  const [expandedRoadmapId, setExpandedRoadmapId] = useState<string | null>(null);

  const [profile, setProfile] = useState<UserProfile>(ARCHETYPES[0].profile);
  const [result, setResult] = useState<RecommendationResult | null>(null);

  const handleRunMatchmaker = async (overrideProfile?: UserProfile) => {
    const activeProfile = overrideProfile ?? profile;
    setLoading(true);
    try {
      saveApiKey(apiKey);
      const res = await generateAiRecommendations(competitions, activeProfile, apiKey, 4);
      setResult(res);
      if (res.items.length > 0) {
        setExpandedRoadmapId(res.items[0].competition.id);
      }
    } catch {
      const fallback = generateLocalRecommendations(competitions, activeProfile, 4);
      setResult(fallback);
    } finally {
      setLoading(false);
    }
  };

  const toggleCategory = (cat: string) => {
    setProfile((prev) => ({
      ...prev,
      preferredCategories: prev.preferredCategories.includes(cat)
        ? prev.preferredCategories.filter((c) => c !== cat)
        : [...prev.preferredCategories, cat],
    }));
  };

  return (
    <div className="rounded-xl border border-emerald-500/30 bg-gradient-to-br from-slate-900/90 via-slate-900/75 to-emerald-950/30 backdrop-blur-md overflow-hidden shadow-lg shadow-emerald-950/20">
      {/* Header Banner */}
      <div
        onClick={() => setExpanded((e) => !e)}
        className="w-full flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-5 py-3.5 cursor-pointer hover:bg-slate-800/30 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-300">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-mono text-[10px] uppercase tracking-widest text-emerald-400">
                QUANT STRATEGY ADVISOR
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                Gemini 3.8 Flash + Walk-Forward Blueprint Engine
              </span>
            </div>
            <h2 className="font-display text-sm sm:text-base font-bold text-white">
              Match Your Quant Stack & Compute Tier to Live Alpha Tournaments & Order-Book Arenas
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-2 self-end sm:self-center">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setExpanded(true);
              handleRunMatchmaker();
            }}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs transition-colors shadow-sm shadow-emerald-500/20"
          >
            <Wand2 className="w-3.5 h-3.5" />
            <span>{loading ? "Synthesizing..." : "Generate Quant Match"}</span>
          </button>
          <button
            type="button"
            className="p-1.5 rounded-lg text-slate-400 hover:text-white"
            aria-label="Toggle quant advisor"
          >
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {expanded && (
        <div className="px-5 pb-5 pt-2 border-t border-slate-800/80 space-y-4">
          {/* 1-Click Quant Archetype Presets */}
          <div className="space-y-1.5">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              1-Click Quant Researcher Archetypes
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
              {ARCHETYPES.map((arch) => (
                <button
                  key={arch.label}
                  type="button"
                  onClick={() => {
                    setProfile(arch.profile);
                    handleRunMatchmaker(arch.profile);
                  }}
                  className="text-left p-2.5 rounded-lg border border-slate-800 bg-slate-950/70 hover:border-emerald-500/50 hover:bg-slate-900 transition-all group"
                >
                  <div className="text-xs font-semibold text-slate-200 group-hover:text-emerald-300">
                    {arch.label}
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">
                    {arch.tagline}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Profile Form */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="md:col-span-2 space-y-1">
              <label className="text-[11px] font-medium text-slate-400">
                Your Quant Stack, Models & Asset Classes
              </label>
              <input
                type="text"
                value={profile.skills}
                onChange={(e) => setProfile((p) => ({ ...p, skills: e.target.value }))}
                placeholder="e.g. Python, Polars, LightGBM, Limit Order Book, Options Volatility, Stat Arb..."
                className="w-full px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-950 text-xs text-slate-100 focus:outline-none focus:border-emerald-500/60"
              />
            </div>

            <div className="space-y-1">
              <label className="text-[11px] font-medium text-slate-400">Primary Objective</label>
              <select
                value={profile.goal}
                onChange={(e) =>
                  setProfile((p) => ({ ...p, goal: e.target.value as UserProfile["goal"] }))
                }
                className="w-full px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-950 text-xs text-slate-200"
              >
                <option value="Win Cash / USDC / NMR">Win Cash / USDC / NMR</option>
                <option value="Prop Trading & Hedge Fund Recruiting">Prop Trading & Hedge Fund Recruiting</option>
                <option value="Build Live Algo Track Record">Build Live Algo Track Record</option>
                <option value="Quant Research & Publications">Quant Research & Publications</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-[11px] font-medium text-slate-400">Compute Environment</label>
              <select
                value={profile.computeTier}
                onChange={(e) =>
                  setProfile((p) => ({
                    ...p,
                    computeTier: e.target.value as UserProfile["computeTier"],
                  }))
                }
                className="w-full px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-950 text-xs text-slate-200"
              >
                <option value="Laptop / CPU (Tabular & Factor)">Laptop / CPU (Tabular & Factor)</option>
                <option value="Single GPU (LOB & Sequence)">Single GPU (LOB & Sequence)</option>
                <option value="Multi-GPU / Cluster (Deep HFT)">Multi-GPU / Cluster (Deep HFT)</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-[11px] font-medium text-slate-400">Target Difficulty</label>
              <select
                value={profile.difficulty}
                onChange={(e) =>
                  setProfile((p) => ({
                    ...p,
                    difficulty: e.target.value as UserProfile["difficulty"],
                  }))
                }
                className="w-full px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-950 text-xs text-slate-200"
              >
                <option value="Any">Any Tier</option>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
                <option value="Research">Research</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-[11px] font-medium text-slate-400">
                Research Bandwidth: <span className="text-emerald-300 font-mono">{profile.hoursPerWeek}h / week</span>
              </label>
              <input
                type="range"
                min={3}
                max={40}
                value={profile.hoursPerWeek}
                onChange={(e) =>
                  setProfile((p) => ({ ...p, hoursPerWeek: Number(e.target.value) }))
                }
                className="w-full accent-emerald-500 cursor-pointer"
              />
            </div>
          </div>

          {/* Domain Chips + Optional Gemini Key */}
          <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
            <div className="flex flex-wrap items-center gap-1.5">
              {categories.map((cat) => {
                const active = profile.preferredCategories.includes(cat);
                return (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => toggleCategory(cat)}
                    className={`px-2.5 py-1 rounded-full text-[11px] font-medium border transition-colors ${
                      active
                        ? "bg-emerald-500/20 border-emerald-500/50 text-emerald-200"
                        : "bg-slate-950/70 border-slate-800 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {cat}
                  </button>
                );
              })}
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setShowKeyInput((s) => !s)}
                className="inline-flex items-center gap-1 text-[11px] text-slate-400 hover:text-emerald-300"
              >
                <KeyRound className="w-3 h-3" />
                <span>{apiKey ? "Custom Gemini Key Active" : "Optional: BYO Gemini API Key"}</span>
              </button>
            </div>
          </div>

          {showKeyInput && (
            <div className="flex items-center gap-2 p-2.5 rounded-lg bg-slate-950/90 border border-slate-800">
              <KeyRound className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Paste AIza... key for direct client-side Gemini 3.8 Flash calls (stored only in your browser)"
                className="flex-1 bg-transparent text-xs text-slate-200 focus:outline-none"
              />
              {apiKey && (
                <button
                  type="button"
                  onClick={() => {
                    setApiKey("");
                    saveApiKey("");
                  }}
                  className="text-[11px] text-rose-400 hover:text-rose-300"
                >
                  Clear
                </button>
              )}
            </div>
          )}

          {/* Results Grid */}
          {result && (
            <div className="space-y-3 pt-2 border-t border-slate-800/80">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <p className="text-xs text-slate-300">{result.summary}</p>
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-slate-950 border border-slate-800 text-emerald-300 shrink-0">
                  <Sparkles className="w-3 h-3" />
                  {result.modelUsed}
                </span>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                {result.items.map((item, idx) => {
                  const c = item.competition;
                  const pStyle = getPlatformStyle(c.platform);
                  const isRoadmapOpen = expandedRoadmapId === c.id;

                  return (
                    <div
                      key={c.id}
                      className="rounded-xl border border-slate-800 bg-slate-950/85 p-4 flex flex-col justify-between space-y-3 hover:border-emerald-500/40 transition-colors"
                    >
                      <div className="space-y-2">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                              #{idx + 1} · {item.matchScore}% FIT
                            </span>
                            <span
                              className={`px-2 py-0.5 rounded-full text-[11px] font-medium border ${pStyle.bg} ${pStyle.text} ${pStyle.border}`}
                            >
                              {c.platform}
                            </span>
                            <span className="text-xs font-semibold text-emerald-300 tabular-nums">
                              {c.prize}
                            </span>
                          </div>
                          <span className="text-[11px] text-slate-400 font-mono shrink-0">
                            {formatDeadlineCountdown(c.days_remaining, c.end_date)}
                          </span>
                        </div>

                        <a
                          href={c.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block font-display text-sm font-bold text-white hover:text-emerald-300 transition-colors"
                        >
                          {c.title}
                        </a>

                        <div className="text-xs font-medium text-emerald-300/90 flex items-center gap-1.5">
                          <Target className="w-3.5 h-3.5 shrink-0" />
                          <span>{item.headlineReason}</span>
                        </div>

                        <ul className="space-y-1 text-xs text-slate-400">
                          {item.whyItFits.map((reason) => (
                            <li key={reason} className="flex items-start gap-1.5">
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                              <span>{reason}</span>
                            </li>
                          ))}
                        </ul>

                        {/* Quantitative Modeling Blueprint */}
                        <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800/90 space-y-1.5">
                          <div className="flex items-center gap-1.5 text-[11px] font-semibold text-indigo-300">
                            <Trophy className="w-3.5 h-3.5" />
                            <span>Alpha & Validation Architecture</span>
                          </div>
                          <p className="text-xs text-slate-300 leading-relaxed">
                            {item.winningStrategy}
                          </p>
                          <div className="flex flex-wrap items-center gap-1 pt-1">
                            <Cpu className="w-3 h-3 text-slate-500 mr-1" />
                            {item.suggestedStack.map((tech) => (
                              <span
                                key={tech}
                                className="px-1.5 py-0.5 rounded bg-slate-950 border border-slate-800 text-[10px] font-mono text-slate-300"
                              >
                                {tech}
                              </span>
                            ))}
                          </div>
                        </div>

                        {/* Collapsible 4-Phase Quant Execution Roadmap */}
                        {item.roadmap && item.roadmap.length > 0 && (
                          <div className="pt-1">
                            <button
                              type="button"
                              onClick={() =>
                                setExpandedRoadmapId(isRoadmapOpen ? null : c.id)
                              }
                              className="inline-flex items-center gap-1.5 text-[11px] font-medium text-cyan-300 hover:text-cyan-200"
                            >
                              <MapPin className="w-3 h-3" />
                              <span>
                                {isRoadmapOpen
                                  ? "Hide 4-Phase Quant Research Roadmap"
                                  : "Show 4-Phase Quant Research Roadmap"}
                              </span>
                            </button>

                            {isRoadmapOpen && (
                              <div className="mt-2 space-y-2 border-l-2 border-emerald-500/30 pl-3">
                                {item.roadmap.map((step) => (
                                  <div key={step.phase} className="space-y-0.5">
                                    <div className="flex items-center gap-2">
                                      <span className="font-mono text-[10px] text-emerald-400">
                                        {step.phase}
                                      </span>
                                      <span className="text-xs font-semibold text-slate-200">
                                        {step.title}
                                      </span>
                                    </div>
                                    <p className="text-[11px] text-slate-400 leading-relaxed">
                                      {step.detail}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
                        <span className="inline-flex items-center gap-1 text-[11px] text-slate-500">
                          <Layers className="w-3 h-3" />
                          {c.category}
                        </span>
                        <a
                          href={c.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-emerald-500/15 hover:bg-emerald-500 text-emerald-300 hover:text-slate-950 text-xs font-semibold transition-colors"
                        >
                          <span>Launch Arena</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

