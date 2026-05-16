"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Siren, FileCheck2, ShieldAlert, Clock3, HandCoins, Map as MapIcon } from "lucide-react";

export interface ActiveIncident {
  incident_id: string;
  scenario_id: string;
  title: string;
  severity: string;
  narrative: string;
  startedAt: number; // epoch ms
  ranger?: { unit: string; eta_min: number; status: string };
  tnfd?: { filing_id: string; materiality: string; status: string };
  funder?: { receipt_id: string; program: string; tier: string; status: string };
  neighbor?: { handoff_id: string; posture: string; window_until: string; status: string };
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
          <div className="text-zinc-500 text-xs px-2 py-8 text-center">
            No active incidents.
            <br />
            <span className="text-zinc-600">Fire a demo scenario from the toolbar.</span>
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

              <AnimatePresence initial={false}>
                {inc.ranger && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="bg-black/30 rounded p-2 text-xs flex items-center gap-2 border border-white/10"
                  >
                    <ShieldAlert className="w-3.5 h-3.5 text-emerald-300 flex-shrink-0" />
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
                    <FileCheck2 className="w-3.5 h-3.5 text-sky-300 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="font-mono text-[11px] text-sky-200">{inc.tnfd.filing_id}</div>
                      <div className="text-[10px] text-zinc-400">
                        TNFD entry filed · {inc.tnfd.materiality} materiality
                      </div>
                    </div>
                  </motion.div>
                )}
                {inc.funder && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="bg-black/30 rounded p-2 text-xs flex items-center gap-2 border border-white/10"
                  >
                    <HandCoins className="w-3.5 h-3.5 text-violet-300 flex-shrink-0" />
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
                    <MapIcon className="w-3.5 h-3.5 text-orange-300 flex-shrink-0" />
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
