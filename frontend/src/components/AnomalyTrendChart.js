import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { buildAnomalyTrend } from "../utils/riskHelpers";

export default function AnomalyTrendChart({ recentAnomalies }) {
  const data = buildAnomalyTrend(recentAnomalies);

  if (data.length === 0) {
    return <p className="empty-state">No anomaly trend data available.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data}>
        <CartesianGrid stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
        <XAxis dataKey="time" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} allowDecimals={false} />
        <Tooltip
          contentStyle={{
            background: "#111827",
            border: "1px solid rgba(255,77,109,0.3)",
            borderRadius: 8,
          }}
        />
        <Line
          type="monotone"
          dataKey="count"
          stroke="#FF4D6D"
          strokeWidth={2}
          dot={{ fill: "#FF4D6D", r: 4 }}
          name="Anomalies"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
