import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { FeatureImportance } from "../../types/model";

interface Props {
  data: FeatureImportance[];
}

export default function FeatureImportanceChart({ data }: Props) {
  const chartData = data.map((d) => ({
    feature: d.feature,
    importance: Number((d.importance * 100).toFixed(2)),
  }));
  return (
    <ResponsiveContainer width="100%" height={360}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 8, right: 24, left: 24, bottom: 8 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#232936" horizontal={false} />
        <XAxis type="number" stroke="#8b93a7" tick={{ fill: "#8b93a7", fontSize: 11 }} />
        <YAxis
          type="category"
          dataKey="feature"
          stroke="#8b93a7"
          width={180}
          tick={{ fill: "#8b93a7", fontSize: 11 }}
        />
        <Tooltip
          cursor={{ fill: "#23293655" }}
          contentStyle={{
            background: "#161a24",
            border: "1px solid #232936",
            borderRadius: 8,
          }}
          itemStyle={{ color: "#e2e8f0" }}
          formatter={(v) => [`${v}%`, "importance"]}
        />
        <Bar dataKey="importance" fill="#00d4aa" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
