import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function TopRiskyUsersChart({ trendData }) {
  const data = (trendData || []).map((item) => ({
    user: item.user,
    score: item.risk_score,
  }));

  if (data.length === 0) {
    return <p className="empty-state">No user risk data available.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
        <CartesianGrid stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
        <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis
          type="category"
          dataKey="user"
          width={80}
          tick={{ fill: "#94a3b8", fontSize: 11 }}
        />
        <Tooltip
          contentStyle={{
            background: "#111827",
            border: "1px solid rgba(0,229,255,0.2)",
            borderRadius: 8,
          }}
        />
        <Bar dataKey="score" fill="#7C3AED" radius={[0, 6, 6, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
