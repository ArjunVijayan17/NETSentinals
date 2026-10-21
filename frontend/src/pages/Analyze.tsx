import { useState } from "react";
import { Link } from "react-router-dom";
import { downloadUrl, uploadCsv } from "../api/analyses";
import type { AnalysisDetail } from "../types/analysis";
import DropZone from "../components/Upload/DropZone";
import ProgressBar from "../components/Upload/ProgressBar";
import StatCard from "../components/Cards/StatCard";

export default function Analyze() {
  const [fileName, setFileName] = useState<string | null>(null);
  const [progress, setProgress] = useState<number | null>(null);
  const [result, setResult] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFile = async (file: File) => {
    setFileName(file.name);
    setResult(null);
    setError(null);
    setProgress(0);
    try {
      const data = await uploadCsv(file, setProgress);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setProgress(null);
    }
  };

  return (
    <div className="space-y-6">
      <DropZone onFile={handleFile} disabled={progress !== null} />

      {fileName && progress !== null && (
        <div className="rounded-lg border border-ink-line bg-ink-soft p-5">
          <div className="mb-2 flex justify-between text-sm">
            <span className="text-slate-200">Analyzing {fileName}…</span>
            <span className="font-mono text-accent">{progress}%</span>
          </div>
          <ProgressBar value={progress} />
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-danger/40 bg-danger/10 p-4 text-sm text-danger">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard label="Total Rows" value={result.total_rows.toLocaleString()} accent="teal" />
            <StatCard label="Benign" value={result.benign_count.toLocaleString()} accent="green" />
            <StatCard label="Attacks" value={result.attack_count.toLocaleString()} accent="red" />
            <StatCard label="Attack Rate" value={`${result.attack_rate.toFixed(2)}%`} accent="red" />
          </div>

          <div className="flex items-center gap-3">
            <Link
              to={`/analyses/${result.id}`}
              className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-ink hover:bg-accent/90"
            >
              View full results
            </Link>
            <a
              href={downloadUrl(result.id)}
              className="rounded-md border border-ink-line bg-ink-soft px-4 py-2 text-sm text-slate-200 hover:border-accent/50"
            >
              Download prediction CSV
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
