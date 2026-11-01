import { useState } from "react";
import { motion } from "motion/react";
import {
  ArrowUpRight,
  Link2,
  LockKeyhole,
  ScanSearch,
  ShieldCheck,
} from "lucide-react";

export default function InvestigationScanner({ onInvestigate, loading = false }) {
  const [url, setUrl] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    const submittedUrl = url.trim();

    if (!submittedUrl || loading) return;

    onInvestigate?.(submittedUrl);
  }

  return (
    <motion.section
      className="v5-scanner"
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
    >
      <div className="v5-scanner-heading">
        <div className="v5-scanner-title">
          <ScanSearch size={23} />
          <span>PHANTOM INVESTIGATION TERMINAL</span>
        </div>

        <div className="v5-scanner-status">
          <span className="v5-status-dot" />
          {loading ? "ANALYZING" : "READY FOR INPUT"}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="v5-scanner-form">
        <div className="v5-scanner-input">
          <Link2 size={21} />

          <input
            type="text"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="Paste a suspicious URL to investigate..."
            aria-label="Suspicious URL"
            maxLength={2048}
            autoComplete="off"
            spellCheck={false}
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          disabled={!url.trim() || loading}
        >
          {loading ? "ANALYZING..." : "INITIATE INVESTIGATION"}
          <ArrowUpRight size={18} />
        </button>
      </form>

      <div className="v5-scanner-footer">
        <span>
          <LockKeyhole size={14} />
          OFFLINE URL ANALYSIS
        </span>

        <span>
          <ShieldCheck size={14} />
          WEBSITE CONTENT IS NOT FETCHED
        </span>
      </div>
    </motion.section>
  );
}
