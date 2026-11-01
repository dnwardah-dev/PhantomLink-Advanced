import { motion } from "motion/react";
import { Link } from "react-router-dom";
import {
  ArrowUpRight,
  Fingerprint,
  ShieldCheck,
  Crosshair,
} from "lucide-react";

import { lazy, Suspense } from "react";

const UniverseCanvas = lazy(
  () => import("../components/UniverseCanvas")
);
import "../styles/underworld.css";

export default function UnderworldHome() {
  return (
    <div className="v5-app">
      <main>
        <section className="v5-hero" id="home">
          <div className="v5-grid-overlay" aria-hidden="true" />

          <motion.div
            className="v5-hero-copy"
            initial={{ opacity: 0, y: 35 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="v5-kicker">
              <Crosshair size={15} />
              DIGITAL FORENSICS / NEXT GENERATION
            </div>

            <h1>
              EVERY LINK
              <br />
              HAS A <span>SHADOW.</span>
            </h1>

            <p>
              Enter the digital underworld. Uncover suspicious
              URL patterns, investigate risk indicators,
              and understand the clues behind every link.
            </p>

            <div className="v5-hero-actions">
              <Link to="/investigate" className="v5-cta">
                ENTER INVESTIGATION
                <ArrowUpRight size={19} />
              </Link>

              <span className="v5-privacy-note">
                <ShieldCheck size={17} />
                URL HEURISTICS + DNS LOOKUP
              </span>
            </div>
          </motion.div>

          <motion.div
            className="v5-universe-wrapper"
            initial={{ opacity: 0, scale: 0.85 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1.2, delay: 0.2 }}
          >
            <Suspense
              fallback={
                <div
                  className="v5-universe-canvas"
                  role="status"
                  aria-label="Loading 3D universe"
                >
                  <div
                    className="v5-universe-glow"
                    aria-hidden="true"
                  />
                </div>
              }
            >
              <UniverseCanvas />
            </Suspense>
          </motion.div>

          <div className="v5-hero-footer">
            <span>PHANTOMLINK / DIGITAL UNDERWORLD</span>
            <span>INTERACTIVE THREAT UNIVERSE</span>
          </div>
        </section>
      </main>
    </div>
  );
}
