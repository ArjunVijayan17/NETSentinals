import { useMemo, useState } from "react";
import type { RowResult } from "../../types/analysis";
import Badge from "./Badge";

const PAGE = 50;

export default function DataTable({ rows }: { rows: RowResult[] }) {
  const [page, setPage] = useState(0);
  const [query, setQuery] = useState("");
  const [sortBy, setSortBy] = useState<"row" | "confidence">("row");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const base = q
      ? rows.filter(
          (r) =>
            r.label.toLowerCase().includes(q) ||
            (r.category ?? "").toLowerCase().includes(q) ||
            String(r.row).includes(q),
        )
      : rows;
    return [...base].sort((a, b) =>
      sortBy === "row" ? a.row - b.row : b.confidence - a.confidence,
    );
  }, [rows, query, sortBy]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE));
  const current = filtered.slice(page * PAGE, (page + 1) * PAGE);

  return (
    <div>
      <div className="mb-3 flex items-center justify-between gap-3">
        <input
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setPage(0);
          }}
          placeholder="Search label, category, or row #"
          className="w-72 rounded-md border border-ink-line bg-ink-soft px-3 py-1.5 text-sm text-slate-200 placeholder:text-ink-mute focus:border-accent focus:outline-none"
        />
        <button
          onClick={() => setSortBy((s) => (s === "row" ? "confidence" : "row"))}
          className="rounded-md border border-ink-line bg-ink-soft px-3 py-1.5 text-xs text-ink-mute hover:text-slate-200"
        >
          Sort: {sortBy === "row" ? "Row #" : "Confidence"}
        </button>
      </div>

      <div className="overflow-x-auto rounded-lg border border-ink-line">
        <table className="w-full text-sm">
          <thead className="bg-ink-soft text-left text-xs uppercase text-ink-mute">
            <tr>
              <th className="px-4 py-2">Row #</th>
              <th className="px-4 py-2">Label</th>
              <th className="px-4 py-2">Category</th>
              <th className="px-4 py-2 text-right">Confidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-ink-line">
            {current.map((r) => (
              <tr key={r.row} className="hover:bg-ink-soft">
                <td className="px-4 py-2 font-mono text-ink-mute">{r.row + 1}</td>
                <td className="px-4 py-2">
                  <Badge kind={r.label === "Attack" ? "attack" : "benign"}>
                    {r.label}
                  </Badge>
                </td>
                <td className="px-4 py-2">
                  {r.category ? (
                    <Badge kind="muted">{r.category}</Badge>
                  ) : (
                    <span className="text-ink-mute">—</span>
                  )}
                </td>
                <td className="px-4 py-2 text-right font-mono text-slate-200">
                  {(r.confidence * 100).toFixed(1)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-3 flex items-center justify-between text-sm text-ink-mute">
        <span>
          {filtered.length} rows · page {page + 1}/{pageCount}
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="rounded border border-ink-line px-3 py-1 disabled:opacity-40"
          >
            Prev
          </button>
          <button
            onClick={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
            disabled={page >= pageCount - 1}
            className="rounded border border-ink-line px-3 py-1 disabled:opacity-40"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
