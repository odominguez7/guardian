"use client";

// v5 — Mission Bridge (renamed + rebuilt from v3.2 Agent Theater).
// Circular topology of the GUARDIAN multi-agent system:
//
//                    [Neighbor]         [Sponsor]
//                          \              /
//                           \  [Stream]  /
//                            \    |    /
//                       [Court]--[O]--[Audio]    O = orchestrator
//                            /    |    \
//                           /  [Species] \         Falsifier sits as
//                          /              \        counter-stage upper-right
//                    [Funder]            [Park]
//
// Active connection lines pulse from the orchestrator to whichever agent
// is currently active. Falsifier's connection line goes amber→rose when
// the verdict is dissent, matching the IncidentPanel tribunal chip.
//
// Producer feedback (2026-05-17): the prior Agent Theater scored 6/10
// because it was a static grid of portraits. This rebuild puts the agents
// on a single visual stage with real topology + live data flow lines.

import { useEffect, useMemo, useRef, useState } from "react";

type Position = "orchestrator" | "specialist" | "adversary" | "peer";

interface AgentSpec {
  id: string;
  name: string;
  portrait: string;
  voiceFile: string;
  intro: string;
  position: Position;
  // Percentage coordinates within the stage container [0-100].
  x: number;
  y: number;
  // Portrait diameter in px.
  size: number;
}

const AGENTS: AgentSpec[] = [
  // Center
  {
    id: "root_agent",
    name: "Orchestrator",
    portrait: "/portraits/root_agent.png",
    voiceFile: "/voices/intro-root_agent.mp3",
    intro: "I route signals to specialists and coordinate the dispatch.",
    position: "orchestrator",
    x: 50, y: 50, size: 116,
  },
  // Inner ring (specialists) — cardinal positions
  {
    id: "stream_watcher",
    name: "Stream Watcher",
    portrait: "/portraits/stream_watcher.png",
    voiceFile: "/voices/intro-stream_watcher.mp3",
    intro: "I analyze camera feeds in real time and flag threats.",
    position: "specialist",
    x: 50, y: 21, size: 92,
  },
  {
    id: "audio_agent",
    name: "Audio Agent",
    portrait: "/portraits/audio_agent.png",
    voiceFile: "/voices/intro-audio_agent.mp3",
    intro: "I classify gunshots, vehicle engines, distress calls.",
    position: "specialist",
    x: 79, y: 50, size: 92,
  },
  {
    id: "species_id",
    name: "Species ID",
    portrait: "/portraits/species_id.png",
    voiceFile: "/voices/intro-species_id.mp3",
    intro: "I identify species and ground findings in the IUCN/CITES corpus.",
    position: "specialist",
    x: 50, y: 79, size: 92,
  },
  {
    id: "court_evidence",
    name: "Court Evidence",
    portrait: "/portraits/court_evidence.png",
    voiceFile: "/voices/intro-court_evidence.mp3",
    intro: "I package every action into chain-of-custody for the auditor.",
    position: "specialist",
    x: 21, y: 50, size: 92,
  },
  // Falsifier — counter-stage, between Stream Watcher and Audio Agent,
  // ring colored rose so the adversarial role reads immediately.
  {
    id: "falsifier",
    name: "Falsifier",
    portrait: "/portraits/falsifier.png",
    voiceFile: "/voices/intro-falsifier.mp3",
    intro: "I challenge every dispatch. Dissent ships in the audit trail.",
    position: "adversary",
    x: 70, y: 28, size: 84,
  },
  // Outer ring (A2A peers) — corners
  {
    id: "neighbor_park",
    name: "Neighbor Park",
    portrait: "/portraits/neighbor_park.png",
    voiceFile: "",
    intro: "External A2A peer · cross-border mutual aid.",
    position: "peer",
    x: 12, y: 14, size: 70,
  },
  {
    id: "sponsor_sustainability",
    name: "Sponsor Sustainability",
    portrait: "/portraits/sponsor_sustainability.png",
    voiceFile: "",
    intro: "External A2A peer · F500 TNFD filer.",
    position: "peer",
    x: 91, y: 14, size: 70,
  },
  {
    id: "funder_reporter",
    name: "Funder Reporter",
    portrait: "/portraits/funder_reporter.png",
    voiceFile: "",
    intro: "External A2A peer · conservation impact issuer.",
    position: "peer",
    x: 12, y: 86, size: 70,
  },
  {
    id: "park_service",
    name: "Park Service",
    portrait: "/portraits/park_service.png",
    voiceFile: "",
    intro: "External A2A peer · ranger dispatch authority.",
    position: "peer",
    x: 91, y: 86, size: 70,
  },
];

const POSITION_STYLE: Record<Position, { ring: string; label: string; lineColor: string }> = {
  orchestrator: {
    ring: "ring-amber-500/70 shadow-[0_0_30px_rgba(245,158,11,0.5)]",
    label: "Root agent · Gemini 2.5 Pro",
    lineColor: "#f59e0b",
  },
  specialist: {
    ring: "ring-sky-500/60 shadow-[0_0_22px_rgba(14,165,233,0.4)]",
    label: "Specialist · Vertex AI",
    lineColor: "#0ea5e9",
  },
  adversary: {
    ring: "ring-rose-500/70 shadow-[0_0_24px_rgba(244,63,94,0.45)]",
    label: "Counter-agent · Falsifier",
    lineColor: "#f43f5e",
  },
  peer: {
    ring: "ring-emerald-500/55 shadow-[0_0_18px_rgba(16,185,129,0.32)]",
    label: "A2A peer · external org",
    lineColor: "#10b981",
  },
};

function AgentBadge({
  agent,
  active,
  onClick,
}: {
  agent: AgentSpec;
  active: boolean;
  onClick: () => void;
}) {
  const style = POSITION_STYLE[agent.position];
  return (
    <button
      onClick={onClick}
      className="absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-1.5 transition-transform duration-300"
      style={{
        left: `${agent.x}%`,
        top: `${agent.y}%`,
        transform: `translate(-50%, -50%) scale(${active ? 1.12 : 1})`,
        zIndex: active ? 30 : agent.position === "orchestrator" ? 20 : 10,
      }}
    >
      <div
        className={`relative rounded-full overflow-hidden ring-2 ${style.ring} ${
          active ? "ring-offset-2 ring-offset-black" : ""
        }`}
        style={{ width: agent.size, height: agent.size }}
      >
        <img
          src={agent.portrait}
          alt={agent.name}
          className="w-full h-full object-cover"
        />
        {active && (
          <div
            className="absolute inset-0 animate-pulse"
            style={{ boxShadow: "inset 0 0 30px rgba(255,255,255,0.18)" }}
          />
        )}
      </div>
      <div className="text-center">
        <div className={`text-[11px] font-semibold uppercase tracking-[0.08em] ${active ? "text-white" : "text-zinc-300"}`}>
          {agent.name}
        </div>
        <div className="text-[8.5px] uppercase tracking-wider text-zinc-500">
          {style.label}
        </div>
      </div>
    </button>
  );
}

interface MissionBridgeProps {
  /** v6: optional live Falsifier verdict driven by the latest incident.
   *  When present + verdict !== "concur", the Falsifier line color shifts
   *  from sky-blue to rose during the active window. */
  falsifierVerdict?: "concur" | "dissent" | "abstain" | null;
}

export default function MissionBridge({ falsifierVerdict }: MissionBridgeProps = {}) {
  const [activeId, setActiveId] = useState<string>("root_agent");
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const active = AGENTS.find((a) => a.id === activeId) ?? AGENTS[0];
  const orchestrator = useMemo(() => AGENTS.find((a) => a.position === "orchestrator")!, []);

  useEffect(() => {
    if (!audioRef.current) return;
    if (active.voiceFile) {
      audioRef.current.src = active.voiceFile;
      audioRef.current.currentTime = 0;
      audioRef.current.play().catch(() => undefined);
    }
  }, [activeId, active.voiceFile]);

  // Auto-walk: orchestrator → 4 specialists → falsifier → 4 peers, then loop.
  // v5 codex BLOCK fix: progression is now driven by audio `ended` (with a
  // 9.5s ceiling for clips that fail to load or peers with no voice). Prior
  // 4.5s setInterval cut narrations mid-sentence on the 6-12s clips.
  useEffect(() => {
    const sequence = [
      "root_agent",
      "stream_watcher",
      "audio_agent",
      "species_id",
      "court_evidence",
      "falsifier",
      "park_service",
      "sponsor_sustainability",
      "funder_reporter",
      "neighbor_park",
    ];
    const audio = audioRef.current;
    let cancelled = false;
    let safetyTimer: ReturnType<typeof setTimeout> | null = null;
    const advance = () => {
      if (cancelled) return;
      setActiveId((cur) => {
        const idx = sequence.indexOf(cur);
        return sequence[(idx + 1) % sequence.length];
      });
    };
    const scheduleSafety = () => {
      if (safetyTimer) clearTimeout(safetyTimer);
      // Upper bound — used when audio.ended doesn't fire (no clip, autoplay
      // blocked, or peers with empty voiceFile). 9.5s covers the longest
      // clip we ship + a 500ms breath.
      safetyTimer = setTimeout(advance, 9500);
    };
    const onEnded = () => {
      if (safetyTimer) clearTimeout(safetyTimer);
      // Hold the speech bubble visible for a beat after the clip ends,
      // then advance. Feels less robotic than instant tick.
      safetyTimer = setTimeout(advance, 900);
    };
    if (audio) audio.addEventListener("ended", onEnded);
    scheduleSafety();
    return () => {
      cancelled = true;
      if (safetyTimer) clearTimeout(safetyTimer);
      if (audio) audio.removeEventListener("ended", onEnded);
    };
  }, [activeId]);

  // Pre-compute the SVG line endpoints (orchestrator → each non-orch agent).
  // Active line draws on top in white; rest in agent's own color at 30% opacity.
  const lines = useMemo(() => {
    return AGENTS.filter((a) => a.position !== "orchestrator").map((a) => {
      const isActive = a.id === activeId;
      const isFalsifierDissent = a.id === "falsifier" && falsifierVerdict && falsifierVerdict !== "concur";
      const color = isFalsifierDissent
        ? "#f43f5e"
        : POSITION_STYLE[a.position].lineColor;
      return {
        id: a.id,
        x1: orchestrator.x,
        y1: orchestrator.y,
        x2: a.x,
        y2: a.y,
        color,
        active: isActive,
        opacity: isActive ? 0.95 : 0.18,
        width: isActive ? 2 : 1,
      };
    });
  }, [activeId, orchestrator.x, orchestrator.y, falsifierVerdict]);

  return (
    <div className="h-full overflow-hidden bg-black flex flex-col">
      <audio ref={audioRef} preload="auto" />

      <div className="px-6 py-3 border-b border-zinc-900 flex items-baseline justify-between">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-[0.15em] text-zinc-200">
            Mission Bridge
          </h2>
          <p className="text-[11px] text-zinc-500 mt-0.5">
            10 agents on one stage · orchestrator center · 4 specialists ring · Falsifier counter-stage · 4 A2A peers outer ring
          </p>
        </div>
        <div className="text-[10px] text-zinc-500 font-mono">
          Imagen 4 portraits · ElevenLabs voice · clip-length pacing (≤9.5s) · click any badge to replay
        </div>
      </div>

      <div className="relative flex-1 min-h-0 flex items-center justify-center">
        {/* v5 codex WARN fix: stage held to square aspect so the circular
            topology stays circular on 16:9 viewports. The SVG and the badge
            layer share coordinates; viewBox + preserveAspectRatio="xMidYMid
            meet" stops the ellipse-distortion seen at deploy. */}
        <div
          className="relative"
          style={{
            width: "min(100%, calc(100vh - 220px))",
            aspectRatio: "1 / 1",
          }}
        >
        {/* SVG connection lines layer — below badges but above background */}
        <svg
          className="absolute inset-0 w-full h-full pointer-events-none"
          viewBox="0 0 100 100"
          preserveAspectRatio="xMidYMid meet"
          style={{ zIndex: 1 }}
        >
          {lines.map((l) => (
            <line
              key={l.id}
              x1={l.x1}
              y1={l.y1}
              x2={l.x2}
              y2={l.y2}
              stroke={l.color}
              strokeOpacity={l.opacity}
              strokeWidth={l.width}
              vectorEffect="non-scaling-stroke"
              strokeDasharray={l.active ? "0" : "1 2"}
            >
              {l.active && (
                <animate
                  attributeName="stroke-opacity"
                  values="0.45;1;0.45"
                  dur="1.2s"
                  repeatCount="indefinite"
                />
              )}
            </line>
          ))}
          {/* Background radial decoration for the stage center */}
          <circle cx={orchestrator.x} cy={orchestrator.y} r={3.2} fill="#f59e0b" opacity={0.05} />
        </svg>

        {/* Badges layer */}
        <div className="absolute inset-0" style={{ zIndex: 2 }}>
          {AGENTS.map((a) => (
            <AgentBadge
              key={a.id}
              agent={a}
              active={activeId === a.id}
              onClick={() => setActiveId(a.id)}
            />
          ))}
        </div>
        </div>
        {/* v5 codex BLOCK fix: speech bubble now lives in a side rail outside
            the topology, so it can never overlap a badge (prior bottom: 88
            collided with Species ID at y=79%). Anchored right on wide screens,
            collapses to a slim header on narrow ones. */}
        <aside
          className="hidden lg:flex absolute right-4 top-4 bottom-4 w-[320px] xl:w-[380px] flex-col gap-2"
          style={{ zIndex: 25 }}
        >
          <div
            className="px-5 py-4 rounded-2xl backdrop-blur"
            style={{
              background: "rgba(9, 9, 11, 0.82)",
              border: "1px solid rgba(255,255,255,0.08)",
              boxShadow: "0 30px 80px rgba(0,0,0,0.55)",
            }}
          >
            <div className="text-[10px] uppercase tracking-[0.15em] text-zinc-500 mb-1.5 flex items-baseline gap-2">
              <span>{active.name}</span>
              {active.id === "falsifier" && falsifierVerdict && falsifierVerdict !== "concur" && (
                <span className="ml-auto px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 ring-1 ring-rose-500/40 text-[9px] uppercase tracking-wider">
                  ● {falsifierVerdict}
                </span>
              )}
            </div>
            <div className="text-[10px] text-zinc-500 mb-2">
              {POSITION_STYLE[active.position].label}
            </div>
            <p className="text-base text-zinc-100 leading-snug font-light">
              "{active.intro}"
            </p>
            {active.voiceFile && (
              <div className="mt-3 flex items-center gap-2 text-[10px] text-zinc-500">
                <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: "#34d399" }} />
                Voice via ElevenLabs · click any badge to replay
              </div>
            )}
          </div>
        </aside>
      </div>

      {/* v5.2 codex WARN fix: render an inline narration strip on viewports
          where the right-side rail is hidden (< lg / 1024px). Same agent
          intro copy, compact form, doesn't overlap the topology. */}
      <div
        className="lg:hidden px-6 py-2 border-t border-zinc-900 bg-zinc-950/70 flex items-start gap-3"
      >
        <span className="text-[10px] uppercase tracking-[0.15em] text-zinc-400 font-semibold shrink-0 mt-0.5">
          {active.name}
        </span>
        <p className="text-[11px] text-zinc-200 leading-snug font-light">
          "{active.intro}"
        </p>
        {active.id === "falsifier" && falsifierVerdict && falsifierVerdict !== "concur" && (
          <span className="ml-auto px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 ring-1 ring-rose-500/40 text-[9px] uppercase tracking-wider shrink-0">
            ● {falsifierVerdict}
          </span>
        )}
      </div>

      {/* Bottom legend */}
      <div className="px-6 py-2 border-t border-zinc-900 bg-zinc-950/60 flex items-center gap-6 text-[10px] text-zinc-500">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-amber-500" />
          Orchestrator
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-sky-500" />
          Specialists × 4
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-rose-500" />
          Falsifier (counter-stage)
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          A2A peers × 4
        </span>
        <span className="ml-auto font-mono">
          10 agents · 1 stage · {falsifierVerdict && falsifierVerdict !== "concur" ? `Falsifier ${falsifierVerdict}` : "idle"}
        </span>
      </div>
    </div>
  );
}
