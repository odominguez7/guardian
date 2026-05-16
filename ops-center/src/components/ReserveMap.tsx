"use client";

import { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
// Mapbox CSS is loaded globally in app/globals.css (per Next.js App Router
// rules; client-component CSS imports can break builds in some toolchains).
import { RESERVES } from "@/lib/reserves";

interface Props {
  activeReserveId: string | null;
  fanOutFiring: boolean;
  /** Names of peers actively being called in the current incident.
   *  Determines which fan-out arrows to draw. If empty + fanOutFiring=true,
   *  defaults to the 2-peer original set for backwards compat. */
  activePeers?: string[];
}

// Peer service icons (placeholder coords — sit at the corners of the map
// for the A2A fan-out arrows). These aren't real-world locations, they're
// map anchors for the demo animation. 4 peers = 4 corners.
const PEER_ANCHORS: Record<string, [number, number]> = {
  park_service: [-5, 8],            // top-left (rangers)
  sponsor_sustainability: [55, 8],  // top-right (F500 sponsor)
  funder_reporter: [-5, -32],       // bottom-left (funder dashboard)
  neighbor_park: [55, -32],         // bottom-right (adjacent park)
};

export default function ReserveMap({ activeReserveId, fanOutFiring, activePeers }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<Map<string, mapboxgl.Marker>>(new Map());
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
        map.flyTo({ center: r.lngLat, zoom: 5, speed: 1.2, curve: 1.4 });
      }
    } else {
      map.flyTo({ center: [25, -10], zoom: 3.1, speed: 1.0 });
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
    } else {
      const src = map.getSource("a2a-lines") as mapboxgl.GeoJSONSource | undefined;
      src?.setData({ type: "FeatureCollection", features: [] });
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
