// Pinned African wildlife reserves the Ops Center map visualizes.
// Coordinates are approximate park centroids (lng, lat for Mapbox).

export interface Reserve {
  id: string;
  name: string;
  country: string;
  lngLat: [number, number];
  flagshipSpecies: string[];
  // Maps a scenario_id to the reserve where it fires, so an incoming
  // incident_event can be visualized on the right pin.
  matchesScenarios?: string[];
}

export const RESERVES: Reserve[] = [
  {
    id: "serengeti",
    name: "Serengeti National Park",
    country: "Tanzania",
    lngLat: [34.8333, -2.3333],
    flagshipSpecies: ["African elephant", "Lion", "Cheetah"],
    matchesScenarios: ["poacher_truck"],
  },
  {
    id: "kruger",
    name: "Kruger National Park",
    country: "South Africa",
    lngLat: [31.5547, -23.9884],
    flagshipSpecies: ["Black rhinoceros", "White rhinoceros", "Lion"],
    matchesScenarios: ["audio_gunshot"],
  },
  {
    id: "etosha",
    name: "Etosha National Park",
    country: "Namibia",
    lngLat: [16.5, -19.0],
    flagshipSpecies: ["Cheetah", "Black rhinoceros", "Lion"],
    matchesScenarios: ["sponsored_species"],
  },
  {
    id: "okavango",
    name: "Okavango Delta",
    country: "Botswana",
    lngLat: [22.7, -19.3],
    flagshipSpecies: ["African elephant", "Lion"],
  },
  {
    id: "masai-mara",
    name: "Maasai Mara",
    country: "Kenya",
    lngLat: [35.05, -1.5],
    flagshipSpecies: ["Lion", "African elephant"],
  },
  {
    id: "selous",
    name: "Selous (Nyerere) Game Reserve",
    country: "Tanzania",
    lngLat: [37.3, -9.0],
    flagshipSpecies: ["African elephant", "Lion"],
  },
];

export function reserveForScenario(scenarioId: string): Reserve | undefined {
  return RESERVES.find((r) => r.matchesScenarios?.includes(scenarioId));
}
