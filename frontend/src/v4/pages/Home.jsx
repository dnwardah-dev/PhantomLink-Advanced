import { useState } from "react";
import { motion } from "motion/react";
import {
  ArrowUpRight,
  ArrowRight,
  Shield,
  ShieldCheck,
  Search,
  Activity,
  Fingerprint,
  LockKeyhole,
  ScanLine,
  Sparkles,
  Globe2,
  Crosshair,
} from "lucide-react";

export default function Home() {
  const [url, setUrl] = useState("");

  return (
    <main className="v4-home">
      <nav className="v4-nav">
        <div className="v4-logo">
          <div className="v4-logo-symbol">
            <Fingerprint size={24} />
          </div>
          <span>phantomlink<span className="v4-logo-dot">.</span></span>
        </div>

        <div className="v4-nav-links">
          <span className="v4-nav-active">Discover</span>
          <span>Investigation</span>
          <span>Intelligence</span>
          <span>Archive</span>
        </div>

        <div className="v4-nav-status">
          <span className="v4-live-dot" />
          SYSTEM ONLINE
        </div>
      </nav>

      <section className="v4-hero">
        <div className="v4-hero-grid" aria-hidden="true" />
        <div className="v4-hero-glow" aria-hidden="true" />

        <motion.div
          className="v4-hero-content"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="v4-eyebrow">
            <Sparkles size={15} />
            THE NEXT GENERATION OF LINK INTELLIGENCE
          </div>

          <h1>
            THE INTERNET
            <br />
            HAS <span>SECRETS.</span>
            <br />
            WE FIND <em>CLUES.</em>
          </h1>

          <p className="v4-description">
            Behind every suspicious link is a story.
            Decode hidden risk signals, investigate
            suspicious patterns, and discover what
            your URL might be hiding.
          </p>

          <div className="v4-hero-actions">
            <a href="#v4-scanner" className="v4-primary-cta">
              START INVESTIGATING <ArrowUpRight size={19} />
            </a>
            <div className="v4-secondary-note">
              <ShieldCheck size={18} />
              PRIVATE. EXPLAINABLE. LOCAL-FIRST.
            </div>
          </div>
        </motion.div>

        <div className="v4-visual" aria-hidden="true">
          <div className="v4-visual-orbit orbit-a" />
          <div className="v4-visual-orbit orbit-b" />
          <div className="v4-visual-orbit orbit-c" />
          <div className="v4-visual-core">
            <Shield size={85} strokeWidth={1} />
          </div>
          <div className="v4-visual-label">
            <Crosshair size={15} />
            PHANTOM / INTELLIGENCE CORE
          </div>
        </div>

        <div className="v4-hero-bottom">
          <span>SCROLL TO INVESTIGATE</span>
          <span>PHANTOM SYSTEM / VERSION 04</span>
        </div>
      </section>

      <section className="v4-console-section" id="v4-scanner">
        <div className="v4-section-heading">
          <div>
            <span className="v4-section-kicker">
              <ScanLine size={15} /> THE INVESTIGATION LAB
            </span>
            <h2>Got a suspicious link?</h2>
            <p>Drop it below. Let's uncover the signals.</p>
          </div>
          <span className="v4-console-index">01 / INVESTIGATE</span>
        </div>

        <div className="v4-console">
          <div className="v4-console-top">
            <div className="v4-console-leds">
              <span /><span /><span />
            </div>
            <span>PHANTOM TERMINAL — OFFLINE HEURISTIC</span>
            <span><Activity size={14} /> READY</span>
          </div>

          <form
            className="v4-scan-form"
            onSubmit={(event) => event.preventDefault()}
          >
            <div className="v4-scan-field">
              <Globe2 size={22} />
              <input
                type="text"
                aria-label="URL to investigate"
                placeholder="Paste a suspicious URL here..."
                value={url}
                onChange={(event) => setUrl(event.target.value)}
              />
            </div>

            <button type="submit" disabled={!url.trim()}>
              INITIATE SCAN <ArrowRight size={19} />
            </button>
          </form>

          <div className="v4-console-bottom">
            <span><LockKeyhole size={14} /> No website content is fetched</span>
            <span><Search size={14} /> Structural URL analysis</span>
          </div>
        </div>
      </section>

      <section className="v4-capabilities">
        <div className="v4-capability">
          <span>01 / DETECT</span>
          <ScanLine size={27} />
          <h3>Spot the signals.</h3>
          <p>Identify suspicious URL patterns and structural anomalies.</p>
        </div>

        <div className="v4-capability">
          <span>02 / UNDERSTAND</span>
          <Activity size={27} />
          <h3>Know the reason.</h3>
          <p>Explore explainable risk indicators behind every score.</p>
        </div>

        <div className="v4-capability">
          <span>03 / REMEMBER</span>
          <ShieldCheck size={27} />
          <h3>Track the evidence.</h3>
          <p>Review investigation records in local history.</p>
        </div>
      </section>

      <footer className="v4-footer">
        <span>PHANTOMLINK © 2026</span>
        <span>QUESTION EVERY LINK. TRUST THE EVIDENCE.</span>
      </footer>
    </main>
  );
}
