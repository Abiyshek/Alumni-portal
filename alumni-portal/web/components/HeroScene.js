"use client";

// Three.js hero background: a calm field of light-blue dots rolling like the sea at Kalapet.
import { Canvas, useFrame } from "@react-three/fiber";
import { useEffect, useMemo, useRef, useState } from "react";

const COLS = 120;
const ROWS = 46;
const GAP = 0.32;

function Waves() {
  const geo = useRef();
  const base = useMemo(() => {
    const arr = new Float32Array(COLS * ROWS * 3);
    let i = 0;
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        arr[i++] = (c - COLS / 2) * GAP;
        arr[i++] = 0;
        arr[i++] = (r - ROWS / 2) * GAP;
      }
    }
    return arr;
  }, []);
  const positions = useMemo(() => base.slice(), [base]);

  useFrame(({ clock }) => {
    const t = clock.elapsedTime * 0.55;
    const pos = geo.current.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = base[i * 3];
      const z = base[i * 3 + 2];
      pos.array[i * 3 + 1] = Math.sin(x * 0.45 + t) * 0.28 + Math.cos(z * 0.6 + t * 0.8) * 0.22;
    }
    pos.needsUpdate = true;
  });

  return (
    <points rotation={[0.18, 0, 0]}>
      <bufferGeometry ref={geo}>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.045} color="#1d5bc4" sizeAttenuation transparent opacity={0.42} depthWrite={false} />
    </points>
  );
}

export default function HeroScene() {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    setReduced(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }, []);

  return (
    <Canvas
      camera={{ position: [0, 3.2, 9], fov: 55 }}
      onCreated={({ camera }) => camera.lookAt(0, -1.2, 0)}
      dpr={[1, 1.5]}
      gl={{ antialias: true, alpha: true }}
      flat
      frameloop={reduced ? "demand" : "always"}
      aria-hidden="true"
    >
      <group position={[0, -2.4, 0]}>
        <Waves />
      </group>
    </Canvas>
  );
}
