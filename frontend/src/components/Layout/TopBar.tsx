export default function TopBar({ title }: { title: string }) {
  return (
    <header className="flex h-14 items-center justify-between border-b border-ink-line bg-ink-soft px-6">
      <h1 className="text-base font-medium text-slate-100">{title}</h1>
      <span className="text-xs text-ink-mute">
        CICIDS2017 · flow-record classifier
      </span>
    </header>
  );
}
