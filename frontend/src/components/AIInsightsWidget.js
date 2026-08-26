import { generateInsights } from "../utils/riskHelpers";

export default function AIInsightsWidget({ dashboard, analytics, previous }) {
  const insights = generateInsights(dashboard, analytics, previous);

  return (
    <div className="glass-panel ai-insights">
      <div className="panel-header">
        <h3>AI Threat Insights</h3>
        <span className="ai-badge">SentinelAI Engine</span>
      </div>
      <ul className="insights-list">
        {insights.map((insight, index) => (
          <li key={index} className={`insight-item insight-${insight.type}`}>
            <span className="insight-dot" />
            {insight.text}
          </li>
        ))}
      </ul>
    </div>
  );
}
