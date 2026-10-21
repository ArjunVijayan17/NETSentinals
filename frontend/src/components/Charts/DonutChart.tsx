import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

interface Props {
  benign: number;
  attack: number;
}

export default function DonutChart({ benign, attack }: Props) {
  const data = [
    { name: "Benign", value: benign, color: "#22c55e" },
    { name: "Attack", value: attack, color: "#ef4444" },
  ];
  return (
    <ResponsiveContainer width="100%" height={240}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          innerRadius={70}
          outerRadius={100}
          paddingAngle={2}
          stroke="none"
        >
          {data.map((d) => (
            <Cell key={d.name} fill={d.color} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            background: "#161a24",
            border: "1px solid #232936",
            borderRadius: 8,
          }}
          itemStyle={{ color: "#e2e8f0" }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
