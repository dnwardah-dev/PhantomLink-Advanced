import CaseDetail from "./CaseDetail";
import { useEffect, useState } from "react";
import {
  Archive,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Activity,
  Database,
} from "lucide-react";

import { getInvestigationHistory } from "../services/api";

export default function IntelligenceArchive({ refreshVersion = 0 }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("ALL");
  const [selectedCase, setSelectedCase] = useState(null);

  async function loadHistory() {
    setLoading(true);
    setError("");

    try {
      const response = await getInvestigationHistory();
      setHistory(
        Array.isArray(response.history) ? response.history : []
      );
    } catch (err) {
      setError(err.message || "Unable to load archive.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHistory();
  }, [refreshVersion]);

  const highRisk = history.filter(
    (item) =>
      item.risk_level === "HIGH" ||
      item.risk_level === "CRITICAL"
  ).length;

  const filteredHistory = history.filter(
    (item) => filter === "ALL" || item.risk_level === filter
  );

  function formatDate(value) {
    if (!value) return "Unknown date";

    const date = new Date(value);
    return Number.isNaN(date.getTime())
      ? "Unknown date"
      : date.toLocaleString("id-ID");
  }

  return (
    <section className="v5-archive" id="archive">
      <div className="v5-archive-heading">
        <div>
          <span className="v5-archive-kicker">
            <Database size={15} />
            INTELLIGENCE DATABASE / 002
          </span>

          <h2>THE ARCHIVE.</h2>

          <p>
            Every investigation leaves a trace.
            Explore the findings stored in your local database.
          </p>
        </div>

        <button
          className="v5-archive-refresh"
          onClick={loadHistory}
          disabled={loading}
        >
          <RefreshCw size={16} />
          {loading ? "LOADING..." : "REFRESH ARCHIVE"}
        </button>
      </div>

      <div className="v5-archive-stats">
        <div className="v5-archive-stat">
          <Archive size={20} />
          <span>TOTAL RECORDS LOADED</span>
          <strong>{history.length}</strong>
        </div>

        <div className="v5-archive-stat">
          <ShieldAlert size={20} />
          <span>HIGH / CRITICAL RISK</span>
          <strong>{highRisk}</strong>
        </div>

        <div className="v5-archive-stat">
          <Activity size={20} />
          <span>ANALYSIS ENGINE</span>
          <strong className="v5-archive-engine">
            OFFLINE HEURISTIC
          </strong>
        </div>
      </div>

      

      <div className="v5-archive-toolbar">
        <span>INVESTIGATION RECORDS</span>

        <div className="v5-archive-filters">
          {["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"].map(
            (level) => (
              <button
                key={level}
                className={filter === level ? "active" : ""}
                onClick={() => setFilter(level)}
              >
                {level}
              </button>
            )
          )}
        </div>
      </div>

      {error && (
        <p className="v5-archive-error" role="alert">
          {error}
        </p>
      )}

      {loading ? (
        <p className="v5-archive-empty">
          Retrieving investigation records...
        </p>
      ) : filteredHistory.length === 0 ? (
        <p className="v5-archive-empty">
          No investigation records match this filter.
        </p>
      ) : (
        <div className="v5-archive-list">
          {filteredHistory.map((item) => (
            <article
              className="v5-archive-record"
              key={item.id}
              onClick={() => setSelectedCase(item)}
              style={{ cursor: "pointer" }}
              tabIndex={0}
              role="button"
              aria-label={`Open case ${item.id}`}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  setSelectedCase(item);
                }
              }}
            >
              <div className="v5-archive-record-icon">
                {item.risk_level === "LOW" ? (
                  <ShieldCheck size={21} />
                ) : (
                  <ShieldAlert size={21} />
                )}
              </div>

              <div className="v5-archive-record-info">
                <strong>{item.hostname || "Unknown host"}</strong>
                <span>
                  CASE #{item.id} · {formatDate(item.created_at)}
                </span>
              </div>

              <div className="v5-archive-record-signals">
                {item.indicators?.length ?? 0} SIGNALS
              </div>

              <div className="v5-archive-record-score">
                <strong>{item.risk_score ?? "—"}/100</strong>
                <span
                  className={`v5-archive-level ${
                    item.risk_level || "UNKNOWN"
                  }`}
                >
                  {item.risk_level || "UNKNOWN"}
                </span>
              </div>
            </article>
          ))}
        </div>
      )}
      <CaseDetail
        caseData={selectedCase}
        onClose={() => setSelectedCase(null)}
      />
    </section>
  );
}
