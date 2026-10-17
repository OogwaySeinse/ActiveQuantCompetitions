import { Competition, DifficultyLevel } from "../types";

export interface UserProfile {
  skills: string;
  preferredCategories: string[];
  difficulty: DifficultyLevel | "Any";
  computeTier: "Laptop / CPU (Tabular & Factor)" | "Single GPU (LOB & Sequence)" | "Multi-GPU / Cluster (Deep HFT)";
  goal: "Win Cash / USDC / NMR" | "Prop Trading & Hedge Fund Recruiting" | "Quant Research & Publications" | "Build Live Algo Track Record";
  hoursPerWeek: number;
}

export interface RoadmapStep {
  phase: string;
  title: string;
  detail: string;
}

export interface RecommendationItem {
  competition: Competition;
  matchScore: number;
  headlineReason: string;
  whyItFits: string[];
  winningStrategy: string;
  suggestedStack: string[];
  roadmap: RoadmapStep[];
}

export interface RecommendationResult {
  mode: "gemini-3.8-flash" | "smart-local";
  modelUsed: string;
  summary: string;
  items: RecommendationItem[];
}

const GEMINI_API_KEY_STORAGE = "active_quant_competitions_gemini_key_v1";
const GEMINI_MODEL = "gemini-3.8-flash";
const GEMINI_API_REVISION = "2026-05-20";

const DEFAULT_WORKER_PROXY_URL = "https://active-quant-recommender.archit-quant.workers.dev";

export function getProxyUrl(): string {
  const envUrl = (import.meta as unknown as { env?: Record<string, string> }).env?.VITE_RECOMMENDER_PROXY_URL;
  if (envUrl && envUrl.trim()) return envUrl.trim();
  return DEFAULT_WORKER_PROXY_URL;
}

export function getSavedApiKey(): string {
  try {
    return localStorage.getItem(GEMINI_API_KEY_STORAGE) ?? "";
  } catch {
    return "";
  }
}

export function saveApiKey(key: string): void {
  try {
    if (key.trim()) {
      localStorage.setItem(GEMINI_API_KEY_STORAGE, key.trim());
    } else {
      localStorage.removeItem(GEMINI_API_KEY_STORAGE);
    }
  } catch {
    // ignore
  }
}

function buildDomainBlueprint(comp: Competition): {
  strategy: string;
  stack: string[];
  roadmap: RoadmapStep[];
} {
  const cat = (comp.category || "").toLowerCase();
  const text = `${comp.title} ${comp.description} ${comp.tags.join(" ")}`.toLowerCase();

  if (cat.includes("microstructure") || text.includes("order book") || text.includes("hft")) {
    return {
      strategy:
        "Construct multi-horizon order flow imbalance (OFI), micro-price deviation, and queue-depletion features across top-10 LOB levels; blend LightGBM with a causal temporal convolution / Mamba sequence encoder.",
      stack: ["Polars / DuckDB", "LightGBM", "PyTorch (TCN / Mamba)", "PurgedEmbargoSplit", "Numba"],
      roadmap: [
        {
          phase: "Phase 1 · Day 1–2",
          title: "Event-Time Clock & Purged Walk-Forward CV",
          detail: `Build a strict chronological walk-forward split with embargo intervals matching the target horizon to eliminate lookahead leakage on ${comp.evaluation_metric || "LOB returns"}.`,
        },
        {
          phase: "Phase 2 · Day 3–5",
          title: "Microstructure & Queue Dynamics Features",
          detail: "Extract Cont-Kukanov-Stoikov Order Flow Imbalance (OFI), VPIN toxicity, book slope, and trade-arrival Hawkes intensities across exponential decay windows.",
        },
        {
          phase: "Phase 3 · Week 2",
          title: "Sequence Encoder + GBDT Hybrid",
          detail: "Train a shallow causal 1D-CNN / GRU on raw L2 state transitions and stack its latent embeddings with gradient boosted trees.",
        },
        {
          phase: "Phase 4 · Final",
          title: "Volatility-Regime Calibration & Ensembling",
          detail: "Scale predictions by realized volatility regime and blend rank-averaged GBDT + neural models to stabilize tail drawdowns.",
        },
      ],
    };
  }

  if (cat.includes("crypto") || text.includes("btc") || text.includes("solana") || text.includes("dvol")) {
    return {
      strategy:
        "Combine cross-exchange perp funding rates, open-interest basis, realized RV/bipower variation jumps, and cross-asset beta neutralization with Huber-loss gradient boosting.",
      stack: ["Polars", "LightGBM + CatBoost", "CCXT / On-Chain Features", "HAR-RV Volatility", "Optuna"],
      roadmap: [
        {
          phase: "Phase 1 · Day 1–2",
          title: "Non-Stationary Regime & Purge Validation",
          detail: `Establish an expanding-window purged CV across bull/bear volatility regimes aligned with ${comp.evaluation_metric || "the tournament metric"}.`,
        },
        {
          phase: "Phase 2 · Day 3–5",
          title: "Cross-Sectional & Volatility Surface Signals",
          detail: "Engineer BTC/ETH beta-residualized momentum, funding-rate z-scores, Garman-Klass volatility, and liquidity shock ratios.",
        },
        {
          phase: "Phase 3 · Week 2",
          title: "Outlier-Robust Objective Tuning",
          detail: "Train Huber / quantile-loss GBDTs and regularize feature exposure so a single memecoin or vol spike cannot dominate portfolio weights.",
        },
        {
          phase: "Phase 4 · Final",
          title: "Turnover-Penalized Meta-Ensemble",
          detail: "Blend diverse lookback horizons (4h, 24h, 7d) with exponentially decayed signal smoothing.",
        },
      ],
    };
  }

  if (cat.includes("credit") || cat.includes("insurance") || text.includes("fraud") || text.includes("churn")) {
    return {
      strategy:
        "Target-encoded entity aggregations, velocity ratios over rolling transaction windows, and monotonic-constrained GBDT ensembles with isotonic probability calibration.",
      stack: ["LightGBM + XGBoost + CatBoost", "Polars", "Scikit-Learn Calibration", "Optuna"],
      roadmap: [
        {
          phase: "Phase 1 · Day 1–2",
          title: "Out-of-Time / Group-Stratified Validation",
          detail: `Split by customer/policy group and time cohort to mirror unseen production cohorts on ${comp.evaluation_metric || "AUC / deviance"}.`,
        },
        {
          phase: "Phase 2 · Day 3–6",
          title: "Behavioral Velocity & Ratio Engineering",
          detail: "Create out-of-fold frequency encodings, spend-to-limit velocity ratios, and peer-cohort residual features.",
        },
        {
          phase: "Phase 3 · Week 2",
          title: "Monotonic Constraints & Tweedie/Focal Loss",
          detail: "Enforce domain monotonicity on key risk drivers and test Tweedie/Gamma objectives for skewed claim severity.",
        },
        {
          phase: "Phase 4 · Final",
          title: "Rank-Averaged Stacking & Post-Calibration",
          detail: "Combine GBDT + neural tabular predictions via rank-averaging and Platt/isotonic calibration.",
        },
      ],
    };
  }

  // Default: Cross-Sectional Alpha, Algorithmic Trading, Econometrics & Portfolio Arenas
  return {
    strategy:
      "Era-boosted gradient trees + ridge/MLP residual models with strict cross-sectional rank normalization, sector/beta neutralization, and Sharpe-optimal portfolio weighting.",
    stack: ["LightGBM + CatBoost", "PyTorch Tabular MLP", "Polars", "CVXPY / Ledoit-Wolf Shrinkage", "SciPy"],
    roadmap: [
      {
        phase: "Phase 1 · Day 1–2",
        title: "Purged Era-Wise Cross-Validation",
        detail: `Set up purged era-by-era cross-validation with an embargo gap ≥ target horizon; track mean IC, Sharpe, and max drawdown on ${comp.evaluation_metric || "out-of-sample eras"}.`,
      },
      {
        phase: "Phase 2 · Day 3–6",
        title: "Cross-Sectional Rank & Orthogonal Factor Engineering",
        detail: "Gaussianize features within each date era, compute group-neutralized momentum/reversal interactions, and extract rolling PCA factor residuals.",
      },
      {
        phase: "Phase 3 · Week 2",
        title: "Era-Boosted GBDT + Residual Neural Ensemble",
        detail: "Train LightGBM, CatBoost, and a Cosine-loss MLP across multiple target horizons; upweight worst-performing eras to harden regime robustness.",
      },
      {
        phase: "Phase 4 · Final",
        title: "Feature Neutralization & Turnover Optimization",
        detail: "Neutralize top factor exposures (50–75% proportion) and apply Ledoit-Wolf covariance shrinkage to maximize out-of-sample Information Ratio.",
      },
    ],
  };
}

export function generateLocalRecommendations(
  competitions: Competition[],
  profile: UserProfile,
  topK = 4,
): RecommendationResult {
  const skillTokens = profile.skills
    .toLowerCase()
    .split(/[,;\s]+/)
    .map((s) => s.trim())
    .filter((s) => s.length >= 2);

  const scored = competitions
    .filter((c) => c.status !== "ended")
    .map((comp) => {
      let score = 52;
      const reasons: string[] = [];
      const textBlob = `${comp.title} ${comp.category} ${comp.tags.join(" ")} ${comp.description} ${comp.organizer} ${comp.evaluation_metric}`.toLowerCase();

      if (
        profile.preferredCategories.length > 0 &&
        profile.preferredCategories.some((cat) => comp.category.toLowerCase() === cat.toLowerCase())
      ) {
        score += 22;
        reasons.push(`Direct match for your ${comp.category} focus`);
      }

      if (profile.difficulty !== "Any") {
        if (comp.difficulty === profile.difficulty) {
          score += 12;
          reasons.push(`Calibrated for ${comp.difficulty}-tier quant modeling`);
        } else {
          score -= 4;
        }
      }

      const matchedSkills = skillTokens.filter((tok) => textBlob.includes(tok));
      if (matchedSkills.length > 0) {
        score += Math.min(18, matchedSkills.length * 6);
        reasons.push(`Aligns with your skills (${matchedSkills.slice(0, 3).join(", ")})`);
      }

      if (profile.computeTier.startsWith("Laptop")) {
        if (
          comp.category.includes("Alpha") ||
          comp.category.includes("Time Series") ||
          comp.category.includes("Credit") ||
          comp.category.includes("Valuation")
        ) {
          score += 10;
          reasons.push("CPU/tabular-friendly — fast local backtesting without multi-GPU clusters");
        }
      }

      if (profile.goal === "Win Cash / USDC / NMR") {
        if (comp.prize_usd >= 25_000) {
          score += 16;
          reasons.push(`High liquid reward pool (${comp.prize}) with strong payout upside`);
        } else if (comp.prize_usd > 0) {
          score += 8;
        } else {
          score -= 10;
        }
      } else if (profile.goal === "Prop Trading & Hedge Fund Recruiting") {
        if (
          comp.conference ||
          ["Wunder Fund", "Jane Street", "WorldQuant BRAIN", "Citadel / Correlation One", "IMC Trading", "Optiver", "G-Research", "ENS Challenge Data"].includes(comp.platform)
        ) {
          score += 18;
          reasons.push(`Direct visibility with institutional quant desks (${comp.organizer})`);
        }
      } else if (profile.goal === "Quant Research & Publications") {
        if (comp.conference || comp.difficulty === "Research" || comp.platform === "ENS Challenge Data") {
          score += 18;
          reasons.push(
            comp.conference
              ? `Backed by ${comp.conference} research track`
              : "Publication-grade institutional dataset & benchmark",
          );
        }
      } else if (profile.goal === "Build Live Algo Track Record") {
        if (comp.competition_type === "tournament" || ["Numerai", "CrunchDAO", "WorldQuant BRAIN", "QuantConnect", "Algogene"].includes(comp.platform)) {
          score += 18;
          reasons.push(`Live out-of-sample track record on ${comp.platform}`);
        }
      }

      if (comp.days_remaining !== null) {
        if (comp.days_remaining >= 7 && comp.days_remaining <= 120) {
          score += 6;
          reasons.push(`${comp.days_remaining} days left — ideal window for walk-forward validation`);
        } else if (comp.days_remaining <= 3 && profile.hoursPerWeek < 15) {
          score -= 12;
        }
      } else if (comp.competition_type === "tournament") {
        score += 6;
        reasons.push("Continuous rolling rounds — deploy when your alpha is ready");
      }

      const clampedScore = Math.max(45, Math.min(99, Math.round(score)));
      const blueprint = buildDomainBlueprint(comp);

      return {
        competition: comp,
        matchScore: clampedScore,
        headlineReason:
          reasons[0] ?? `High-signal ${comp.category} arena on ${comp.platform}`,
        whyItFits:
          reasons.length > 0
            ? reasons.slice(0, 3)
            : [
                `Active ${comp.category} challenge hosted by ${comp.organizer}`,
                `Difficulty (${comp.difficulty}) fits a ${profile.hoursPerWeek}h/wk research schedule`,
              ],
        winningStrategy: blueprint.strategy,
        suggestedStack: blueprint.stack,
        roadmap: blueprint.roadmap,
      };
    })
    .sort((a, b) => b.matchScore - a.matchScore || b.competition.prize_usd - a.competition.prize_usd)
    .slice(0, topK);

  return {
    mode: "smart-local",
    modelUsed: "Deterministic Quant Strategy Engine",
    summary: `Ranked ${competitions.length} live quant arenas against your ${profile.computeTier.split(" ")[0]} setup, ${profile.hoursPerWeek}h/wk bandwidth, and "${profile.goal}" objective.`,
    items: scored,
  };
}

export async function generateAiRecommendations(
  competitions: Competition[],
  profile: UserProfile,
  apiKey: string,
  topK = 4,
): Promise<RecommendationResult> {
  const localFallback = generateLocalRecommendations(competitions, profile, topK);
  const proxyUrl = getProxyUrl();

  const candidatePool = generateLocalRecommendations(competitions, profile, 16).items.map((item) => ({
    id: item.competition.id,
    title: item.competition.title,
    platform: item.competition.platform,
    organizer: item.competition.organizer,
    category: item.competition.category,
    prize: item.competition.prize,
    prize_usd: item.competition.prize_usd,
    days_remaining: item.competition.days_remaining,
    difficulty: item.competition.difficulty,
    competition_type: item.competition.competition_type,
    conference: item.competition.conference,
    evaluation_metric: item.competition.evaluation_metric,
    tags: item.competition.tags.slice(0, 5),
  }));

  if (!apiKey.trim() && proxyUrl) {
    try {
      const proxyRes = await fetch(proxyUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile, candidatePool, topK }),
      });
      if (proxyRes.ok) {
        const parsed = await proxyRes.json();
        const byId = new Map(competitions.map((c) => [c.id, c]));
        const items: RecommendationItem[] = [];
        for (const rec of parsed.recommendations ?? []) {
          const comp = byId.get(rec.id);
          if (!comp) continue;
          const fallbackBlueprint = buildDomainBlueprint(comp);
          items.push({
            competition: comp,
            matchScore: Math.max(55, Math.min(99, Number(rec.matchScore) || 88)),
            headlineReason: String(rec.headlineReason || "High-conviction quant match"),
            whyItFits: Array.isArray(rec.whyItFits) ? rec.whyItFits.map(String).slice(0, 3) : [],
            winningStrategy: String(rec.winningStrategy || fallbackBlueprint.strategy),
            suggestedStack: Array.isArray(rec.suggestedStack)
              ? rec.suggestedStack.map(String).slice(0, 5)
              : fallbackBlueprint.stack,
            roadmap:
              Array.isArray(rec.roadmap) && rec.roadmap.length > 0
                ? rec.roadmap.slice(0, 4).map((s: RoadmapStep) => ({
                    phase: String(s.phase || "Phase"),
                    title: String(s.title || "Milestone"),
                    detail: String(s.detail || ""),
                  }))
                : fallbackBlueprint.roadmap,
          });
        }
        if (items.length > 0) {
          return {
            mode: "gemini-3.8-flash",
            modelUsed: parsed.modelUsed || `${GEMINI_MODEL} (Live Quant Advisor)`,
            summary: String(parsed.summary || localFallback.summary),
            items: items.slice(0, topK),
          };
        }
      }
    } catch {
      // fall through
    }
  }

  if (!apiKey.trim()) {
    return localFallback;
  }

  const prompt = `You are a Principal Quantitative Researcher and Head of Alpha Strategy advising a quant researcher on which active competitions to enter right now.

User Profile:
- Technical Skills & Interests: ${profile.skills || "Python, LightGBM, PyTorch, Time-Series, Factor Modeling"}
- Preferred Quant Domains: ${profile.preferredCategories.join(", ") || "Open to any"}
- Preferred Difficulty: ${profile.difficulty}
- Compute Available: ${profile.computeTier}
- Primary Goal: ${profile.goal}
- Weekly Time Commitment: ${profile.hoursPerWeek} hours/week

Active Candidate Quant Competitions (JSON):
${JSON.stringify(candidatePool, null, 2)}

Select the top ${topK} best-matching competitions from the candidate list and return ONLY valid JSON matching the schema.`;

  const responseSchema = {
    type: "object",
    properties: {
      summary: { type: "string" },
      recommendations: {
        type: "array",
        items: {
          type: "object",
          properties: {
            id: { type: "string" },
            matchScore: { type: "integer" },
            headlineReason: { type: "string" },
            whyItFits: { type: "array", items: { type: "string" } },
            winningStrategy: { type: "string" },
            suggestedStack: { type: "array", items: { type: "string" } },
            roadmap: {
              type: "array",
              items: {
                type: "object",
                properties: {
                  phase: { type: "string" },
                  title: { type: "string" },
                  detail: { type: "string" },
                },
                required: ["phase", "title", "detail"],
              },
            },
          },
          required: [
            "id",
            "matchScore",
            "headlineReason",
            "whyItFits",
            "winningStrategy",
            "suggestedStack",
            "roadmap",
          ],
        },
      },
    },
    required: ["summary", "recommendations"],
  };

  try {
    const res = await fetch("https://generativelanguage.googleapis.com/v1beta/interactions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-goog-api-key": apiKey.trim(),
        "Api-Revision": GEMINI_API_REVISION,
      },
      body: JSON.stringify({
        model: GEMINI_MODEL,
        input: prompt,
        response_format: responseSchema,
        generation_config: {
          thinking_level: "low",
          temperature: 0.3,
        },
      }),
    });

    if (!res.ok) {
      throw new Error(`Gemini API HTTP ${res.status}`);
    }

    const data = await res.json();
    const outputs: Array<{ type?: string; text?: string }> = data.outputs ?? [];
    const textNode = [...outputs].reverse().find((o) => o.type === "text" && o.text) ?? outputs[outputs.length - 1];
    const rawJson = textNode?.text ?? "";
    const parsed = JSON.parse(rawJson);

    const byId = new Map(competitions.map((c) => [c.id, c]));
    const items: RecommendationItem[] = [];

    for (const rec of parsed.recommendations ?? []) {
      const comp = byId.get(rec.id);
      if (!comp) continue;
      const fallbackBlueprint = buildDomainBlueprint(comp);
      items.push({
        competition: comp,
        matchScore: Math.max(55, Math.min(99, Number(rec.matchScore) || 88)),
        headlineReason: String(rec.headlineReason || "Strong strategic quant fit"),
        whyItFits: Array.isArray(rec.whyItFits) ? rec.whyItFits.map(String).slice(0, 3) : [],
        winningStrategy: String(rec.winningStrategy || fallbackBlueprint.strategy),
        suggestedStack: Array.isArray(rec.suggestedStack)
          ? rec.suggestedStack.map(String).slice(0, 5)
          : fallbackBlueprint.stack,
        roadmap:
          Array.isArray(rec.roadmap) && rec.roadmap.length > 0
            ? rec.roadmap.slice(0, 4).map((s: RoadmapStep) => ({
                phase: String(s.phase || "Phase"),
                title: String(s.title || "Milestone"),
                detail: String(s.detail || ""),
              }))
            : fallbackBlueprint.roadmap,
      });
    }

    if (items.length === 0) return localFallback;

    return {
      mode: "gemini-3.8-flash",
      modelUsed: `${GEMINI_MODEL} (Api-Revision ${GEMINI_API_REVISION})`,
      summary: String(parsed.summary || localFallback.summary),
      items: items.slice(0, topK),
    };
  } catch {
    return localFallback;
  }
}

