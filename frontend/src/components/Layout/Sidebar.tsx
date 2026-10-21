import { NavLink } from "react-router-dom";

const items = [
  { to: "/", label: "Overview", icon: "◉" },
  { to: "/live", label: "Live Monitor", icon: "●" },
  { to: "/analyze", label: "Analyze Traffic", icon: "⇪" },
  { to: "/history", label: "History", icon: "▤" },
  { to: "/models", label: "Model Evaluation", icon: "◆" },
];

export default function Sidebar() {
  return (
    <aside className="flex w-56 shrink-0 flex-col border-r border-ink-line bg-ink-soft">
      <div className="flex items-center gap-2 px-5 py-5">
        <span className="grid h-8 w-8 place-items-center rounded bg-accent/15 text-accent">
          ⛨
        </span>
        <span className="text-lg font-semibold tracking-tight text-white">
          NetSentinel
        </span>
      </div>
      <nav className="flex flex-col gap-1 px-3">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                isActive
                  ? "bg-accent/15 text-accent"
                  : "text-ink-mute hover:bg-ink-line hover:text-slate-200"
              }`
            }
          >
            <span className="w-4 text-center">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
