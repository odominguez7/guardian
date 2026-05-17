"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Siren, Clock3 } from "lucide-react";

export interface ActiveIncident {
  incident_id: string;
  scenario_id: string;
  title: string;
  severity: string;
  narrative: string;
  startedAt: number; // epoch ms
  // List of peer names the orchestrator will fan out to for this scenario.
  // Used as the completion-gate signal (incident is "in progress" until
  // every expected peer's slot is filled). Empty if the incident_event
  // didn't include a fanout list (legacy / backwards compat).
  expectedPeers?: string[];
  ranger?: { unit: string; eta_min: number; status: string };
  tnfd?: { filing_id: string; materiality: string; status: string; board_slide_url?: string };
  funder?: { receipt_id: string; program: string; tier: string; status: string };
  neighbor?: { handoff_id: string; posture: string; window_until: string; status: string };
  // Falsifier adversarial-review verdict. Populated when the orchestrator
  // delegates to the falsifier agent before dispatch (PLAN_V3.md Move 1).
  // Big-4 auditors and TNFD reviewers require this record on every
  // dispatched action.
  falsifier?: {
    verdict: "concur" | "dissent" | "abstain";
    severity_0_5: number;
    reason: string;
  };
}

interface Props {
  incidents: ActiveIncident[];
}

function severityColor(sev: string): string {
  const map: Record<string, string> = {
    critical: "bg-rose-500/20 border-rose-500/40 text-rose-200",
    high: "bg-amber-500/20 border-amber-500/40 text-amber-200",
    medium: "bg-sky-500/20 border-sky-500/40 text-sky-200",
    low: "bg-zinc-500/20 border-zinc-500/40 text-zinc-300",
  };
  return map[sev] ?? map.low;
}

function elapsedSec(startedAt: number): number {
  return Math.max(0, Math.round((Date.now() - startedAt) / 1000));
}

export default function IncidentPanel({ incidents }: Props) {
  return (
    <div className="h-full flex flex-col bg-zinc-900/80 border-r border-zinc-800">
      <div className="px-4 py-3 border-b border-zinc-800">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-300">
          Active Incidents
        </h2>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {incidents.length === 0 && (
          <div className="relative overflow-hidden rounded-lg border border-zinc-800 bg-black">
            {/* Veo 3.1 Fast hero loop — PLAN_V3.md Move 2.3. Plays in the
                IncidentPanel idle region so the page has motion even before
                any scenario fires. Muted, loops, autoplays (no user-gesture
                gate since it has no audio). */}
            <video
              src="/hero-6s.mp4"
              autoPlay
              loop
              muted
              playsInline
              className="w-full h-48 object-cover opacity-80"
              aria-hidden="true"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent" />
            <div className="absolute bottom-3 left-3 right-3 text-zinc-300">
              <div className="text-xs font-semibold uppercase tracking-wider">
                Standing watch
              </div>
              <div className="text-[10px] text-zinc-400 mt-1 leading-relaxed">
                Fire a scenario from the toolbar — or wait 10s for Auto Demo Mode.
              </div>
            </div>
          </div>
        )}
        <AnimatePresence initial={false}>
          {incidents.map((inc) => (
            <motion.div
              key={inc.incident_id}
              initial={{ opacity: 0, y: 8, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -8, scale: 0.98 }}
              transition={{ duration: 0.2 }}
              className={`rounded-lg border ${severityColor(inc.severity)} p-3 space-y-2`}
            >
              <div className="flex items-start gap-2">
                <Siren className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="text-[10px] uppercase tracking-wider font-semibold opacity-80">
                    {inc.severity}
                  </div>
                  <div className="text-sm font-semibold leading-snug">{inc.title}</div>
                  <div className="text-xs opacity-80 mt-1 leading-relaxed">
                    {inc.narrative}
                  </div>
                </div>
              </div>

              <div className="text-[10px] font-mono opacity-70 flex items-center gap-2">
                <Clock3 className="w-3 h-3" />
                <span>{elapsedSec(inc.startedAt)}s elapsed</span>
                <span className="ml-auto">{inc.incident_id}</span>
              </div>

              {inc.falsifier && (
                <motion.div
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`rounded p-2 text-xs flex items-start gap-2 border ${
                    inc.falsifier.verdict === "dissent"
                      ? "bg-rose-950/40 border-rose-500/40"
                      : inc.falsifier.verdict === "concur"
                      ? "bg-emerald-950/30 border-emerald-500/30"
                      : "bg-zinc-900/40 border-zinc-700/40"
                  }`}
                >
                  <img
                    src="/portraits/falsifier.png"
                    alt=""
                    className={`w-6 h-6 rounded-full object-cover flex-shrink-0 mt-0.5 ring-1 ${
                      inc.falsifier.verdict === "dissent"
                        ? "ring-rose-500/50"
                        : inc.falsifier.verdict === "concur"
                        ? "ring-emerald-500/50"
                        : "ring-zinc-600/40"
                    }`}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-[10px] uppercase tracking-wider font-semibold ${
                          inc.falsifier.verdict === "dissent"
                            ? "text-rose-300"
                            : inc.falsifier.verdict === "concur"
                            ? "text-emerald-300"
                            : "text-zinc-400"
                        }`}
                      >
                        Falsifier · {inc.falsifier.verdict}
                      </span>
                      {inc.falsifier.severity_0_5 >= 3 && (
                        <span className="px-1.5 py-0.5 rounded text-[9px] bg-rose-500/30 text-rose-200 font-semibold">
                          AUDIT FLAG
                        </span>
                      )}
                    </div>
                    {inc.falsifier.reason && (
                      <div className="text-[10px] text-zinc-400 mt-1 leading-relaxed">
                        {inc.falsifier.reason}
                      </div>
                    )}
                  </div>
                </motion.div>
              )}

              <AnimatePresence initial={false}>
                {inc.ranger && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="bg-black/30 rounded p-2 text-xs flex items-center gap-2 border border-white/10"
                  >
                    <img
                      src="/portraits/park_service.png"
                      alt=""
                      className="w-6 h-6 rounded-full object-cover flex-shrink-0 ring-1 ring-emerald-500/40"
                    />
                    <div className="flex-1">
                      <span className="font-semibold text-emerald-200">{inc.ranger.unit}</span>
                      <span className="text-zinc-400"> dispatched</span>
                    </div>
                    <span className="text-emerald-300 font-mono text-[10px]">
                      ETA {inc.ranger.eta_min}m
                    </span>
                  </motion.div>
                )}
                {inc.tnfd && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="bg-black/30 rounded p-2 text-xs flex items-center gap-2 border border-white/10"
                  >
                    <img
                      src="/portraits/sponsor_sustainability.png"
                      alt=""
                      className="w-6 h-6 rounded-full object-cover flex-shrink-0 ring-1 ring-sky-500/40"
                    />
                    <div className="flex-1">
                      <div className="font-mono text-[11px] text-sky-200">{inc.tnfd.filing_id}</div>
                      <div className="text-[10px] text-zinc-400">
                        TNFD entry filed · {inc.tnfd.materiality} materiality
                      </div>
                    </div>
                    {inc.tnfd.board_slide_url && (
                      <a
                        href={inc.tnfd.board_slide_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded bg-sky-500/15 text-sky-200 ring-1 ring-sky-500/40 hover:bg-sky-500/30 flex-shrink-0"
                        title="Open the board-ready slide (Maya CSO's Q2 deck)"
                      >
                        📋 Slide
                      </a>
                    )}
                  </motion.div>
                )}
                {inc.funder && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="bg-black/30 rounded p-2 text-xs flex items-center gap-2 border border-white/10"
                  >
                    <img
                      src="/portraits/funder_reporter.png"
                      alt=""
                      className="w-6 h-6 rounded-full object-cover flex-shrink-0 ring-1 ring-violet-500/40"
                    />
                    <div className="flex-1">
                      <div className="font-mono text-[11px] text-violet-200">{inc.funder.receipt_id}</div>
                      <div className="text-[10px] text-zinc-400">
                        Funder receipt · {inc.funder.program.replace(/_/g, " ")} · {inc.funder.tier.replace(/_/g, " ")}
                      </div>
                    </div>
                  </motion.div>
                )}
                {inc.neighbor && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="bg-black/30 rounded p-2 text-xs flex items-center gap-2 border border-white/10"
                  >
                    <img
                      src="/portraits/neighbor_park.png"
                      alt=""
                      className="w-6 h-6 rounded-full object-cover flex-shrink-0 ring-1 ring-orange-500/40"
                    />
                    <div className="flex-1">
                      <div className="font-mono text-[11px] text-orange-200">{inc.neighbor.handoff_id}</div>
                      <div className="text-[10px] text-zinc-400">
                        Mutual aid · {inc.neighbor.posture.replace(/_/g, " ")}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
