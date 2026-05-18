"use client";

// v9 W1 — bottom narration strip for the Hero view. Three jobs:
//
// 1. Rotate three business-model / impact lines every 8s (producer issue
//    #15: "communicate business model, impact, revolutionary tool").
// 2. Surface live protocol activity as it flows through the firehose
//    (producer issue #7: "show Google protocols visibly while agents
//    speak"). Renders a transient chip like `[A2A v0.3]` or
//    `[Vertex AI Search]` for ~6s when a new event with a protocol_stack
//    field arrives.
// 3. Stay quiet when nothing is happening — the static rotation is the
//    idle fallback, the live chips are the wow moments.

import { useEffect, useMemo, useState } from "react";
import type { GuardianEvent } from "@/types/events";

const ROTATION_MS = 8_000;
const PROTOCOL_CHIP_TTL_MS = 6_000;

// Locked 2026-05-17 (v9 plan). Order matters — first line on cold
// load gives F500 buyers the chain-of-custody anchor; second line is
// the CSRD/TNFD revenue story; third is the agentic infrastructure.
const LINES = [
  "Every incident here lands in a SHA-256 chain-of-custody bundle.",
  "Fortune 500 sustainability officers file CSRD-E4 + TNFD disclosures from this stream.",
  "Four enterprise organizations coordinate live over A2A v0.3.",
];

interface Props {
  events: GuardianEvent[];
}

// v9 W2a will add `protocol_stack` to every emission. Until then we
// derive a plausible chip from the event's tool + agent so the UI is
// useful immediately. When W2a lands, this map becomes a fallback for
// events that don't yet declare their stack explicitly.
function deriveProtocolChip(evt: GuardianEvent): string | null {
  const tool = evt.tool ?? "";
  if (!tool) return null;
  if (tool.includes("notify") || evt.agent?.includes("peer")) return "A2A v0.3";
  if (tool.includes("analyze_image") || tool.includes("vision")) return "Vertex AI · Gemini Vision";
  if (tool.includes("species_id") || tool.includes("lookup")) return "Vertex AI Search · RAG";
  if (tool.includes("audio")) return "Vertex AI · Gemini Audio";
  if (tool.includes("court_evidence") || tool.includes("bundle")) return "BigQuery · SHA-256";
  if (tool.includes("falsifier") || tool.includes("review")) return "ADK 2.0 · SequentialAgent";
  if (tool.includes("board_slide")) return "Cloud Run · HTML render";
  return null;
}

interface LiveChip {
  id: string;
  label: string;
  expiresAt: number;
}

export default function NarrationStrip({ events }: Props) {
  const [lineIdx, setLineIdx] = useState(0);
  const [chips, setChips] = useState<LiveChip[]>([]);

  // 1. Rotate the static lines.
  useEffect(() => {
    const id = setInterval(() => setLineIdx((i) => (i + 1) % LINES.length), ROTATION_MS);
    return () => clearInterval(id);
  }, []);

  // 2. Surface protocol activity from the firehose as transient chips.
  // We watch only the latest event, derive a chip, and push it. Stale
  // chips reap themselves via expiresAt.
  useEffect(() => {
    if (events.length === 0) return;
    const latest = events[events.length - 1];
    const label = deriveProtocolChip(latest);
    if (!label) return;
    const chip: LiveChip = {
      id: `${latest.kind}:${latest.ts ?? Date.now()}:${label}`,
      label,
      expiresAt: Date.now() + PROTOCOL_CHIP_TTL_MS,
    };
    setChips((prev) => {
      // De-dup on label so the same protocol firing rapidly doesn't
      // stack 8 identical chips.
      const filtered = prev.filter((c) => c.label !== label);
      return [...filtered, chip].slice(-3);
    });
  }, [events]);

  // 3. Reap expired chips on a ticker — keeps the strip clean.
  useEffect(() => {
    const id = setInterval(() => {
      const now = Date.now();
      setChips((prev) => prev.filter((c) => c.expiresAt > now));
    }, 1_000);
    return () => clearInterval(id);
  }, []);

  const currentLine = useMemo(() => LINES[lineIdx], [lineIdx]);

  return (
    <div
      className="h-[44px] flex items-center px-6 border-t border-white/[0.06] gap-4"
      style={{ background: "rgba(0,0,0,0.55)" }}
      aria-label="Mission narration and live protocol activity"
    >
      <div className="flex-1 min-w-0 flex items-center gap-3 overflow-hidden">
        <span
          className="text-[11px] uppercase tracking-[0.16em] text-amber-300/85 font-mono shrink-0"
        >
          GUARDIAN
        </span>
        <span
          key={lineIdx}
          className="text-[12.5px] text-zinc-200 leading-tight truncate animate-[fadein_0.45s_ease-out_both]"
          style={{ textShadow: "0 0 12px rgba(245,158,11,0.08)" }}
        >
          {currentLine}
        </span>
      </div>
      <div className="flex items-center gap-1.5 shrink-0">
        {chips.length === 0 ? (
          <span className="text-[10px] text-zinc-600 font-mono uppercase tracking-[0.14em]">
            awaiting agent activity
          </span>
        ) : (
          chips.map((c) => (
            <span
              key={c.id}
              className="px-2 py-0.5 rounded-full text-[10px] font-mono uppercase tracking-[0.12em] border animate-[fadein_0.3s_ease-out_both]"
              style={{
                background: "rgba(16,185,129,0.10)",
                borderColor: "rgba(16,185,129,0.45)",
                color: "rgb(110,231,183)",
                boxShadow: "0 0 10px rgba(16,185,129,0.12)",
              }}
            >
              {c.label}
            </span>
          ))
        )}
      </div>
      <style jsx>{`
        @keyframes fadein {
          from { opacity: 0; transform: translateY(2px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
