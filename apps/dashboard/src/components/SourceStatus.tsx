import React, { useState } from "react";
import { Activity, AlertCircle, CheckCircle2, ChevronDown, ChevronUp, Database } from "lucide-react";
import { SourceStatusItem } from "../types";

interface SourceStatusProps {
  sources: SourceStatusItem[];
}

export const SourceStatus: React.FC<SourceStatusProps> = ({ sources }) => {
  const [expanded, setExpanded] = useState(false);
  if (!sources || sources.length === 0) return null;

  const okCount = sources.filter((s) => s.status === "ok" || s.status === "cached").length;

  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 backdrop-blur-md overflow-hidden">
      <button
        type="button"
        onClick={() => setExpanded((e) => !e)}
        className="w-full flex items-center justify-between px-4 py-3 text-xs text-slate-400 hover:text-slate-200 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-emerald-400" />
          <span className="font-medium text-slate-300">Quant Scraper Feed Health</span>
          <span className="text-slate-500">
            ({okCount}/{sources.length} sources operational)
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="hidden sm:flex items-center gap-1">
            {sources.map((s) => (
              <span
                key={s.name}
                title={`${s.name}: ${s.status} (${s.count} quant records)`}
                className={`w-2 h-2 rounded-full ${
                  s.status === "ok"
                    ? "bg-emerald-400"
                    : s.status === "cached"
                      ? "bg-amber-400"
                      : "bg-slate-600"
                }`}
              />
            ))}
          </div>
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {expanded && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2.5 px-4 pb-4 pt-1 border-t border-slate-800/60">
          {sources.map((src) => {
            const isOk = src.status === "ok";
            const isCached = src.status === "cached";
            return (
              <div
                key={src.name}
                className="rounded-lg border border-slate-800/80 bg-slate-950/60 p-2.5 flex items-start justify-between gap-2"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-1.5">
                    {isOk ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    ) : isCached ? (
                      <Database className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    ) : (
                      <AlertCircle className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    )}
                    <span className="text-xs font-semibold text-slate-200 capitalize truncate">
                      {src.name}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">
                    {src.count} quant records · {(src.duration_ms / 1000).toFixed(1)}s
                  </div>
                  {src.error && (
                    <div className="text-[10px] text-amber-400/80 truncate mt-0.5" title={src.error}>
                      {src.error}
                    </div>
                  )}
                </div>
                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-semibold tracking-wider ${
                    isOk
                      ? "bg-emerald-500/15 text-emerald-300"
                      : isCached
                        ? "bg-amber-500/15 text-amber-300"
                        : "bg-slate-800 text-slate-400"
                  }`}
                >
                  {src.status}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

