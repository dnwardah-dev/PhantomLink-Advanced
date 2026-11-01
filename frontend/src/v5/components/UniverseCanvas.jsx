import { Suspense, useEffect, useState } from "react";
import { Canvas } from "@react-three/fiber";
import ThreatUniverse from "../scenes/ThreatUniverse";

export default function UniverseCanvas() {
  const [isVisible, setIsVisible] = useState(
    () => typeof document === "undefined"
      ? true
      : !document.hidden
  );

  useEffect(() => {
    const updateVisibility = () => {
      setIsVisible(!document.hidden);
    };

    document.addEventListener(
      "visibilitychange",
      updateVisibility
    );

    return () => {
      document.removeEventListener(
        "visibilitychange",
        updateVisibility
      );
    };
  }, []);

  return (
    <div className="v5-universe-canvas">
      <div className="v5-universe-glow" aria-hidden="true" />

      <Canvas
        frameloop={isVisible ? "always" : "never"}
        camera={{
          position: [0, 0, 7.5],
          fov: 45,
          near: 0.1,
          far: 100,
        }}
        dpr={[1, 1.5]}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: "low-power",
        }}
        fallback={
          <div className="v5-canvas-fallback">
            3D visualization unavailable
          </div>
        }
      >
        <Suspense fallback={null}>
          <ThreatUniverse />
        </Suspense>
      </Canvas>

      <div className="v5-universe-caption">
        <span className="v5-universe-dot" />
        PHANTOM NETWORK
        <span className="v5-universe-caption-divider">/</span>
        INTERACTIVE 3D
      </div>

      <div className="v5-universe-hint">
        DRAG TO ROTATE
      </div>
    </div>
  );
}
