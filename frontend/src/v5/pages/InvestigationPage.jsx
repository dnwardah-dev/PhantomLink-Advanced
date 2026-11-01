import { useState } from "react";
﻿import { useInvestigation } from "../context/InvestigationContext";

import InvestigationScanner from "../components/InvestigationScanner";
import RiskAssessment from "../components/RiskAssessment";
import ThreatExplanation from "../components/ThreatExplanation";
import V2EvidenceIntelligence from "../components/V2EvidenceIntelligence";

import EvidenceTraceabilityPanel from "../components/EvidenceTraceabilityPanel";
import "../styles/evidence-traceability.css";
import URLEvidenceHighlighter from "../components/URLEvidenceHighlighter";
import "../styles/url-evidence-highlighter.css";
import "../styles/scanner.css";
import "../styles/risk.css";
import "../styles/threat-explanation.css";

export default function InvestigationPage() {
  const [selectedEvidenceId, setSelectedEvidenceId] = useState(null);
  const {
    result,
    loading,
    error,
    v2Result,
    v2Loading,
    v2Error,
    runInvestigation,
  } = useInvestigation();

  const handleInvestigate = (url) => {
    setSelectedEvidenceId(null);
    return runInvestigation(url);
  };

  return (
    <section className="v5-investigate-section">
      <div className="v5-section-label">
        PHANTOMLINK / INVESTIGATION LAB
      </div>

      <h2>INVESTIGATE THE UNKNOWN.</h2>

      <p>
        Analyze suspicious URL patterns and uncover
        the evidence behind each risk assessment.
      </p>

      <InvestigationScanner
        onInvestigate={handleInvestigate}
        loading={loading}
      />

      {error && (
        <p role="alert" style={{
          color: "#ff8d9e",
          marginTop: 20
        }}>
          Investigation failed: {error}
        </p>
      )}

      {result && (
        <>
          <RiskAssessment result={result} />
          <ThreatExplanation result={result} />
          <V2EvidenceIntelligence
            data={v2Result}
            loading={v2Loading}
            error={v2Error}
          />
          <EvidenceTraceabilityPanel
            data={v2Result}
            selectedEvidenceId={selectedEvidenceId}
            onSelectEvidence={setSelectedEvidenceId}
          />
          <URLEvidenceHighlighter
            data={v2Result}
            selectedEvidenceId={selectedEvidenceId}
            onSelectEvidence={setSelectedEvidenceId}
          />
        </>
      )}
    </section>
  );
}

