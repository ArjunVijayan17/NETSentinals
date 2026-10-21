import { useEffect, useMemo, useRef, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { liveStreamUrl, simulateAttack } from "../api/live";
import type { LiveFlow } from "../types/live";
import StatCard from "../components/Cards/StatCard";
import Badge from "../components/Table/Badge";

interface Bucket {
  time: string;
  benign: number;
  attack: number;
}

const BUCKET_MS = 5000;
const MAX_BUCKETS = 40;
const MAX_ALERTS = 50;

export default function LiveMonitor() {
  const [connected, setConnected] = useState(false);
  const [total, setTotal] = useState(0);
  const [benign, setBenign] = useState(0);
  const [attack, setAttack] = useState(0);
  const [alerts, setAlerts] = useState<LiveFlow[]>([]);
  const [buckets, setBuckets] = useState<Bucket[]>([]);
  const [injecting, setInjecting] = useState(false);

  const startRef = useRef(Date.now());

  useEffect(() => {
    const es = new EventSource(liveStreamUrl());
    es.onopen = () => setConnected(true);
    es.onerror = () => setConnected(false);
    es.onmessage = (e) => {
      if (!e.data) return;
      const flow = JSON.parse(e.data) as LiveFlow;
      setTotal((t) => t + 1);
      if (flow.label === "Attack") {
        setAttack((a) => a + 1);
        setAlerts((prev) => [flow, ...prev].slice(0, MAX_ALERTS));
      } else {
        setBenign((b) => b + 1);
      }

      const now = Date.now();
      if (now - startRef.current > BUCKET_MS) {
        startRef.current = now;
        setBuckets((prev) =>
          [
            ...prev,
            { time: new Date(now).toLocaleTimeString(), benign: 0, attack: 0 },
          ].slice(-MAX_BUCKETS),
        );
      }
      setBuckets((prev) => {
        const last = prev[prev.length - 1];
        if (!last) return prev;
        const key = flow.label === "Attack" ? "attack" : "benign";
        return [...prev.slice(0, -1), { ...last, [key]: last[key] + 1 }];
      });
    };
    return () => es.close();
  }, []);

  const attackRate = total ? ((attack / total) * 100).toFixed(1) : "0.0";

  const chartData = useMemo(
    () => buckets.map((b) => ({ time: b.time, benign: b.benign, attack: b.attack })),
    [buckets],
  );

  const handleSimulate = async () => {
    setInjecting(true);
    try {
      await simulateAttack(20);
    } finally {
      setInjecting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span
            className={`inline-flex items-center gap-2 text-sm ${
              connected ? "text-safe" : "text-danger"
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                connected ? "bg-safe" : "bg-danger"
              }`}
            />
            {connected ? "Live" : "Disconnected"}
          </span>
        </div>
        <button
          onClick={handleSimulate}
          disabled={injecting || !connected}
          className="rounded-md bg-danger px-4 py-2 text-sm font-medium text-white hover:bg-danger/90 disabled:opacity-50"
        >
          {injecting ? "Injecting…" : "Simulate Attack (20)"}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Flows Analyzed" value={total.toLocaleString()} accent="teal" />
        <StatCard label="Attack Rate" value={`${attackRate}%`} accent="red" />
        <StatCard label="Benign" value={benign.toLocaleString()} accent="green" />
        <StatCard label="Attacks" value={attack.toLocaleString()} accent="red" />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <section className="rounded-lg border border-ink-line bg-ink-soft p-5 lg:col-span-2">
          <h3 className="mb-3 text-sm font-medium text-slate-200">Live Traffic</h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={chartData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
              <defs>
                <linearGradient id="benignGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.5} />
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="attackGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.6} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#232936" vertical={false} />
              <XAxis dataKey="time" stroke="#8b93a7" tick={{ fill: "#8b93a7", fontSize: 11 }} />
              <YAxis
                stroke="#8b93a7"
                tick={{ fill: "#8b93a7", fontSize: 11 }}
                allowDecimals={false}
              />
              <Tooltip
                contentStyle={{
                  background: "#161a24",
                  border: "1px solid #232936",
                  borderRadius: 8,
                }}
                itemStyle={{ color: "#e2e8f0" }}
              />
              <Area
                type="monotone"
                dataKey="benign"
                stroke="#22c55e"
                fill="url(#benignGrad)"
                name="Benign"
              />
              <Area
                type="monotone"
                dataKey="attack"
                stroke="#ef4444"
                fill="url(#attackGrad)"
                name="Attack"
              />
            </AreaChart>
          </ResponsiveContainer>
        </section>

        <section className="rounded-lg border border-ink-line bg-ink-soft p-5">
          <h3 className="mb-3 text-sm font-medium text-slate-200">Alert Feed</h3>
          {alerts.length === 0 ? (
            <div className="grid h-64 place-items-center text-sm text-ink-mute">
              No attacks yet. Click "Simulate Attack".
            </div>
          ) : (
            <ul className="max-h-[280px] space-y-2 overflow-y-auto pr-1">
              {alerts.map((a, i) => (
                <li
                  key={`${a.timestamp}-${i}`}
                  className="flex items-center justify-between gap-2 rounded-md border border-danger/25 bg-danger/10 px-3 py-2"
                >
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <Badge kind="attack">{a.category ?? "Attack"}</Badge>
                      {a.source === "simulated" && <Badge kind="muted">sim</Badge>}
                    </div>
                    <div className="mt-0.5 text-xs text-ink-mute">
                      {new Date(a.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                  <span className="shrink-0 font-mono text-sm text-danger">
                    {(a.confidence * 100).toFixed(1)}%
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
