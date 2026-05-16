"use client";

import { useEffect, useRef } from "react";
import { Activity, AlertTriangle, ArrowRight, CheckCircle2, Radio } from "lucide-react";
import type { GuardianEvent } from "@/types/events";

interface Props {
  events: GuardianEvent[];
  status: string;
}

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

function formatTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString("en-US", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch {
    return iso;
  }
}

export default function EventStream({ events, status }: Props) {
  const scrollRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  return (
    <div className="h-full flex flex-col bg-zinc-900/80 border-l border-zinc-800">
      <div className="px-4 py-3 border-b border-zinc-800 flex items-center justify-between">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-300">Agent Activity Stream</h2>
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
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-2 py-2 space-y-1 font-mono text-xs">
        {events.length === 0 && (
          <div className="text-zinc-500 px-2 py-4 text-center">
            Waiting for events… try the demo button.
          </div>
        )}
        {events.map((e, i) => (
          <div key={e.id || `${e.kind}-${e.ts}-${i}`} className="px-2 py-1.5 rounded hover:bg-zinc-800/40 border border-transparent hover:border-zinc-700/50">
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
        ))}
      </div>
    </div>
  );
}
