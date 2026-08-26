import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { formatTimestamp, getRiskColor } from "../utils/riskHelpers";

export default function CorrelationAlertsPanel({ correlationAlerts, analytics }) {
  const { authFetch, apiBase } = useAuth();
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);

  const alerts = correlationAlerts?.alerts || analytics?.correlation_alerts?.alerts || [];

  const loadDetail = async (id) => {
    setLoading(true);
    setSelected(id);
    try {
      const res = await authFetch(`${apiBase}/correlation-alerts/${id}`);
      if (res.ok) setDetail(await res.json());
    } catch {
      setDetail(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel correlation-panel">
      <div className="panel-header">
        <h3>SIEM Correlation Alerts</h3>
        <span className="panel-sub">Multi-event attack chain detection</span>
      </div>

      {alerts.length === 0 ? (
        <p className="empty-state">No correlation alerts yet. Attack chains appear after multi-event patterns.</p>
      ) : (
        <div className="correlation-layout">
          <div className="correlation-list">
            <h4>Recent Correlation Alerts</h4>
            <table className="soc-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>User</th>
                  <th>Severity</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((a) => (
                  <tr
                    key={a.id}
                    className={selected === a.id ? "active-row" : ""}
                    onClick={() => loadDetail(a.id)}
                    style={{ cursor: "pointer" }}
                  >
                    <td>{a.alert_type}</td>
                    <td>{a.user_id}</td>
                    <td>
                      <span
                        className="severity-badge"
                        style={{ color: getRiskColor(a.severity === "CRITICAL" ? "CRITICAL" : "HIGH"), borderColor: getRiskColor(a.severity === "CRITICAL" ? "CRITICAL" : "HIGH") }}
                      >
                        {a.severity}
                      </span>
                    </td>
                    <td>{(a.confidence * 100).toFixed(0)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="correlation-detail">
            {loading && <p className="empty-state">Loading attack chain…</p>}
            {!loading && !detail && <p className="empty-state">Select an alert to view attack chain timeline.</p>}
            {detail && !loading && (
              <>
                <h4>{detail.alert_type}</h4>
                <p>{detail.alert?.description || detail.recommended_action}</p>
                <p className="recommended-action"><strong>Action:</strong> {detail.recommended_action}</p>
                <h5>Attack Chain Timeline</h5>
                <div className="mini-timeline">
                  {(detail.timeline || []).map((node, i) => (
                    <div key={i} className="timeline-node">
                      <span>{node.event_type} — {node.location} (risk: {node.risk_score})</span>
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
