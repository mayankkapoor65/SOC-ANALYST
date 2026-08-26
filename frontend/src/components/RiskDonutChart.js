import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import { getCriticalCount, RISK_COLORS } from "../utils/riskHelpers";

export default function RiskDonutChart({ dashboard, analytics }) {
  const critical = getCriticalCount(analytics?.anomaly_stats);
  const high = Math.max((dashboard?.high_risk_events || 0) - critical, 0);

  const data = [
    { name: "LOW", value: dashboard?.low_risk_events || 0, color: RISK_COLORS.LOW },
    { name: "MEDIUM", value: dashboard?.medium_risk_events || 0, color: RISK_COLORS.MEDIUM },
    { name: "HIGH", value: high, color: RISK_COLORS.HIGH },
    { name: "CRITICAL", value: critical, color: RISK_COLORS.CRITICAL },
  ].filter((d) => d.value > 0);

  if (data.length === 0) {
    return <p className="empty-state">No risk data available yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          innerRadius={70}
          outerRadius={105}
          paddingAngle={3}
          animationDuration={800}
        >
          {data.map((entry) => (
            <Cell key={entry.name} fill={entry.color} stroke="transparent" />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            background: "#111827",
            border: "1px solid rgba(0,229,255,0.2)",
            borderRadius: 8,
          }}
        />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
