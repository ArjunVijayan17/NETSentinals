import type { ReactNode } from "react";

export default function Badge({
  kind,
  children,
}: {
  kind: "attack" | "benign" | "muted";
  children: ReactNode;
}) {
  const styles: Record<string, string> = {
    attack: "bg-danger/15 text-danger border-danger/30",
    benign: "bg-safe/15 text-safe border-safe/30",
    muted: "bg-ink-line text-ink-mute border-ink-line",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${styles[kind]}`}
    >
      {children}
    </span>
  );
}
