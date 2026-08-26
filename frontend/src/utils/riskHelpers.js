export const RISK_COLORS = {
  LOW: "#00FF9D",
  MEDIUM: "#FFC857",
  HIGH: "#FF4D6D",
  CRITICAL: "#FF0040",
};

export function getRiskLevel(score) {
  if (score >= 90) return "CRITICAL";
  if (score >= 80) return "HIGH";
  if (score >= 50) return "MEDIUM";
  return "LOW";
}

export function getRiskColor(level) {
  return RISK_COLORS[level] || RISK_COLORS.LOW;
}

export function formatTimestamp(ts) {
  if (!ts) return "—";
  const date = new Date(ts.replace(" ", "T"));
  if (Number.isNaN(date.getTime())) return ts;
  return date.toLocaleString();
}

export function getCriticalCount(anomalyStats) {
  const spike = (anomalyStats?.by_type || []).find(
    (item) => item.type === "High Risk Spike"
  );
  return spike?.count || 0;
}

export function getSecurityPosture(dashboard, analytics) {
  const high = dashboard?.high_risk_events || 0;
  const total = dashboard?.total_logs || 1;
  const ratio = high / total;
  const critical = getCriticalCount(analytics?.anomaly_stats);

  if (critical > 5 || ratio > 0.25) return "ELEVATED RISK";
  if (high > 10 || ratio > 0.1) return "GUARDED";
  return "STABLE";
}

export function generateInsights(dashboard, analytics, previous) {
  const insights = [];
  const anomalies = analytics?.anomaly_stats?.total_anomalies || 0;
  const alerts = analytics?.total_alerts || 0;
  const avgRisk = analytics?.average_risk || 0;
  const targeted = analytics?.most_targeted_user;

  if (anomalies > 0) {
    insights.push({
      type: "warning",
      text: `${anomalies} anomal${anomalies === 1 ? "y" : "ies"} detected across monitored accounts.`,
    });
  }

  if (targeted && targeted !== "N/A") {
    insights.push({
      type: "critical",
      text: `${targeted} shows the highest cumulative risk exposure.`,
    });
  }

  if (previous?.analytics && alerts > previous.analytics.total_alerts) {
    const delta = alerts - previous.analytics.total_alerts;
    insights.push({
      type: "warning",
      text: `Alert volume increased by ${delta} since last refresh cycle.`,
    });
  } else if (avgRisk > 0 && avgRisk < 40) {
    insights.push({
      type: "success",
      text: "Risk trend remains stable across the monitored environment.",
    });
  }

  const recentSpikes = (analytics?.anomaly_stats?.by_type || []).find(
    (t) => t.type === "High Risk Spike"
  );
  if (recentSpikes?.count > 0) {
    insights.push({
      type: "critical",
      text: "Unusual high-risk login activity detected in recent events.",
    });
  }

  if (insights.length === 0) {
    insights.push({
      type: "success",
      text: "No significant threat indicators detected in the current window.",
    });
  }

  return insights;
}

export function buildTimelineData(latestEvents) {
  const buckets = {};
  (latestEvents || []).forEach((event) => {
    const key = event.timestamp?.slice(0, 13) || "Unknown";
    if (!buckets[key]) {
      buckets[key] = { time: key, events: 0, riskSum: 0, alerts: 0 };
    }
    buckets[key].events += 1;
    buckets[key].riskSum += event.risk_score || 0;
    if (event.risk_score >= 80) buckets[key].alerts += 1;
  });

  return Object.values(buckets)
    .map((b) => ({
      time: b.time,
      events: b.events,
      avgRisk: Math.round(b.riskSum / b.events),
      alerts: b.alerts,
    }))
    .sort((a, b) => a.time.localeCompare(b.time));
}

export function buildAnomalyTrend(recentAnomalies) {
  const buckets = {};
  (recentAnomalies || []).forEach((a) => {
    const key = a.created_at?.slice(0, 13) || "Unknown";
    buckets[key] = (buckets[key] || 0) + 1;
  });

  return Object.entries(buckets)
    .map(([time, count]) => ({ time, count }))
    .sort((a, b) => a.time.localeCompare(b.time));
}

export function buildHeatmapData(trendData) {
  return (trendData || []).map((item) => ({
    user: item.user,
    exposure: item.risk_score,
    level:
      item.risk_score >= 300
        ? "CRITICAL"
        : item.risk_score >= 200
        ? "HIGH"
        : item.risk_score >= 100
        ? "MEDIUM"
        : "LOW",
  }));
}
