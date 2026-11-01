import { useState } from "react";
import { Crosshair } from "lucide-react";

export default function URLEvidenceHighlighter({
  data,
  selectedEvidenceId,
  onSelectEvidence,
}) {
  

  const hostname = data?.hostname || "";

  const mappings = Array.isArray(data?.url_evidence_map)
    ? data.url_evidence_map.filter(
        (item) =>
          item.component === "hostname" &&
          item.component_value === hostname &&
          Array.isArray(item.spans)
      )
    : [];

  if (!data || !Array.isArray(data.url_evidence_map)) {
    return null;
  }

  const activeId = selectedEvidenceId;

  const active = mappings.find(
    (item) => item.evidence_id === activeId
  ) || null;

  const highlighted = new Set();

  if (active) {
    for (const span of active.spans) {
      if (
        !Number.isInteger(span.start) ||
        !Number.isInteger(span.end) ||
        span.start < 0 ||
        span.end > hostname.length ||
        span.start >= span.end
      ) {
        continue;
      }

      for (let i = span.start; i < span.end; i++) {
        highlighted.add(i);
      }
    }
  }

  return (
    <section
      className="v5-url-map"
      aria-label="URL Evidence Highlighter"
    >
      <div className="v5-url-map-heading">
        <div>
          <span className="v5-url-map-kicker">
            PHANTOMLINK / URL FORENSICS
          </span>
          <h3>
            <Crosshair size={20} />
            URL EVIDENCE EXPLORER
          </h3>
          <p>
            Select a structural indicator to inspect the
            corresponding hostname characters.
          </p>
        </div>
        <span className="v5-url-map-count">
          {mappings.length} MAPPINGS
        </span>
      </div>

      <div
        className="v5-url-map-hostname"
        aria-label={`Analyzed hostname: ${hostname}`}
      >
        {Array.from(hostname).map((char, index) => (
          <span
            key={index}
            className={
              highlighted.has(index)
                ? "v5-url-map-character is-highlighted"
                : "v5-url-map-character"
            }
          >
            {char}
          </span>
        ))}
      </div>

      {mappings.length === 0 ? (
        <p className="v5-url-map-empty">
          No supported direct character mappings are
          available for this investigation.
        </p>
      ) : (
        <div className="v5-url-map-controls">
          {mappings.map((mapping) => (
            <button
              key={mapping.evidence_id}
              type="button"
              aria-pressed={
                selectedEvidenceId === mapping.evidence_id
              }
              onClick={() =>
                onSelectEvidence?.(
                  selectedEvidenceId === mapping.evidence_id
                    ? null
                    : mapping.evidence_id
                )
              }
            >
              {mapping.signal_code}
            </button>
          ))}
        </div>
      )}

      <p className="v5-url-map-disclaimer">
        Highlighted characters represent observed URL
        structure, not proof of phishing or website safety.
      </p>
    </section>
  );
}
