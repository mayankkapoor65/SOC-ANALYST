import { buildHeatmapData, getRiskColor } from "../utils/riskHelpers";

export default function ThreatHeatmap({ trendData }) {
  const data = buildHeatmapData(trendData);

  if (data.length === 0) {
    return <p className="empty-state">No exposure data for heatmap.</p>;
  }

  const maxExposure = Math.max(...data.map((d) => d.exposure), 1);

  return (
    <div className="threat-heatmap">
      {data.map((item) => {
        const intensity = item.exposure / maxExposure;
        return (
          <div key={item.user} className="heatmap-row">
            <span className="heatmap-user">{item.user}</span>
            <div className="heatmap-bar-track">
              <div
                className="heatmap-bar-fill"
                style={{
                  width: `${intensity * 100}%`,
                  background: getRiskColor(item.level),
                  boxShadow: `0 0 12px ${getRiskColor(item.level)}55`,
                }}
              />
            </div>
            <span className="heatmap-value">{item.exposure}</span>
            <span
              className="severity-badge small"
              style={{
                color: getRiskColor(item.level),
                borderColor: getRiskColor(item.level),
              }}
            >
              {item.level}
            </span>
          </div>
        );
      })}
    </div>
  );
}
