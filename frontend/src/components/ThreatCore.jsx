import { motion } from "motion/react";
import { ShieldAlert, Radar } from "lucide-react";
import "./ThreatCore.css";

const themes = {
  IDLE: { color: "#9b7bff", label: "SYSTEM STANDBY" },
  LOW: { color: "#a3e635", label: "LOW RISK" },
  MEDIUM: { color: "#fbbf24", label: "MEDIUM RISK" },
  HIGH: { color: "#fb5b83", label: "HIGH RISK" },
};

export default function ThreatCore({
  riskLevel = "IDLE",
  score = null,
  scanning = false,
}) {
  const theme = themes[riskLevel] || themes.IDLE;

  return (
    <div
      className="threat-core"
      style={{ "--threat-color": theme.color }}
    >
      <div className="core-topline">
        <span><Radar size={15} /> LIVE THREAT CORE</span>
        <span className="core-signal">
          <span className="core-signal-dot" />
          {scanning ? "ANALYZING" : "ENGINE READY"}
        </span>
      </div>

      <div className="core-stage">
        <div className="core-glow" />
        <div className="core-crosshair core-crosshair-h" />
        <div className="core-crosshair core-crosshair-v" />

        <motion.div
          className="core-ring core-ring-outer"
          animate={{ rotate: 360 }}
          transition={{
            duration: 30,
            repeat: Infinity,
            ease: "linear",
          }}
        />

        <motion.div
          className="core-ring core-ring-middle"
          animate={{ rotate: -360 }}
          transition={{
            duration: 22,
            repeat: Infinity,
            ease: "linear",
          }}
        />

        <motion.div
          className="core-ring core-ring-inner"
          animate={{ rotate: 360 }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "linear",
          }}
        />

        <motion.div
          className="core-center"
          animate={{
            scale: scanning ? [1, 1.08, 1] : 1,
          }}
          transition={{
            duration: 1.4,
            repeat: scanning ? Infinity : 0,
          }}
        >
          <ShieldAlert size={37} strokeWidth={1.4} />

          <strong>
            {scanning
              ? "..."
              : score === null
                ? "READY"
                : score}
          </strong>

          <small>{scanning ? "SCANNING" : theme.label}</small>
        </motion.div>

        <div className="core-orbit-dot" />
      </div>

      <div className="core-footer">
        <span>PHANTOMLINK / INTELLIGENCE ENGINE</span>
        <span>{scanning ? "PROCESSING" : "OFFLINE MODE"}</span>
      </div>
    </div>
  );
}
