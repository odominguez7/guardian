"use client";

// PLAN_V3_1 sub-move 6.5 — Google Heavy-Lifting panel.
// Bottom strip that aggregates REAL events from the live firehose into a
// per-product summary: which Google AI products are doing the work, how
// many calls, how much latency. Text-only product names (no logo art —
// codex flagged brand-compliance risk in the v3.1 review). Answers the
// "feels pre-fabricated" complaint by surfacing the real model calls
// happening live, not synthetic metrics on canned fixtures.

import { useMemo, useState } from "react";
import { ChevronDown } from "lucide-react";
import type { GuardianEvent } from "@/types/events";

interface Props {
  events: GuardianEvent[];
}

interface ProductStat {
  name: string;
  blurb: string;
  calls: number;
  totalLatency: number;
  lastTool?: string;
}

// Map (agent, kind, tool) → Google AI product name. Best-effort heuristics
// based on the orchestrator + sub-agent topology shipped in Moves 1-3.
function classify(e: GuardianEvent): string | null {
  if (e.kind === "tool_end") {
    if (e.agent === "root_agent") return "Gemini 2.5 Pro (ADK orchestrator)";
    if (e.agent === "stream_watcher") return "Gemini 2.5 Pro (vision)";
    if (e.agent === "audio_agent") return "Gemini 2.5 Flash";
    if (e.agent === "species_id") {
      if (e.tool === "lookup_species_factsheet") return "Vertex AI Search";
      return "Gemini 2.5 Pro (vision)";
    }
    if (e.agent === "falsifier") return "Gemini 2.5 Flash";
    if (e.agent === "court_evidence") return "Gemini 2.5 Pro";
  }
  if (e.kind === "a2a_request" || e.kind === "a2a_response") {
    return "A2A protocol v0.3.0";
  }
  return null;
}

function PRODUCT_BLURBS(): Record<string, string> {
  return {
    "Gemini 2.5 Pro (ADK orchestrator)": "Routes signals across specialists; multi-tool calls",
    "Gemini 2.5 Pro (vision)": "Multimodal: frame analysis + species identification",
    "Gemini 2.5 Pro": "Reasoning + tool use for legal-grade output",
    "Gemini 2.5 Flash": "Fast classifier + adversarial gate evaluation",
    "Vertex AI Search": "RAG over IUCN / CITES / TNFD corpus",
    "A2A protocol v0.3.0": "Cross-organization agent fan-out",
  };
}

export default function HeavyLifting({ events }: Props) {
  const [expanded, setExpanded] = useState(true);

  const stats = useMemo<ProductStat[]>(() => {
    const acc = new Map<string, ProductStat>();
    const blurbs = PRODUCT_BLURBS();
    for (const e of events) {
      const product = classify(e);
      if (!product) continue;
      const cur = acc.get(product) ?? {
        name: product,
        blurb: blurbs[product] ?? "",
        calls: 0,
        totalLatency: 0,
      };
      cur.calls += 1;
      cur.totalLatency += e.latency_ms ?? 0;
      cur.lastTool = e.tool ?? cur.lastTool;
      acc.set(product, cur);
    }
    return Array.from(acc.values()).sort((a, b) => b.calls - a.calls);
  }, [events]);

  const totalCalls = stats.reduce((s, x) => s + x.calls, 0);
  const totalLatency = stats.reduce((s, x) => s + x.totalLatency, 0);

  return (
    <div className="border-t border-zinc-800 bg-zinc-950/95 backdrop-blur">
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="w-full px-4 py-1.5 flex items-center gap-3 text-left hover:bg-zinc-900/60"
      >
        <ChevronDown
          className={`w-3.5 h-3.5 text-zinc-500 transition-transform ${expanded ? "" : "-rotate-90"}`}
        />
        <span className="text-[10px] uppercase tracking-[0.18em] text-zinc-300 font-semibold">
          Google AI · heavy lifting · live
        </span>
        <span className="text-[10px] text-zinc-500 tabular-nums">
          {totalCalls} model + RAG + A2A calls · {totalLatency.toLocaleString()}ms aggregate
        </span>
        <span className="ml-auto text-[10px] text-zinc-500 italic">
          {expanded ? "click to collapse" : "click to expand"}
        </span>
      </button>
      {expanded && (
        <div className="px-4 pb-2 pt-1">
          {stats.length === 0 ? (
            <div className="text-[11px] text-zinc-500 py-2">
              Idle. Fire a scenario to watch the agents work.
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
              {stats.map((s) => (
                <div
                  key={s.name}
                  className="rounded border border-zinc-800 bg-zinc-900/60 px-2.5 py-1.5"
                >
                  <div className="text-[10px] uppercase tracking-wider text-zinc-300 font-semibold leading-tight">
                    {s.name}
                  </div>
                  <div className="text-[9px] text-zinc-500 mt-0.5 line-clamp-1">
                    {s.blurb}
                  </div>
                  <div className="mt-1 flex items-baseline gap-2 tabular-nums">
                    <span className="text-base font-bold text-zinc-100">{s.calls}</span>
                    <span className="text-[9px] text-zinc-500">calls</span>
                    <span className="ml-auto text-[10px] text-emerald-300">
                      {s.totalLatency}ms
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
