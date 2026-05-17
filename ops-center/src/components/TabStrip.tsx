"use client";

// PLAN_V3_2 sub-move 7.1 — Vision Pro segmented control for top-level
// navigation between Operations / Live Cams / Agent Theater. Frosted
// backdrop-blur, sliding amber indicator, no emoji icons (thin Lucide
// glyphs at 14px). Replaces the "tabs look old" scenario-button strip
// per producer feedback.

import { Monitor, Video, Users } from "lucide-react";

export type TabId = "operations" | "live-cams" | "agent-theater";

interface Props {
  active: TabId;
  onChange: (id: TabId) => void;
}

const TABS: { id: TabId; label: string; icon: React.ReactNode }[] = [
  { id: "operations", label: "Operations", icon: <Monitor className="w-3.5 h-3.5" strokeWidth={1.6} /> },
  { id: "live-cams", label: "Live Cams", icon: <Video className="w-3.5 h-3.5" strokeWidth={1.6} /> },
  { id: "agent-theater", label: "Agent Theater", icon: <Users className="w-3.5 h-3.5" strokeWidth={1.6} /> },
];

export default function TabStrip({ active, onChange }: Props) {
  return (
    <div
      className="inline-flex items-center gap-1 p-1 rounded-xl"
      style={{
        background: "rgba(255,255,255,0.04)",
        backdropFilter: "blur(24px) saturate(1.6)",
        WebkitBackdropFilter: "blur(24px) saturate(1.6)",
        border: "1px solid rgba(255,255,255,0.06)",
      }}
      role="tablist"
    >
      {TABS.map((tab) => {
        const selected = active === tab.id;
        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={selected}
            onClick={() => onChange(tab.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium tracking-[0.02em] transition-all duration-200
              ${selected
                ? "text-white bg-white/[0.08]"
                : "text-white/55 hover:text-white/85 hover:bg-white/[0.03]"
              }`}
            style={
              selected
                ? {
                    boxShadow:
                      "0 0 0 1px rgba(245,158,11,0.45), 0 0 18px rgba(245,158,11,0.18)",
                  }
                : undefined
            }
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
}
