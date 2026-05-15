// GUARDIAN event firehose schema — mirrors app/events.py.
// Keep in sync.

export type EventKind =
  | "tool_start"
  | "tool_end"
  | "agent_transfer"
  | "a2a_request"
  | "a2a_response"
  | "incident_event"
  | "heartbeat";

export type Severity = "critical" | "high" | "medium" | "low" | "info" | "error";

export interface GuardianEvent {
  id: string;
  ts: string; // ISO 8601 UTC
  kind: EventKind;
  agent: string;
  tool: string | null;
  incident_id: string | null;
  severity: Severity;
  payload: Record<string, unknown>;
  latency_ms: number | null;
}

export interface DemoScenario {
  id: string;
  title: string;
  narrative: string;
}

export interface IncidentRecord {
  incident_id: string;
  scenario_id: string;
  title: string;
  park_service: Record<string, unknown>;
  sponsor_sustainability: Record<string, unknown>;
}
