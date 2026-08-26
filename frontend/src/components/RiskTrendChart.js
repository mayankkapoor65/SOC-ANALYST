import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { buildTimelineData } from "../utils/riskHelpers";

export default function RiskTrendChart({ latestEvents }) {
  const data = buildTimelineData(latestEvents);

  if (data.length === 0) {
    return <p className="empty-state">Insufficient data for risk trend.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="areaRisk" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#7C3AED" stopOpacity={0.5} />
            <stop offset="100%" stopColor="#7C3AED" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
        <XAxis dataKey="time" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <Tooltip
          contentStyle={{
            background: "#111827",
            border: "1px solid rgba(124,58,237,0.3)",
            borderRadius: 8,
          }}
        />
        <Area
          type="monotone"
          dataKey="avgRisk"
          stroke="#7C3AED"
          fill="url(#areaRisk)"
          name="Average Risk"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
