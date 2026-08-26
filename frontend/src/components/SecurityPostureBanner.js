import { getSecurityPosture } from "../utils/riskHelpers";

export default function SecurityPostureBanner({ dashboard, analytics }) {
  const posture = getSecurityPosture(dashboard, analytics);
  const elevated = posture === "ELEVATED RISK";

  return (
    <div className={`posture-banner ${elevated ? "elevated" : "stable"}`}>
      <div className="posture-glow" />
      <div className="posture-content">
        <span className="posture-label">Security Posture</span>
        <strong className="posture-value">{posture}</strong>
        <span className="posture-sub">
          {elevated
            ? "Elevated threat activity detected — review anomalies and alerts."
            : "Environment operating within expected security thresholds."}
        </span>
      </div>
      <div className={`posture-indicator ${elevated ? "pulse-critical" : "pulse-stable"}`} />
    </div>
  );
}
