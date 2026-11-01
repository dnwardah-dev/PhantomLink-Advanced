import {
  Globe2,
  Network,
  ShieldAlert,
  Server,
  Activity,
} from "lucide-react";

export default function DNSIntelligence({ data, loading, error }) {
  if (!data && !loading && !error) return null;

  const ipv4 = Array.isArray(data?.ipv4) ? data.ipv4 : [];
  const ipv6 = Array.isArray(data?.ipv6) ? data.ipv6 : [];
  const blocked = Array.isArray(data?.blocked_addresses)
    ? data.blocked_addresses
    : [];
  const errors = Array.isArray(data?.errors) ? data.errors : [];

  return (
    <section className="v5-dns-panel">
      <div className="v5-dns-header">
        <div className="v5-dns-heading">
          <Globe2 size={23} />
          <span>DNS INTELLIGENCE</span>
        </div>

        <span className="v5-dns-status">
          <Activity size={14} />
          {loading ? "RESOLVING" : data?.status ?? "ERROR"}
        </span>
      </div>

      {loading && (
        <p className="v5-dns-message">
          Resolving DNS records...
        </p>
      )}

      {error && (
        <p className="v5-dns-error" role="alert">
          DNS lookup failed: {error}
        </p>
      )}

      {data && (
        <>
          <div className="v5-dns-target">
            <span>TARGET HOSTNAME</span>
            <strong>{data.hostname}</strong>
          </div>

          <div className="v5-dns-grid">
            <div className="v5-dns-card">
              <div className="v5-dns-card-heading">
                <Server size={18} />
                <span>IPv4 / A RECORDS</span>
              </div>

              {ipv4.length ? (
                ipv4.map((ip) => (
                  <code key={ip}>{ip}</code>
                ))
              ) : (
                <p>No public IPv4 records returned.</p>
              )}
            </div>

            <div className="v5-dns-card">
              <div className="v5-dns-card-heading">
                <Network size={18} />
                <span>IPv6 / AAAA RECORDS</span>
              </div>

              {ipv6.length ? (
                ipv6.map((ip) => (
                  <code key={ip}>{ip}</code>
                ))
              ) : (
                <p>No public IPv6 records returned.</p>
              )}
            </div>
          </div>

          {blocked.length > 0 && (
            <div className="v5-dns-warning">
              <ShieldAlert size={19} />
              <div>
                <strong>NON-PUBLIC ADDRESSES DETECTED</strong>
                {blocked.map((item, index) => (
                  <p key={index}>
                    {item.record_type}: {item.address}
                  </p>
                ))}
              </div>
            </div>
          )}

          {errors.length > 0 && (
            <div className="v5-dns-warning">
              <ShieldAlert size={19} />
              <div>
                <strong>DNS LOOKUP NOTES</strong>
                {errors.map((message, index) => (
                  <p key={index}>{message}</p>
                ))}
              </div>
            </div>
          )}

          <p className="v5-dns-disclaimer">
            DNS records were queried without fetching website
            content. DNS resolution does not establish whether
            a website is safe or malicious.
          </p>
        </>
      )}
    </section>
  );
}
