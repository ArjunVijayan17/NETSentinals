import { Link } from "react-router-dom";
import { useAnalyses } from "../hooks/useAnalysis";
import StatCard from "../components/Cards/StatCard";
import DonutChart from "../components/Charts/DonutChart";
import CategoryBarChart from "../components/Charts/CategoryBarChart";

export default function Overview() {
  const { analyses, loading, error } = useAnalyses();

  const totals = analyses.reduce(
    (acc, a) => ({
      rows: acc.rows + a.total_rows,
      benign: acc.benign + a.benign_count,
      attack: acc.attack + a.attack_count,
    }),
    { rows: 0, benign: 0, attack: 0 },
  );
  const categoryTotals = analyses.reduce<Record<string, number>>((acc, a) => {
    for (const [cat, n] of Object.entries(a.categories ?? {})) {
      acc[cat] = (acc[cat] ?? 0) + n;
    }
    return acc;
  }, {});
  const categoryData = Object.entries(categoryTotals)
    .map(([category, count]) => ({ category, count }))
    .sort((a, b) => b.count - a.count);
  const attackRate = totals.rows ? (totals.attack / totals.rows) * 100 : 0;
  const recent = analyses.slice(0, 5);

  if (loading) return <p className="p-6 text-ink-mute">Loading…</p>;
  if (error) return <p className="p-6 text-danger">Error: {error}</p>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Total Analyzed" value={totals.rows.toLocaleString()} accent="teal" />
        <StatCard label="Attack Rate" value={`${attackRate.toFixed(2)}%`} accent="red" />
        <StatCard label="Benign" value={totals.benign.toLocaleString()} accent="green" />
        <StatCard label="Attacks" value={totals.attack.toLocaleString()} accent="red" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-lg border border-ink-line bg-ink-soft p-5">
          <h2 className="mb-3 text-sm font-medium text-slate-200">
            Benign vs Attack
          </h2>
          {totals.rows ? (
            <DonutChart benign={totals.benign} attack={totals.attack} />
          ) : (
            <EmptyHint />
          )}
        </section>

        <section className="rounded-lg border border-ink-line bg-ink-soft p-5">
          <h2 className="mb-3 text-sm font-medium text-slate-200">
            Recent Analyses
          </h2>
          <RecentTable rows={recent} />
        </section>
      </div>

      <section className="rounded-lg border border-ink-line bg-ink-soft p-5">
        <h2 className="mb-3 text-sm font-medium text-slate-200">
          Attack Categories (all analyses)
        </h2>
        {categoryData.length ? (
          <CategoryBarChart data={categoryData} />
        ) : (
          <EmptyHint />
        )}
      </section>
    </div>
  );
}

function EmptyHint() {
  return (
    <div className="grid h-40 place-items-center text-sm text-ink-mute">
      No analyses yet. Upload a CSV from the Analyze tab.
    </div>
  );
}

function RecentTable({ rows }: { rows: ReturnType<typeof useAnalyses>["analyses"] }) {
  if (!rows.length) return <EmptyHint />;
  return (
    <table className="w-full text-sm">
      <thead className="text-left text-xs uppercase text-ink-mute">
        <tr>
          <th className="py-2">File</th>
          <th className="py-2">Date</th>
          <th className="py-2 text-right">Rows</th>
          <th className="py-2 text-right">Attack %</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-ink-line">
        {rows.map((a) => (
          <tr key={a.id} className="hover:bg-ink-line/40">
            <td className="py-2">
              <Link to={`/analyses/${a.id}`} className="text-accent hover:underline">
                {a.filename}
              </Link>
            </td>
            <td className="py-2 text-ink-mute">
              {new Date(a.created_at).toLocaleString()}
            </td>
            <td className="py-2 text-right font-mono">{a.total_rows.toLocaleString()}</td>
            <td className="py-2 text-right font-mono">{a.attack_rate.toFixed(2)}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
