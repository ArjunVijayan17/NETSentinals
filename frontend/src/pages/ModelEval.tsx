import { useModels } from "../hooks/useModels";
import ModelCard from "../components/Cards/ModelCard";
import ConfusionMatrix from "../components/Charts/ConfusionMatrix";
import FeatureImportanceChart from "../components/Charts/FeatureImportanceChart";

const NAME: Record<string, string> = {
  random_forest: "Random Forest",
  decision_tree: "Decision Tree",
  knn: "K-Nearest Neighbors",
};

export default function ModelEval() {
  const { metrics, loading, error } = useModels();

  if (loading) return <p className="p-6 text-ink-mute">Loading…</p>;
  if (error) return <p className="p-6 text-danger">Error: {error}</p>;
  if (!metrics) return <p className="p-6 text-ink-mute">No metrics available.</p>;

  const binaryNames = Object.keys(metrics.binary);

  return (
    <div className="space-y-8">
      <div className="rounded-lg border border-ink-line bg-ink-soft p-5 text-sm text-ink-mute">
        {metrics.dataset.disclaimer}
      </div>

      <section>
        <h2 className="mb-3 text-base font-medium text-slate-100">
          Binary Models
        </h2>
        <div className="grid gap-4 md:grid-cols-3">
          {binaryNames.map((name) => (
            <ModelCard key={name} name={name} summary={metrics.binary[name].summary} />
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-base font-medium text-slate-100">
          Confusion Matrices
        </h2>
        <div className="grid gap-6 lg:grid-cols-3">
          {binaryNames.map((name) => (
            <div key={name} className="rounded-lg border border-ink-line bg-ink-soft p-5">
              <h3 className="mb-3 text-sm font-medium text-slate-200">
                {NAME[name]}
              </h3>
              <ConfusionMatrix data={metrics.binary[name].confusion_matrix} />
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-base font-medium text-slate-100">
          Feature Importance — Binary Random Forest
        </h2>
        <div className="rounded-lg border border-ink-line bg-ink-soft p-5">
          <FeatureImportanceChart data={metrics.feature_importance.binary} />
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-base font-medium text-slate-100">
          Feature Importance — Attack-Type Random Forest
        </h2>
        <div className="rounded-lg border border-ink-line bg-ink-soft p-5">
          <FeatureImportanceChart data={metrics.feature_importance.attack_type} />
        </div>
      </section>
    </div>
  );
}
