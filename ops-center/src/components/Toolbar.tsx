"use client";

import { useEffect, useState } from "react";
import { Play, LogIn, LogOut, ShieldCheck } from "lucide-react";
import type { User } from "firebase/auth";
import { getFirebase, signInWithGoogle, signOutUser } from "@/lib/firebase";
import type { DemoScenario } from "@/types/events";

interface Props {
  scenarios: DemoScenario[];
  onRunScenario: (id: string) => void;
  runningId: string | null;
  autoCycleActive?: boolean;
  ambientReady?: boolean;
}

export default function Toolbar({ scenarios, onRunScenario, runningId, autoCycleActive, ambientReady }: Props) {
  const [user, setUser] = useState<User | null>(null);
  const [authConfigured, setAuthConfigured] = useState(false);

  useEffect(() => {
    let unsub: (() => void) | null = null;
    (async () => {
      const { auth, configured } = await getFirebase();
      setAuthConfigured(configured);
      if (auth) {
        const { onAuthStateChanged } = await import("firebase/auth");
        unsub = onAuthStateChanged(auth, setUser);
      }
    })();
    return () => unsub?.();
  }, []);

  return (
    <header className="px-5 py-3 bg-zinc-950 border-b border-zinc-800 flex items-center gap-4">
      <div className="flex items-center gap-2">
        <ShieldCheck className="w-5 h-5 text-emerald-400" />
        <div className="leading-tight">
          <div className="text-sm font-semibold text-zinc-100">
            GUARDIAN Operations Center
          </div>
          <div className="text-[10px] uppercase tracking-wider text-zinc-500">
            Multi-agent biodiversity defense · live demo
          </div>
        </div>
      </div>

      {autoCycleActive && (
        <span className="ml-4 px-2 py-0.5 rounded text-[10px] uppercase tracking-wider bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-500/40 animate-pulse">
          ● AUTO DEMO
        </span>
      )}
      {ambientReady && (
        <span
          className="ml-2 px-2 py-0.5 rounded text-[10px] uppercase tracking-wider bg-zinc-800/60 text-zinc-400 ring-1 ring-zinc-700/40"
          title="Lyria 2 ambient bed (Vertex AI)"
        >
          ♪ AMBIENT
        </span>
      )}

      <div className="ml-6 flex items-center gap-2">
        {scenarios.map((s) => (
          <button
            key={s.id}
            onClick={() => onRunScenario(s.id)}
            disabled={runningId !== null}
            title={s.narrative}
            className={`group flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium ring-1 transition-colors
              ${runningId === s.id
                ? "bg-amber-500/20 text-amber-300 ring-amber-500/40 animate-pulse"
                : "bg-zinc-800/80 text-zinc-200 ring-zinc-700/60 hover:bg-amber-500/20 hover:text-amber-200 hover:ring-amber-500/40"}
              ${runningId !== null && runningId !== s.id ? "opacity-40 cursor-not-allowed" : "cursor-pointer"}
            `}
          >
            <Play className="w-3 h-3" />
            <span>{s.title.split(" — ")[0]}</span>
          </button>
        ))}
      </div>

      <div className="ml-auto flex items-center gap-3">
        {!authConfigured && process.env.NEXT_PUBLIC_DEMO_MODE !== "1" && (
          <span className="text-[10px] uppercase tracking-wider text-zinc-500">
            Anonymous demo · Firebase Auth not configured
          </span>
        )}
        {authConfigured && user && (
          <>
            <span className="text-xs text-zinc-300">{user.displayName ?? user.email}</span>
            <button
              onClick={() => signOutUser()}
              className="flex items-center gap-1 text-xs text-zinc-400 hover:text-zinc-200"
            >
              <LogOut className="w-3.5 h-3.5" />
              Sign out
            </button>
          </>
        )}
        {authConfigured && !user && (
          <button
            onClick={() => signInWithGoogle()}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs bg-zinc-800 text-zinc-200 hover:bg-zinc-700"
          >
            <LogIn className="w-3.5 h-3.5" />
            Sign in with Google
          </button>
        )}
      </div>
    </header>
  );
}
