import { render, screen } from "@testing-library/react";
import App from "./App";

jest.mock("./hooks/useDashboardData", () => ({
  useDashboardData: () => ({
    dashboard: {
      total_logs: 100,
      high_risk_events: 10,
      medium_risk_events: 20,
      low_risk_events: 70,
      latest_events: [],
    },
    analytics: {
      average_risk: 35.5,
      total_alerts: 5,
      most_targeted_user: "Alice",
      trend_data: [],
      anomaly_stats: {
        total_anomalies: 3,
        by_type: [],
        recent_anomalies: [],
        ml_anomalies: 1,
        baseline_deviations: 2,
        hybrid_detection_count: 1,
        average_confidence: 0.87,
      },
      ml_stats: { total_ml_anomalies: 1, average_confidence: 0.87, latest_ml_anomalies: [] },
      hybrid_stats: {
        ml_anomalies: 1,
        baseline_deviations: 2,
        hybrid_detection_rate: 33.3,
        average_confidence: 0.87,
      },
      threat_intel: { total_iocs: 10, malicious_ips: 4, suspicious_ips: 3, high_confidence_threats: 5, average_threat_score: 72, categories: {} },
      correlation_alerts: { alerts: [], total: 0 },
      ml_explanation: null,
    },
    health: { status: "healthy", database: "connected" },
    alerts: { alerts: [], total: 0 },
    loading: false,
    error: null,
    lastUpdated: new Date(),
    toast: null,
    previous: null,
    refresh: jest.fn(),
    apiBase: "http://127.0.0.1:8000",
  }),
}));

jest.mock("./context/AuthContext", () => {
  const actual = jest.requireActual("./context/AuthContext");
  return {
    ...actual,
    useAuth: () => ({
      user: { id: 1, username: "admin", email: "admin@test.com", role: "ADMIN", created_at: "" },
      token: "test-token",
      isGuest: false,
      loading: false,
      error: null,
      setError: jest.fn(),
      login: jest.fn(),
      loginAsGuest: jest.fn(),
      logout: jest.fn(),
      authFetch: jest.fn(),
      hasRole: () => true,
      apiBase: "http://127.0.0.1:8000",
    }),
  };
});

test("renders SentinelAI dashboard", () => {
  render(<App />);
  expect(screen.getByText(/Security Operations Center/i)).toBeInTheDocument();
  expect(screen.getAllByText(/SentinelAI/i).length).toBeGreaterThan(0);
});
