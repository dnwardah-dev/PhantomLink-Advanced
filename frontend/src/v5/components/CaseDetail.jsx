import { useEffect } from "react";
import {
  X, Fingerprint, CalendarClock,
  ShieldAlert, Activity, Database,
} from "lucide-react";
import "../styles/case-detail.css";

export default function CaseDetail({ caseData, onClose }) {
  useEffect(() => {
    if (!caseData) return;

    function handleKeyDown(event) {
      if (event.key === "Escape") onClose();
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [caseData, onClose]);

  if (!caseData) return null;

  const signals = Array.isArray(caseData.indicators)
    ? caseData.indicators
    : [];

  const level = caseData.risk_level || "UNKNOWN";

  const date = caseData.created_at
    ? new Date(caseData.created_at)
    : null;

  const formattedDate =
    date && !Number.isNaN(date.getTime())
      ? date.toLocaleString("id-ID")
      : "Unknown";

  return (
    <div
      className="v5-case-overlay"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <aside
        className="v5-case-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="v5-case-title"
      >
        <header className="v5-case-header">
          <span>
            <Fingerprint size={20} />
            PHANTOM CASE FILE
          </span>

          <button onClick={onClose} aria-label="Close case detail">
            <X size={20} />
          </button>
        </header>

        <div className="v5-case-body">
          <span className="v5-case-label">INVESTIGATION ID</span>
          <h2 id="v5-case-title">
            CASE #{caseData.id}
          </h2>

          <div className="v5-case-target">
            <span className="v5-case-label">TARGET HOSTNAME</span>
            <strong>{caseData.hostname || "Unknown host"}</strong>
          </div>

          <div className="v5-case-risk">
            <div>
              <span className="v5-case-label">RISK SCORE</span>
              <strong>{caseData.risk_score ?? "—"}<small>/100</small></strong>
            </div>

            <span className={`v5-archive-level ${level}`}>
              <ShieldAlert size={13} />
              {level}
            </span>
          </div>

          <div className="v5-case-meta">
            <div>
              <CalendarClock size={17} />
              <span>{formattedDate}</span>
            </div>

            <div>
              <Database size={17} />
              <span>{caseData.analysis_type || "Unknown method"}</span>
            </div>
          </div>

          <div className="v5-case-evidence">
            <h3>
              <Activity size={18} />
              DETECTED INDICATORS ({signals.length})
            </h3>

            {signals.length === 0 ? (
              <p>No indicators recorded for this case.</p>
            ) : (
              signals.map((item, index) => (
                <div className="v5-case-signal" key={index}>
                  <span>{item.code || "UNKNOWN"}</span>
                  <strong>+{item.points ?? 0}</strong>
                </div>
              ))
            )}
          </div>

          <p className="v5-case-notice">
            This case file contains the information retained in
            the local investigation archive. It reflects offline
            URL heuristics, not observed website activity.
          </p>
        </div>
      </aside>
    </div>
  );
}
