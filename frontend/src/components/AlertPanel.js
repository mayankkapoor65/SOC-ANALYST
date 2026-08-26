import { useState } from "react";
import { getRiskLevel, getRiskColor, formatTimestamp } from "../utils/riskHelpers";

export default function AlertPanel({ events, totalAlerts }) {
  const [expanded, setExpanded] = useState(null);

  const alertEvents = (events || []).filter((e) => e.risk_score >= 80);

  return (
    <div className="alert-panel">
      <div className="panel-header">
        <div>
          <h3>Alert Investigation Panel</h3>
          <p>{totalAlerts} total alerts in system · {alertEvents.length} high-risk events in live feed</p>
        </div>
      </div>

      {alertEvents.length === 0 ? (
        <p className="empty-state">No high-risk events in the current live feed.</p>
      ) : (
        <div className="alert-cards">
          {alertEvents.map((event, index) => {
            const level = getRiskLevel(event.risk_score);
            const id = `ALT-${event.timestamp?.replace(/[\s:-]/g, "") || index}`;
            const isOpen = expanded === id;

            return (
              <div
                key={id}
                className={`alert-card ${isOpen ? "expanded" : ""}`}
                style={{ borderColor: getRiskColor(level) }}
              >
                <button
                  type="button"
                  className="alert-card-header"
                  onClick={() => setExpanded(isOpen ? null : id)}
                >
                  <div>
                    <span className="alert-id">{id}</span>
                    <span
                      className="severity-badge"
                      style={{
                        color: getRiskColor(level),
                        borderColor: getRiskColor(level),
                      }}
                    >
                      {level}
                    </span>
                  </div>
                  <span className="mono">{formatTimestamp(event.timestamp)}</span>
                </button>

                <div className="alert-card-body">
                  <p>
                    Suspicious {event.event_type} activity detected for{" "}
                    <strong>{event.user_id}</strong> with risk score{" "}
                    <strong>{event.risk_score}</strong>.
                  </p>

                  {isOpen && (
                    <div className="alert-details">
                      <h4>Evidence View</h4>
                      <ul>
                        <li>User: {event.user_id}</li>
                        <li>Event Type: {event.event_type}</li>
                        <li>Risk Score: {event.risk_score}</li>
                        <li>Severity: {level}</li>
                      </ul>
                      <h4>Alert Timeline</h4>
                      <div className="mini-timeline">
                        <div className="timeline-node">
                          <span>Event Logged</span>
                          <span className="mono">{formatTimestamp(event.timestamp)}</span>
                        </div>
                        <div className="timeline-node">
                          <span>Risk Engine Scored</span>
                          <span>Score: {event.risk_score}</span>
                        </div>
                        {event.risk_score >= 80 && (
                          <div className="timeline-node critical">
                            <span>Alert Generated</span>
                            <span>Threshold exceeded</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
