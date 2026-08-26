import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const COLORS = ["#FF4D6D", "#FFC857", "#00E5FF", "#7C3AED", "#00FF9D"];

export default function ThreatIntelPanel({ threatIntel }) {
  const ti = threatIntel || {};
  const categories = Object.entries(ti.categories || {}).map(([name, count]) => ({
    name,
    count,
  }));

  const scoreDistribution = [
    { range: "Critical (90+)", count: categories.filter((c) => c.name === "Botnet" || c.name === "Malicious").reduce((s, c) => s + c.count, 0) },
    { range: "High (70-89)", count: categories.filter((c) => c.name === "Scanner").reduce((s, c) => s + c.count, 0) },
    { range: "Medium (40-69)", count: categories.filter((c) => c.name === "Suspicious").reduce((s, c) => s + c.count, 0) },
  ].filter((d) => d.count > 0);

  if (!ti.total_iocs) {
    return (
      <div className="glass-panel threat-intel-panel">
        <div className="panel-header">
          <h3>Threat Intelligence</h3>
          <span className="panel-sub">IOC Enrichment Feed</span>
        </div>
        <p className="empty-state">No threat intelligence data loaded.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel threat-intel-panel">
      <div className="panel-header">
        <h3>Threat Intelligence</h3>
        <span className="panel-sub">{ti.feed_type?.toUpperCase() || "JSON"} Feed · {ti.total_iocs} IOCs</span>
      </div>

      <div className="ti-metrics">
        <div className="ti-metric"><span>Malicious</span><strong>{ti.malicious_ips ?? 0}</strong></div>
        <div className="ti-metric"><span>Suspicious</span><strong>{ti.suspicious_ips ?? 0}</strong></div>
        <div className="ti-metric"><span>High Confidence</span><strong>{ti.high_confidence_threats ?? 0}</strong></div>
        <div className="ti-metric"><span>Avg Score</span><strong>{ti.average_threat_score ?? 0}</strong></div>
      </div>

      <div className="ti-charts">
        {categories.length > 0 && (
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={categories} dataKey="count" nameKey="name" cx="50%" cy="50%" outerRadius={70} label>
                {categories.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "#111827", border: "1px solid rgba(255,77,109,0.3)", borderRadius: 8 }} />
            </PieChart>
          </ResponsiveContainer>
        )}
        {scoreDistribution.length > 0 && (
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={scoreDistribution}>
              <CartesianGrid stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
              <XAxis dataKey="range" tick={{ fill: "#94a3b8", fontSize: 10 }} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} allowDecimals={false} />
              <Tooltip contentStyle={{ background: "#111827", border: "1px solid rgba(255,77,109,0.3)", borderRadius: 8 }} />
              <Bar dataKey="count" fill="#FF4D6D" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
