import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function BaselineDeviationChart({ anomalyStats }) {
  const deviations = (anomalyStats?.recent_anomalies || []).filter(
    (a) => a.baseline_deviation
  );

  const byUser = {};
  deviations.forEach((a) => {
    byUser[a.user_id] = (byUser[a.user_id] || 0) + 1;
  });

  const data = Object.entries(byUser).map(([user, count]) => ({
    user,
    count,
  }));

  if (data.length === 0) {
    return <p className="empty-state">No baseline deviations detected yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data}>
        <CartesianGrid stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
        <XAxis dataKey="user" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} allowDecimals={false} />
        <Tooltip
          contentStyle={{
            background: "#111827",
            border: "1px solid rgba(255,200,87,0.3)",
            borderRadius: 8,
          }}
        />
        <Bar dataKey="count" fill="#FFC857" radius={[4, 4, 0, 0]} name="Deviations" />
      </BarChart>
    </ResponsiveContainer>
  );
}
