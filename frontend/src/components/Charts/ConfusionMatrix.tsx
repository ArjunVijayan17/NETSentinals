import type { ConfusionMatrix as CM } from "../../types/model";

export default function ConfusionMatrix({ data }: { data: CM }) {
  const [rowLabels, colLabels] = [data.labels, data.labels];
  const max = Math.max(...data.matrix.flat(), 1);

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr>
            <th className="p-2 text-right text-xs font-normal text-ink-mute">
              actual ↓ / predicted →
            </th>
            {colLabels.map((c) => (
              <th key={c} className="p-2 text-center font-medium text-slate-200">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rowLabels.map((r, i) => (
            <tr key={r}>
              <th className="p-2 text-right font-medium text-slate-200">{r}</th>
              {data.matrix[i].map((v, j) => {
                const diag = i === j;
                const intensity = Math.round((v / max) * 100);
                return (
                  <td key={j} className="p-1.5">
                    <div
                      className="grid h-14 place-items-center rounded font-mono text-slate-100"
                      style={{
                        background: diag
                          ? `rgba(0, 212, 170, ${0.15 + (intensity / 100) * 0.5})`
                          : `rgba(239, 68, 68, ${0.1 + (intensity / 100) * 0.4})`,
                      }}
                      title={`${r} → ${colLabels[j]}: ${v.toLocaleString()}`}
                    >
                      {v.toLocaleString()}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
