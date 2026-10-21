interface Props {
  label: string;
  value: string | number;
  accent?: "teal" | "green" | "red" | "neutral";
  hint?: string;
}

const accentMap: Record<NonNullable<Props["accent"]>, string> = {
  teal: "text-accent",
  green: "text-safe",
  red: "text-danger",
  neutral: "text-slate-100",
};

export default function StatCard({ label, value, accent = "neutral", hint }: Props) {
  return (
    <div className="rounded-lg border border-ink-line bg-ink-soft p-5">
      <div className="text-xs uppercase tracking-wide text-ink-mute">{label}</div>
      <div className={`mt-2 text-3xl font-semibold ${accentMap[accent]}`}>{value}</div>
      {hint && <div className="mt-1 text-xs text-ink-mute">{hint}</div>}
    </div>
  );
}
