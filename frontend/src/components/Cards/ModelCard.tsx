import type { BinarySummary } from "../../types/model";

const NAME: Record<string, string> = {
  random_forest: "Random Forest",
  decision_tree: "Decision Tree",
  knn: "K-Nearest Neighbors",
};

function Pct({ value }: { value: number }) {
  return <span>{(value * 100).toFixed(2)}%</span>;
}

export default function ModelCard({
  name,
  summary,
}: {
  name: string;
  summary: BinarySummary;
}) {
  const rows: Array<[string, number]> = [
    ["Accuracy", summary.accuracy],
    ["Precision", summary.precision],
    ["Recall", summary.recall],
    ["F1", summary.f1],
  ];
  return (
    <div className="rounded-lg border border-ink-line bg-ink-soft p-5">
      <h3 className="font-medium text-white">{NAME[name] ?? name}</h3>
      <p className="mt-0.5 text-xs text-ink-mute">{name}</p>
      <dl className="mt-4 space-y-2">
        {rows.map(([k, v]) => (
          <div key={k} className="flex justify-between text-sm">
            <dt className="text-ink-mute">{k}</dt>
            <dd className="font-medium text-accent">
              <Pct value={v} />
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
