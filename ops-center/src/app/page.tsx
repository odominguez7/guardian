"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import dynamic from "next/dynamic";

import EventStream from "@/components/EventStream";
import IncidentPanel, { type ActiveIncident } from "@/components/IncidentPanel";
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

export default function Home() {
  const [events, setEvents] = useState<GuardianEvent[]>([]);
  const [status, setStatus] = useState<FirehoseStatus>("disconnected");
  const [scenarios, setScenarios] = useState<DemoScenario[]>([]);
  const [runningScenarioId, setRunningScenarioId] = useState<string | null>(null);
  const [activeReserveId, setActiveReserveId] = useState<string | null>(null);
  const [fanOutFiring, setFanOutFiring] = useState(false);
  const [activePeers, setActivePeers] = useState<string[]>([]);
  const [incidents, setIncidents] = useState<ActiveIncident[]>([]);
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
      setRunningScenarioId(id);
      // Codex challenge 2026-05-15 (final) flagged: if the firehose dies or
      // :complete event is never received, the toolbar stays disabled
      // forever. Belt-and-suspenders timeout resets the running flag after
      // 90s regardless. The cooldown on the server is 15s so this is
      // generous but not infinite.
      const fallbackResetMs = 90_000;
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

  return (
    <div className="h-screen w-screen flex flex-col bg-black text-zinc-100">
      <Toolbar
        scenarios={scenarios}
        onRunScenario={runScenario}
        runningId={runningScenarioId}
      />
      <div className="flex-1 grid grid-cols-[320px_1fr_360px] min-h-0">
        <IncidentPanel incidents={incidents} />
        <div className="relative">
          <ReserveMap
            activeReserveId={activeReserveId}
            fanOutFiring={fanOutFiring}
            activePeers={activePeers}
          />
        </div>
        <EventStream events={visibleEvents} status={status} />
      </div>
    </div>
  );
}
