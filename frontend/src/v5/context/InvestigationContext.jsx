import {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
} from "react";

import { investigateURL, investigateURLV2, inspectDNS } from "../services/api";

const InvestigationContext = createContext(null);

export function InvestigationProvider({ children }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [dnsData, setDnsData] = useState(null);
  const [dnsLoading, setDnsLoading] = useState(false);
  const [dnsError, setDnsError] = useState("");

  const [v2Result, setV2Result] = useState(null);
  const [v2Loading, setV2Loading] = useState(false);
  const [v2Error, setV2Error] = useState("");

  const [archiveVersion, setArchiveVersion] = useState(0);

  // Prevent older requests from overwriting newer results.
  const requestId = useRef(0);

  const runInvestigation = useCallback(async (url) => {
    const currentId = ++requestId.current;

    setLoading(true);
    setError("");
    setResult(null);
    setDnsData(null);
    setDnsError("");
    setDnsLoading(false);
    setV2Result(null);
    setV2Error("");
    setV2Loading(false);

    try {
      const data = await investigateURL(url);

      if (currentId !== requestId.current) return;

      setResult(data);
      setArchiveVersion((version) => version + 1);
      setLoading(false);

      setDnsLoading(true);
      setV2Loading(true);

      // Run supplementary analyses independently.
      void (async () => {
        try {
          const dns = await inspectDNS(url);
          if (currentId === requestId.current) {
            setDnsData(dns);
          }
        } catch (err) {
          if (currentId === requestId.current) {
            setDnsError(err.message || "DNS lookup failed.");
          }
        } finally {
          if (currentId === requestId.current) {
            setDnsLoading(false);
          }
        }
      })();

      void (async () => {
        try {
          const v2 = await investigateURLV2(url);
          if (currentId === requestId.current) {
            setV2Result(v2);
          }
        } catch (err) {
          if (currentId === requestId.current) {
            setV2Error(err.message || "V2 analysis failed.");
          }
        } finally {
          if (currentId === requestId.current) {
            setV2Loading(false);
          }
        }
      })();
    } catch (err) {
      if (currentId === requestId.current) {
        setError(err.message || "Investigation failed.");
      }
    } finally {
      if (currentId === requestId.current) {
        setLoading(false);
      }
    }
  }, []);

  return (
    <InvestigationContext.Provider
      value={{
        result,
        loading,
        error,
        dnsData,
        dnsLoading,
        dnsError,
        archiveVersion,
        v2Result,
        v2Loading,
        v2Error,
        runInvestigation,
      }}
    >
      {children}
    </InvestigationContext.Provider>
  );
}

export function useInvestigation() {
  const context = useContext(InvestigationContext);

  if (!context) {
    throw new Error(
      "useInvestigation must be used inside InvestigationProvider"
    );
  }

  return context;
}

