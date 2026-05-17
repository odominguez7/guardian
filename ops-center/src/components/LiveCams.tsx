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

import { useState, useRef } from "react";
import { Sparkles } from "lucide-react";

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

function CamTile({ cam }: { cam: CamProps }) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  // v6: "Spot Now" — POST the live thumbnail to /livecam/spot, which runs
  // Gemini 2.5 Pro vision on a fresh frame and fans the result out to all 4
  // A2A peers if anything material is detected.
  const [spotState, setSpotState] = useState<"idle" | "running" | "done" | "error">("idle");
  const [spotMessage, setSpotMessage] = useState<string>("");
  const handleSpot = async () => {
    if (!cam.youtubeId || spotState === "running") return;
    setSpotState("running");
    setSpotMessage("Pulling fresh frame…");
    try {
      const res = await fetch(`${ORCH_URL}/livecam/spot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ youtube_id: cam.youtubeId, cam_label: cam.label }),
      });
      if (res.status === 429) {
        const body = await res.json().catch(() => ({}));
        setSpotMessage(body.detail ?? "Cooldown — retry in a few seconds.");
        setSpotState("error");
        return;
      }
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const body = await res.json();
      const species = body?.vision?.primary_species?.common_name ?? "no clear subject";
      const escalated = body?.requires_escalation;
      setSpotMessage(
        escalated
          ? `Spotted: ${species} → fanned out to all 4 A2A peers`
          : `Spotted: ${species} (no escalation needed)`,
      );
      setSpotState("done");
    } catch (err) {
      setSpotMessage(err instanceof Error ? err.message : "Spot failed");
      setSpotState("error");
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
            <button
              type="button"
              onClick={handleSpot}
              disabled={spotState === "running"}
              className={`flex items-center gap-1 px-2.5 py-1 rounded text-[10px] font-semibold uppercase tracking-wider ring-1 transition-colors shrink-0 ${
                spotState === "running"
                  ? "bg-amber-500/20 text-amber-200 ring-amber-500/50 animate-pulse cursor-wait"
                  : "bg-emerald-500/20 text-emerald-200 ring-emerald-500/50 hover:bg-emerald-500/30"
              }`}
              title="Run Gemini Vision on a fresh frame from this live cam, then fan out to all 4 A2A peers"
            >
              <Sparkles className="w-3 h-3" />
              {spotState === "running" ? "Spotting…" : "Spot Now"}
            </button>
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
