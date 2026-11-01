import { useState } from "react";
import {
  BrainCircuit,
  ChevronDown,
  AlertTriangle,
  ShieldCheck,
} from "lucide-react";
import "../styles/threat-explanation.css";

export default function ThreatExplanation({ result }) {
  const explanations = Array.isArray(result?.threat_explanations)
    ? result.threat_explanations
    : [];

  const [openIndex, setOpenIndex] = useState(0);

  if (!explanations.length) return null;

  return (
    <section className="v5-explain-panel">
      <div className="v5-explain-header">
        <div className="v5-explain-heading">
          <BrainCircuit size={22} />
          <span>EXPLAINABLE THREAT INTELLIGENCE</span>
        </div>

        <span className="v5-explain-count">
          {explanations.length} FINDINGS
        </span>
      </div>

      <p className="v5-explain-intro">
        Understand why URL patterns were flagged and
        what precautions you can take.
      </p>

      <div className="v5-explain-list">
        {explanations.map((item, index) => {
          const isOpen = openIndex === index;

          return (
            <article
              className={`v5-explain-item ${isOpen ? "is-open" : ""}`}
              key={`${item.code}-${index}`}
            >
              <button
                type="button"
                className="v5-explain-trigger"
                aria-expanded={isOpen}
                aria-controls={`v5-explanation-${index}`}
                onClick={() =>
                  setOpenIndex(isOpen ? -1 : index)
                }
              >
                <span className="v5-explain-trigger-icon">
                  <AlertTriangle size={18} />
                </span>

                <span className="v5-explain-trigger-text">
                  <strong>{item.title || item.code}</strong>
                  <small>{item.code}</small>
                </span>

                <span className="v5-explain-points">
                  +{item.points ?? 0}
                </span>

                <ChevronDown
                  size={17}
                  className={`v5-explain-chevron ${
                    isOpen ? "rotated" : ""
                  }`}
                />
              </button>

              {isOpen && (
                <div
                  id={`v5-explanation-${index}`}
                  className="v5-explain-content"
                >
                  <div className="v5-explain-detail">
                    <span>WHY WAS THIS FLAGGED?</span>
                    <p>{item.reason}</p>
                  </div>

                  <div className="v5-explain-detail action">
                    <span>
                      <ShieldCheck size={15} />
                      RECOMMENDED PRECAUTION
                    </span>
                    <p>{item.action}</p>
                  </div>
                </div>
              )}
            </article>
          );
        })}
      </div>

      <p className="v5-explain-note">
        Explanations are based on predefined URL heuristics.
        They do not establish that a website is malicious.
      </p>
    </section>
  );
}
