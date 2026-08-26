import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "../context/AuthContext";

const REFRESH_MS = 5000;

export function useDashboardData() {
  const { authFetch, apiBase, user } = useAuth();
  const [dashboard, setDashboard] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [health, setHealth] = useState(null);
  const [alerts, setAlerts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [toast, setToast] = useState(null);
  const previousRef = useRef(null);
  const dashboardRef = useRef(null);
  const analyticsRef = useRef(null);

  const showToast = useCallback((message, type = "info") => {
    setToast({ message, type, id: Date.now() });
    setTimeout(() => setToast(null), 4000);
  }, []);

  const canAnalytics = ["ADMIN", "ANALYST", "VIEWER"].includes(user?.role);
  const canAlerts = user?.role === "ADMIN" || user?.role === "ANALYST";

  const loadData = useCallback(async () => {
    try {
      const fetches = [
        authFetch(`${apiBase}/realtime-dashboard`),
        authFetch(`${apiBase}/health`),
      ];
      if (canAnalytics) {
        fetches.splice(1, 0, authFetch(`${apiBase}/analytics`));
      }
      if (canAlerts) {
        fetches.push(authFetch(`${apiBase}/alerts`));
      }

      const responses = await Promise.all(fetches);
      let idx = 0;
      const dashboardRes = responses[idx++];
      const analyticsRes = canAnalytics ? responses[idx++] : null;
      const healthRes = responses[idx++];
      const alertsRes = canAlerts ? responses[idx] : null;

      if (!dashboardRes.ok) {
        throw new Error("Failed to fetch security data");
      }

      const dashboardData = await dashboardRes.json();
      const analyticsData = analyticsRes?.ok ? await analyticsRes.json() : null;
      const healthData = healthRes.ok ? await healthRes.json() : null;
      const alertsData = alertsRes?.ok ? await alertsRes.json() : null;

      previousRef.current = {
        dashboard: dashboardRef.current,
        analytics: analyticsRef.current,
      };
      dashboardRef.current = dashboardData;
      analyticsRef.current = analyticsData;

      setDashboard(dashboardData);
      setAnalytics(analyticsData);
      setHealth(healthData);
      setAlerts(alertsData);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      setError(err.message);
      showToast(err.message, "error");
    } finally {
      setLoading(false);
    }
  }, [authFetch, apiBase, canAnalytics, canAlerts, showToast]);

  useEffect(() => {
    if (!user) return;
    loadData();
    const interval = setInterval(loadData, REFRESH_MS);
    return () => clearInterval(interval);
  }, [loadData, user]);

  return {
    dashboard,
    analytics,
    health,
    alerts,
    loading,
    error,
    lastUpdated,
    toast,
    previous: previousRef.current,
    refresh: loadData,
    apiBase,
  };
}
