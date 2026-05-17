"use client";

// Watch Dogs-style chase path overlay — PLAN_V3_1 sub-move 6.4.
// Sits at the bottom of the map column as an absolute-positioned strip.
// Shows the poacher truck closing distance to the elephant herd, the
// ranger unit intercepting. This is the 15-year-old's unlock: a literal
// red dot approaching a green dot, with the ranger sprite cutting in.
// Renders independent of Mapbox so the narrative reads even if WebGL
// fails / token is missing / headless capture is in use.

import { motion, AnimatePresence } from "framer-motion";
import type { ActiveIncident } from "./IncidentPanel";

interface Props {
  /** The most recent active incident; null when idle. */
  activeIncident: ActiveIncident | null;
}

function severityAccent(sev: string): { stroke: string; bg: string; glow: string } {
  switch (sev) {
    case "critical":
      return { stroke: "#f43f5e", bg: "rgba(244, 63, 94, 0.12)", glow: "0 0 24px rgba(244, 63, 94, 0.6)" };
    case "high":
      return { stroke: "#f59e0b", bg: "rgba(245, 158, 11, 0.12)", glow: "0 0 24px rgba(245, 158, 11, 0.5)" };
    case "medium":
      return { stroke: "#0ea5e9", bg: "rgba(14, 165, 233, 0.12)", glow: "0 0 18px rgba(14, 165, 233, 0.45)" };
    default:
      return { stroke: "#71717a", bg: "rgba(113, 113, 122, 0.1)", glow: "0 0 12px rgba(113, 113, 122, 0.3)" };
  }
}

export default function ChasePath({ activeIncident }: Props) {
  if (!activeIncident) {
    return (
      <div className="absolute bottom-0 left-0 right-0 h-32 px-8 py-4 bg-gradient-to-t from-black/95 via-black/60 to-transparent pointer-events-none">
        <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600 mb-2">Threat Vector · Standing By</div>
        <div className="h-px bg-zinc-800/80 mt-7" />
      </div>
    );
  }

  const accent = severityAccent(activeIncident.severity);
  const rangerDispatched = Boolean(activeIncident.ranger);
  const sponsorFiled = Boolean(activeIncident.tnfd);

  // Truck progress: empirically, ranger ack arrives ~8s into scenario.
  // Without ranger dispatch yet, the truck is approaching (60% closer).
  // With ranger dispatch, the truck is intercepted at 70% of the path.
  const truckProgress = rangerDispatched ? 0.7 : 0.55;
  const rangerProgress = rangerDispatched ? 0.72 : -0.1; // off-screen until dispatch

  return (
    <div className="absolute bottom-0 left-0 right-0 h-32 px-8 py-4 bg-gradient-to-t from-black/95 via-black/70 to-transparent pointer-events-none">
      {/* Header */}
      <div className="flex items-baseline justify-between mb-3">
        <div className="text-[10px] uppercase tracking-[0.2em]" style={{ color: accent.stroke }}>
          Threat Vector · {activeIncident.severity}
        </div>
        <div className="text-[10px] text-zinc-400 font-mono">
          {activeIncident.incident_id}
        </div>
      </div>

      {/* Path strip */}
      <div className="relative h-12">
        {/* dashed baseline */}
        <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none" viewBox="0 0 1000 48">
          <line
            x1="40"
            y1="24"
            x2="960"
            y2="24"
            stroke={accent.stroke}
            strokeWidth="1.5"
            strokeDasharray="6 8"
            opacity="0.7"
          />
        </svg>

        {/* Poacher truck — red diamond, advancing right */}
        <motion.div
          className="absolute top-0 -mt-1"
          initial={{ left: "4%" }}
          animate={{ left: `${4 + truckProgress * 75}%` }}
          transition={{ duration: 4.5, ease: "easeOut" }}
        >
          <div className="flex flex-col items-center">
            <div
              className="w-4 h-4 rotate-45"
              style={{
                backgroundColor: rangerDispatched ? "#71717a" : "#f43f5e",
                boxShadow: rangerDispatched ? "none" : accent.glow,
                transition: "all 600ms ease-out",
              }}
            />
            <div className="text-[9px] font-mono mt-2" style={{ color: rangerDispatched ? "#71717a" : "#f43f5e" }}>
              POACHER · {rangerDispatched ? "STOPPED" : "APPROACHING"}
            </div>
          </div>
        </motion.div>

        {/* Ranger interceptor — yellow chevron descending from above */}
        <AnimatePresence>
          {rangerDispatched && (
            <motion.div
              className="absolute top-0 -mt-1"
              initial={{ left: `${rangerProgress * 100}%`, opacity: 0, y: -20 }}
              animate={{ left: `${rangerProgress * 100}%`, opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
            >
              <div className="flex flex-col items-center">
                <div className="w-0 h-0" style={{
                  borderLeft: "8px solid transparent",
                  borderRight: "8px solid transparent",
                  borderTop: "14px solid #fde047",
                  filter: "drop-shadow(0 0 8px rgba(253, 224, 71, 0.6))",
                }} />
                <div className="text-[9px] font-mono mt-2 text-yellow-300">
                  {activeIncident.ranger?.unit ?? "RANGER"} · ETA {activeIncident.ranger?.eta_min ?? "?"}m
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Protected herd — green circle, right side, gentle pulse */}
        <motion.div
          className="absolute top-0 -mt-1 right-[6%]"
          animate={{ scale: [1, 1.08, 1] }}
          transition={{ duration: 2.4, repeat: Infinity, ease: "easeInOut" }}
        >
          <div className="flex flex-col items-center">
            <div
              className="w-4 h-4 rounded-full"
              style={{
                backgroundColor: "#10b981",
                boxShadow: "0 0 14px rgba(16, 185, 129, 0.6)",
              }}
            />
            <div className="text-[9px] font-mono mt-2 text-emerald-300">
              PROTECTED HERD
            </div>
          </div>
        </motion.div>
      </div>

      {/* Footer status */}
      {sponsorFiled && (
        <div className="mt-2 text-[9px] uppercase tracking-wider text-sky-300/80">
          ✓ TNFD filing posted · audit chain anchored
        </div>
      )}
    </div>
  );
}
