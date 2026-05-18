"use client";

// v9 W1 — Hero view. Producer 2026-05-17 night:
//   #9  Live Cams + Operations should be HERO SCREEN
//   #11 Map should be small + reference, not center
//   #13 Main screen "feels like a boring dashboard"
//   #15 Communicate business model, impact, revolutionary tool
//
// Layout:
//   ┌─────────────────────────────────────────────────────┬──────────────┐
//   │                                                     │  Mini-map    │
//   │         LIVE WILDLIFE CAMS (2x2 grid)               │  (compact)   │
//   │                                                     ├──────────────┤
//   │         center of attention                         │  Incidents   │
//   │                                                     │  (last 2)    │
//   │                                                     ├──────────────┤
//   │                                                     │  Peer chips  │
//   ├─────────────────────────────────────────────────────┴──────────────┤
//   │  NARRATION STRIP — rotating business model + live protocol chips    │
//   └─────────────────────────────────────────────────────────────────────┘
//
// Existing tabs (Operations / Live Cams / Mission Bridge) stay accessible
// via the TabStrip. Hero is the new default landing surface.

import dynamic from "next/dynamic";
import { Radio } from "lucide-react";

import LiveCams from "@/components/LiveCams";
import NarrationStrip from "@/components/NarrationStrip";
import IncidentPanel, { type ActiveIncident } from "@/components/IncidentPanel";
import type { GuardianEvent } from "@/types/events";

const ReserveMap = dynamic(() => import("@/components/ReserveMap"), { ssr: false });

interface Props {
  events: GuardianEvent[];
  incidents: ActiveIncident[];
  activeReserveId: string | null;
  fanOutFiring: boolean;
  activePeers: string[];
}

const PEERS = [
  { id: "park_service", label: "Park Service", org: "Dar es Salaam · TZ" },
  { id: "sponsor_sustainability", label: "Sponsor", org: "London · F500" },
  { id: "funder_reporter", label: "Funder Reporter", org: "Geneva · CH" },
  { id: "neighbor_park", label: "Neighbor Park", org: "Maasai Mara · KE" },
];

export default function Hero({
  events,
  incidents,
  activeReserveId,
  fanOutFiring,
  activePeers,
}: Props) {
  const recentIncidents = incidents.slice(-2);

  return (
    <div className="flex-1 min-h-0 flex flex-col">
      <div className="flex-1 min-h-0 grid grid-cols-[1fr_320px]">
        {/* Center: real wildlife cam grid — this is the HERO */}
        <div className="min-h-0 border-r border-white/[0.06]">
          <LiveCams />
        </div>
        {/* Right rail: compact map · recent incidents · peer chips */}
        <aside className="min-h-0 flex flex-col bg-black">
          <div className="h-[260px] relative shrink-0 border-b border-white/[0.06]">
            <ReserveMap
              activeReserveId={activeReserveId}
              fanOutFiring={fanOutFiring}
              activePeers={activePeers}
            />
            <div
              className="absolute top-2 left-2 px-2 py-0.5 rounded-full text-[9.5px] uppercase tracking-[0.16em] font-mono pointer-events-none"
              style={{
                background: "rgba(0,0,0,0.55)",
                border: "1px solid rgba(245,158,11,0.35)",
                color: "rgb(252,211,77)",
                textShadow: "0 0 6px rgba(245,158,11,0.45)",
              }}
            >
              MISSION MAP
            </div>
          </div>
          <div className="flex-1 min-h-0 overflow-hidden">
            {recentIncidents.length > 0 ? (
              <IncidentPanel incidents={recentIncidents} />
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-zinc-600 text-xs gap-2 px-4 text-center">
                <Radio className="w-5 h-5" strokeWidth={1.4} />
                <span>Listening for live signals across 4 wildlife cams.</span>
                <span className="text-[10px] text-zinc-700">
                  Click <span className="text-zinc-400">Spot Now</span> on any tile.
                </span>
              </div>
            )}
          </div>
          <div className="px-3 py-2 border-t border-white/[0.06] shrink-0">
            <div className="text-[9px] uppercase tracking-[0.18em] text-zinc-500 font-mono mb-1.5">
              A2A v0.3 peers
            </div>
            <div className="grid grid-cols-2 gap-1.5">
              {PEERS.map((p) => {
                const active = activePeers.includes(p.id);
                return (
                  <div
                    key={p.id}
                    className="px-2 py-1.5 rounded-md text-[10px] leading-tight font-mono transition-colors"
                    style={{
                      background: active
                        ? "rgba(16,185,129,0.12)"
                        : "rgba(255,255,255,0.025)",
                      border: active
                        ? "1px solid rgba(16,185,129,0.5)"
                        : "1px solid rgba(255,255,255,0.05)",
                      color: active ? "rgb(167,243,208)" : "rgb(161,161,170)",
                      boxShadow: active
                        ? "0 0 12px rgba(16,185,129,0.20)"
                        : "none",
                    }}
                  >
                    <div className="font-semibold">{p.label}</div>
                    <div className="text-[9px] opacity-70">{p.org}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </aside>
      </div>
      <NarrationStrip events={events} />
    </div>
  );
}
