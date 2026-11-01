import { Link } from "react-router-dom";
import { Globe2, ArrowUpRight } from "lucide-react";

import { useInvestigation } from "../context/InvestigationContext";
import DNSIntelligence from "../components/DNSIntelligence";

import "../styles/dns.css";

export default function DNSPage() {
  const {
    result,
    dnsData,
    dnsLoading,
    dnsError,
  } = useInvestigation();

  return (
    <section className="v5-investigate-section">
      <div className="v5-section-label">
        <Globe2 size={17} />
        PHANTOMLINK / DNS INTELLIGENCE
      </div>

      <h2>BEYOND THE DOMAIN.</h2>

      <p>
        Discover DNS records associated with an investigated
        hostname, including IPv4 and IPv6 addresses.
      </p>

      {result ? (
        <DNSIntelligence
          data={dnsData}
          loading={dnsLoading}
          error={dnsError}
        />
      ) : (
        <div className="v5-dns-panel">
          <h3>NO ACTIVE INVESTIGATION</h3>

          <p className="v5-dns-message">
            Investigate a URL first to inspect its DNS records.
          </p>

          <Link to="/investigate" className="v5-cta">
            START INVESTIGATION
            <ArrowUpRight size={18} />
          </Link>
        </div>
      )}
    </section>
  );
}
