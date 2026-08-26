import AnimatedCounter from "./AnimatedCounter";

export default function MetricCard({
  label,
  value,
  trend,
  accent = "cyan",
  icon,
  decimals = 0,
}) {
  return (
    <div className={`metric-card glow-${accent}`}>
      <div className="metric-card-top">
        <span className="metric-label">{label}</span>
        {icon && <span className="metric-icon">{icon}</span>}
      </div>
      <div className="metric-value">
        <AnimatedCounter value={value} decimals={decimals} />
      </div>
      {trend && <div className={`metric-trend trend-${trend.type}`}>{trend.text}</div>}
    </div>
  );
}
