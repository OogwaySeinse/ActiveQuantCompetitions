import React, { useMemo, useState } from "react";
import {
  ColumnDef,
  SortingState,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import {
  ArrowDown,
  ArrowUp,
  ArrowUpDown,
  Bookmark,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  FileText,
  GraduationCap,
  Sparkles,
  Users,
} from "lucide-react";
import { Competition } from "../types";
import {
  DIFFICULTY_STYLES,
  STATUS_STYLES,
  formatDeadlineCountdown,
  getPlatformStyle,
} from "../utils/format";

interface CompetitionTableProps {
  competitions: Competition[];
  bookmarks: Set<string>;
  onToggleBookmark: (id: string) => void;
  onSelectTag: (tag: string) => void;
}

export const CompetitionTable: React.FC<CompetitionTableProps> = ({
  competitions,
  bookmarks,
  onToggleBookmark,
  onSelectTag,
}) => {
  const [sorting, setSorting] = useState<SortingState>([]);

  const columns = useMemo<ColumnDef<Competition>[]>(
    () => [
      {
        id: "bookmark",
        header: () => <span className="sr-only">Save</span>,
        cell: ({ row }) => {
          const isSaved = bookmarks.has(row.original.id);
          return (
            <button
              type="button"
              onClick={() => onToggleBookmark(row.original.id)}
              title={isSaved ? "Remove from saved quant arenas" : "Bookmark quant arena"}
              className="p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
            >
              <Bookmark
                className={`w-4 h-4 ${
                  isSaved ? "fill-pink-500 text-pink-400" : "text-slate-600 hover:text-slate-300"
                }`}
              />
            </button>
          );
        },
        size: 40,
      },
      {
        accessorKey: "title",
        header: "Quant Arena / Challenge",
        cell: ({ row }) => {
          const c = row.original;
          return (
            <div className="space-y-1.5 min-w-[260px] max-w-xl">
              <div className="flex items-start gap-2 flex-wrap">
                <a
                  href={c.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-semibold text-slate-100 hover:text-emerald-300 transition-colors leading-snug inline-flex items-center gap-1.5 group"
                >
                  <span>{c.title}</span>
                  <ExternalLink className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity text-emerald-400 shrink-0" />
                </a>

                {c.is_new && (
                  <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                    <Sparkles className="w-2.5 h-2.5" />
                    NEW
                  </span>
                )}

                {c.competition_type === "tournament" && (
                  <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                    ⟳ Rolling Tournament
                  </span>
                )}

                {c.competition_type === "benchmark" && (
                  <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-400 border border-slate-700">
                    ♾️ Archive Benchmark
                  </span>
                )}

                {c.conference && (
                  <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-purple-500/15 text-purple-300 border border-purple-500/35">
                    <GraduationCap className="w-2.5 h-2.5" />
                    {c.conference}
                    {c.conference_year ? ` ${c.conference_year}` : ""}
                  </span>
                )}

                {c.paper_url && (
                  <a
                    href={c.paper_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-sky-500/15 text-sky-300 border border-sky-500/30 hover:bg-sky-500/25 transition-colors"
                    title="View associated research paper / SSRN / arXiv specification"
                  >
                    <FileText className="w-2.5 h-2.5" />
                    Paper
                  </a>
                )}
              </div>

              {c.description && (
                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                  {c.description}
                </p>
              )}

              <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
                {c.organizer && c.organizer !== c.platform && (
                  <span className="text-[11px] text-slate-400 font-medium">
                    Sponsor: <span className="text-slate-300">{c.organizer}</span> ·
                  </span>
                )}
                {(c.teams_count || c.competitors_count) && (
                  <span className="inline-flex items-center gap-1 text-[11px] text-slate-400">
                    <Users className="w-3 h-3 text-slate-500" />
                    {(c.teams_count ?? c.competitors_count)?.toLocaleString("en-US")}{" "}
                    {c.teams_count ? "teams" : "quants"}
                  </span>
                )}
                {c.tags.slice(0, 4).map((tag) => (
                  <button
                    key={tag}
                    type="button"
                    onClick={() => onSelectTag(tag)}
                    className="px-1.5 py-0.5 rounded bg-slate-800/80 hover:bg-slate-700/80 text-[10px] text-slate-300 transition-colors"
                  >
                    #{tag}
                  </button>
                ))}
              </div>
            </div>
          );
        },
      },
      {
        accessorKey: "platform",
        header: "Venue",
        cell: ({ row }) => {
          const p = row.original.platform;
          const style = getPlatformStyle(p);
          return (
            <span
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border whitespace-nowrap ${style.bg} ${style.text} ${style.border}`}
            >
              <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: style.dot }} />
              {p}
            </span>
          );
        },
      },
      {
        accessorKey: "category",
        header: "Quant Domain",
        cell: ({ row }) => (
          <span className="inline-block px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs text-slate-200 whitespace-nowrap">
            {row.original.category}
          </span>
        ),
      },
      {
        accessorKey: "prize_usd",
        header: "Prize / Staking Pool",
        cell: ({ row }) => {
          const c = row.original;
          const isCash = c.prize_usd > 0;
          const delta = c.prize_delta_usd ?? 0;
          return (
            <div className="whitespace-nowrap">
              <div className="flex items-center gap-1.5">
                <span
                  className={`font-semibold text-sm tabular-nums ${
                    isCash ? "text-emerald-300" : "text-slate-400 font-normal text-xs"
                  }`}
                >
                  {c.prize}
                </span>
                {delta !== 0 && (
                  <span
                    className={`px-1 py-0.5 rounded text-[10px] font-semibold tabular-nums ${
                      delta > 0
                        ? "bg-emerald-500/20 text-emerald-300"
                        : "bg-rose-500/20 text-rose-300"
                    }`}
                  >
                    {delta > 0 ? `+$${delta.toLocaleString()}` : `-$${Math.abs(delta).toLocaleString()}`}
                  </span>
                )}
              </div>
              {isCash && c.prize_currency !== "USD" && c.prize_currency !== "USDC" && (
                <div className="text-[11px] text-slate-500">{c.prize_currency} pool</div>
              )}
            </div>
          );
        },
      },
      {
        id: "deadline",
        accessorFn: (row) => row.days_remaining ?? 999999,
        header: "Settlement / Deadline",
        cell: ({ row }) => {
          const c = row.original;
          const st = STATUS_STYLES[c.status] ?? STATUS_STYLES.active;
          const countdown = formatDeadlineCountdown(c.days_remaining, c.end_date);
          const urgencyPct =
            c.days_remaining !== null && c.days_remaining >= 0
              ? Math.max(6, Math.min(100, Math.round(((60 - Math.min(60, c.days_remaining)) / 60) * 100)))
              : null;

          return (
            <div className="space-y-1 min-w-[140px]">
              <div className="flex items-center gap-1.5">
                <span
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium border ${st.bg} ${st.text} ${st.border}`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${st.dot}`} />
                  {countdown}
                </span>
              </div>
              {c.end_date && (
                <div className="text-[11px] text-slate-500 tabular-nums pl-1 flex items-center gap-1.5">
                  <span>{c.end_date}</span>
                  {c.days_Shift ? (
                    <span
                      className="text-[10px] px-1 rounded bg-amber-500/15 text-amber-300"
                      title="Deadline shifted since previous snapshot"
                    >
                      {c.days_Shift > 0 ? `+${c.days_Shift}d` : `${c.days_Shift}d`}
                    </span>
                  ) : null}
                </div>
              )}
              {urgencyPct !== null && c.days_remaining !== null && c.days_remaining <= 45 && (
                <div className="w-24 h-1 rounded-full bg-slate-800 overflow-hidden ml-1">
                  <div
                    className={`h-full rounded-full ${
                      c.days_remaining <= 7 ? "bg-amber-400" : "bg-emerald-400"
                    }`}
                    style={{ width: `${urgencyPct}%` }}
                  />
                </div>
              )}
            </div>
          );
        },
      },
      {
        accessorKey: "difficulty",
        header: "Tier & Metric",
        cell: ({ row }) => {
          const diff = row.original.difficulty;
          const cls = DIFFICULTY_STYLES[diff] ?? DIFFICULTY_STYLES.Intermediate;
          return (
            <div className="space-y-1">
              <span className={`inline-block px-2 py-0.5 rounded-md text-xs font-medium border ${cls}`}>
                {diff}
              </span>
              {row.original.evaluation_metric && (
                <div className="text-[11px] text-slate-500 truncate max-w-[145px]" title={row.original.evaluation_metric}>
                  {row.original.evaluation_metric}
                </div>
              )}
            </div>
          );
        },
      },
      {
        id: "action",
        header: () => <span className="sr-only">Action</span>,
        cell: ({ row }) => (
          <a
            href={row.original.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-500/15 hover:bg-emerald-500 text-emerald-300 hover:text-slate-950 border border-emerald-500/30 text-xs font-semibold transition-all whitespace-nowrap"
          >
            <span>Enter</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        ),
      },
    ],
    [bookmarks, onToggleBookmark, onSelectTag],
  );

  const table = useReactTable({
    data: competitions,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize: 25,
      },
    },
  });

  if (competitions.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 p-12 text-center space-y-2">
        <div className="text-base font-medium text-slate-300">
          No quant arenas match your current filter criteria
        </div>
        <p className="text-xs text-slate-500">
          Try clearing a venue/domain filter, lowering the minimum pool threshold, or toggling{" "}
          <span className="text-cyan-400">♾️ Archive Benchmarks</span>.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 backdrop-blur-md overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id} className="border-b border-slate-800/80 bg-slate-950/60">
                {headerGroup.headers.map((header) => {
                  const canSort = header.column.getCanSort();
                  const sorted = header.column.getIsSorted();
                  return (
                    <th
                      key={header.id}
                      onClick={canSort ? header.column.getToggleSortingHandler() : undefined}
                      className={`px-4 py-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400 select-none ${
                        canSort ? "cursor-pointer hover:text-slate-200" : ""
                      }`}
                    >
                      <div className="flex items-center gap-1.5">
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {canSort && header.id !== "bookmark" && header.id !== "action" && (
                          <span className="text-slate-600">
                            {sorted === "asc" ? (
                              <ArrowUp className="w-3 h-3 text-emerald-400" />
                            ) : sorted === "desc" ? (
                              <ArrowDown className="w-3 h-3 text-emerald-400" />
                            ) : (
                              <ArrowUpDown className="w-3 h-3 opacity-60" />
                            )}
                          </span>
                        )}
                      </div>
                    </th>
                  );
                })}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-slate-800/50 text-sm">
            {table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                className="hover:bg-slate-800/35 transition-colors group"
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-3.5 align-top">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 px-4 py-3 border-t border-slate-800/80 bg-slate-950/40 text-xs text-slate-400">
        <div>
          Showing{" "}
          <span className="font-medium text-slate-200">
            {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1}
          </span>{" "}
          to{" "}
          <span className="font-medium text-slate-200">
            {Math.min(
              (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
              competitions.length,
            )}
          </span>{" "}
          of <span className="font-medium text-slate-200">{competitions.length}</span> quant arenas
        </div>

        <div className="flex items-center gap-2">
          <select
            value={table.getState().pagination.pageSize}
            onChange={(e) => table.setPageSize(Number(e.target.value))}
            className="px-2 py-1 rounded-lg border border-slate-800 bg-slate-900 text-xs text-slate-300"
          >
            {[15, 25, 50, 100].map((size) => (
              <option key={size} value={size}>
                {size} / page
              </option>
            ))}
          </select>

          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 disabled:opacity-40 hover:border-slate-700"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <span className="px-2 tabular-nums">
              Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
            </span>
            <button
              type="button"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 disabled:opacity-40 hover:border-slate-700"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

