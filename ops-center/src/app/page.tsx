"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
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

export default function Home() {
  const [events, setEvents] = useState<GuardianEvent[]>([]);
  const [status, setStatus] = useState<FirehoseStatus>("disconnected");
  const [scenarios, setScenarios] = useState<DemoScenario[]>([]);
  const [runningScenarioId, setRunningScenarioId] = useState<string | null>(null);
  const [activeReserveId, setActiveReserveId] = useState<string | null>(null);
  const [fanOutFiring, setFanOutFiring] = useState(false);
  const [incidents, setIncidents] = useState<ActiveIncident[]>([]);

  // 1. Bootstrap: fetch scenario list + start firehose
  useEffect(() => {
    let cancelled = false;
    fetch(`${ORCH_URL}/demo/scenarios`)
      .then((r) => r.json())
      .then((body) => {
        if (!cancelled) setScenarios(body.scenarios ?? []);
      })
      .catch(() => {
        // Orchestrator probably needs CORS or is starting up.
      });

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
        // New scenario starting (not the :complete event)
        if (!latest.tool?.endsWith(":complete")) {
          setIncidents((prev) => [
            ...prev.filter((i) => i.incident_id !== latest.incident_id),
            {
              incident_id: latest.incident_id!,
              scenario_id: scenarioId,
              title: payload.title as string,
              severity: latest.severity,
              narrative: (payload.narrative as string) ?? "",
              startedAt: Date.now(),
            },
          ]);
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
          return inc;
        }),
      );

      // Once both peers responded, stop the fan-out animation after a beat
      setTimeout(() => setFanOutFiring(false), 4000);
    }
  }, [events]);

  // 3. Active reserve fades back to null when an incident is fully resolved
  useEffect(() => {
    const incidentInProgress = incidents.some((i) => !i.ranger || !i.tnfd);
    if (!incidentInProgress) {
      const t = setTimeout(() => setActiveReserveId(null), 6000);
      return () => clearTimeout(t);
    }
  }, [incidents]);

  // 4. Reset running scenario flag when a :complete event arrives
  useEffect(() => {
    if (events.length === 0) return;
    const latest = events[events.length - 1];
    if (latest.tool?.endsWith(":complete")) setRunningScenarioId(null);
  }, [events]);

  const runScenario = useCallback(
    async (id: string) => {
      setRunningScenarioId(id);
      try {
        const res = await fetch(`${ORCH_URL}/demo/run/${id}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        });
        if (!res.ok) {
          throw new Error(`Demo scenario failed: ${res.status}`);
        }
        await res.json().catch(() => null);
        // The :complete event arrives on the firehose and resets running flag.
      } catch (err) {
        console.error(err);
        setRunningScenarioId(null);
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
          <ReserveMap activeReserveId={activeReserveId} fanOutFiring={fanOutFiring} />
        </div>
        <EventStream events={visibleEvents} status={status} />
      </div>
    </div>
  );
}
