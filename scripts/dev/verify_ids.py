"""Verify the GUARDIAN demo endpoint is deterministic.

Hits POST /demo/run/multimodal_pipeline N times and asserts every ID family
stays stable across calls. Used to back the video's "every on-screen ID
comes from a live, reproducible call to a public endpoint" claim.

Usage:
    python scripts/dev/verify_ids.py
    python scripts/dev/verify_ids.py --runs 20
    python scripts/dev/verify_ids.py --url https://staging-...run.app

Auth: uses `gcloud auth print-identity-token` automatically.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any

DEFAULT_URL = "https://guardian-180171737110.us-central1.run.app"
SCENARIO = "multimodal_pipeline"
TIMEOUT_S = 60

# Path through the response → ID we want to assert stable across calls.
ID_PATHS: dict[str, tuple[str, ...]] = {
    "incident_id": ("incident_id",),
    "ranger_unit": ("park_service", "ranger_unit"),
    "filing_id": ("sponsor_sustainability", "filing_id"),
    "funder_receipt_id": ("funder_reporter", "receipt_id"),
    "neighbor_handoff_id": ("neighbor_park", "handoff_id"),
}


def gcloud_identity_token() -> str:
    out = subprocess.run(
        ["gcloud", "auth", "print-identity-token"],
        check=True, capture_output=True, text=True,
    )
    return out.stdout.strip()


def call_once(base_url: str, token: str) -> dict[str, Any]:
    req = urllib.request.Request(
        f"{base_url}/demo/run/{SCENARIO}",
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data=b"",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    cur: Any = data
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--url", default=DEFAULT_URL)
    p.add_argument("--runs", type=int, default=10)
    p.add_argument("--cooldown", type=float, default=16.0,
                   help="Seconds between calls (demo endpoint has 15s lock).")
    args = p.parse_args()

    print(f"verifying {args.url}/demo/run/{SCENARIO} across {args.runs} calls…")
    token = gcloud_identity_token()

    runs: list[dict[str, Any]] = []
    for i in range(args.runs):
        try:
            data = call_once(args.url, token)
        except urllib.error.HTTPError as e:
            print(f"  run {i+1}: HTTP {e.code} {e.reason}")
            return 2
        except Exception as e:
            print(f"  run {i+1}: {e!r}")
            return 2

        snapshot = {name: extract(data, path) for name, path in ID_PATHS.items()}
        runs.append(snapshot)
        print(f"  run {i+1:>2}: " + " · ".join(f"{k}={v}" for k, v in snapshot.items()))
        if i < args.runs - 1:
            import time
            time.sleep(args.cooldown)

    print()
    failures = []
    for name in ID_PATHS:
        values = {r[name] for r in runs}
        status = "✅ stable" if len(values) == 1 else f"❌ varies ({len(values)} distinct)"
        print(f"  {name:24s} {status}")
        if len(values) > 1:
            failures.append((name, values))

    if failures:
        print("\nNOT DETERMINISTIC. The 'reproducible' claim is unsafe to ship "
              "until these IDs are seeded:")
        for name, values in failures:
            print(f"  - {name}: {values}")
        return 1

    print("\nAll ID families deterministic across {} calls. The reproducibility "
          "claim is fully defensible.".format(args.runs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
