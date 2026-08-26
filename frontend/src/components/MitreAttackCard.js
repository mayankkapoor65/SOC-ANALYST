export default function MitreAttackCard({ alerts, analytics }) {
  const alertList = alerts?.alerts || [];
  const techniqueCounts = {};

  alertList.forEach((a) => {
    const tid = a.mitre_technique_id || "T1078";
    techniqueCounts[tid] = (techniqueCounts[tid] || 0) + 1;
  });

  const entries = Object.entries(techniqueCounts)
    .map(([tid, count]) => {
      const match = alertList.find((a) => a.mitre_technique_id === tid);
      return {
        technique_id: tid,
        technique_name: match?.mitre_technique_name || "Valid Accounts",
        count,
      };
    })
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  const totalAnomalies = analytics?.anomaly_stats?.total_anomalies || 0;

  if (entries.length === 0) {
    return (
      <div className="glass-panel mitre-card">
        <div className="panel-header">
          <h3>MITRE ATT&CK Mapping</h3>
          <span className="panel-sub">Technique coverage</span>
        </div>
        <p className="empty-state">
          No MITRE-mapped alerts yet. High-risk events will appear here.
        </p>
        {totalAnomalies > 0 && (
          <p className="mitre-footnote">
            {totalAnomalies} anomalies detected — awaiting alert-level mapping.
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="glass-panel mitre-card">
      <div className="panel-header">
        <h3>MITRE ATT&CK Mapping</h3>
        <span className="panel-sub">Active technique detections</span>
      </div>
      <div className="mitre-list">
        {entries.map((t) => (
          <div key={t.technique_id} className="mitre-item">
            <div className="mitre-id">{t.technique_id}</div>
            <div className="mitre-info">
              <strong>{t.technique_name}</strong>
              <span>{t.count} alert{t.count !== 1 ? "s" : ""}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
