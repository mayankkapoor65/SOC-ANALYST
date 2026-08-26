import { useMemo, useState } from "react";
import { getRiskColor, formatTimestamp } from "../utils/riskHelpers";

export default function AnomalyCenter({ anomalyStats }) {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("ALL");

  const anomalies = useMemo(
    () => anomalyStats?.recent_anomalies || [],
    [anomalyStats]
  );
  const types = ["ALL", ...new Set(anomalies.map((a) => a.anomaly_type))];

  const filtered = useMemo(() => {
    return anomalies.filter((a) => {
      const matchesSearch =
        !search ||
        a.user_id?.toLowerCase().includes(search.toLowerCase()) ||
        a.anomaly_type?.toLowerCase().includes(search.toLowerCase());
      const matchesFilter = filter === "ALL" || a.anomaly_type === filter;
      return matchesSearch && matchesFilter;
    });
  }, [anomalies, search, filter]);

  return (
    <div className="anomaly-center glass-panel">
      <div className="panel-header">
        <div>
          <h3>Anomaly Investigation Center</h3>
          <p>{anomalyStats?.total_anomalies || 0} total anomalies detected</p>
        </div>
        <div className="anomaly-controls">
          <input
            type="search"
            placeholder="Search user or type..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="filter-select"
          >
            {types.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="anomaly-table-wrap">
        <table className="soc-table">
          <thead>
            <tr>
              <th>Anomaly Type</th>
              <th>User</th>
              <th>Risk Score</th>
              <th>Anomaly Score</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={5} className="empty-cell">
                  No anomalies match your filters.
                </td>
              </tr>
            ) : (
              filtered.map((a) => (
                <tr key={`${a.user_id}-${a.created_at}`}>
                  <td>
                    <span
                      className="severity-badge"
                      style={{
                        color: getRiskColor("HIGH"),
                        borderColor: getRiskColor("HIGH"),
                      }}
                    >
                      {a.anomaly_type}
                    </span>
                  </td>
                  <td>{a.user_id}</td>
                  <td>{a.risk_score ?? "—"}</td>
                  <td>{a.anomaly_score?.toFixed(2)}</td>
                  <td className="mono">{formatTimestamp(a.created_at)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
