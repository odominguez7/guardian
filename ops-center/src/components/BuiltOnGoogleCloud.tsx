"use client";

// v5 — "Built on Google Cloud" panel.
// Replaces the v3.1 HeavyLifting strip after producer feedback that the
// section was under-selling the actual GCP stack in use. Format modeled
// on the O22 GOOGLE STACK panel: one row per product, role tag, cost,
// one-line description, model ID. Live event counts overlay onto the
// row when a scenario fires.
//
// Products in the GUARDIAN stack (all Vertex AI / GCP unless noted):
//   Gemini 2.5 Pro / Flash / Vertex AI Search / Imagen 4 / Veo 3.1 Fast
//   Lyria 2 / Nano Banana (kept) / ADK 2.0 / A2A protocol v0.3.0
//   Cloud Run / BigQuery / ElevenLabs (3rd-party badge)

import { useMemo, useState } from "react";
import { ChevronDown } from "lucide-react";
import type { GuardianEvent } from "@/types/events";

interface Props {
  events: GuardianEvent[];
}

interface ProductRow {
  tag: string;                    // [Orchestrator] etc.
  name: string;                   // Gemini 2.5 Pro
  cost: string;                   // ~$0.06 / response
  role: string;                   // One-line description
  modelId: string;                // gemini-2.5-pro
  classifyKey: string;            // Key used in classify()
  thirdParty?: boolean;           // ElevenLabs etc.
  amortized?: boolean;            // Veo / Imagen / Lyria (pre-rendered)
}

// Canonical product registry. Costs sourced from public Vertex AI pricing
// 2026-05; ElevenLabs from their tiered subscription divided by character.
const PRODUCTS: ProductRow[] = [
  {
    tag: "Orchestrator",
    name: "Gemini 2.5 Pro",
    cost: "~$0.06 / response",
    role: "Routes signals across specialists; multi-tool calls; the brain.",
    modelId: "gemini-2.5-pro",
    classifyKey: "gemini-pro-orch",
  },
  {
    tag: "Vision",
    name: "Gemini 2.5 Pro (multimodal)",
    cost: "~$0.05 / frame",
    role: "Stream Watcher video + Species ID image grounding.",
    modelId: "gemini-2.5-pro",
    classifyKey: "gemini-pro-vision",
  },
  {
    tag: "Adversary + Audio",
    name: "Gemini 2.5 Flash",
    cost: "~$0.003 / call",
    role: "Falsifier 4-gate review + Audio Agent classification.",
    modelId: "gemini-2.5-flash",
    classifyKey: "gemini-flash",
  },
  {
    tag: "RAG",
    name: "Vertex AI Search",
    cost: "~$0.002 / query",
    role: "Grounded retrieval over IUCN / CITES / TNFD corpus.",
    modelId: "discoveryengine.v1",
    classifyKey: "vertex-search",
  },
  {
    tag: "Portraits",
    name: "Imagen 4",
    cost: "$0.04 × 10 = $0.40",
    role: "Agent portrait set + board-slide art (pre-rendered).",
    modelId: "imagen-4.0-generate-001",
    classifyKey: "imagen",
    amortized: true,
  },
  {
    tag: "Live Cams",
    name: "Veo 3.1 Fast",
    cost: "$0.10/s × 27s ≈ $2.70",
    role: "3 wildlife loop renders + 1 hero clip (pre-rendered).",
    modelId: "veo-3.1-fast-generate-001",
    classifyKey: "veo",
    amortized: true,
  },
  {
    tag: "Music",
    name: "Lyria 2",
    cost: "$0.06 / 15s clip",
    role: "Demo-video ambient bed (REST API, not in SDK).",
    modelId: "lyria-002",
    classifyKey: "lyria",
    amortized: true,
  },
  {
    tag: "Continuity",
    name: "Nano Banana",
    cost: "$0.039 / image",
    role: "Species-identity continuity (reserved for v5).",
    modelId: "gemini-2.5-flash-image",
    classifyKey: "nano-banana",
    amortized: true,
  },
  {
    tag: "Framework",
    name: "Agent Development Kit 2.0",
    cost: "Free · open source",
    role: "ParallelAgent + SequentialAgent topology; the spine.",
    modelId: "google-adk 2.0",
    classifyKey: "adk",
  },
  {
    tag: "Interop",
    name: "A2A Protocol",
    cost: "Free · open standard",
    role: "Cross-org agent coordination; 4 enterprise peer fan-out.",
    modelId: "a2a v0.3.0",
    classifyKey: "a2a",
  },
  {
    tag: "Compute",
    name: "Cloud Run",
    cost: "~$0.000024 / vCPU-s",
    role: "Orchestrator + 4 A2A peers + Ops Center (5 services).",
    modelId: "run.googleapis.com",
    classifyKey: "cloud-run",
  },
  {
    tag: "Analytics",
    name: "BigQuery",
    cost: "~$5 / TB scanned",
    role: "ADK Agent Analytics plugin · agent observability spine.",
    modelId: "bigquery.googleapis.com",
    classifyKey: "bigquery",
  },
  {
    tag: "Voice (3rd-party)",
    name: "ElevenLabs",
    cost: "~$0.003 / line",
    role: "9 agent voice clips · only non-Google in the stack.",
    modelId: "eleven_v3 + Voice Design",
    classifyKey: "elevenlabs",
    thirdParty: true,
  },
];

// Map a firehose event to one of the live-traffic-bearing classifyKeys.
// Static products (Imagen / Veo / Lyria / Nano Banana) don't tick on
// live events — they were rendered at build time. ADK / Cloud Run /
// BigQuery / Mapbox tick on every event implicitly; we don't bump those
// per-event either because the counts would dominate.
function classifyLive(e: GuardianEvent): string | null {
  if (e.kind === "tool_end") {
    if (e.agent === "root_agent") return "gemini-pro-orch";
    if (e.agent === "stream_watcher") return "gemini-pro-vision";
    if (e.agent === "species_id") {
      if (e.tool === "lookup_species_factsheet") return "vertex-search";
      return "gemini-pro-vision";
    }
    if (e.agent === "court_evidence") return "gemini-pro-orch";
    if (e.agent === "audio_agent") return "gemini-flash";
    if (e.agent === "falsifier") return "gemini-flash";
  }
  if (e.kind === "a2a_request" || e.kind === "a2a_response") {
    return "a2a";
  }
  return null;
}

export default function BuiltOnGoogleCloud({ events }: Props) {
  const [expanded, setExpanded] = useState(false);

  // Live call counts per classifyKey. Static products show "—".
  const liveCounts = useMemo(() => {
    const acc = new Map<string, number>();
    for (const e of events) {
      const k = classifyLive(e);
      if (!k) continue;
      acc.set(k, (acc.get(k) ?? 0) + 1);
    }
    return acc;
  }, [events]);

  const liveTotalCalls = Array.from(liveCounts.values()).reduce((s, x) => s + x, 0);
  const totalProducts = PRODUCTS.length;
  const googleProducts = PRODUCTS.filter((p) => !p.thirdParty).length;

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
        <span className="text-[10px] uppercase tracking-[0.18em] text-zinc-100 font-semibold">
          Built on Google Cloud
        </span>
        <span className="text-[10px] text-zinc-500">
          {googleProducts} Google products + 1 partner · {liveTotalCalls} live calls this session
        </span>
        <span className="ml-auto text-[10px] text-zinc-500 italic">
          {expanded ? "click to collapse" : `click to expand the full ${totalProducts}-product stack`}
        </span>
      </button>
      {expanded && (
        <div className="px-4 pb-3 pt-1 max-h-[60vh] overflow-y-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-2">
            {PRODUCTS.map((p) => {
              const calls = liveCounts.get(p.classifyKey);
              const isLiveTickable = !p.amortized && !p.thirdParty || p.classifyKey === "a2a" || p.classifyKey === "elevenlabs";
              return (
                <div
                  key={p.modelId + p.tag}
                  className={`rounded border px-3 py-2 ${
                    p.thirdParty
                      ? "bg-zinc-900/40 border-zinc-800/80"
                      : p.amortized
                        ? "bg-zinc-900/60 border-zinc-800"
                        : "bg-zinc-900/80 border-zinc-700/70"
                  }`}
                >
                  <div className="flex items-baseline justify-between gap-2">
                    <span
                      className={`text-[8.5px] uppercase tracking-wider font-semibold px-1.5 py-0.5 rounded ${
                        p.thirdParty
                          ? "bg-zinc-800 text-zinc-300"
                          : "bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-500/40"
                      }`}
                    >
                      [{p.tag}]
                    </span>
                    <span className="text-[10px] text-amber-300 font-mono tabular-nums">
                      {p.cost}
                    </span>
                  </div>
                  <div className="mt-1.5 text-[12px] font-semibold text-zinc-100 leading-tight">
                    {p.name}
                  </div>
                  <div className="mt-0.5 text-[10px] text-zinc-400 leading-snug">
                    {p.role}
                  </div>
                  <div className="mt-1 flex items-baseline justify-between gap-2">
                    <span className="text-[9px] font-mono text-zinc-500 truncate">
                      Model: {p.modelId}
                    </span>
                    {isLiveTickable && (
                      <span className="text-[9px] text-zinc-500 tabular-nums shrink-0">
                        {calls !== undefined ? (
                          <span className="text-emerald-300">● {calls} live</span>
                        ) : (
                          <span>idle</span>
                        )}
                      </span>
                    )}
                    {p.amortized && (
                      <span className="text-[9px] text-zinc-600 italic shrink-0">
                        pre-rendered
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
          <div className="mt-3 text-[9.5px] text-zinc-500 leading-relaxed">
            All Vertex AI calls run in <span className="text-zinc-300 font-mono">us-central1</span> against project{" "}
            <span className="text-zinc-300 font-mono">guardian-gfs-2026</span>. Pre-rendered assets (Imagen / Veo / Lyria / Nano Banana) build at deploy time so live demos hit static URLs, not generative endpoints, keeping demo latency &lt; 1s and reproducibility deterministic. ADK + A2A + Cloud Run + BigQuery are the always-on spine: every event you see in the stream emits via BigQuery agent analytics, fans out via A2A, executes on Cloud Run.
          </div>
        </div>
      )}
    </div>
  );
}
