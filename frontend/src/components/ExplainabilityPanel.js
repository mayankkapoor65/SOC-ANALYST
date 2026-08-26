import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const FEATURE_LABELS = {
  login_hour: "Login Hour",
  elevated_risk_count: "Elevated Risk Count",
  event_frequency: "Event Frequency",
  risk_score: "Rule Risk Score",
};

export default function ExplainabilityPanel({ mlExplanation, analytics }) {
  const explanation = mlExplanation || analytics?.ml_explanation;

  if (!explanation) {
    return (
      <div className="glass-panel explain-panel">
        <div className="panel-header">
          <h3>Explainable AI</h3>
          <span className="panel-sub">SHAP Feature Impact Analysis</span>
        </div>
        <p className="empty-state">No ML anomalies to explain yet. Explanations appear when Isolation Forest flags an event.</p>
      </div>
    );
  }

  const chartData = (explanation.top_factors || []).map((f) => ({
    feature: FEATURE_LABELS[f.feature] || f.feature,
    impact: f.impact,
  }));

  return (
    <div className="glass-panel explain-panel">
      <div className="panel-header">
        <h3>Explainable AI</h3>
        <span className="panel-sub">
          Log #{explanation.log_id} · Score {explanation.anomaly_score?.toFixed(2)} · {explanation.method || "shap"}
        </span>
      </div>

      <div className="explanation-summary">
        <h4>AI Explanation Summary</h4>
        <p>{explanation.explanation_summary}</p>
      </div>

      {chartData.length > 0 && (
        <>
          <h4>Top Contributing Features</h4>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} layout="vertical">
              <CartesianGrid stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 1]} tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis type="category" dataKey="feature" width={130} tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#111827", border: "1px solid rgba(124,58,237,0.3)", borderRadius: 8 }} />
              <Bar dataKey="impact" fill="#7C3AED" radius={[0, 4, 4, 0]} name="Impact" />
            </BarChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  );
}
