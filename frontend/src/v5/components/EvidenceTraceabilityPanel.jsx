import { useState } from "react";
import { ChevronDown, Fingerprint, ShieldAlert } from "lucide-react";

export default function EvidenceTraceabilityPanel({
  data,
  onSelectEvidence,
  selectedEvidenceId,
}) {
  

  const traces = Array.isArray(data?.evidence_trace)
    ? data.evidence_trace
    : [];

  if (!data || !Array.isArray(data.evidence_trace)) {
    return null;
  }

  return (
    <section
      className="v5-trace-panel"
      aria-label="Evidence Traceability"
    >
      <div className="v5-trace-heading">
        <div>
          <span className="v5-trace-kicker">
            PHANTOMLINK / EVIDENCE INTELLIGENCE
          </span>
          <h3>
            <Fingerprint size={22} />
            EVIDENCE TRACEABILITY
          </h3>
          <p>
            Explore the observations behind this URL analysis.
            These indicators are not proof of phishing.
          </p>
        </div>
        <span className="v5-trace-counter">
          {traces.length} EVIDENCE RECORDS
        </span>
      </div>

      {traces.length === 0 ? (
        <div className="v5-trace-empty">
          No evidence signals were recorded by this module.
          This does not establish that the URL is safe.
        </div>
      ) : (
        <div className="v5-trace-list">
          {traces.map((record, index) => {
            const key = `${record.evidence_id}-${index}`;
            const isOpen = selectedEvidenceId === record.evidence_id;

            return (
              <article className="v5-trace-item" key={key}>
                <button
                  type="button"
                  className="v5-trace-toggle"
                  aria-expanded={isOpen}
                  onClick={() =>
                    onSelectEvidence?.(
                      isOpen ? null : record.evidence_id
                    )
                  }
                >
                  <div className="v5-trace-item-name">
                    <ShieldAlert size={18} />
                    <span>{record.signal_code}</span>
                  </div>
                  <div className="v5-trace-meta">
                    <span>{record.confidence || "UNSPECIFIED"}</span>
                    <ChevronDown
                      size={17}
                      className={isOpen ? "v5-trace-rotated" : ""}
                    />
                  </div>
                </button>

                {isOpen && (
                  <div className="v5-trace-detail">
                    <p><strong>Evidence ID:</strong> {record.evidence_id}</p>
                    <p><strong>Source:</strong> {record.source}</p>
                    <p>
                      <strong>Observed evidence:</strong>{" "}
                      {record.observed_evidence}
                    </p>
                    <p>
                      <strong>Explanation:</strong>{" "}
                      {record.explanation}
                    </p>
                    <p>
                      <strong>Limitation:</strong>{" "}
                      {record.limitation}
                    </p>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
