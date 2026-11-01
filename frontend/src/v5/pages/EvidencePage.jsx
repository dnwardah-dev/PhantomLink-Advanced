import { Link } from "react-router-dom";
import { Network, ArrowUpRight } from "lucide-react";

import { useInvestigation } from "../context/InvestigationContext";
import EvidenceGraph from "../components/EvidenceGraph";

import "../styles/graph.css";

export default function EvidencePage() {
  const { result, dnsData } = useInvestigation();

  return (
    <section className="v5-investigate-section">
      <div className="v5-section-label">
        <Network size={17} />
        PHANTOMLINK / EVIDENCE LAB
      </div>

      <h2>FOLLOW THE EVIDENCE.</h2>

      <p>
        Explore the relationship between the investigated URL,
        its hostname, and detected heuristic risk indicators.
      </p>

      {result ? (
        <EvidenceGraph result={result} dnsData={dnsData} />
      ) : (
        <div className="v5-graph-panel">
          <h3 style={{ color: "#f4f7ff" }}>
            NO ACTIVE INVESTIGATION
          </h3>

          <p style={{ color: "#a4adc5" }}>
            Start an investigation first to generate
            an interactive evidence map.
          </p>

          <Link
            to="/investigate"
            className="v5-cta"
            style={{ marginTop: 20 }}
          >
            START INVESTIGATION
            <ArrowUpRight size={18} />
          </Link>
        </div>
      )}
    </section>
  );
}
