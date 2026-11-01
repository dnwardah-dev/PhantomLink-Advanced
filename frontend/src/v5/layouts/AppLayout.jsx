import { NavLink, Outlet } from "react-router-dom";
import {
  Fingerprint,
  House,
  ScanSearch,
  Network,
  Globe2,
  Archive,
  ChartNoAxesCombined,
  ShieldCheck,
} from "lucide-react";

const navigation = [
  { to: "/", label: "Home", icon: House, end: true },
  { to: "/investigate", label: "Investigation Lab", icon: ScanSearch },
  { to: "/evidence", label: "Evidence Lab", icon: Network },
  { to: "/dns", label: "DNS Intelligence", icon: Globe2 },
  { to: "/archive", label: "Intelligence Archive", icon: Archive },
  { to: "/analytics", label: "Threat Analytics", icon: ChartNoAxesCombined },
];

export default function AppLayout() {
  return (
    <div className="v5-platform">
      <aside className="v5-sidebar">
        <NavLink to="/" className="v5-sidebar-brand">
          <Fingerprint size={30} />
          <span>
            <strong>phantomlink.</strong>
            <small>DIGITAL UNDERWORLD</small>
          </span>
        </NavLink>

        <div className="v5-sidebar-section">NAVIGATION / 001</div>

        <nav className="v5-sidebar-nav" aria-label="Platform navigation">
          {navigation.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `v5-sidebar-link ${isActive ? "active" : ""}`
              }
            >
              <Icon size={19} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="v5-sidebar-bottom">
          <ShieldCheck size={17} />
          <span>
            <strong>HEURISTIC ENGINE</strong>
            <small>LOCAL ANALYSIS MODE</small>
          </span>
        </div>
      </aside>

      <div className="v5-platform-content">
        <header className="v5-platform-topbar">
          <span>PHANTOMLINK / INVESTIGATION PLATFORM</span>
          <span className="v5-platform-mode">
            <span className="v5-status-dot" />
            LOCAL ANALYSIS
          </span>
        </header>

        <main className="v5-platform-main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
