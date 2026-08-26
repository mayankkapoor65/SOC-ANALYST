import { useState } from "react";
import { useAuth } from "../context/AuthContext";

const DEMO_ACCOUNTS = [
  { role: "ADMIN", username: "admin", password: "Admin123!" },
  { role: "ANALYST", username: "analyst1", password: "Analyst123!" },
  { role: "VIEWER", username: "viewer1", password: "Viewer123!" },
];

export default function LoginPage() {
  const { login, loginAsGuest, setError, error, apiBase } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [guestLoading, setGuestLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(username, password);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleGuest = async () => {
    setGuestLoading(true);
    setError(null);
    try {
      await loginAsGuest();
    } catch (err) {
      setError(err.message);
    } finally {
      setGuestLoading(false);
    }
  };

  const fillDemo = (account) => {
    setUsername(account.username);
    setPassword(account.password);
    setError(null);
  };

  return (
    <div className="login-screen">
      <div className="login-card glass-panel">
        <div className="login-brand">
          <h1>SentinelAI</h1>
          <p>Security Operations Center</p>
        </div>

        <div className="demo-accounts-card">
          <h3>Demo Accounts</h3>
          {DEMO_ACCOUNTS.map((account) => (
            <button
              key={account.role}
              type="button"
              className="demo-account-row"
              onClick={() => fillDemo(account)}
            >
              <span className="demo-role">{account.role}</span>
              <span className="demo-creds mono">
                {account.username} / {account.password}
              </span>
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <label>
            Username
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="admin"
              required
              autoComplete="username"
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              autoComplete="current-password"
            />
          </label>
          {error && <p className="login-error">{error}</p>}
          <div className="login-actions">
            <button type="submit" className="btn-login" disabled={submitting || guestLoading}>
              {submitting ? "Authenticating…" : "Login"}
            </button>
            <button
              type="button"
              className="btn-guest"
              onClick={handleGuest}
              disabled={submitting || guestLoading}
            >
              {guestLoading ? "Starting…" : "Continue as Guest"}
            </button>
          </div>
        </form>

        <p className="login-hint mono">API: {apiBase}</p>
      </div>
    </div>
  );
}
