"use client";

// PLAN_V3_2 sub-move 7.2 — Live Cams tab. 2×2 grid of Veo-rendered
// wildlife clips with IR-style overlays. When Veo files aren't yet
// present (still rendering in background), tiles show a placeholder.
//
// Producer's "fake-staged live cams showing videos of animals" ask.

import { useRef } from "react";

interface CamProps {
  id: string;
  label: string;
  src: string;
  subtitle: string;
  accent: string;
}

const CAMS: CamProps[] = [
  {
    id: "elephant-dusk",
    label: "CAM-12 · Selous · NW Sector",
    src: "/cams/elephant-dusk.mp4",
    subtitle: "African elephant herd · dusk patrol",
    accent: "#10b981",
  },
  {
    id: "cheetah-crossing",
    label: "CAM-07 · Etosha · F-14 fenceline",
    src: "/cams/cheetah-crossing.mp4",
    subtitle: "Cheetah crossing · IUCN Vulnerable",
    accent: "#f59e0b",
  },
  {
    id: "vehicle-night",
    label: "CAM-22 · Serengeti · Tag-22 corridor",
    src: "/cams/vehicle-night.mp4",
    subtitle: "Vehicle approach · night IR",
    accent: "#f43f5e",
  },
  {
    id: "trap-perspective",
    label: "CAM-04 · Maasai Mara · Border",
    src: "/cams/trap-perspective.mp4",
    subtitle: "Camera trap · dawn ambient",
    accent: "#0ea5e9",
  },
];

function CamTile({ cam }: { cam: CamProps }) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  return (
    <div
      className="relative rounded-lg overflow-hidden border bg-black"
      style={{ borderColor: `${cam.accent}40` }}
    >
      <video
        ref={videoRef}
        src={cam.src}
        autoPlay
        loop
        muted
        playsInline
        className="w-full h-full object-cover"
        onError={() => {
          // Veo asset not yet on disk; the placeholder backdrop is fine.
        }}
      />
      {/* IR overlay vignette */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(circle at 50% 50%, transparent 60%, rgba(0,0,0,0.55) 100%)",
        }}
      />
      {/* Top-left tag */}
      <div className="absolute top-2 left-2 flex items-center gap-1.5">
        <div
          className="w-1.5 h-1.5 rounded-full animate-pulse"
          style={{ backgroundColor: cam.accent }}
        />
        <div className="text-[9px] font-mono text-white/85 tracking-[0.05em]">
          {cam.label}
        </div>
      </div>
      {/* Top-right LIVE */}
      <div className="absolute top-2 right-2 text-[9px] font-mono text-rose-400 uppercase tracking-wider">
        ● live
      </div>
      {/* Bottom subtitle */}
      <div className="absolute bottom-0 left-0 right-0 px-3 py-2 bg-gradient-to-t from-black via-black/70 to-transparent">
        <div
          className="text-[10px] uppercase tracking-wider font-semibold"
          style={{ color: cam.accent }}
        >
          {cam.subtitle}
        </div>
      </div>
    </div>
  );
}

export default function LiveCams() {
  return (
    <div className="h-full overflow-hidden bg-black flex flex-col">
      <div className="px-6 py-3 border-b border-zinc-900 flex items-baseline justify-between">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-[0.15em] text-zinc-200">
            Live Field Cameras
          </h2>
          <p className="text-[11px] text-zinc-500 mt-0.5">
            Veo 3.1 Fast generated · 6s loops · what the Stream Watcher & Audio Agent see in production
          </p>
        </div>
        <div className="text-[10px] text-zinc-500 font-mono">
          4 of 187 sponsored-reserve cameras shown
        </div>
      </div>
      <div className="flex-1 p-4 grid grid-cols-2 grid-rows-2 gap-4 min-h-0">
        {CAMS.map((cam) => (
          <CamTile key={cam.id} cam={cam} />
        ))}
      </div>
      <div className="px-6 py-2 border-t border-zinc-900 text-[10px] text-zinc-500 flex items-center justify-between">
        <span>
          Generated via{" "}
          <span className="text-zinc-300">Veo 3.1 Fast</span>{" "}
          (Vertex AI) · audio-off · 16:9 1080p · indistinguishable from a real
          camera-trap stream in the demo loop
        </span>
        <span className="font-mono">$0.60/clip · $2.40 total</span>
      </div>
    </div>
  );
}
