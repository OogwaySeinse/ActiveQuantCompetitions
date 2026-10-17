import React, { useEffect, useRef, useState } from "react";
import { Check, ChevronDown } from "lucide-react";

interface MultiSelectProps {
  label: string;
  options: { value: string; count: number }[];
  selected: string[];
  onChange: (next: string[]) => void;
}

export const MultiSelect: React.FC<MultiSelectProps> = ({
  label,
  options,
  selected,
  onChange,
}) => {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const toggleOption = (val: string) => {
    if (selected.includes(val)) {
      onChange(selected.filter((x) => x !== val));
    } else {
      onChange([...selected, val]);
    }
  };

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-xs font-medium transition-colors ${
          selected.length > 0
            ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-200"
            : "border-slate-800 bg-slate-900/90 text-slate-300 hover:border-slate-700"
        }`}
      >
        <span>{label}</span>
        {selected.length > 0 && (
          <span className="px-1.5 py-0.5 text-[10px] rounded-full bg-emerald-500 text-slate-950 font-semibold">
            {selected.length}
          </span>
        )}
        <ChevronDown className="w-3.5 h-3.5 opacity-70" />
      </button>

      {open && (
        <div className="absolute left-0 mt-1.5 w-68 max-h-72 overflow-y-auto rounded-xl border border-slate-800 bg-slate-900/95 backdrop-blur-xl shadow-2xl z-30 p-1.5">
          <div className="flex items-center justify-between px-2 py-1 text-[11px] text-slate-400 border-b border-slate-800/80 mb-1">
            <span>{options.length} available</span>
            {selected.length > 0 && (
              <button
                type="button"
                onClick={() => onChange([])}
                className="text-emerald-400 hover:text-emerald-300 font-medium"
              >
                Clear
              </button>
            )}
          </div>
          {options.map((opt) => {
            const isChecked = selected.includes(opt.value);
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => toggleOption(opt.value)}
                className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-left transition-colors ${
                  isChecked
                    ? "bg-emerald-500/15 text-emerald-200"
                    : "text-slate-300 hover:bg-slate-800/70"
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <div
                    className={`w-3.5 h-3.5 rounded flex items-center justify-center border ${
                      isChecked
                        ? "bg-emerald-500 border-emerald-400 text-slate-950"
                        : "border-slate-700 bg-slate-950"
                    }`}
                  >
                    {isChecked && <Check className="w-2.5 h-2.5 stroke-[3]" />}
                  </div>
                  <span className="truncate">{opt.value}</span>
                </div>
                <span className="text-[11px] text-slate-500 tabular-nums ml-2">{opt.count}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

