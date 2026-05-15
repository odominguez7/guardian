// WebSocket client for the GUARDIAN event firehose.
// - Connects to NEXT_PUBLIC_ORCHESTRATOR_URL/events/stream
// - Auto-reconnects with exponential backoff on disconnect
// - Falls back to HTTP polling on /events/replay when WS is unavailable
// - Sends a Firebase ID token in the URL when the user is authed; the
//   backend will need to accept token-in-url because browsers can't set
//   Authorization headers on WebSocket upgrades.

import type { GuardianEvent } from "@/types/events";

export interface FirehoseHandlers {
  onEvent: (event: GuardianEvent) => void;
  onStatusChange?: (status: FirehoseStatus) => void;
}

export type FirehoseStatus = "connecting" | "connected" | "disconnected" | "fallback-polling";

const POLL_INTERVAL_MS = 3000;
const RECONNECT_MAX_DELAY_MS = 15_000;

export class FirehoseClient {
  private ws: WebSocket | null = null;
  private pollTimer: ReturnType<typeof setInterval> | null = null;
  private reconnectAttempts = 0;
  private closed = false;
  private seenIds = new Set<string>();

  constructor(
    private orchestratorUrl: string,
    private handlers: FirehoseHandlers,
    private idToken: string | null = null,
  ) {}

  start(): void {
    this.closed = false;
    this.connect();
  }

  stop(): void {
    this.closed = true;
    this.ws?.close();
    if (this.pollTimer) clearInterval(this.pollTimer);
  }

  setIdToken(token: string | null): void {
    this.idToken = token;
    // Reconnect with the new token so server-side filtering uses fresh creds.
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.close();
    }
  }

  private setStatus(status: FirehoseStatus) {
    this.handlers.onStatusChange?.(status);
  }

  private dispatch(event: GuardianEvent) {
    if (event.kind === "heartbeat") return;
    if (this.seenIds.has(event.id)) return;
    this.seenIds.add(event.id);
    if (this.seenIds.size > 2000) {
      // Keep the set bounded.
      const arr = Array.from(this.seenIds);
      this.seenIds = new Set(arr.slice(-1000));
    }
    this.handlers.onEvent(event);
  }

  private connect(): void {
    const wsUrl = this.buildWsUrl();
    this.setStatus("connecting");
    try {
      this.ws = new WebSocket(wsUrl);
    } catch {
      this.startPolling();
      return;
    }

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      this.setStatus("connected");
      if (this.pollTimer) {
        clearInterval(this.pollTimer);
        this.pollTimer = null;
      }
    };

    this.ws.onmessage = (msg) => {
      try {
        const evt = JSON.parse(msg.data) as GuardianEvent;
        this.dispatch(evt);
      } catch {
        // ignore malformed frames
      }
    };

    this.ws.onerror = () => {
      // Will trigger onclose; reconnect logic lives there.
    };

    this.ws.onclose = () => {
      if (this.closed) return;
      this.setStatus("disconnected");
      this.scheduleReconnect();
    };
  }

  private scheduleReconnect(): void {
    if (this.closed) return;
    this.reconnectAttempts += 1;
    // Exponential backoff with full jitter so a fleet of clients doesn't
    // reconnect in sync after an outage (codex challenge 2026-05-15 flagged
    // the deterministic backoff as a reconnect-storm risk).
    const base = Math.min(
      RECONNECT_MAX_DELAY_MS,
      500 * 2 ** Math.min(this.reconnectAttempts, 6),
    );
    const delay = Math.floor(base * (0.5 + Math.random() * 0.5));
    setTimeout(() => {
      if (this.closed) return;
      // After 3 failed WS attempts, fall back to HTTP polling so the UI
      // keeps showing events even on networks that block upgrades. Stop the
      // poller before reconnecting so they don't run in parallel.
      if (this.reconnectAttempts >= 3 && !this.pollTimer) {
        this.startPolling();
      }
      this.connect();
    }, delay);
  }

  private async startPolling(): Promise<void> {
    this.setStatus("fallback-polling");
    if (this.pollTimer) return;
    this.pollTimer = setInterval(() => {
      void this.pollOnce();
    }, POLL_INTERVAL_MS);
    void this.pollOnce();
  }

  private async pollOnce(): Promise<void> {
    try {
      const res = await fetch(`${this.orchestratorUrl}/events/replay`, {
        headers: this.idToken ? { Authorization: `Bearer ${this.idToken}` } : {},
        cache: "no-store",
      });
      if (!res.ok) return;
      const body = (await res.json()) as { events: GuardianEvent[] };
      for (const evt of body.events ?? []) this.dispatch(evt);
    } catch {
      // ignore; next poll will retry
    }
  }

  private buildWsUrl(): string {
    const base = this.orchestratorUrl.replace(/^http/, "ws");
    const sep = base.includes("?") ? "&" : "?";
    return this.idToken
      ? `${base}/events/stream${sep}token=${encodeURIComponent(this.idToken)}`
      : `${base}/events/stream`;
  }
}
