"use client";

// PLAN_V3_2 sub-move 7.2 — Live Cams tab. 2×2 grid of Veo-rendered
// wildlife clips with IR-style overlays. When Veo files aren't yet
// present (still rendering in background), tiles show a placeholder.
//
// v6 — "Spot Now" button on the youtube-live tile triggers a REAL
// Gemini 2.5 Pro vision call against a freshly-pulled frame, then fans
// out to all 4 A2A peers if anything material is detected. Producer
// ask 2026-05-17: "is there a way to launch some agent in real life
// when we spot something in the screen?" YES.

import { useState, useRef, useEffect } from "react";
import { Sparkles, Repeat } from "lucide-react";

const ORCH_URL =
  process.env.NEXT_PUBLIC_ORCHESTRATOR_URL ?? "http://localhost:8000";

interface CamProps {
  id: string;
  label: string;
  /** Local Veo-rendered MP4 OR YouTube live-stream embed URL. Exactly one
   *  of `src` or `embedUrl` must be set. */
  src?: string;
  embedUrl?: string;
  subtitle: string;
  accent: string;
  /** When true, render a small "REAL · 24/7" pill — for the YouTube live
   *  stream that's not a Veo render. v4 sub-move A1. */
  realLive?: boolean;
  /** Source YouTube video id — required when realLive=true so the
   *  "Spot Now" button can POST it to /livecam/spot. */
  youtubeId?: string;
}

const CAMS: CamProps[] = [
  {
    // v5.4 — Producer flagged "this live stream recording is not available"
    // 2026-05-17. Africam's vr4o_AsrU1k stream returns oembed metadata but
    // YouTube's embed shows the unavailable splash (channel disabled embed
    // for that asset OR archived the live broadcast). Replaced with NamibiaCam
    // waterhole stream (ydYDqZQpim8) — verified live + playableInEmbed:true
    // at swap time. Same vibe (24/7 wildlife waterhole), known stable.
    id: "namib-waterhole-live",
    label: "CAM-12 · NAMIB DESERT · Waterhole",
    embedUrl: "https://www.youtube-nocookie.com/embed/ydYDqZQpim8?autoplay=1&mute=1&controls=0&loop=1&playlist=ydYDqZQpim8&modestbranding=1&playsinline=1&rel=0",
    subtitle: "Live Namib waterhole · YouTube 24/7",
    accent: "#10b981",
    realLive: true,
    youtubeId: "ydYDqZQpim8",
  },
  {
    id: "cheetah-crossing",
    label: "CAM-07 · Etosha · F-14 fenceline",
    src: "/cams/cheetah-crossing.mp4",
    subtitle: "Cheetah crossing · IUCN Vulnerable",
    accent: "#f59e0b",
  },
  {
    id: "vehicle-night",
    label: "CAM-22 · Serengeti · Tag-22 corridor",
    src: "/cams/vehicle-night.mp4",
    subtitle: "Vehicle approach · night IR",
    accent: "#f43f5e",
  },
  {
    id: "trap-perspective",
    label: "CAM-04 · Maasai Mara · Border",
    src: "/cams/trap-perspective.mp4",
    subtitle: "Camera trap · dawn ambient",
    accent: "#0ea5e9",
  },
];

interface SpotResult {
  incident_id: string;
  requires_escalation: boolean;
  escalationReason: string; // "gemini_model" | "threat_signal" | "hot_species:..." | "none"
  speciesLabel: string;
  totalCount: number;
  topConfidence: number;
  threatSignals: string[];
  behaviors: string[];
  thumbnail_url?: string;
  frame_sha?: string;
  frame_fresh?: boolean;
  falsifier: { verdict: string; severity_0_5?: number; reason?: string } | null;
  rangerUnit?: string;
  rangerEta?: number;
  tnfdFilingId?: string;
  boardSlideUrl?: string;
  funderReceiptId?: string;
  neighborHandoffId?: string;
}

const AUTO_SPOT_INTERVAL_MS = 60_000;

function pickTopSpecies(speciesArr: unknown): {
  label: string;
  count: number;
  confidence: number;
} {
  if (!Array.isArray(speciesArr) || speciesArr.length === 0) {
    return { label: "wildlife sighting", count: 0, confidence: 0 };
  }
  let top: Record<string, unknown> | null = null;
  let topConf = -1;
  for (const s of speciesArr) {
    if (s && typeof s === "object") {
      const conf = Number((s as Record<string, unknown>).confidence ?? 0);
      if (conf > topConf) {
        topConf = conf;
        top = s as Record<string, unknown>;
      }
    }
  }
  if (!top) return { label: "wildlife sighting", count: 0, confidence: 0 };
  const label =
    String(top.common_name ?? top.name ?? "").trim() || "wildlife sighting";
  const count = Number(top.count ?? 0) || 0;
  return { label, count, confidence: topConf };
}

function CamTile({ cam }: { cam: CamProps }) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  // v6: "Spot Now" — POST the live thumbnail to /livecam/spot, which runs
  // Gemini 2.5 Pro vision on a fresh frame and fans the result out to all 4
  // A2A peers if anything material is detected.
  const [spotState, setSpotState] = useState<"idle" | "running" | "done" | "error">("idle");
  const [spotMessage, setSpotMessage] = useState<string>("");
  // v6.4: full result panel so producer sees the agent fan-out INLINE on
  // the Live Cams tab. Prior version returned a one-line status that
  // (a) read the wrong vision schema and (b) hid the fan-out behind a
  // tab switch. Producer flagged 2026-05-17: "We saw a real life animal
  // by agents didnt do nothing."
  const [spotResult, setSpotResult] = useState<SpotResult | null>(null);
  // v7: auto-spot mode for the demo. Toggle on → fires Spot Now every
  // 60s so judges who land on the URL see real agentic activity without
  // clicking. Persists across reloads via localStorage.
  const autoStorageKey = cam.youtubeId ? `guardian.autospot.${cam.youtubeId}` : null;
  const [autoSpot, setAutoSpot] = useState<boolean>(() => {
    if (typeof window === "undefined" || !autoStorageKey) return false;
    return window.localStorage.getItem(autoStorageKey) === "1";
  });
  const inFlightRef = useRef(false);
  const handleSpot = async () => {
    if (!cam.youtubeId) return;
    // v7.1 codex WARN fix: gate on inFlightRef (always current) instead of
    // spotState (stale closure inside the auto-spot useEffect tick).
    if (inFlightRef.current) return;
    setSpotState("running");
    setSpotMessage("Pulling fresh frame…");
    setSpotResult(null);
    try {
      const res = await fetch(`${ORCH_URL}/livecam/spot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ youtube_id: cam.youtubeId, cam_label: cam.label }),
      });
      if (res.status === 429) {
        const body = (await res.json().catch(() => null)) as { detail?: string } | null;
        setSpotMessage(
          body?.detail ?? "Live cam on cooldown — retry in a few seconds.",
        );
        setSpotState("error");
        return;
      }
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const body = await res.json();
      // v6.4: read the current schema (species[] + total_animal_count, not
      // the legacy primary_species).
      const top = pickTopSpecies(body?.vision?.species);
      const totalCount = Number(body?.vision?.total_animal_count ?? top.count) || top.count;
      const threatSignals: string[] = Array.isArray(body?.vision?.threat_signals)
        ? body.vision.threat_signals
        : [];
      const behaviors: string[] = Array.isArray(body?.vision?.behaviors)
        ? body.vision.behaviors
        : [];
      const escalated = !!body?.requires_escalation;
      // Headline: include count when > 1.
      const speciesLabel =
        totalCount > 1 ? `${totalCount} × ${top.label}` : top.label;
      setSpotMessage(
        escalated
          ? `Spotted ${speciesLabel} → all 4 peers responding`
          : `Spotted ${speciesLabel} (no escalation needed)`,
      );
      setSpotResult({
        incident_id: String(body?.incident_id ?? ""),
        requires_escalation: escalated,
        escalationReason: String(body?.escalation_reason ?? ""),
        speciesLabel,
        totalCount,
        topConfidence: top.confidence,
        threatSignals,
        behaviors,
        thumbnail_url: body?.thumbnail_url ? String(body.thumbnail_url) : undefined,
        frame_sha: body?.frame_sha ? String(body.frame_sha) : undefined,
        frame_fresh: typeof body?.frame_fresh === "boolean" ? body.frame_fresh : undefined,
        falsifier: body?.adversarial_review
          ? {
              verdict: String(body.adversarial_review.verdict ?? ""),
              severity_0_5: Number(body.adversarial_review.severity_0_5 ?? 0) || 0,
              reason: String(body.adversarial_review.dissent_reason ?? ""),
            }
          : null,
        rangerUnit: body?.park_service?.ranger_unit,
        rangerEta: body?.park_service?.estimated_arrival_minutes,
        tnfdFilingId: body?.sponsor_sustainability?.filing_id,
        boardSlideUrl: body?.sponsor_sustainability?.board_slide_url,
        funderReceiptId:
          body?.funder_reporter?.receipt_id ??
          body?.funder_reporter?.impact_entry?.receipt_id,
        neighborHandoffId: body?.neighbor_park?.handoff_id,
      });
      setSpotState("done");
    } catch (err) {
      setSpotMessage(err instanceof Error ? err.message : "Spot failed");
      setSpotState("error");
    }
  };

  // v7.1 codex WARN fix: previous useEffect closed over `spotState` at
  // mount, so toggling auto while a manual spot was "running" cached the
  // stale value and every future tick aborted. Now the only re-entry gate
  // is the inFlightRef ref (always current), and the effect only restarts
  // when autoSpot or the cam id changes — not on every spotState tick.
  useEffect(() => {
    if (!autoSpot || !cam.youtubeId) return;
    let cancelled = false;
    const tick = async () => {
      if (cancelled) return;
      if (inFlightRef.current) return;
      inFlightRef.current = true;
      try {
        await handleSpot();
      } finally {
        inFlightRef.current = false;
      }
    };
    tick(); // fire immediately when toggled on
    const id = setInterval(tick, AUTO_SPOT_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoSpot, cam.youtubeId]);

  const toggleAuto = () => {
    if (!autoStorageKey) return;
    const next = !autoSpot;
    setAutoSpot(next);
    try {
      window.localStorage.setItem(autoStorageKey, next ? "1" : "0");
    } catch {
      // Private-mode browser etc. — toggle still works in-session.
    }
  };
  return (
    <div
      className="relative rounded-lg overflow-hidden border bg-black min-h-0"
      style={{ borderColor: `${cam.accent}40` }}
    >
      {cam.embedUrl ? (
        <iframe
          src={cam.embedUrl}
          className="absolute inset-0 w-full h-full"
          style={{ border: 0 }}
          // v5.3: producer flagged "live cam not working" 2026-05-17 — sandbox
          // was too tight (player JS couldn't run). Restored the standard
          // YouTube embed `allow` set per their oembed response, dropped
          // sandbox. youtube-nocookie still gives us zero tracking cookies,
          // which was the original security ask. allowFullScreen so users
          // can pop the live stream out.
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          allowFullScreen
          loading="lazy"
          referrerPolicy="strict-origin-when-cross-origin"
          title={cam.label}
        />
      ) : (
        <video
          ref={videoRef}
          src={cam.src}
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 w-full h-full object-cover"
        />
      )}
      {/* IR overlay vignette (skipped on real YouTube embeds — let the
          actual broadcast through without our color cast) */}
      {!cam.realLive && (
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "radial-gradient(circle at 50% 50%, transparent 60%, rgba(0,0,0,0.55) 100%)",
          }}
        />
      )}
      {/* Top-left tag */}
      <div className="absolute top-2 left-2 flex items-center gap-1.5 z-10 pointer-events-none">
        <div
          className="w-1.5 h-1.5 rounded-full animate-pulse"
          style={{ backgroundColor: cam.accent }}
        />
        <div className="text-[9px] font-mono text-white/85 tracking-[0.05em]">
          {cam.label}
        </div>
      </div>
      {/* Top-right LIVE — v4 sub-move A1 distinguishes REAL vs Veo */}
      <div className="absolute top-2 right-2 z-10 pointer-events-none flex flex-col items-end gap-1">
        <div className="text-[9px] font-mono text-rose-400 uppercase tracking-wider">
          ● live
        </div>
        {cam.realLive && (
          <div className="px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-200 text-[8px] uppercase tracking-wider ring-1 ring-rose-500/40">
            real · 24/7
          </div>
        )}
      </div>
      {/* v6.4 — Spot result overlay. Pops over the video when the agents
          have responded so the producer doesn't have to switch tabs to see
          the fan-out happen. Click X (or the next Spot Now) to dismiss. */}
      {spotResult && spotState === "done" && (
        <div
          className="absolute inset-x-2 top-2 bottom-12 z-20 rounded-lg p-3 overflow-y-auto"
          style={{
            background: "rgba(0,0,0,0.86)",
            border: "1px solid rgba(16,185,129,0.45)",
            backdropFilter: "blur(8px)",
          }}
        >
          <div className="flex items-center justify-between mb-2 gap-2 flex-wrap">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 ring-1 ring-emerald-500/40 text-[9px] uppercase tracking-wider">
                LIVE SPOT · {spotResult.incident_id}
              </span>
              {spotResult.requires_escalation ? (
                <span
                  className="px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 ring-1 ring-rose-500/40 text-[9px] uppercase tracking-wider"
                  title={`escalation reason: ${spotResult.escalationReason || "unknown"}`}
                >
                  ESCALATED
                </span>
              ) : (
                <span
                  className="px-1.5 py-0.5 rounded bg-sky-500/15 text-sky-300 ring-1 ring-sky-500/40 text-[9px] uppercase tracking-wider"
                  title="No threat signal, no IUCN hot-list species — logged but no peer fan-out"
                >
                  LOGGED
                </span>
              )}
              {spotResult.frame_sha && (
                <span
                  className={`px-1.5 py-0.5 rounded text-[9px] uppercase tracking-wider ring-1 font-mono ${
                    spotResult.frame_fresh
                      ? "bg-emerald-500/10 text-emerald-200/80 ring-emerald-500/30"
                      : "bg-zinc-700/40 text-zinc-300/80 ring-zinc-500/40"
                  }`}
                  title={
                    spotResult.frame_fresh
                      ? "Live HLS frame (yt-dlp + ffmpeg path)"
                      : "Latest published thumbnail (YouTube refreshes every few minutes; HLS path blocked by YouTube anti-bot on Cloud Run)"
                  }
                >
                  {spotResult.frame_fresh ? "LIVE" : "RECENT"} · {spotResult.frame_sha.slice(0, 8)}
                </span>
              )}
            </div>
            <button
              type="button"
              onClick={() => {
                setSpotResult(null);
                setSpotState("idle");
                setSpotMessage("");
              }}
              className="text-[11px] text-zinc-400 hover:text-zinc-100 px-1.5 leading-none"
              aria-label="Dismiss spot result"
            >
              ✕
            </button>
          </div>
          <div className="text-base font-semibold text-zinc-100 leading-tight">
            {spotResult.speciesLabel}
            {spotResult.topConfidence > 0 && (
              <span className="ml-1.5 text-[10px] text-zinc-400 font-normal">
                · {Math.round(spotResult.topConfidence * 100)}% conf
              </span>
            )}
          </div>
          {spotResult.behaviors.length > 0 && (
            <div className="text-[10px] text-zinc-400 mt-0.5">
              behaviors: {spotResult.behaviors.join(", ")}
            </div>
          )}
          {spotResult.threatSignals.length > 0 && (
            <div className="text-[10px] text-rose-300 mt-0.5">
              threat signals: {spotResult.threatSignals.join(", ")}
            </div>
          )}
          {spotResult.falsifier && (
            <div className="text-[10px] text-zinc-400 mt-2">
              <span className="text-zinc-500">Falsifier:</span>{" "}
              <span
                className={
                  spotResult.falsifier.verdict === "dissent"
                    ? "text-rose-300"
                    : spotResult.falsifier.verdict === "abstain"
                      ? "text-amber-300"
                      : "text-emerald-300"
                }
              >
                {spotResult.falsifier.verdict}
              </span>
            </div>
          )}
          {spotResult.requires_escalation && (
            <div className="mt-2 space-y-1 text-[10px]">
              <div className="text-zinc-500 uppercase tracking-wider text-[9px]">
                4-peer fan-out · all live
              </div>
              {spotResult.rangerUnit && (
                <div className="flex items-baseline gap-2">
                  <span className="text-emerald-400 shrink-0">●</span>
                  <span className="text-zinc-300">
                    Park Service: ranger <span className="font-mono">{spotResult.rangerUnit}</span>
                    {spotResult.rangerEta ? ` · ETA ${spotResult.rangerEta}m` : ""}
                  </span>
                </div>
              )}
              {spotResult.tnfdFilingId && (
                <div className="flex items-baseline gap-2">
                  <span className="text-emerald-400 shrink-0">●</span>
                  <span className="text-zinc-300">
                    Sponsor TNFD:{" "}
                    {spotResult.boardSlideUrl ? (
                      <a
                        href={spotResult.boardSlideUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="font-mono underline text-amber-200"
                      >
                        {spotResult.tnfdFilingId}
                      </a>
                    ) : (
                      <span className="font-mono">{spotResult.tnfdFilingId}</span>
                    )}
                  </span>
                </div>
              )}
              {spotResult.funderReceiptId && (
                <div className="flex items-baseline gap-2">
                  <span className="text-emerald-400 shrink-0">●</span>
                  <span className="text-zinc-300">
                    Funder: <span className="font-mono">{spotResult.funderReceiptId}</span>
                  </span>
                </div>
              )}
              {spotResult.neighborHandoffId && (
                <div className="flex items-baseline gap-2">
                  <span className="text-emerald-400 shrink-0">●</span>
                  <span className="text-zinc-300">
                    Neighbor Park: <span className="font-mono">{spotResult.neighborHandoffId}</span>
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      )}
      {/* Bottom subtitle + v6 Spot Now button on the real live cam */}
      <div className="absolute bottom-0 left-0 right-0 px-3 py-2 bg-gradient-to-t from-black via-black/85 to-transparent z-10">
        <div className="flex items-end justify-between gap-2">
          <div className="min-w-0">
            <div
              className="text-[10px] uppercase tracking-wider font-semibold truncate"
              style={{ color: cam.accent }}
            >
              {cam.subtitle}
            </div>
            {cam.realLive && spotState !== "idle" && (
              <div
                className={`mt-1 text-[10px] truncate ${
                  spotState === "done"
                    ? "text-emerald-300"
                    : spotState === "error"
                      ? "text-rose-300"
                      : "text-amber-300 animate-pulse"
                }`}
                title={spotMessage}
              >
                {spotState === "running" ? "● " : ""}
                {spotMessage}
              </div>
            )}
          </div>
          {cam.realLive && cam.youtubeId && (
            <div className="flex items-center gap-1.5 shrink-0">
              <button
                type="button"
                onClick={toggleAuto}
                className={`flex items-center gap-1 px-2 py-1 rounded text-[10px] font-semibold uppercase tracking-wider ring-1 transition-colors ${
                  autoSpot
                    ? "bg-amber-500/30 text-amber-100 ring-amber-500/60 animate-pulse"
                    : "bg-zinc-800/60 text-zinc-300 ring-zinc-600/60 hover:bg-zinc-700/60"
                }`}
                title={
                  autoSpot
                    ? `Auto-spot ON · runs every ${AUTO_SPOT_INTERVAL_MS / 1000}s · click to stop`
                    : "Auto-spot the live cam every 60s. Real frames, real agents."
                }
              >
                <Repeat className="w-3 h-3" />
                {autoSpot ? "Auto: ON" : "Auto"}
              </button>
              <button
                type="button"
                onClick={handleSpot}
                disabled={spotState === "running"}
                className={`flex items-center gap-1 px-2.5 py-1 rounded text-[10px] font-semibold uppercase tracking-wider ring-1 transition-colors ${
                  spotState === "running"
                    ? "bg-amber-500/20 text-amber-200 ring-amber-500/50 animate-pulse cursor-wait"
                    : "bg-emerald-500/20 text-emerald-200 ring-emerald-500/50 hover:bg-emerald-500/30"
                }`}
                title="Pull the live cam's latest frame, run Gemini Vision + Falsifier. Escalates only on threats or IUCN/CITES hot-list species."
              >
                <Sparkles className="w-3 h-3" />
                {spotState === "running" ? "Spotting…" : "Spot Now"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function LiveCams() {
  return (
    <div className="h-full overflow-hidden bg-black flex flex-col">
      <div className="px-6 py-3 border-b border-zinc-900 flex items-baseline justify-between">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-[0.15em] text-zinc-200">
            Live Field Cameras
          </h2>
          <p className="text-[11px] text-zinc-500 mt-0.5">
            3 Veo 3.1 Fast loops + 1 live YouTube embed · what the Stream Watcher & Audio Agent see in production
          </p>
        </div>
        <div className="text-[10px] text-zinc-500 font-mono">
          4 of 187 sponsored-reserve cameras shown
        </div>
      </div>
      <div className="flex-1 p-4 grid grid-cols-2 grid-rows-2 gap-4 min-h-0">
        {CAMS.map((cam) => (
          <CamTile key={cam.id} cam={cam} />
        ))}
      </div>
      <div className="px-6 py-2 border-t border-zinc-900 text-[10px] text-zinc-500 flex items-center justify-between">
        <span>
          1 real (YouTube live · Wild Africa) · 3 rendered via{" "}
          <span className="text-zinc-300">Veo 3.1 Fast</span>{" "}
          (Vertex AI) · audio-off · 16:9 1080p
        </span>
        <span className="font-mono">3 × $0.60 Veo · 1 × $0 YouTube embed</span>
      </div>
    </div>
  );
}
