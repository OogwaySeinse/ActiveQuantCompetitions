/**
 * Cloudflare Worker proxy for the Active Quant Competitions AI Strategy Matchmaker.
 * Holds GEMINI_API_KEY as an encrypted Worker Secret and calls Gemini 3.8 Flash
 * (/v1beta/interactions with Api-Revision: 2026-05-20).
 */

export interface Env {
  GEMINI_API_KEY: string;
  ALLOWED_ORIGIN?: string;
}

const GEMINI_MODEL = "gemini-3.8-flash";
const GEMINI_API_REVISION = "2026-05-20";

function corsHeaders(origin: string | null, allowedOrigin?: string): Record<string, string> {
  const allow = allowedOrigin && allowedOrigin !== "*" ? allowedOrigin : origin || "*";
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
  };
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const origin = request.headers.get("Origin");
    const headers = corsHeaders(origin, env.ALLOWED_ORIGIN);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers });
    }

    if (request.method !== "POST") {
      return new Response(
        JSON.stringify({ status: "ok", model: GEMINI_MODEL, service: "active-quant-recommender" }),
        { status: 200, headers: { ...headers, "Content-Type": "application/json" } },
      );
    }

    if (!env.GEMINI_API_KEY) {
      return new Response(
        JSON.stringify({ error: "GEMINI_API_KEY secret is not configured on Worker" }),
        { status: 503, headers: { ...headers, "Content-Type": "application/json" } },
      );
    }

    try {
      const body: {
        profile?: {
          skills?: string;
          preferredCategories?: string[];
          difficulty?: string;
          computeTier?: string;
          goal?: string;
          hoursPerWeek?: number;
        };
        candidatePool?: unknown[];
        topK?: number;
      } = await request.json();

      const profile = body.profile ?? {};
      const candidatePool = (body.candidatePool ?? []).slice(0, 18);
      const topK = Math.min(6, Math.max(1, Number(body.topK) || 4));

      const prompt = `You are a Principal Quantitative Researcher and Head of Alpha Strategy advising a quant researcher on which active competitions to enter right now.

User Profile:
- Technical Skills & Interests: ${profile.skills || "Python, LightGBM, PyTorch, Time-Series, Factor Modeling"}
- Preferred Quant Domains: ${(profile.preferredCategories || []).join(", ") || "Open to any"}
- Preferred Difficulty: ${profile.difficulty || "Any"}
- Compute Available: ${profile.computeTier || "Single GPU"}
- Primary Goal: ${profile.goal || "Win Cash / USDC / NMR"}
- Weekly Time Commitment: ${profile.hoursPerWeek || 10} hours/week

Active Candidate Quant Competitions (JSON):
${JSON.stringify(candidatePool)}

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

      const upstream = await fetch("https://generativelanguage.googleapis.com/v1beta/interactions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-goog-api-key": env.GEMINI_API_KEY,
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

      if (!upstream.ok) {
        const errText = await upstream.text();
        return new Response(
          JSON.stringify({ error: `Gemini upstream ${upstream.status}`, detail: errText }),
          { status: 502, headers: { ...headers, "Content-Type": "application/json" } },
        );
      }

      const data: { outputs?: Array<{ type?: string; text?: string }> } = await upstream.json();
      const outputs = data.outputs ?? [];
      const textNode =
        [...outputs].reverse().find((o) => o.type === "text" && o.text) ?? outputs[outputs.length - 1];
      const parsed = JSON.parse(textNode?.text ?? "{}");

      return new Response(
        JSON.stringify({
          modelUsed: `${GEMINI_MODEL} (Live Quant Cloud Advisor)`,
          ...parsed,
        }),
        { status: 200, headers: { ...headers, "Content-Type": "application/json" } },
      );
    } catch (err) {
      return new Response(
        JSON.stringify({ error: err instanceof Error ? err.message : "Internal error" }),
        { status: 500, headers: { ...headers, "Content-Type": "application/json" } },
      );
    }
  },
};

