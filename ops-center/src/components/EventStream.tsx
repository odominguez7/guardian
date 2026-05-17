"use client";

import { useEffect, useRef, useState } from "react";
import { Activity, AlertTriangle, ArrowRight, CheckCircle2, Radio } from "lucide-react";
import type { GuardianEvent } from "@/types/events";

interface Props {
  events: GuardianEvent[];
  status: string;
}

type Mode = "plain" | "trace";

function kindIcon(kind: string) {
  if (kind === "a2a_request") return <ArrowRight className="w-3.5 h-3.5 text-amber-400" />;
  if (kind === "a2a_response") return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />;
  if (kind === "incident_event") return <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />;
  if (kind.startsWith("tool")) return <Radio className="w-3.5 h-3.5 text-sky-400" />;
  return <Activity className="w-3.5 h-3.5 text-zinc-500" />;
}

function severityBadge(severity: string) {
  const map: Record<string, string> = {
    critical: "bg-rose-500/15 text-rose-300 ring-rose-500/30",
    high: "bg-amber-500/15 text-amber-300 ring-amber-500/30",
    medium: "bg-sky-500/15 text-sky-300 ring-sky-500/30",
    low: "bg-zinc-500/15 text-zinc-300 ring-zinc-500/30",
    info: "bg-zinc-500/15 text-zinc-300 ring-zinc-500/30",
    error: "bg-rose-500/15 text-rose-300 ring-rose-500/30",
  };
  return (
    <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider ring-1 ${map[severity] ?? map.info}`}>
      {severity}
    </span>
  );
}

function severityDot(severity: string): string {
  const map: Record<string, string> = {
    critical: "bg-rose-400",
    high: "bg-amber-400",
    medium: "bg-sky-400",
    low: "bg-zinc-400",
    info: "bg-zinc-500",
    error: "bg-rose-400",
  };
  return map[severity] ?? map.info;
}

function formatTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString("en-US", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch {
    return iso;
  }
}

// PLAN_V3_1 sub-move 6.1 — narrative interpolation for the plain-language
// ticker. NO LLM call: deterministic template per event kind, fields pulled
// straight from payload. Keeps the firehose real-time (codex flagged the
// LLM-at-emit-time backlog risk). Default mode is "plain" so first-paint
// reads as a human ticker, not a developer log.
function narrate(e: GuardianEvent): string {
  const payload = (e.payload ?? {}) as Record<string, unknown>;
  // tool_span wraps tool_end payloads under payload.result; canned pre_step
  // emits put the result dict at the top level. Handle both.
  const r = (payload.result ?? payload) as Record<string, unknown>;
  const pct = (x: unknown): string | null =>
    typeof x === "number" ? `${Math.round(x * 100)}%` : null;

  if (e.kind === "incident_event") {
    if (e.tool?.endsWith(":complete")) return "Response complete. All four enterprise agents acknowledged.";
    if (e.tool?.startsWith("scenario:")) {
      const title = (payload.title as string) || e.tool;
      return `${title} — scenario in motion.`;
    }
    return "Incident detected.";
  }

  if (e.kind === "tool_end" && e.agent === "stream_watcher") {
    const species = (r.primary_species as string) ?? "wildlife";
    const count = r.total_animal_count;
    const signals = Array.isArray(r.threat_signals) ? (r.threat_signals as string[]).slice(0, 2).join(", ") : "";
    const countText = typeof count === "number" ? ` (${count} animals)` : "";
    const signalText = signals ? ` · flagged: ${signals}` : "";
    return `Stream Watcher spotted ${species}${countText}${signalText}.`;
  }

  if (e.kind === "tool_end" && e.agent === "audio_agent") {
    const sound = (r.sound_class as string) ?? "audio signal";
    const conf = pct(r.confidence);
    return `Audio Agent heard a ${sound.replace(/_/g, " ")}${conf ? `. ${conf} confidence.` : "."}`;
  }

  if (e.kind === "tool_end" && e.agent === "species_id" && e.tool === "identify_species") {
    const ps = (r.primary_species as { common_name?: string; confidence?: number }) ?? {};
    const conf = pct(ps.confidence);
    return `Species ID identified ${ps.common_name ?? "the herd"}${conf ? ` (${conf} confidence)` : ""}.`;
  }

  if (e.kind === "tool_end" && e.agent === "species_id" && e.tool === "lookup_species_factsheet") {
    const tm = (r.top_match as { common_name?: string; iucn_status?: string; cites_appendix?: string }) ?? {};
    const flag = (r.compliance_flag as string) ?? "";
    const iucn = tm.iucn_status ? ` IUCN ${tm.iucn_status}.` : "";
    const cites = tm.cites_appendix ? ` CITES Appendix ${tm.cites_appendix}.` : "";
    return `Corpus match: ${tm.common_name ?? "species"}.${iucn}${cites}${flag ? ` Materiality: ${flag}.` : ""}`;
  }

  if (e.kind === "tool_end" && e.agent === "falsifier") {
    const verdict = r.verdict as string;
    if (verdict === "concur") return "Falsifier reviewed the dispatch. All standard-operating-procedure gates pass.";
    if (verdict === "dissent") {
      const reason = (r.dissent_reason as string) ?? "a gate failed";
      return `Falsifier flagged the dispatch — ${reason}.`;
    }
    return "Falsifier abstained — not enough telemetry to evaluate.";
  }

  if (e.kind === "a2a_request") {
    if (e.tool?.includes("park_service")) return "Calling Park Service to dispatch rangers…";
    if (e.tool?.includes("sponsor")) return "Filing TNFD biodiversity disclosure with Sponsor Sustainability…";
    if (e.tool?.includes("funder")) return "Notifying Funder Reporter for impact tracking…";
    if (e.tool?.includes("neighbor")) return "Sending cross-border handoff to Neighbor Park…";
    return `Calling ${(e.tool ?? e.agent).replace(/^notify_/, "").replace(/_/g, " ")}…`;
  }

  if (e.kind === "a2a_response" && e.agent === "park_service") {
    const unit = (r.ranger_unit as string) ?? "ranger";
    const eta = r.estimated_arrival_minutes;
    const etaText = typeof eta === "number" ? `, ETA ${eta} minutes` : "";
    return `Park Service acknowledged. ${unit} dispatched${etaText}.`;
  }

  if (e.kind === "a2a_response" && e.agent === "sponsor_sustainability") {
    const fid = (r.filing_id as string) ?? "filing";
    const mat = (r.materiality as string) ?? "logged";
    return `TNFD filing ${fid} accepted. ${mat} materiality.`;
  }

  if (e.kind === "a2a_response" && e.agent === "funder_reporter") {
    const rid = (r.receipt_id as string) ?? "receipt";
    return `Funder Reporter issued impact receipt ${rid}.`;
  }

  if (e.kind === "a2a_response" && e.agent === "neighbor_park") {
    const hid = (r.handoff_id as string) ?? "handoff";
    return `Neighbor Park accepted the mutual-aid handoff (${hid}).`;
  }

  // Fallback for anything we haven't templated yet.
  return `${e.agent}${e.tool ? ` · ${e.tool.replace(/_/g, " ")}` : ""}`;
}

export default function EventStream({ events, status }: Props) {
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const [mode, setMode] = useState<Mode>("plain");
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events, mode]);

  return (
    <div className="h-full flex flex-col bg-zinc-900/80 border-l border-zinc-800">
      <div className="px-4 py-3 border-b border-zinc-800 flex items-center justify-between gap-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-300">Agent Activity</h2>
        <div className="flex items-center gap-2">
          {/* PLAIN / TRACE toggle — sub-move 6.1. PLAIN = ticker for any
              viewer; TRACE = developer log for researchers. */}
          <div className="flex items-center text-[10px] uppercase tracking-wider rounded-full bg-zinc-800/80 ring-1 ring-zinc-700/60 p-0.5">
            <button
              onClick={() => setMode("plain")}
              className={`px-2 py-0.5 rounded-full transition-colors ${
                mode === "plain" ? "bg-zinc-700 text-zinc-100" : "text-zinc-400 hover:text-zinc-200"
              }`}
              title="Plain language ticker"
            >
              plain
            </button>
            <button
              onClick={() => setMode("trace")}
              className={`px-2 py-0.5 rounded-full transition-colors ${
                mode === "trace" ? "bg-zinc-700 text-zinc-100" : "text-zinc-400 hover:text-zinc-200"
              }`}
              title="Developer trace mode"
            >
              trace
            </button>
          </div>
          <span className={`text-[10px] uppercase tracking-wider font-medium ${
            status === "connected" ? "text-emerald-400" :
            status === "fallback-polling" ? "text-amber-400" :
            status === "connecting" ? "text-sky-400" :
            "text-zinc-500"
          }`}>
            {status === "connected" && "● live"}
            {status === "fallback-polling" && "● polling"}
            {status === "connecting" && "● connecting…"}
            {status === "disconnected" && "● offline"}
          </span>
        </div>
      </div>
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
        {events.length === 0 && (
          <div className="text-zinc-500 px-2 py-4 text-center text-xs">
            Waiting for events… try the demo button.
          </div>
        )}
        {events.map((e, i) =>
          mode === "plain" ? (
            <div
              key={e.id || `${e.kind}-${e.ts}-${i}`}
              className="px-2 py-2 rounded hover:bg-zinc-800/40 flex items-start gap-3 text-[13px] leading-snug"
            >
              <div className={`w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0 ${severityDot(e.severity)}`} />
              <div className="flex-1 min-w-0">
                <div className="text-zinc-200">{narrate(e)}</div>
                <div className="text-[10px] text-zinc-500 mt-0.5 tabular-nums">
                  {formatTime(e.ts)}
                  {e.latency_ms != null && <> · {e.latency_ms}ms</>}
                </div>
              </div>
            </div>
          ) : (
            <div
              key={e.id || `${e.kind}-${e.ts}-${i}`}
              className="px-2 py-1.5 rounded hover:bg-zinc-800/40 border border-transparent hover:border-zinc-700/50 font-mono text-xs"
            >
              <div className="flex items-center gap-2">
                {kindIcon(e.kind)}
                <span className="text-zinc-500 tabular-nums">{formatTime(e.ts)}</span>
                {severityBadge(e.severity)}
                <span className="text-zinc-300 truncate">
                  <span className="text-zinc-400">{e.agent}</span>
                  {e.tool && <> · <span className="text-amber-300">{e.tool}</span></>}
                </span>
                {e.latency_ms != null && (
                  <span className="text-zinc-500 ml-auto tabular-nums">{e.latency_ms}ms</span>
                )}
              </div>
              {e.incident_id && (
                <div className="pl-6 mt-0.5 text-[10px] text-zinc-500">
                  incident: <span className="text-zinc-400">{e.incident_id}</span>
                </div>
              )}
            </div>
          )
        )}
      </div>
    </div>
  );
}
