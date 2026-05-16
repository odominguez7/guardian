"use client";

import { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
// Mapbox CSS is loaded globally in app/globals.css (per Next.js App Router
// rules; client-component CSS imports can break builds in some toolchains).
import { RESERVES, PEER_ANCHORS } from "@/lib/reserves";

interface Props {
  activeReserveId: string | null;
  fanOutFiring: boolean;
  /** Names of peers actively being called in the current incident.
   *  Determines which fan-out arrows to draw. If empty + fanOutFiring=true,
   *  defaults to the 2-peer original set for backwards compat. */
  activePeers?: string[];
}

// Peer labels for the on-map markers (real-world anchors live in lib/reserves.ts)
const PEER_LABELS: Record<string, { name: string; org: string }> = {
  park_service: { name: "Park Service", org: "Dar es Salaam · TZ" },
  sponsor_sustainability: { name: "Sponsor Sustainability", org: "London · F500" },
  funder_reporter: { name: "Funder Reporter", org: "Geneva · CH" },
  neighbor_park: { name: "Neighbor Park", org: "Maasai Mara · KE" },
};

export default function ReserveMap({ activeReserveId, fanOutFiring, activePeers }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<Map<string, mapboxgl.Marker>>(new Map());
  const peerMarkersRef = useRef<Map<string, mapboxgl.Marker>>(new Map());
  const animationFrameRef = useRef<number | null>(null);

  const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;

  useEffect(() => {
    if (!containerRef.current || !token || mapRef.current) return;

    mapboxgl.accessToken = token;
    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/dark-v11",
      center: [25, -10],
      zoom: 3.1,
      attributionControl: true,
      cooperativeGestures: true,
    });
    mapRef.current = map;

    map.on("load", () => {
      // Add reserve markers
      for (const r of RESERVES) {
        const el = document.createElement("div");
        el.className =
          "w-4 h-4 rounded-full bg-emerald-400 border-2 border-emerald-200 shadow-[0_0_10px_rgba(52,211,153,0.6)] transition-all duration-300";
        el.title = `${r.name} — ${r.country}`;
        const marker = new mapboxgl.Marker({ element: el })
          .setLngLat(r.lngLat)
          .setPopup(
            new mapboxgl.Popup({ offset: 16, closeButton: false }).setHTML(
              `<div class="text-xs"><div class="font-semibold">${r.name}</div><div class="text-zinc-400">${r.country}</div><div class="text-zinc-500 mt-1">${r.flagshipSpecies.join(" · ")}</div></div>`,
            ),
          )
          .addTo(map);
        markersRef.current.set(r.id, marker);
      }

      // Source + layer for A2A fan-out lines
      map.addSource("a2a-lines", {
        type: "geojson",
        data: { type: "FeatureCollection", features: [] },
      });
      map.addLayer({
        id: "a2a-lines-layer",
        type: "line",
        source: "a2a-lines",
        paint: {
          "line-color": "#f59e0b",
          "line-width": 2,
          "line-opacity": 0.85,
          "line-dasharray": [0.5, 1.5],
        },
      });

      // Peer markers — hidden by default, fade in when their ack lands.
      // Sit at real-world coords (Dar es Salaam, London, Geneva, Maasai Mara).
      for (const [peerId, coords] of Object.entries(PEER_ANCHORS)) {
        const wrap = document.createElement("div");
        const label = PEER_LABELS[peerId];
        wrap.className = "peer-marker-wrap";
        wrap.style.opacity = "0";
        wrap.style.transition = "opacity 600ms ease-out";
        wrap.innerHTML = `
          <div style="display:flex;align-items:center;gap:6px;background:rgba(20,20,20,0.85);border:1px solid #f59e0b;border-radius:6px;padding:4px 8px;backdrop-filter:blur(4px);">
            <div style="width:8px;height:8px;border-radius:50%;background:#f59e0b;box-shadow:0 0 8px #f59e0b;"></div>
            <div style="font-size:11px;line-height:1.2;color:#fff;">
              <div style="font-weight:600;">${label?.name ?? peerId}</div>
              <div style="color:#a3a3a3;font-size:9px;">${label?.org ?? ""}</div>
            </div>
          </div>`;
        const marker = new mapboxgl.Marker({ element: wrap, anchor: "bottom" })
          .setLngLat(coords)
          .addTo(map);
        peerMarkersRef.current.set(peerId, marker);
      }
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [token]);

  // Pulse the active reserve marker
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    for (const [id, marker] of markersRef.current.entries()) {
      const el = marker.getElement();
      if (id === activeReserveId) {
        el.classList.remove("bg-emerald-400");
        el.classList.add("bg-amber-300", "animate-ping-slow", "scale-150");
      } else {
        el.classList.add("bg-emerald-400");
        el.classList.remove("bg-amber-300", "animate-ping-slow", "scale-150");
      }
    }
    if (activeReserveId) {
      const r = RESERVES.find((r) => r.id === activeReserveId);
      if (r) {
        // Frame Selous + all 4 peer markers (Africa + Europe) in one shot.
        // Center halfway between Tanzania and Western Europe; zoom out
        // enough to see London + Geneva at the top of the frame.
        const cinemaCenter: [number, number] = [
          (r.lngLat[0] + 5) / 2,         // ~20°E, midway between Selous (37°E) and Geneva (6°E)
          (r.lngLat[1] + 30) / 2,        // ~10°N, between Selous (-9°S) and Geneva (46°N)
        ];
        map.flyTo({ center: cinemaCenter, zoom: 2.6, speed: 1.0, curve: 1.4, duration: 1500 });
      }
    } else {
      // Reset to wide Africa view; also hide peer markers
      map.flyTo({ center: [25, -10], zoom: 3.1, speed: 1.0 });
      for (const m of peerMarkersRef.current.values()) {
        m.getElement().style.opacity = "0";
      }
    }
  }, [activeReserveId]);

  // A2A fan-out arrows
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !activeReserveId) return;
    const r = RESERVES.find((r) => r.id === activeReserveId);
    if (!r) return;

    if (fanOutFiring) {
      const peersToShow = activePeers && activePeers.length > 0
        ? activePeers
        : ["park_service", "sponsor_sustainability"];
      const features = peersToShow
        .filter((p) => PEER_ANCHORS[p])
        .map((peer) => ({
          type: "Feature" as const,
          properties: { peer },
          geometry: {
            type: "LineString" as const,
            coordinates: [r.lngLat, PEER_ANCHORS[peer]],
          },
        }));
      const src = map.getSource("a2a-lines") as mapboxgl.GeoJSONSource | undefined;
      if (src) {
        src.setData({ type: "FeatureCollection", features });
      }
      // Fade in peer markers in sequence (250ms staggered) for cinema feel
      peersToShow.forEach((peer, idx) => {
        const marker = peerMarkersRef.current.get(peer);
        if (marker) {
          setTimeout(() => {
            marker.getElement().style.opacity = "1";
          }, idx * 250);
        }
      });
    } else {
      const src = map.getSource("a2a-lines") as mapboxgl.GeoJSONSource | undefined;
      src?.setData({ type: "FeatureCollection", features: [] });
      for (const m of peerMarkersRef.current.values()) {
        m.getElement().style.opacity = "0";
      }
    }
  }, [fanOutFiring, activeReserveId, activePeers]);

  // Animate the dashed lines marching forward (offset cycle)
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !fanOutFiring) return;
    let offset = 0;
    const tick = () => {
      offset = (offset + 0.3) % 10;
      if (map.getLayer("a2a-lines-layer")) {
        try {
          map.setPaintProperty("a2a-lines-layer", "line-dasharray", [offset, 2]);
        } catch {
          // map may be disposing
        }
      }
      animationFrameRef.current = requestAnimationFrame(tick);
    };
    animationFrameRef.current = requestAnimationFrame(tick);
    return () => {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    };
  }, [fanOutFiring]);

  if (!token) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-zinc-900 text-zinc-400 p-8 text-center">
        <div className="max-w-md">
          <h2 className="text-xl font-semibold text-zinc-200 mb-2">
            Mapbox token required
          </h2>
          <p className="text-sm leading-relaxed">
            Add <code className="bg-zinc-800 px-1.5 py-0.5 rounded">NEXT_PUBLIC_MAPBOX_TOKEN</code>{" "}
            to the Cloud Run env vars for this service. The map + A2A
            fan-out visualization will light up immediately on next deploy.
          </p>
          <p className="text-xs text-zinc-500 mt-4">
            Get a token at <a href="https://account.mapbox.com/access-tokens/" className="underline text-amber-400">mapbox.com/access-tokens</a>.
            Free tier covers 50k map loads/month.
          </p>
        </div>
      </div>
    );
  }

  return <div ref={containerRef} className="w-full h-full" />;
}
