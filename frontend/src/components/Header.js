export default function Header({
  health,
  dashboard,
  analytics,
  lastUpdated,
  onRefresh,
  user,
  onLogout,
}) {
  const isHealthy = health?.status === "healthy";
  const activeThreats =
    (dashboard?.high_risk_events || 0) +
    (analytics?.anomaly_stats?.total_anomalies || 0);

  return (
    <header className="top-header glass-panel">
      <div className="header-left">
        <h1>Security Operations Center</h1>
        <p>Real-time threat monitoring &amp; anomaly intelligence</p>
      </div>

      <div className="header-stats">
        {user && (
          <div className="header-stat">
            <span className="stat-label">Operator</span>
            <span className="stat-value">
              {user.username}
              <span className="role-badge-sm">{user.role}</span>
            </span>
          </div>
        )}
        <div className="header-stat">
          <span className="stat-label">System Status</span>
          <span className={`stat-value status-pill ${isHealthy ? "online" : "offline"}`}>
            <span className="pulse-dot" />
            {isHealthy ? "Operational" : "Degraded"}
          </span>
        </div>

        <div className="header-stat">
          <span className="stat-label">Total Events</span>
          <span className="stat-value">{dashboard?.total_logs?.toLocaleString() ?? "—"}</span>
        </div>

        <div className="header-stat">
          <span className="stat-label">Active Threats</span>
          <span className="stat-value threat-count">{activeThreats.toLocaleString()}</span>
        </div>

        <div className="header-stat">
          <span className="stat-label">Last Updated</span>
          <span className="stat-value mono">
            {lastUpdated ? lastUpdated.toLocaleTimeString() : "—"}
          </span>
        </div>

        <button type="button" className="refresh-btn" onClick={onRefresh}>
          Refresh
        </button>

        {onLogout && user?.username !== "guest" && (
          <button type="button" className="logout-btn-sm" onClick={onLogout}>
            Sign Out
          </button>
        )}
      </div>
    </header>
  );
}
