import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function MLAnomalyTrendChart({ mlStats }) {
  const data = (mlStats?.latest_ml_anomalies || []).map((a) => ({
    time: a.created_at?.slice(11, 16) || "—",
    score: a.ml_score || a.anomaly_score || 0,
    confidence: a.confidence || 0,
  })).reverse();

  if (data.length === 0) {
    return <p className="empty-state">No ML anomaly data available yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data}>
        <CartesianGrid stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
        <XAxis dataKey="time" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} domain={[0, 1]} />
        <Tooltip
          contentStyle={{
            background: "#111827",
            border: "1px solid rgba(0,229,255,0.2)",
            borderRadius: 8,
          }}
        />
        <Line
          type="monotone"
          dataKey="score"
          stroke="#00E5FF"
          strokeWidth={2}
          dot={{ fill: "#00E5FF", r: 4 }}
          name="ML Score"
        />
        <Line
          type="monotone"
          dataKey="confidence"
          stroke="#7C3AED"
          strokeWidth={2}
          dot={false}
          name="Confidence"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
