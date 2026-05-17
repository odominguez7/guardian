"use client";

import { useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Siren, Clock3, Volume2 } from "lucide-react";

// PLAN_V3_1 sub-move 6.3 — Falsifier Tribunal. Click-to-expand inline panel
// (NOT modal, per codex Move 6 RECONSIDER) showing the orchestrator's claim
// LEFT vs the Falsifier's challenge RIGHT. Optional "🔊 Hear the dissent"
// button uses the browser's native SpeechSynthesis API — zero server cost,
// works offline, and the voice is recognizably different from any narrator.
function FalsifierTribunal({
  falsifier,
  rangerUnit,
  incidentTitle,
}: {
  falsifier: NonNullable<ActiveIncident["falsifier"]>;
  rangerUnit?: string;
  incidentTitle: string;
}) {
  const [expanded, setExpanded] = useState(false);
  const verdict = falsifier.verdict;
  const isDissent = verdict === "dissent";
  const isConcur = verdict === "concur";
  const colorRing = isDissent ? "ring-rose-500/50" : isConcur ? "ring-emerald-500/50" : "ring-zinc-600/40";
  const colorText = isDissent ? "text-rose-300" : isConcur ? "text-emerald-300" : "text-zinc-400";
  const colorBg = isDissent ? "bg-rose-950/40 border-rose-500/40" : isConcur ? "bg-emerald-950/30 border-emerald-500/30" : "bg-zinc-900/40 border-zinc-700/40";

  // Orchestrator's claim narrative — interpolated from the incident state.
  const orchestratorClaim = rangerUnit
    ? `Dispatching ${rangerUnit} based on the multimodal signal chain. Evidence reconciled across Stream Watcher, Audio Agent, and Species ID.`
    : `Preparing to fan out to four enterprise A2A peers based on the multimodal signal chain for ${incidentTitle}.`;

  function speakDissent() {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const text = `Falsifier dissent. ${falsifier.reason || "A standard operating procedure gate failed."}`;
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 0.92;
    utter.pitch = 0.85;
    // Prefer a lower-register voice to distinguish from any narrator
    const voices = window.speechSynthesis.getVoices();
    const lowVoice = voices.find((v) => /daniel|alex|fred|james/i.test(v.name)) ?? voices[0];
    if (lowVoice) utter.voice = lowVoice;
    window.speechSynthesis.speak(utter);
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -4 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded text-xs border ${colorBg}`}
    >
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="w-full p-2 flex items-start gap-2 text-left hover:bg-white/[0.02] rounded-t"
      >
        <img
          src="/portraits/falsifier.png"
          alt=""
          className={`w-6 h-6 rounded-full object-cover flex-shrink-0 mt-0.5 ring-1 ${colorRing}`}
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={`text-[10px] uppercase tracking-wider font-semibold ${colorText}`}>
              Falsifier · {verdict}
            </span>
            {falsifier.severity_0_5 >= 3 && (
              <span className="px-1.5 py-0.5 rounded text-[9px] bg-rose-500/30 text-rose-200 font-semibold">
                AUDIT FLAG
              </span>
            )}
            <span className={`ml-auto text-[10px] ${colorText} opacity-60`}>
              {expanded ? "▾ tribunal" : "▸ tribunal"}
            </span>
          </div>
          {falsifier.reason && (
            <div className="text-[10px] text-zinc-400 mt-1 leading-relaxed">
              {falsifier.reason}
            </div>
          )}
        </div>
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.18 }}
            className="border-t border-white/10 overflow-hidden"
          >
            <div className="p-3 grid grid-cols-2 gap-3">
              {/* Orchestrator side */}
              <div className="space-y-1.5">
                <div className="text-[9px] uppercase tracking-[0.15em] text-emerald-300/80 font-semibold">
                  Orchestrator claim
                </div>
                <div className="text-[11px] text-zinc-200 leading-snug">
                  {orchestratorClaim}
                </div>
                <div className="text-[9px] text-zinc-500">
                  Evidence: Stream Watcher · Audio Agent · Species ID
                </div>
              </div>
              {/* Falsifier side */}
              <div className="space-y-1.5 pl-3 border-l border-white/10">
                <div className={`text-[9px] uppercase tracking-[0.15em] font-semibold ${colorText}`}>
                  Falsifier challenge
                </div>
                <div className="text-[11px] text-zinc-200 leading-snug">
                  {falsifier.reason || "No challenge raised."}
                </div>
                <div className="text-[9px] text-zinc-500">
                  Verdict severity {falsifier.severity_0_5}/5 · gates evaluated per SOP
                </div>
              </div>
            </div>
            {isDissent && (
              <div className="px-3 pb-3">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    speakDissent();
                  }}
                  className="text-[10px] uppercase tracking-wider px-2 py-1 rounded bg-rose-500/20 text-rose-200 ring-1 ring-rose-500/40 hover:bg-rose-500/30"
                  title="Browser SpeechSynthesis reads the dissent reason aloud — Falsifier voice"
                >
                  🔊 Hear the dissent
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// PLAN_V3_1 sub-move 6.2 — chip that plays the gunshot impulse sample.
function AudioReplayChip({ soundClass, confidence }: { soundClass: string; confidence: number }) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playing, setPlaying] = useState(false);
  const conf = Math.round(confidence * 100);
  return (
    <div className="bg-black/30 rounded p-2 text-xs flex items-center gap-2 border border-white/10">
      <Volume2 className="w-3.5 h-3.5 text-rose-300 flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <div className="text-rose-200 font-semibold">
          Audio captured · {soundClass.replace(/_/g, " ")}
        </div>
        <div className="text-[10px] text-zinc-400">
          {conf}% confidence · click to replay what the agent heard
        </div>
      </div>
      <button
        onClick={() => {
          if (!audioRef.current) return;
          audioRef.current.currentTime = 0;
          audioRef.current.play().catch(() => {});
          setPlaying(true);
          setTimeout(() => setPlaying(false), 800);
        }}
        className={`px-2 py-0.5 rounded text-[10px] uppercase tracking-wider ring-1 transition-colors flex-shrink-0 ${
          playing
            ? "bg-rose-500/30 text-rose-100 ring-rose-500/60 animate-pulse"
            : "bg-rose-500/15 text-rose-200 ring-rose-500/40 hover:bg-rose-500/30"
        }`}
      >
        🔊 Replay
      </button>
      <audio ref={audioRef} src="/audio/gunshot-sample.mp3" preload="auto" />
    </div>
  );
}

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
  /** What the Audio Agent classified, if anything. PLAN_V3_1 sub-move 6.2:
   *  surfaces a "Replay what the agent heard" chip in the incident card. */
  audio?: { sound_class: string; confidence: number };
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
      <div
        className="flex-1 overflow-y-auto p-3 space-y-3 [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-track]:bg-zinc-900 [&::-webkit-scrollbar-thumb]:bg-zinc-700 [&::-webkit-scrollbar-thumb]:rounded"
        style={{ scrollbarWidth: "thin", scrollbarColor: "#3f3f46 #18181b" }}
      >
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
                <FalsifierTribunal
                  falsifier={inc.falsifier}
                  rangerUnit={inc.ranger?.unit}
                  incidentTitle={inc.title}
                />
              )}

              {/* PLAN_V3_1 sub-move 6.2 — Audio replay chip. When the Audio
                  Agent classified a non-silence signal, surface a click-to-
                  play button so a human-in-the-loop can hear what the
                  agent heard. CC0 short impulse, ~700ms, 12KB. */}
              {inc.audio && inc.audio.sound_class !== "silence" && (
                <AudioReplayChip
                  soundClass={inc.audio.sound_class}
                  confidence={inc.audio.confidence}
                />
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
