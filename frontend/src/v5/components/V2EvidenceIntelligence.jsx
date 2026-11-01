import { ShieldCheck, AlertTriangle, ScanSearch } from "lucide-react";

const categoryLabels = {
  ADDITIONAL_REVIEW: "ADDITIONAL REVIEW",
  STRUCTURAL_OBSERVATION: "STRUCTURAL OBSERVATION",
  INSUFFICIENT_EVIDENCE: "INSUFFICIENT EVIDENCE",
};

export default function V2EvidenceIntelligence({
  data,
  loading,
  error,
}) {
  if (!data && !loading && !error) return null;
  const interpretation = data?.interpretation;

  const structural = interpretation?.structural_signals ?? [];
  const domain = interpretation?.domain_signals ?? [];

  const signals = [...structural, ...domain];

  const category = interpretation?.category;

  const accent =
    category === "ADDITIONAL_REVIEW"
      ? "#ffbc73"
      : category === "STRUCTURAL_OBSERVATION"
      ? "#ae9cff"
      : "#76d9c7";

  const panelStyle = {
    marginTop: 28,
    padding: 24,
    borderRadius: 20,
    background:
      "linear-gradient(145deg, #151b30 0%, #0d1324 100%)",
    border: "1px solid rgba(160,145,255,0.25)",
    boxShadow: "0 12px 45px rgba(0,0,0,0.18)",
    color: "#e9efff",
  };

  return (
    <section style={panelStyle} aria-label="V2 Evidence Intelligence">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: 12,
          flexWrap: "wrap",
          marginBottom: 20,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <ShieldCheck size={22} color="#ad9aff" />
          <strong style={{ letterSpacing: 1.3 }}>
            V2 EVIDENCE INTELLIGENCE
          </strong>
        </div>

        <span
          style={{
            fontSize: 11,
            color: "#c3b5ff",
            border: "1px solid #655596",
            borderRadius: 30,
            padding: "5px 11px",
          }}
        >
          EXPERIMENTAL
        </span>
      </div>

      {loading && (
        <p role="status" style={{ color: "#b8c7e3" }}>
          Analyzing additional URL evidence...
        </p>
      )}

      {error && !loading && (
        <div role="alert" style={{ color: "#ff9cae" }}>
          <AlertTriangle size={17} style={{ verticalAlign: "middle" }} />
          {" "}V2 analysis unavailable: {error}
          <p style={{ color: "#aab8d0", fontSize: 13 }}>
            The primary V1 investigation remains available.
          </p>
        </div>
      )}

      {interpretation && !loading && (
        <>
          <div
            style={{
              padding: 18,
              borderRadius: 14,
              background: "#1b233a",
              borderLeft: `3px solid ${accent}`,
            }}
          >
            <div
              style={{
                color: accent,
                fontSize: 13,
                fontWeight: 800,
                letterSpacing: 1,
                marginBottom: 9,
              }}
            >
              {categoryLabels[category] ?? "EVIDENCE REVIEW"}
            </div>

            <p style={{ color: "#d4dff3", lineHeight: 1.7, margin: 0 }}>
              {interpretation.message}
            </p>
          </div>

          <div style={{ marginTop: 23 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                marginBottom: 13,
              }}
            >
              <ScanSearch size={17} color="#ad9aff" />
              <strong>DETECTED EVIDENCE</strong>
            </div>

            {signals.length === 0 ? (
              <p style={{ color: "#a9b8d3", fontSize: 14 }}>
                No indicators identified by the experimental V2 modules.
                This does not establish that the URL is safe.
              </p>
            ) : (
              <div style={{ display: "grid", gap: 10 }}>
                {signals.map((signal, index) => (
                  <div
                    key={`${signal.code}-${index}`}
                    style={{
                      background: "#192139",
                      border: "1px solid #303b59",
                      borderRadius: 12,
                      padding: 14,
                    }}
                  >
                    <div
                      style={{
                        color: "#c2b6ff",
                        fontWeight: 700,
                        fontSize: 12,
                        overflowWrap: "anywhere",
                      }}
                    >
                      {signal.code}
                    </div>

                    {(signal.evidence || signal.description) && (
                      <p
                        style={{
                          color: "#b8c6df",
                          fontSize: 13,
                          lineHeight: 1.6,
                          margin: "7px 0 0",
                          overflowWrap: "anywhere",
                        }}
                      >
                        {signal.evidence || signal.description}
                      </p>
                    )}

                    {signal.confidence && (
                      <small style={{ color: "#889bbd" }}>
                        Confidence: {signal.confidence}
                      </small>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <p
            style={{
              fontSize: 12,
              color: "#8e9fbd",
              borderTop: "1px solid #303b59",
              paddingTop: 16,
              marginTop: 24,
              lineHeight: 1.7,
            }}
          >
            V2 is an experimental evidence interpretation system.
            Structural scores are not phishing probabilities.
            A missing indicator does not mean a website is safe.
          </p>
        </>
      )}
    </section>
  );
}


