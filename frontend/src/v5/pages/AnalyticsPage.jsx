import { useEffect, useState } from "react";
import { Activity, RefreshCw } from "lucide-react";

import InvestigationAnalytics from "../components/InvestigationAnalytics";
import { getInvestigationHistory } from "../services/api";
import { useInvestigation } from "../context/InvestigationContext";

import "../styles/analytics.css";
import "../styles/archive.css";

export default function AnalyticsPage() {
  const { archiveVersion } = useInvestigation();

  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let active = true;

    async function loadAnalytics() {
      setLoading(true);
      setError("");

      try {
        const response = await getInvestigationHistory();

        if (active) {
          setHistory(
            Array.isArray(response.history) ? response.history : []
          );
        }
      } catch (err) {
        if (active) {
          setError(err.message || "Failed to load analytics.");
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    loadAnalytics();

    return () => {
      active = false;
    };
  }, [archiveVersion, refreshKey]);

  return (
    <section className="v5-investigate-section">
      <div className="v5-section-label">
        <Activity size={17} />
        PHANTOMLINK / THREAT ANALYTICS
      </div>

      <h2>DECODE THE PATTERNS.</h2>

      <p>
        Explore risk distribution and detected indicators
        across investigation records loaded from SQLite.
      </p>

      <button
        type="button"
        className="v5-archive-refresh"
        disabled={loading}
        onClick={() => setRefreshKey((key) => key + 1)}
        style={{ marginTop: 24 }}
      >
        <RefreshCw size={16} />
        {loading ? "LOADING..." : "REFRESH ANALYTICS"}
      </button>

      {error && (
        <p role="alert" className="v5-archive-error">
          {error}
        </p>
      )}

      {loading ? (
        <p className="v5-archive-empty">
          Loading threat intelligence statistics...
        </p>
      ) : (
        <InvestigationAnalytics history={history} />
      )}
    </section>
  );
}
