import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Line,
} from "recharts";
import { buildTimelineData } from "../utils/riskHelpers";

export default function ThreatTimeline({ latestEvents }) {
  const data = buildTimelineData(latestEvents);

  if (data.length === 0) {
    return <p className="empty-state">Insufficient event data for timeline.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#00E5FF" stopOpacity={0.4} />
            <stop offset="100%" stopColor="#00E5FF" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
        <XAxis dataKey="time" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <Tooltip
          contentStyle={{
            background: "#111827",
            border: "1px solid rgba(0,229,255,0.2)",
            borderRadius: 8,
          }}
        />
        <Area
          type="monotone"
          dataKey="events"
          stroke="#00E5FF"
          fill="url(#riskGradient)"
          name="Events"
        />
        <Line
          type="monotone"
          dataKey="avgRisk"
          stroke="#FFC857"
          strokeWidth={2}
          dot={false}
          name="Avg Risk"
        />
        <Line
          type="monotone"
          dataKey="alerts"
          stroke="#FF4D6D"
          strokeWidth={2}
          dot={false}
          name="Alert Spikes"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
