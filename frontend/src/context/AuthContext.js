import { createContext, useCallback, useContext, useEffect, useState } from "react";

const API_BASE = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";
const TOKEN_KEY = "sentinel_token";
const GUEST_KEY = "sentinel_guest";

export const GUEST_USER = {
  id: 0,
  username: "guest",
  email: "guest@local",
  role: "VIEWER",
  created_at: "",
};

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [isGuest, setIsGuest] = useState(() => localStorage.getItem(GUEST_KEY) === "true");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMe = useCallback(async (authToken, guestMode = false) => {
    const headers = {};
    if (authToken) {
      headers.Authorization = `Bearer ${authToken}`;
    }
    if (guestMode) {
      headers["X-Sentinel-Guest"] = "1";
    }
    const res = await fetch(`${API_BASE}/me`, { headers });
    if (!res.ok) {
      throw new Error("Session expired");
    }
    return res.json();
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        if (token) {
          const me = await fetchMe(token, false);
          if (!cancelled) {
            setUser(me);
            setIsGuest(false);
            setError(null);
          }
        } else if (localStorage.getItem(GUEST_KEY) === "true") {
          const me = await fetchMe(null, true);
          if (!cancelled) {
            setUser(me);
            setIsGuest(true);
            setError(null);
          }
        } else if (!cancelled) {
          setUser(null);
          setIsGuest(false);
        }
      } catch {
        if (!cancelled) {
          setUser(null);
          setIsGuest(false);
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(GUEST_KEY);
          setToken(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [token, fetchMe]);

  const login = async (username, password) => {
    setError(null);
    const res = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Login failed");
    }
    const data = await res.json();
    localStorage.removeItem(GUEST_KEY);
    localStorage.setItem(TOKEN_KEY, data.access_token);
    setIsGuest(false);
    setToken(data.access_token);
    const me = await fetchMe(data.access_token);
    setUser(me);
    return me;
  };

  const loginAsGuest = async () => {
    setError(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.setItem(GUEST_KEY, "true");
    setToken(null);
    setIsGuest(true);
    try {
      const me = await fetchMe(null, true);
      setUser(me);
      return me;
    } catch (err) {
      localStorage.removeItem(GUEST_KEY);
      setIsGuest(false);
      setUser(null);
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(GUEST_KEY);
    setToken(null);
    setIsGuest(false);
    setUser(null);
  };

  const authFetch = useCallback(
    (url, options = {}) => {
      const headers = { ...(options.headers || {}) };
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (isGuest || localStorage.getItem(GUEST_KEY) === "true") {
        headers["X-Sentinel-Guest"] = "1";
      }
      return fetch(url, { ...options, headers });
    },
    [token, isGuest]
  );

  const hasRole = (roles) => {
    if (!user) return false;
    return roles.includes(user.role);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isGuest,
        loading,
        error,
        setError,
        login,
        loginAsGuest,
        logout,
        authFetch,
        hasRole,
        apiBase: API_BASE,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export function canAccessView(role, viewId) {
  const viewerViews = ["dashboard", "analytics", "threat-intel", "correlation", "explainability"];
  const analystViews = [...viewerViews, "threats", "anomalies", "alerts", "investigation", "settings"];
  const adminViews = [...analystViews];

  if (role === "ADMIN") return adminViews.includes(viewId);
  if (role === "ANALYST") return analystViews.includes(viewId);
  if (role === "VIEWER") return viewerViews.includes(viewId);
  return viewerViews.includes(viewId);
}
