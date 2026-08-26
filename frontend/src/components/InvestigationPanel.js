import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { formatTimestamp, getRiskColor } from "../utils/riskHelpers";

export default function InvestigationPanel({ alerts }) {
  const { authFetch, apiBase, hasRole } = useAuth();
  const [selectedId, setSelectedId] = useState(null);
  const [investigation, setInvestigation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);

  const alertList = alerts?.alerts || [];

  if (!hasRole(["ADMIN", "ANALYST"])) {
    return (
      <div className="glass-panel">
        <p className="empty-state">Investigation tools require ANALYST or ADMIN role.</p>
      </div>
    );
  }

  const loadInvestigation = async (alertId) => {
    setLoading(true);
    setSelectedId(alertId);
    try {
      const res = await authFetch(`${apiBase}/investigation/${alertId}`);
      if (!res.ok) throw new Error("Failed to load investigation");
      setInvestigation(await res.json());
    } catch {
      setInvestigation(null);
    } finally {
      setLoading(false);
    }
  };

  const exportReport = async (alertId) => {
    setExporting(true);
    try {
      const res = await authFetch(`${apiBase}/incident-report/${alertId}`);
      if (!res.ok) throw new Error("Failed to generate report");
      const report = await res.json();
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `incident-report-${alertId}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(err.message);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="investigation-panel glass-panel">
      <div className="panel-header">
        <div>
          <h3>SOC Investigation Workbench</h3>
          <p>{alertList.length} alerts available for investigation</p>
        </div>
      </div>

      {alertList.length === 0 ? (
        <p className="empty-state">No alerts in the system yet.</p>
      ) : (
        <div className="investigation-layout">
          <div className="alert-list-panel">
            {alertList.map((alert) => (
              <button
                key={alert.id}
                type="button"
                className={`investigation-alert-item ${selectedId === alert.id ? "active" : ""}`}
                onClick={() => loadInvestigation(alert.id)}
              >
                <span className="alert-id">ALT-{alert.id}</span>
                <span
                  className="severity-badge"
                  style={{
                    color: getRiskColor(alert.severity === "CRITICAL" ? "CRITICAL" : "HIGH"),
                    borderColor: getRiskColor(alert.severity === "CRITICAL" ? "CRITICAL" : "HIGH"),
                  }}
                >
                  {alert.severity}
                </span>
                <span>{alert.user_id}</span>
                <span className="mono">{formatTimestamp(alert.timestamp)}</span>
              </button>
            ))}
          </div>

          <div className="investigation-detail">
            {loading && <p className="empty-state">Loading investigation…</p>}
            {!loading && !investigation && selectedId && (
              <p className="empty-state">Could not load investigation data.</p>
            )}
            {!loading && !selectedId && (
              <p className="empty-state">Select an alert to begin investigation.</p>
            )}
            {investigation && !loading && (
              <>
                <div className="investigation-header">
                  <h4>Alert #{investigation.alert_id}</h4>
                  <button
                    type="button"
                    className="export-btn"
                    onClick={() => exportReport(investigation.alert_id)}
                    disabled={exporting}
                  >
                    {exporting ? "Exporting…" : "Export Incident Report"}
                  </button>
                </div>

                <dl className="investigation-meta">
                  <div><dt>User</dt><dd>{investigation.user}</dd></div>
                  <div><dt>Source IP</dt><dd>{investigation.source_ip}</dd></div>
                  <div><dt>Severity</dt><dd>{investigation.severity}</dd></div>
                  <div><dt>Risk Score</dt><dd>{investigation.risk_score}</dd></div>
                  <div>
                    <dt>MITRE ATT&CK</dt>
                    <dd>
                      {investigation.mitre_mapping?.technique_id}{" "}
                      — {investigation.mitre_mapping?.technique_name}
                    </dd>
                  </div>
                </dl>

                <div className="recommended-action">
                  <h5>Recommended Action</h5>
                  <p>{investigation.recommended_action}</p>
                </div>

                <h5>Evidence ({investigation.evidence?.length || 0})</h5>
                <ul className="evidence-list">
                  {(investigation.evidence || []).map((ev, i) => (
                    <li key={i}>
                      {ev.anomaly_type || ev.event_type || ev.type} — score: {ev.risk_score ?? ev.anomaly_score ?? "—"}
                    </li>
                  ))}
                </ul>

                <h5>Timeline</h5>
                <div className="mini-timeline">
                  {(investigation.timeline || []).map((node, i) => (
                    <div key={i} className="timeline-node">
                      <span>{node.event} ({node.location})</span>
                      <span className="mono">{formatTimestamp(node.timestamp)}</span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
