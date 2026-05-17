"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import dynamic from "next/dynamic";

import MissionBridge from "@/components/MissionBridge";
import ChasePath from "@/components/ChasePath";
import EventStream from "@/components/EventStream";
import BuiltOnGoogleCloud from "@/components/BuiltOnGoogleCloud";
import IncidentPanel, { type ActiveIncident } from "@/components/IncidentPanel";
import LiveCams from "@/components/LiveCams";
import TabStrip, { type TabId } from "@/components/TabStrip";
import Toolbar from "@/components/Toolbar";
import { FirehoseClient, type FirehoseStatus } from "@/lib/firehose";
import { reserveForScenario } from "@/lib/reserves";
import type { DemoScenario, GuardianEvent, IncidentRecord } from "@/types/events";

// Map is client-only (mapbox-gl needs window). Dynamic import with ssr:false.
const ReserveMap = dynamic(() => import("@/components/ReserveMap"), { ssr: false });

const ORCH_URL = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL ?? "http://localhost:8000";

// Cap how many incidents we keep mounted at once. Codex challenge 2026-05-15
// flagged unbounded growth during long-running demo sessions; this keeps the
// DOM + memory bounded without losing the active scenario.
const MAX_VISIBLE_INCIDENTS = 5;

// Auto-Cycle Demo Mode: when a judge lands on the public URL and doesn't
// click anything for AUTO_CYCLE_IDLE_MS, scenarios start firing automatically
// so the page is always alive. Any manual scenario click counts as activity
// and resets the idle clock — the cycle then picks back up after the next
// idle window. Locked 2026-05-17 (PLAN_V3.md Move 0). Disabled in tests via
// NEXT_PUBLIC_DISABLE_AUTOCYCLE=1 if it ever becomes a nuisance.
const AUTO_CYCLE_IDLE_MS = 10_000;

export default function Home() {
  const [events, setEvents] = useState<GuardianEvent[]>([]);
  const [status, setStatus] = useState<FirehoseStatus>("disconnected");
  const [scenarios, setScenarios] = useState<DemoScenario[]>([]);
  const [runningScenarioId, setRunningScenarioId] = useState<string | null>(null);
  const [activeReserveId, setActiveReserveId] = useState<string | null>(null);
  const [fanOutFiring, setFanOutFiring] = useState(false);
  const [activePeers, setActivePeers] = useState<string[]>([]);
  const [incidents, setIncidents] = useState<ActiveIncident[]>([]);
  const [autoCycleActive, setAutoCycleActive] = useState(false);
  const [activeTab, setActiveTab] = useState<TabId>("operations");
  const lastActivityRef = useRef<number>(Date.now());
  const autoCycleIdxRef = useRef<number>(0);
  // Buffer for Falsifier verdicts that arrive BEFORE their incident_event.
  // Codex Move 1 handshake P1 fix. Adopted on next incident upsert.
  const pendingFalsifierRef = useRef<Map<string, ActiveIncident["falsifier"]>>(new Map());
  // v3.2 sub-move 7.5: ambientRef + ambientReady removed (Lyria bed killed
  // from Ops Center; lives in the demo video only).
  // Codex challenge 2026-05-15: setTimeout was scheduled inside an event
  // handler without cleanup. On unmount (or rapid back-to-back triggers),
  // the timeout could fire on an unmounted component → React warning + leak.
  // Track active timers via ref so we can cancel on unmount.
  const fanOutTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => () => {
    if (fanOutTimerRef.current) clearTimeout(fanOutTimerRef.current);
  }, []);

  // 1. Bootstrap: fetch scenario list (with retry) + start firehose.
  // Codex challenge 2026-05-15 flagged: original code had no retry on the
  // initial fetch, so a cold-start CORS / 503 made the toolbar permanently
  // empty. Retry up to 5x with exponential backoff before giving up.
  useEffect(() => {
    let cancelled = false;
    let retryTimer: ReturnType<typeof setTimeout> | null = null;

    const fetchScenarios = (attempt = 0) => {
      fetch(`${ORCH_URL}/demo/scenarios`)
        .then((r) => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          return r.json();
        })
        .then((body) => {
          if (!cancelled) setScenarios(body.scenarios ?? []);
        })
        .catch(() => {
          if (cancelled || attempt >= 5) return;
          const delay = Math.min(15_000, 1000 * 2 ** attempt) * (0.5 + Math.random() * 0.5);
          retryTimer = setTimeout(() => fetchScenarios(attempt + 1), delay);
        });
    };
    fetchScenarios();

    const client = new FirehoseClient(
      ORCH_URL,
      {
        onEvent: (evt) => setEvents((prev) => [...prev, evt].slice(-500)),
        onStatusChange: (s) => setStatus(s),
      },
    );
    client.start();
    return () => {
      cancelled = true;
      if (retryTimer) clearTimeout(retryTimer);
      client.stop();
    };
  }, []);

  // 2. React to events: drive map state + incident cards
  useEffect(() => {
    if (events.length === 0) return;
    const latest = events[events.length - 1];

    if (latest.kind === "incident_event") {
      const payload = latest.payload as Record<string, unknown>;
      const scenarioId = (payload.scenario_id ?? "") as string;
      const reserve = reserveForScenario(scenarioId);
      if (reserve) setActiveReserveId(reserve.id);

      if (scenarioId && latest.incident_id && payload.title) {
        // New scenario starting (not the :complete event). Cap visible
        // incidents so long-running demos don't grow the DOM unbounded
        // (codex challenge 2026-05-15 flagged the missing cap).
        if (!latest.tool?.endsWith(":complete")) {
          // Record which peers will fan out for this scenario, so the map
          // can draw the right arrows.
          const fanout = (payload.fanout as string[] | undefined) ?? [];
          if (fanout.length > 0) setActivePeers(fanout);
          setIncidents((prev) => {
            const without = prev.filter((i) => i.incident_id !== latest.incident_id);
            // Adopt any falsifier verdict that arrived before this event
            // (P1 race fix, codex Move 1 handshake).
            const buffered = pendingFalsifierRef.current.get(latest.incident_id!);
            if (buffered) pendingFalsifierRef.current.delete(latest.incident_id!);
            const next = [
              ...without,
              {
                incident_id: latest.incident_id!,
                scenario_id: scenarioId,
                title: payload.title as string,
                severity: latest.severity,
                narrative: (payload.narrative as string) ?? "",
                startedAt: Date.now(),
                expectedPeers: fanout,
                ...(buffered ? { falsifier: buffered } : {}),
              },
            ];
            // Keep most recent N; drop oldest if we exceed the cap.
            return next.length > MAX_VISIBLE_INCIDENTS
              ? next.slice(-MAX_VISIBLE_INCIDENTS)
              : next;
          });
        }
      }
    }

    // Falsifier verdict — populate the IncidentPanel chip from the
    // falsifier's tool_end event. PLAN_V3.md Move 1.5/1.6.
    // Codex Move 1 handshake P1: in /demo/run, the falsifier event fires
    // BEFORE the incident_event creates the inc record. Solution: buffer
    // the verdict, replay on the next incident_event for the same id.
    if (
      latest.kind === "tool_end" &&
      latest.agent === "falsifier" &&
      latest.tool === "review_dispatch" &&
      latest.incident_id
    ) {
      const payload = latest.payload as Record<string, unknown>;
      const verdictPayload =
        (payload?.result as Record<string, unknown> | undefined) ?? payload;
      const v = verdictPayload?.verdict as string | undefined;
      if (v === "concur" || v === "dissent" || v === "abstain") {
        const verdict = v as "concur" | "dissent" | "abstain";
        const severity_0_5 =
          (verdictPayload?.severity_0_5 as number | undefined) ?? 0;
        const reason =
          (verdictPayload?.dissent_reason as string | undefined) ?? "";
        const targetIid = latest.incident_id;
        setIncidents((prev) => {
          // If incident already exists, attach directly.
          if (prev.some((inc) => inc.incident_id === targetIid)) {
            return prev.map((inc) =>
              inc.incident_id === targetIid
                ? { ...inc, falsifier: { verdict, severity_0_5, reason } }
                : inc,
            );
          }
          // Otherwise, buffer the verdict so the next incident_event-driven
          // upsert (see useEffect below) can adopt it.
          pendingFalsifierRef.current.set(targetIid, { verdict, severity_0_5, reason });
          return prev;
        });
      }
    }

    // PLAN_V3_1 sub-move 6.2 — surface audio_agent classification onto the
    // incident card so the human-in-the-loop replay chip can render.
    if (
      latest.kind === "tool_end" &&
      latest.agent === "audio_agent" &&
      latest.incident_id
    ) {
      const payload = latest.payload as Record<string, unknown>;
      const r = (payload?.result as Record<string, unknown> | undefined) ?? payload;
      const sc = r?.sound_class as string | undefined;
      const conf = r?.confidence as number | undefined;
      if (sc && typeof conf === "number") {
        const targetIid = latest.incident_id;
        setIncidents((prev) =>
          prev.map((inc) =>
            inc.incident_id === targetIid
              ? { ...inc, audio: { sound_class: sc, confidence: conf } }
              : inc,
          ),
        );
      }
    }

    if (latest.kind === "a2a_request") setFanOutFiring(true);

    if (latest.kind === "a2a_response" && latest.incident_id) {
      const payload = latest.payload as Record<string, unknown>;
      const peer = (latest.agent ?? "") as string;
      setIncidents((prev) =>
        prev.map((inc) => {
          if (inc.incident_id !== latest.incident_id) return inc;
          if (peer === "park_service" && payload.status === "dispatched") {
            return {
              ...inc,
              ranger: {
                unit: (payload.ranger_unit as string) ?? "?",
                eta_min: (payload.estimated_arrival_minutes as number) ?? 0,
                status: "dispatched",
              },
            };
          }
          if (peer === "sponsor_sustainability" && payload.status === "filed") {
            return {
              ...inc,
              tnfd: {
                filing_id: (payload.filing_id as string) ?? "?",
                materiality: (payload.materiality as string) ?? "?",
                status: "filed",
                board_slide_url: (payload.board_slide_url as string) ?? undefined,
              },
            };
          }
          if (peer === "funder_reporter" && payload.status === "filed") {
            return {
              ...inc,
              funder: {
                receipt_id: (payload.receipt_id as string) ?? "?",
                program: (payload.funder_program as string) ?? "?",
                tier: (payload.impact_tier as string) ?? "?",
                status: "filed",
              },
            };
          }
          if (peer === "neighbor_park" && payload.status === "accepted") {
            return {
              ...inc,
              neighbor: {
                handoff_id: (payload.handoff_id as string) ?? "?",
                posture: (payload.posture as string) ?? "?",
                window_until: (payload.window_open_until as string) ?? "?",
                status: "accepted",
              },
            };
          }
          return inc;
        }),
      );

      // Fan-out animation lives until all expected peers respond OR a
      // :complete event arrives (handled in the :complete effect below).
      // Belt-and-suspenders 12s ceiling kills the animation if the
      // firehose dies mid-fanout so we don't burn a stuck UI in the demo.
      if (fanOutTimerRef.current) clearTimeout(fanOutTimerRef.current);
      fanOutTimerRef.current = setTimeout(() => {
        setFanOutFiring(false);
        setActivePeers([]);
      }, 12000);
    }
  }, [events]);

  // Peer-name → ActiveIncident slot key (the slot whose presence proves
  // that peer responded). Kept in sync with notify_* wiring in page.tsx.
  const peerSlot = (peer: string): keyof ActiveIncident | null => {
    if (peer === "park_service") return "ranger";
    if (peer === "sponsor_sustainability") return "tnfd";
    if (peer === "funder_reporter") return "funder";
    if (peer === "neighbor_park") return "neighbor";
    return null;
  };

  // 3. Active reserve fades back to null when EVERY expected peer for
  // every visible incident has filled its slot. Codex flagged that the
  // old check (!ranger || !tnfd) reset the reserve while the funder
  // and neighbor cards were still pending — premature cinema cut.
  const allIncidentsResolved = useMemo(() => {
    if (incidents.length === 0) return false;
    return incidents.every((inc) => {
      const expected = inc.expectedPeers ?? ["park_service", "sponsor_sustainability"];
      return expected.every((peer) => {
        const slot = peerSlot(peer);
        return slot ? inc[slot] !== undefined : true;
      });
    });
  }, [incidents]);

  useEffect(() => {
    if (allIncidentsResolved) {
      const t = setTimeout(() => setActiveReserveId(null), 6000);
      return () => clearTimeout(t);
    }
  }, [allIncidentsResolved]);

  // 3b. Kill the fan-out animation as soon as every expected peer on the
  // latest incident has responded — cleaner cinema than waiting for the
  // 12s belt-and-suspenders timer above.
  useEffect(() => {
    if (incidents.length === 0) return;
    const latest = incidents[incidents.length - 1];
    const expected = latest.expectedPeers ?? [];
    if (expected.length === 0) return;
    const allIn = expected.every((peer) => {
      const slot = peerSlot(peer);
      return slot ? latest[slot] !== undefined : true;
    });
    if (allIn) {
      if (fanOutTimerRef.current) clearTimeout(fanOutTimerRef.current);
      fanOutTimerRef.current = setTimeout(() => {
        setFanOutFiring(false);
        setActivePeers([]);
      }, 1500);
    }
  }, [incidents]);

  // 4. Reset running scenario flag + clean up fan-out state on :complete.
  useEffect(() => {
    if (events.length === 0) return;
    const latest = events[events.length - 1];
    if (latest.tool?.endsWith(":complete")) {
      setRunningScenarioId(null);
      // Defensive: :complete arrives after results — make sure animation
      // and active-peer arrows clear even if the per-incident gate didn't
      // catch it (e.g., one peer slot mapping is missing for a new peer).
      if (fanOutTimerRef.current) clearTimeout(fanOutTimerRef.current);
      fanOutTimerRef.current = setTimeout(() => {
        setFanOutFiring(false);
        setActivePeers([]);
      }, 2000);
    }
  }, [events]);

  const runScenario = useCallback(
    async (id: string) => {
      lastActivityRef.current = Date.now();
      setRunningScenarioId(id);
      // v5 producer feedback: 90s fallback reads as "menu frozen" when the
      // firehose stutters. Drop to 18s — just past the 15s server cooldown
      // so a legit second click is still gated, but the UI doesn't feel
      // locked for a minute and a half when a scenario silently fails.
      const fallbackResetMs = 18_000;
      const fallback = setTimeout(() => setRunningScenarioId((cur) => (cur === id ? null : cur)), fallbackResetMs);
      try {
        const res = await fetch(`${ORCH_URL}/demo/run/${id}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        });
        if (res.status === 429) {
          // Cooldown hit. Don't clear runningScenarioId — the previously-
          // running scenario is still in flight. Log and exit silently;
          // the firehose :complete event from the first run will reset us.
          console.warn(`Scenario ${id} on cooldown; first run still in flight`);
          // Clear the fallback only because we won't get the success path.
          // The firehose-driven reset is still expected.
          return;
        }
        if (!res.ok) {
          throw new Error(`Demo scenario failed: ${res.status}`);
        }
        await res.json().catch(() => null);
        // The :complete event arrives on the firehose and resets running flag.
      } catch (err) {
        console.error(err);
        // Only clear if the running scenario is still us (don't stomp a
        // newer click).
        setRunningScenarioId((cur) => (cur === id ? null : cur));
        clearTimeout(fallback);
      }
    },
    [],
  );

  const visibleEvents = useMemo(
    () => events.filter((e) => e.kind !== "heartbeat"),
    [events],
  );

  // 5. Auto-Cycle Demo Mode. When the user is idle for AUTO_CYCLE_IDLE_MS
  // and no scenario is running, fire the next scenario in rotation. Keeps
  // the public demo URL alive for judges who land without clicking.
  // Disabled if NEXT_PUBLIC_DISABLE_AUTOCYCLE=1 (e.g. for dev).
  useEffect(() => {
    if (process.env.NEXT_PUBLIC_DISABLE_AUTOCYCLE === "1") return;
    if (scenarios.length === 0) return;

    const checkInterval = setInterval(() => {
      if (runningScenarioId !== null) {
        // A scenario is in flight; treat that as activity so the cycle waits.
        lastActivityRef.current = Date.now();
        return;
      }
      const idle = Date.now() - lastActivityRef.current;
      if (idle >= AUTO_CYCLE_IDLE_MS) {
        const idx = autoCycleIdxRef.current % scenarios.length;
        autoCycleIdxRef.current += 1;
        setAutoCycleActive(true);
        runScenario(scenarios[idx].id);
      } else {
        setAutoCycleActive(false);
      }
    }, 1000);

    return () => clearInterval(checkInterval);
  }, [scenarios, runningScenarioId, runScenario]);

  // 6. Any user pointer / keyboard activity counts as "still here" — pauses
  // Auto-Cycle so the user can read incident cards without interruption.
  // (v3.2 sub-move 7.5: ambient-bed kickoff removed; no more page-load audio.)
  useEffect(() => {
    const onActivity = () => {
      lastActivityRef.current = Date.now();
      setAutoCycleActive(false);
    };
    window.addEventListener("pointerdown", onActivity);
    window.addEventListener("keydown", onActivity);
    window.addEventListener("wheel", onActivity, { passive: true });
    window.addEventListener("touchstart", onActivity, { passive: true });
    return () => {
      window.removeEventListener("pointerdown", onActivity);
      window.removeEventListener("keydown", onActivity);
      window.removeEventListener("wheel", onActivity);
      window.removeEventListener("touchstart", onActivity);
    };
  }, []);

  return (
    <div className="h-screen w-screen flex flex-col bg-black text-zinc-100">
      {/* v3.2 sub-move 7.5: ambient bed removed from Ops Center. Producer
          feedback "music doesn't make sense" + the agent narration via
          ElevenLabs (added in sub-move 7.4) is the right per-scenario
          audio cue. The Lyria bed remains in the demo VIDEO (Move 4)
          where it has narrative purpose. */}
      <Toolbar
        scenarios={scenarios}
        onRunScenario={runScenario}
        runningId={runningScenarioId}
        autoCycleActive={autoCycleActive}
        leadingChrome={<TabStrip active={activeTab} onChange={setActiveTab} />}
      />
      {activeTab === "operations" && (
        <div className="flex-1 grid grid-cols-[320px_1fr_360px] min-h-0">
          <IncidentPanel incidents={incidents} />
          <div className="relative h-full min-h-0">
            <ReserveMap
              activeReserveId={activeReserveId}
              fanOutFiring={fanOutFiring}
              activePeers={activePeers}
            />
            <ChasePath activeIncident={incidents.length > 0 ? incidents[incidents.length - 1] : null} />
          </div>
          <EventStream events={visibleEvents} status={status} />
        </div>
      )}
      {activeTab === "live-cams" && (
        <div className="flex-1 min-h-0">
          <LiveCams />
        </div>
      )}
      {activeTab === "mission-bridge" && (
        <div className="flex-1 min-h-0">
          <MissionBridge
            falsifierVerdict={
              incidents.length > 0
                ? incidents[incidents.length - 1].falsifier?.verdict ?? null
                : null
            }
          />
        </div>
      )}
      {/* v5: "Built on Google Cloud" strip persists across all tabs. Shows
          every product in the stack (Gemini Pro/Flash, Imagen, Veo, Lyria,
          Vertex AI Search, ADK, A2A, Cloud Run, BigQuery + ElevenLabs as
          3rd-party) with cost-per-call, role, and model ID. Live call
          counts tick when scenarios fire. */}
      <BuiltOnGoogleCloud events={visibleEvents} />
    </div>
  );
}
