import { useState } from "react";
import { useAuth, canAccessView } from "./context/AuthContext";
import { useDashboardData } from "./hooks/useDashboardData";
import LoginPage from "./components/LoginPage";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import MetricCard from "./components/MetricCard";
import SecurityPostureBanner from "./components/SecurityPostureBanner";
import AIInsightsWidget from "./components/AIInsightsWidget";
import RiskDonutChart from "./components/RiskDonutChart";
import ThreatTimeline from "./components/ThreatTimeline";
import LiveSecurityFeed from "./components/LiveSecurityFeed";
import AnomalyCenter from "./components/AnomalyCenter";
import AlertPanel from "./components/AlertPanel";
import TopRiskyUsersChart from "./components/TopRiskyUsersChart";
import ThreatHeatmap from "./components/ThreatHeatmap";
import RiskTrendChart from "./components/RiskTrendChart";
import AnomalyTrendChart from "./components/AnomalyTrendChart";
import MLAnomalyTrendChart from "./components/MLAnomalyTrendChart";
import BaselineDeviationChart from "./components/BaselineDeviationChart";
import MitreAttackCard from "./components/MitreAttackCard";
import InvestigationPanel from "./components/InvestigationPanel";
import ThreatIntelPanel from "./components/ThreatIntelPanel";
import CorrelationAlertsPanel from "./components/CorrelationAlertsPanel";
import ExplainabilityPanel from "./components/ExplainabilityPanel";
import SkeletonLoader from "./components/SkeletonLoader";
import Toast from "./components/Toast";
import "./styles/sentinel.css";

function DashboardView({ dashboard, analytics, alerts, previous }) {
  return (
    <>
      <SecurityPostureBanner dashboard={dashboard} analytics={analytics} />

      <div className="metrics-grid">
        <MetricCard label="Total Logs" value={dashboard.total_logs} accent="cyan" trend={{ type: "up", text: "Live ingestion active" }} />
        <MetricCard label="Total Alerts" value={analytics?.total_alerts ?? 0} accent="red" trend={{ type: "warn", text: "High-risk threshold alerts" }} />
        <MetricCard label="Total Anomalies" value={analytics?.anomaly_stats?.total_anomalies || 0} accent="purple" trend={{ type: "warn", text: "Behavioral deviations detected" }} />
        <MetricCard label="Average Risk Score" value={analytics?.average_risk ?? 0} decimals={2} accent="green" trend={{ type: "neutral", text: "Environment-wide average" }} />
      </div>

      {analytics && (
        <div className="metrics-grid">
          <MetricCard label="ML Anomalies" value={analytics.hybrid_stats?.ml_anomalies ?? analytics.ml_stats?.total_ml_anomalies ?? 0} accent="cyan" trend={{ type: "up", text: "Isolation Forest detections" }} />
          <MetricCard label="Behavior Deviations" value={analytics.hybrid_stats?.baseline_deviations ?? 0} accent="green" trend={{ type: "warn", text: "Baseline profile mismatches" }} />
          <MetricCard label="Hybrid Detection Rate" value={analytics.hybrid_stats?.hybrid_detection_rate ?? 0} decimals={1} accent="purple" trend={{ type: "neutral", text: "Percent of hybrid-flagged anomalies" }} />
          <MetricCard label="Avg Confidence Score" value={analytics.hybrid_stats?.average_confidence ?? 0} decimals={2} accent="red" trend={{ type: "up", text: "Hybrid engine confidence" }} />
        </div>
      )}

      <div className="content-grid two-col">
        <div className="glass-panel chart-panel">
          <div className="panel-header">
            <h3>Risk Distribution</h3>
            <span className="panel-sub">LOW · MEDIUM · HIGH · CRITICAL</span>
          </div>
          <RiskDonutChart dashboard={dashboard} analytics={analytics} />
        </div>
        <AIInsightsWidget dashboard={dashboard} analytics={analytics} previous={previous} />
      </div>

      <div className="content-grid two-col">
        <ThreatIntelPanel threatIntel={analytics?.threat_intel} />
        <CorrelationAlertsPanel correlationAlerts={analytics?.correlation_alerts} analytics={analytics} />
      </div>

      <div className="content-grid two-col">
        <ExplainabilityPanel mlExplanation={analytics?.ml_explanation} analytics={analytics} />
        <MitreAttackCard alerts={alerts} analytics={analytics} />
      </div>

      <div className="content-grid two-col">
        <div className="glass-panel chart-panel">
          <div className="panel-header">
            <h3>Threat Timeline</h3>
            <span className="panel-sub">Events · Risk · Alert spikes</span>
          </div>
          <ThreatTimeline latestEvents={dashboard.latest_events} />
        </div>
      </div>

      <div className="content-grid two-col">
        <div className="glass-panel feed-panel">
          <div className="panel-header">
            <h3>Live Security Feed</h3>
            <span className="live-badge">LIVE</span>
          </div>
          <LiveSecurityFeed events={dashboard.latest_events} />
        </div>
      </div>
    </>
  );
}

function AnalyticsView({ dashboard, analytics }) {
  if (!analytics) {
    return <p className="empty-state">Analytics require ANALYST or ADMIN role.</p>;
  }
  return (
    <div className="content-grid two-col">
      <div className="glass-panel chart-panel">
        <div className="panel-header"><h3>Risk Trend Analysis</h3></div>
        <RiskTrendChart latestEvents={dashboard.latest_events} />
      </div>
      <div className="glass-panel chart-panel">
        <div className="panel-header"><h3>Anomaly Trend</h3></div>
        <AnomalyTrendChart recentAnomalies={analytics.anomaly_stats?.recent_anomalies} />
      </div>
      <div className="glass-panel chart-panel">
        <div className="panel-header"><h3>ML Anomaly Trend</h3></div>
        <MLAnomalyTrendChart mlStats={analytics.ml_stats} />
      </div>
      <div className="glass-panel chart-panel">
        <div className="panel-header"><h3>Baseline Deviation Trend</h3></div>
        <BaselineDeviationChart anomalyStats={analytics.anomaly_stats} />
      </div>
    </div>
  );
}

function App() {
  const { user, loading: authLoading, logout } = useAuth();
  const [activeView, setActiveView] = useState("dashboard");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const {
    dashboard, analytics, health, alerts, loading, error,
    lastUpdated, toast, previous, refresh, apiBase,
  } = useDashboardData();

  if (authLoading) {
    return <SkeletonLoader />;
  }

  if (!user) {
    return <LoginPage />;
  }

  if (loading && !dashboard) {
    return <SkeletonLoader />;
  }

  if (error && !dashboard) {
    return (
      <div className="error-screen">
        <h2>SentinelAI — Connection Failed</h2>
        <p>{error}</p>
        <p className="mono">Backend: {apiBase}</p>
        <button type="button" onClick={refresh}>Retry Connection</button>
      </div>
    );
  }

  const renderView = () => {
    if (!canAccessView(user.role, activeView)) {
      return <p className="empty-state">Your role ({user.role}) does not have access to this view.</p>;
    }
    switch (activeView) {
      case "analytics":
        return <AnalyticsView dashboard={dashboard} analytics={analytics} />;
      case "threats":
        return analytics ? (
          <div className="content-grid two-col">
            <div className="glass-panel chart-panel">
              <div className="panel-header"><h3>Top Risky Users</h3></div>
              <TopRiskyUsersChart trendData={analytics.trend_data} />
            </div>
            <div className="glass-panel chart-panel">
              <div className="panel-header"><h3>Threat Exposure Heatmap</h3></div>
              <ThreatHeatmap trendData={analytics.trend_data} />
            </div>
          </div>
        ) : <p className="empty-state">Threat analysis requires ANALYST role.</p>;
      case "anomalies":
        return analytics ? <AnomalyCenter anomalyStats={analytics.anomaly_stats} /> : null;
      case "alerts":
        return <AlertPanel events={dashboard.latest_events} totalAlerts={analytics?.total_alerts ?? 0} />;
      case "investigation":
        return <InvestigationPanel alerts={alerts} />;
      case "correlation":
        return <CorrelationAlertsPanel correlationAlerts={analytics?.correlation_alerts} analytics={analytics} />;
      case "threat-intel":
        return <ThreatIntelPanel threatIntel={analytics?.threat_intel} />;
      case "explainability":
        return <ExplainabilityPanel mlExplanation={analytics?.ml_explanation} analytics={analytics} />;
      case "settings":
        return (
          <div className="glass-panel settings-panel">
            <div className="panel-header"><h3>Platform Settings</h3></div>
            <dl className="settings-list">
              <div><dt>API Endpoint</dt><dd className="mono">{apiBase}</dd></div>
              <div><dt>Logged In As</dt><dd>{user.username} ({user.role})</dd></div>
              <div><dt>Database Status</dt><dd>{health?.database || "Unknown"}</dd></div>
              <div><dt>Last Sync</dt><dd>{lastUpdated ? lastUpdated.toLocaleString() : "—"}</dd></div>
            </dl>
            <button type="button" className="logout-btn" onClick={logout}>Sign Out</button>
          </div>
        );
      default:
        return <DashboardView dashboard={dashboard} analytics={analytics} alerts={alerts} previous={previous} />;
    }
  };

  return (
    <div className="sentinel-app">
      <Sidebar
        activeView={activeView}
        onNavigate={setActiveView}
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed((c) => !c)}
        userRole={user.role}
      />
      <main className={`main-content ${sidebarCollapsed ? "expanded" : ""}`}>
        <Header
          health={health}
          dashboard={dashboard}
          analytics={analytics}
          lastUpdated={lastUpdated}
          onRefresh={refresh}
          user={user}
          onLogout={logout}
        />
        <div className="view-container">{renderView()}</div>
      </main>
      <Toast toast={toast} />
    </div>
  );
}

export default App;
