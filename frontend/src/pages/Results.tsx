import { Link, useParams } from "react-router-dom";
import { downloadUrl } from "../api/analyses";
import { useAnalysisDetail } from "../hooks/useAnalysis";
import StatCard from "../components/Cards/StatCard";
import DonutChart from "../components/Charts/DonutChart";
import CategoryBarChart from "../components/Charts/CategoryBarChart";
import DataTable from "../components/Table/DataTable";

export default function Results() {
  const { id } = useParams();
  const { analysis, loading, error } = useAnalysisDetail(id);

  if (loading) return <p className="p-6 text-ink-mute">Loading…</p>;
  if (error) return <p className="p-6 text-danger">Error: {error}</p>;
  if (!analysis) return <p className="p-6 text-ink-mute">Analysis not found.</p>;

  const categoryData = Object.entries(analysis.categories)
    .map(([category, count]) => ({ category, count }))
    .sort((a, b) => b.count - a.count);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-medium text-white">{analysis.filename}</h2>
          <p className="text-xs text-ink-mute">
            {new Date(analysis.created_at).toLocaleString()} · model{" "}
            {analysis.model_name}
          </p>
        </div>
        <div className="flex gap-2">
          <a
            href={downloadUrl(analysis.id)}
            className="rounded-md border border-ink-line bg-ink-soft px-3 py-1.5 text-sm text-slate-200 hover:border-accent/50"
          >
            Download CSV
          </a>
          <Link
            to="/analyze"
            className="rounded-md border border-ink-line bg-ink-soft px-3 py-1.5 text-sm text-slate-200 hover:border-accent/50"
          >
            New analysis
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Total Rows" value={analysis.total_rows.toLocaleString()} accent="teal" />
        <StatCard label="Benign" value={analysis.benign_count.toLocaleString()} accent="green" />
        <StatCard label="Attacks" value={analysis.attack_count.toLocaleString()} accent="red" />
        <StatCard label="Attack Rate" value={`${analysis.attack_rate.toFixed(2)}%`} accent="red" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-lg border border-ink-line bg-ink-soft p-5">
          <h3 className="mb-3 text-sm font-medium text-slate-200">Benign vs Attack</h3>
          <DonutChart benign={analysis.benign_count} attack={analysis.attack_count} />
        </section>
        <section className="rounded-lg border border-ink-line bg-ink-soft p-5">
          <h3 className="mb-3 text-sm font-medium text-slate-200">Attack Categories</h3>
          {categoryData.length ? (
            <CategoryBarChart data={categoryData} />
          ) : (
            <div className="grid h-40 place-items-center text-sm text-ink-mute">
              No attack rows detected.
            </div>
          )}
        </section>
      </div>

      <section className="rounded-lg border border-ink-line bg-ink-soft p-5">
        <h3 className="mb-3 text-sm font-medium text-slate-200">Row Results</h3>
        <DataTable rows={analysis.row_results} />
      </section>
    </div>
  );
}
