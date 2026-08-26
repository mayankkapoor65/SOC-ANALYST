import {
  IconDashboard,
  IconAnalytics,
  IconThreats,
  IconAnomalies,
  IconAlerts,
  IconSettings,
  IconShield,
  IconChevron,
} from "./icons/NavIcons";
import { canAccessView } from "../context/AuthContext";

const NAV_ITEMS = [
  { id: "dashboard", label: "Dashboard", Icon: IconDashboard },
  { id: "analytics", label: "Analytics", Icon: IconAnalytics },
  { id: "threat-intel", label: "Threat Intel", Icon: IconThreats },
  { id: "correlation", label: "Correlation", Icon: IconAlerts },
  { id: "explainability", label: "Explainable AI", Icon: IconAnomalies },
  { id: "threats", label: "Threats", Icon: IconThreats },
  { id: "anomalies", label: "Anomalies", Icon: IconAnomalies },
  { id: "alerts", label: "Alerts", Icon: IconAlerts },
  { id: "investigation", label: "Investigation", Icon: IconShield },
  { id: "settings", label: "Settings", Icon: IconSettings },
];

export default function Sidebar({ activeView, onNavigate, collapsed, onToggle, userRole = "VIEWER" }) {
  const visibleItems = NAV_ITEMS.filter((item) => canAccessView(userRole, item.id));

  return (
    <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
      <div className="sidebar-brand">
        <div className="brand-icon">
          <IconShield />
        </div>
        {!collapsed && (
          <div className="brand-text">
            <strong>SentinelAI</strong>
            <span>Security Analytics</span>
          </div>
        )}
      </div>

      <nav className="sidebar-nav">
        {visibleItems.map(({ id, label, Icon }) => (
          <button
            key={id}
            type="button"
            className={`nav-item ${activeView === id ? "active" : ""}`}
            onClick={() => onNavigate(id)}
            title={label}
          >
            <Icon />
            {!collapsed && <span>{label}</span>}
          </button>
        ))}
      </nav>

      {!collapsed && (
        <div className="sidebar-role">
          <span className="role-badge">{userRole}</span>
        </div>
      )}

      <button
        type="button"
        className="sidebar-toggle"
        onClick={onToggle}
        aria-label="Toggle sidebar"
      >
        <IconChevron />
      </button>
    </aside>
  );
}
