import { useMemo, useRef, useState, useEffect } from "react";
import { useFrame } from "@react-three/fiber";
import { Float, OrbitControls } from "@react-three/drei";
import * as THREE from "three";

function NetworkGlobe({ reduceMotion = false }) {
  const group = useRef();

  const { nodes, edges } = useMemo(() => {
    const nodes = [];
    const edges = [];
    const count = 95;
    const radius = 2.15;
    const goldenAngle = Math.PI * (3 - Math.sqrt(5));

    for (let i = 0; i < count; i++) {
      const y = 1 - (i / (count - 1)) * 2;
      const radial = Math.sqrt(1 - y * y);
      const angle = goldenAngle * i;

      nodes.push(new THREE.Vector3(
        Math.cos(angle) * radial * radius,
        y * radius,
        Math.sin(angle) * radial * radius
      ));
    }

    for (let i = 0; i < nodes.length; i++) {
      const nearest = nodes
        .map((node, j) => ({
          j,
          distance: nodes[i].distanceToSquared(node),
        }))
        .filter((item) => item.j !== i)
        .sort((a, b) => a.distance - b.distance)
        .slice(0, 3);

      nearest.forEach(({ j }) => {
        if (i < j) edges.push(nodes[i], nodes[j]);
      });
    }

    return { nodes, edges };
  }, []);

  const positions = useMemo(
    () => new Float32Array(nodes.flatMap((node) => node.toArray())),
    [nodes]
  );

  const linePositions = useMemo(
    () => new Float32Array(edges.flatMap((point) => point.toArray())),
    [edges]
  );

  useFrame((_, delta) => {
    if (group.current && !reduceMotion) {
      group.current.rotation.y += delta * 0.055;
    }
  });

  return (
    <group ref={group}>
      <mesh>
        <sphereGeometry args={[2.03, 48, 48]} />
        <meshBasicMaterial
          color="#302063"
          transparent
          opacity={0.085}
          depthWrite={false}
        />
      </mesh>

      <lineSegments>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[linePositions, 3]}
          />
        </bufferGeometry>
        <lineBasicMaterial
          color="#806bdf"
          transparent
          opacity={0.36}
          depthWrite={false}
        />
      </lineSegments>

      <points>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[positions, 3]}
          />
        </bufferGeometry>
        <pointsMaterial
          color="#7ceaff"
          size={0.055}
          sizeAttenuation
          transparent
          opacity={0.95}
          depthWrite={false}
        />
      </points>

      <mesh rotation={[0.3, 0, 0.4]}>
        <torusGeometry args={[2.38, 0.006, 8, 160]} />
        <meshBasicMaterial color="#b29cff" transparent opacity={0.5} />
      </mesh>

      <mesh rotation={[1.2, 0.7, 0]}>
        <torusGeometry args={[2.55, 0.004, 8, 160]} />
        <meshBasicMaterial color="#46d9ee" transparent opacity={0.35} />
      </mesh>
    </group>
  );
}

export default function ThreatUniverse() {
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    );

    const updatePreference = () => {
      setReduceMotion(media.matches);
    };

    updatePreference();
    media.addEventListener("change", updatePreference);

    return () => {
      media.removeEventListener("change", updatePreference);
    };
  }, []);

  return (
    <>
      <ambientLight intensity={0.6} />
      <Float
        speed={reduceMotion ? 0 : 1.2}
        rotationIntensity={reduceMotion ? 0 : 0.08}
        floatIntensity={reduceMotion ? 0 : 0.2}
      >
        <NetworkGlobe reduceMotion={reduceMotion} />
      </Float>
      <OrbitControls
        enablePan={false}
        enableZoom={false}
        autoRotate={false}
      />
    </>
  );
}
