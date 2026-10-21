import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface Props {
  data: Array<{ category: string; count: number }>;
}

export default function CategoryBarChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#232936" vertical={false} />
        <XAxis
          dataKey="category"
          stroke="#8b93a7"
          tick={{ fill: "#8b93a7", fontSize: 11 }}
          interval={0}
          angle={-30}
          textAnchor="end"
          height={70}
        />
        <YAxis stroke="#8b93a7" tick={{ fill: "#8b93a7", fontSize: 11 }} allowDecimals={false} />
        <Tooltip
          cursor={{ fill: "#23293655" }}
          contentStyle={{
            background: "#161a24",
            border: "1px solid #232936",
            borderRadius: 8,
          }}
          itemStyle={{ color: "#e2e8f0" }}
        />
        <Bar dataKey="count" fill="#00d4aa" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
