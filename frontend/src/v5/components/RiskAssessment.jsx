import { exportInvestigationPDF } from "../services/pdfExport";
import { exportInvestigationJSON } from "../services/reportExport";
import { motion } from "motion/react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Fingerprint,
  ShieldAlert,
} from "lucide-react";

function getRiskTheme(level) {
  switch (level) {
    case "HIGH":
    case "CRITICAL":
      return { color: "#ff718c", icon: ShieldAlert };
    case "MEDIUM":
      return { color: "#ffbd69", icon: AlertTriangle };
    default:
      return { color: "#65e8f4", icon: CheckCircle2 };
  }
}

export default function RiskAssessment({ result }) {
  if (!result) return null;

  const assessment = result.risk_assessment ?? {};
  const score = Math.max(
    0,
    Math.min(100, Number(assessment.score) || 0)
  );

  const level = assessment.level ?? "UNKNOWN";
  const evidence = Array.isArray(result.evidence)
    ? result.evidence
    : [];

  const theme = getRiskTheme(level);
  const RiskIcon = theme.icon;
  const circumference = 2 * Math.PI * 76;

  return (
    <motion.section
      className="v5-risk-panel"
      initial={{ opacity: 0, y: 28 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.65 }}
      aria-label="Investigation risk assessment"
    >
      <div className="v5-risk-header">
        <div className="v5-risk-heading">
          <Fingerprint size={23} />
          <span>PHANTOM INTELLIGENCE REPORT</span>
        </div>

        <span className="v5-risk-complete">
          <Activity size={15} />
          ANALYSIS COMPLETE
        </span>
      </div>

      <div className="v5-risk-main">
        <div className="v5-risk-gauge">
          <svg viewBox="0 0 200 200" role="img"
            aria-label={`Risk score ${score} out of 100`}>
            <circle
              cx="100" cy="100" r="76"
              fill="none" stroke="#242c42"
              strokeWidth="11"
            />
            <motion.circle
              cx="100" cy="100" r="76"
              fill="none"
              stroke={theme.color}
              strokeWidth="11"
              strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{
                strokeDashoffset:
                  circumference * (1 - score / 100),
              }}
              transition={{ duration: 1.5, ease: "easeOut" }}
              transform="rotate(-90 100 100)"
            />
            <text x="100" y="108" textAnchor="middle"
              fill="#f5f7ff" fontSize="52" fontWeight="700">
              {score}
            </text>
            <text x="100" y="134" textAnchor="middle"
              fill="#8995b0" fontSize="12">
              RISK / 100
            </text>
          </svg>
        </div>

        <div className="v5-risk-details">
          <span className="v5-risk-eyebrow">
            THREAT CLASSIFICATION
          </span>

          <div className="v5-risk-level"
            style={{ color: theme.color }}>
            <RiskIcon size={30} />
            {level} RISK
          </div>

          <p>{assessment.summary ?? "No summary available."}</p>

          <div className="v5-risk-meta">
            <span>ANALYSIS METHOD</span>
            <strong>
              {result.investigation?.analysis_type ??
                "offline_heuristic"}
            </strong>
          </div>

          <div className="v5-risk-meta">
            <span>EVIDENCE SIGNALS</span>
            <strong>{evidence.length}</strong>
          </div>

          <div className="v5-risk-meta">
            <span>INVESTIGATION ID</span>
            <strong>
              #{result.investigation?.id ?? "—"}
            </strong>
          </div>
        </div>
      </div>

      <div className="v5-evidence-section">
        <h3>DETECTED EVIDENCE</h3>

        {evidence.length === 0 ? (
          <p className="v5-evidence-empty">
            No suspicious indicators were reported.
          </p>
        ) : (
          <div className="v5-evidence-list">
            {evidence.map((item, index) => (
              <div className="v5-evidence-item" key={index}>
                <div className="v5-evidence-icon">
                  <AlertTriangle size={17} />
                </div>

                <div>
                  <strong>{item.code}</strong>
                  <p>
                    {item.explanation ??
                      "A URL risk indicator was detected."}
                  </p>
                </div>

                <span className="v5-evidence-points">
                  +{item.points ?? 0}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {result.recommendation && (
        <div className="v5-risk-recommendation">
          <strong>RECOMMENDED ACTION</strong>
          <p>{result.recommendation}</p>
        </div>
      )}

      <div className="v5-report-actions">
        <button
          type="button"
          className="v5-report-download"
          onClick={() => exportInvestigationJSON(result)}
        >
          <span>DOWNLOAD JSON</span>
          <span className="v5-report-format">JSON</span>
        </button>

        <button
          type="button"
          className="v5-report-download v5-report-pdf"
          onClick={() => exportInvestigationPDF(result)}
        >
          <span>DOWNLOAD PDF REPORT</span>
          <span className="v5-report-format">PDF</span>
        </button>
      </div>

      <p className="v5-risk-disclaimer">
        {result.disclaimer ??
          "Heuristic URL analysis only. A low score does not guarantee safety."}
      </p>
    </motion.section>
  );
}
