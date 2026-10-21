import { Link } from "react-router-dom";
import { useAnalyses } from "../hooks/useAnalysis";
import Badge from "../components/Table/Badge";

export default function History() {
  const { analyses, loading, error } = useAnalyses();

  if (loading) return <p className="p-6 text-ink-mute">Loading…</p>;
  if (error) return <p className="p-6 text-danger">Error: {error}</p>;

  if (!analyses.length) {
    return (
      <div className="grid h-40 place-items-center text-sm text-ink-mute">
        No analyses yet.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-ink-line">
      <table className="w-full text-sm">
        <thead className="bg-ink-soft text-left text-xs uppercase text-ink-mute">
          <tr>
            <th className="px-4 py-2">File</th>
            <th className="px-4 py-2">Date</th>
            <th className="px-4 py-2 text-right">Rows</th>
            <th className="px-4 py-2 text-right">Benign</th>
            <th className="px-4 py-2 text-right">Attack</th>
            <th className="px-4 py-2 text-right">Rate</th>
            <th className="px-4 py-2">Label</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-ink-line">
          {analyses.map((a) => (
            <tr key={a.id} className="hover:bg-ink-soft">
              <td className="px-4 py-2">
                <Link to={`/analyses/${a.id}`} className="text-accent hover:underline">
                  {a.filename}
                </Link>
              </td>
              <td className="px-4 py-2 text-ink-mute">
                {new Date(a.created_at).toLocaleString()}
              </td>
              <td className="px-4 py-2 text-right font-mono">{a.total_rows.toLocaleString()}</td>
              <td className="px-4 py-2 text-right font-mono text-safe">
                {a.benign_count.toLocaleString()}
              </td>
              <td className="px-4 py-2 text-right font-mono text-danger">
                {a.attack_count.toLocaleString()}
              </td>
              <td className="px-4 py-2 text-right font-mono">{a.attack_rate.toFixed(2)}%</td>
              <td className="px-4 py-2">
                <Badge kind={a.attack_count > 0 ? "attack" : "benign"}>
                  {a.attack_count > 0 ? "Attack found" : "All benign"}
                </Badge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
