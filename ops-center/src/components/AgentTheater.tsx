"use client";

// PLAN_V3_2 sub-move 7.3 — Agent Theater tab. The producer's most-requested
// visual: "a special place where we can see the agents interacting in a
// visual way." 10 Imagen 4 portraits center-stage at 160px, with speech
// bubbles and ElevenLabs voice playback walking through the scenario flow.
// Falsifier gets stage-right counter-position to dramatize the
// counter-agent role.

import { useEffect, useRef, useState } from "react";

interface AgentSpec {
  id: string;
  name: string;
  portrait: string;
  voiceFile: string;
  intro: string;
  position: "orchestrator" | "specialist" | "adversary" | "peer";
}

const AGENTS: AgentSpec[] = [
  {
    id: "root_agent",
    name: "Orchestrator",
    portrait: "/portraits/root_agent.png",
    voiceFile: "/voices/intro-root_agent.mp3",
    intro: "I route signals to specialists and coordinate the dispatch.",
    position: "orchestrator",
  },
  {
    id: "stream_watcher",
    name: "Stream Watcher",
    portrait: "/portraits/stream_watcher.png",
    voiceFile: "/voices/intro-stream_watcher.mp3",
    intro: "I analyze camera feeds in real time and flag threats.",
    position: "specialist",
  },
  {
    id: "audio_agent",
    name: "Audio Agent",
    portrait: "/portraits/audio_agent.png",
    voiceFile: "/voices/intro-audio_agent.mp3",
    intro: "I classify gunshots, vehicle engines, distress calls.",
    position: "specialist",
  },
  {
    id: "species_id",
    name: "Species ID",
    portrait: "/portraits/species_id.png",
    voiceFile: "/voices/intro-species_id.mp3",
    intro: "I identify species and ground findings in the corpus.",
    position: "specialist",
  },
  {
    id: "court_evidence",
    name: "Court Evidence",
    portrait: "/portraits/court_evidence.png",
    voiceFile: "/voices/intro-court_evidence.mp3",
    intro: "I package every action into chain-of-custody for the auditor.",
    position: "specialist",
  },
  {
    id: "falsifier",
    name: "Falsifier",
    portrait: "/portraits/falsifier.png",
    voiceFile: "/voices/intro-falsifier.mp3",
    intro: "I challenge every dispatch. Dissent ships in the audit trail.",
    position: "adversary",
  },
  {
    id: "park_service",
    name: "Park Service",
    portrait: "/portraits/park_service.png",
    voiceFile: "",
    intro: "External A2A peer · ranger dispatch authority.",
    position: "peer",
  },
  {
    id: "sponsor_sustainability",
    name: "Sponsor Sustainability",
    portrait: "/portraits/sponsor_sustainability.png",
    voiceFile: "",
    intro: "External A2A peer · F500 TNFD filer.",
    position: "peer",
  },
  {
    id: "funder_reporter",
    name: "Funder Reporter",
    portrait: "/portraits/funder_reporter.png",
    voiceFile: "",
    intro: "External A2A peer · conservation impact issuer.",
    position: "peer",
  },
  {
    id: "neighbor_park",
    name: "Neighbor Park",
    portrait: "/portraits/neighbor_park.png",
    voiceFile: "",
    intro: "External A2A peer · cross-border mutual aid.",
    position: "peer",
  },
];

function AgentBadge({
  agent,
  active,
  onClick,
}: {
  agent: AgentSpec;
  active: boolean;
  onClick: () => void;
}) {
  const ring = {
    orchestrator: "ring-amber-500/60 shadow-[0_0_30px_rgba(245,158,11,0.4)]",
    specialist: "ring-sky-500/60 shadow-[0_0_22px_rgba(14,165,233,0.4)]",
    adversary: "ring-rose-500/70 shadow-[0_0_28px_rgba(244,63,94,0.45)]",
    peer: "ring-emerald-500/50 shadow-[0_0_18px_rgba(16,185,129,0.32)]",
  }[agent.position];
  return (
    <button
      onClick={onClick}
      className={`group flex flex-col items-center gap-2 transition-all duration-300 ${
        active ? "scale-110" : "scale-100 hover:scale-105 opacity-85 hover:opacity-100"
      }`}
    >
      <div
        className={`relative rounded-full overflow-hidden ring-2 ${ring} ${
          active ? "ring-offset-2 ring-offset-black" : ""
        }`}
        style={{ width: 132, height: 132 }}
      >
        <img
          src={agent.portrait}
          alt={agent.name}
          className="w-full h-full object-cover"
        />
        {active && (
          <div
            className="absolute inset-0 animate-pulse"
            style={{
              boxShadow: "inset 0 0 30px rgba(255,255,255,0.15)",
            }}
          />
        )}
      </div>
      <div className="text-center">
        <div
          className={`text-[12px] font-semibold uppercase tracking-[0.08em] ${
            active ? "text-white" : "text-zinc-300"
          }`}
        >
          {agent.name}
        </div>
        <div className="text-[9px] uppercase tracking-wider text-zinc-500">
          {agent.position === "adversary"
            ? "counter-agent"
            : agent.position === "peer"
            ? "a2a peer"
            : agent.position === "orchestrator"
            ? "root agent"
            : "specialist"}
        </div>
      </div>
    </button>
  );
}

export default function AgentTheater() {
  const [activeId, setActiveId] = useState<string>("root_agent");
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const active = AGENTS.find((a) => a.id === activeId) ?? AGENTS[0];

  // Play voice when active agent changes
  useEffect(() => {
    if (!audioRef.current) return;
    if (active.voiceFile) {
      audioRef.current.src = active.voiceFile;
      audioRef.current.currentTime = 0;
      audioRef.current.play().catch(() => {
        // Autoplay may be blocked until first user gesture; ignore.
      });
    }
  }, [activeId, active.voiceFile]);

  // Auto-walk through orchestrator → specialists → falsifier on mount
  useEffect(() => {
    const sequence = ["root_agent", "stream_watcher", "audio_agent", "species_id", "falsifier"];
    let idx = 0;
    const tick = () => {
      idx = (idx + 1) % sequence.length;
      setActiveId(sequence[idx]);
    };
    const interval = setInterval(tick, 7000);
    return () => clearInterval(interval);
  }, []);

  const specialists = AGENTS.filter((a) => a.position === "specialist");
  const orchestrator = AGENTS.find((a) => a.position === "orchestrator")!;
  const adversary = AGENTS.find((a) => a.position === "adversary")!;
  const peers = AGENTS.filter((a) => a.position === "peer");

  return (
    <div className="h-full overflow-hidden bg-black flex flex-col">
      <audio ref={audioRef} preload="auto" />

      <div className="px-6 py-3 border-b border-zinc-900 flex items-baseline justify-between">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-[0.15em] text-zinc-200">
            Agent Theater
          </h2>
          <p className="text-[11px] text-zinc-500 mt-0.5">
            Click any agent to hear them introduce themselves · 5-agent core + Falsifier counter-stage + 4 A2A peers
          </p>
        </div>
        <div className="text-[10px] text-zinc-500 font-mono">
          Imagen 4 portraits · ElevenLabs narration · click cycles auto every 7s
        </div>
      </div>

      <div className="flex-1 px-12 py-8 grid grid-rows-[auto_1fr_auto] gap-6 min-h-0">
        {/* Orchestrator on top */}
        <div className="flex justify-center">
          <AgentBadge
            agent={orchestrator}
            active={activeId === orchestrator.id}
            onClick={() => setActiveId(orchestrator.id)}
          />
        </div>

        {/* Center stage: speech bubble */}
        <div className="flex items-center justify-center">
          <div className="relative max-w-2xl">
            <div
              className="px-8 py-6 rounded-2xl backdrop-blur"
              style={{
                background: "rgba(24, 24, 27, 0.7)",
                border: "1px solid rgba(255,255,255,0.08)",
                boxShadow: "0 30px 80px rgba(0,0,0,0.5)",
              }}
            >
              <div className="text-[11px] uppercase tracking-[0.15em] text-zinc-500 mb-2">
                {active.name} {active.id === "falsifier" ? "· counter-agent" : ""}
              </div>
              <p className="text-2xl text-zinc-100 leading-snug font-light">
                "{active.intro}"
              </p>
              {active.voiceFile && (
                <div className="mt-4 flex items-center gap-2 text-[10px] text-zinc-500">
                  <span
                    className="w-1.5 h-1.5 rounded-full animate-pulse"
                    style={{ backgroundColor: "#34d399" }}
                  />
                  Voice via ElevenLabs · click any agent to replay
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Bottom row: specialists left + Falsifier right (adversary counter-stage) */}
        <div className="grid grid-cols-[1fr_auto_1fr] gap-8 items-end">
          <div className="flex flex-wrap gap-6 justify-end items-end">
            {specialists.map((a) => (
              <AgentBadge
                key={a.id}
                agent={a}
                active={activeId === a.id}
                onClick={() => setActiveId(a.id)}
              />
            ))}
          </div>
          <div className="border-l border-zinc-800 h-32 mx-2"></div>
          <div className="flex flex-wrap gap-6 items-end">
            <AgentBadge
              agent={adversary}
              active={activeId === adversary.id}
              onClick={() => setActiveId(adversary.id)}
            />
          </div>
        </div>
      </div>

      {/* Peer rail */}
      <div className="px-12 py-3 border-t border-zinc-900 bg-zinc-950/40">
        <div className="flex items-center gap-6">
          <div className="text-[10px] uppercase tracking-[0.15em] text-zinc-500 flex-shrink-0">
            A2A peers · external orgs
          </div>
          <div className="flex gap-4 overflow-x-auto">
            {peers.map((a) => (
              <button
                key={a.id}
                onClick={() => setActiveId(a.id)}
                className="flex items-center gap-2 px-2 py-1 rounded hover:bg-white/5"
              >
                <img
                  src={a.portrait}
                  alt={a.name}
                  className={`w-7 h-7 rounded-full object-cover ring-1 ${
                    activeId === a.id ? "ring-emerald-400" : "ring-emerald-500/40"
                  }`}
                />
                <span className="text-[11px] text-zinc-300 whitespace-nowrap">
                  {a.name}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
