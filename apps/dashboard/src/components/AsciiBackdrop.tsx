import React from "react";

const QUANT_ASCII_LINES = [
  "┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐",
  "│  WUNDERQUANT // ORDER-BOOK & ALPHA TELEMETRY   dS_t = μ S_t dt + σ S_t dW_t    IC(α_t, r_{t+h}) = E[rank(α)·rank(r)] │",
  "├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤",
  "│  L2_BOOK [BID]  99.98 (420) ── 99.99 (185) ── [MID: 100.000] ── 100.01 (110) ── 100.02 (640) [ASK]   OFI_t = +0.418  │",
  "│  SHARPE_OOS = E[R_p - R_f] / σ_p = 3.42      IR = α / ω = 2.87      PURGED_CV(k=5, embargo=20d)      TURNOVER = 8.4% │",
  "│  NUMERAI :: CRUNCHDAO :: WORLDQUANT_BRAIN :: ENS_QRT :: WUNDERNN_LOB :: JANE_STREET :: IMC_PROSPERITY :: CITADEL     │",
  "│  w* = argmax_w (w^T α - λ w^T Σ_LW w - γ ||Δw||_1)     s.t.  β^T w = 0,  1^T w = 0,  ||w||_∞ ≤ 0.02                  │",
  "│  Hawkes λ(t) = μ + ∑ α_i exp(-β_i (t - t_i))     VolSurface σ_impl(K, T)     GARCH(1,1) σ²_t = ω + α ε²_{t-1} + β σ² │",
  "└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘",
];

export const AsciiBackdrop: React.FC = () => {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none select-none overflow-hidden absolute inset-x-0 top-0 h-[420px] opacity-[0.045]"
    >
      <pre className="ascii-drift font-mono text-[11px] leading-[1.65] text-emerald-300 whitespace-pre px-4 pt-3">
        {QUANT_ASCII_LINES.join("\n")}
        {"\n"}
        {QUANT_ASCII_LINES.join("\n")}
      </pre>
    </div>
  );
};

