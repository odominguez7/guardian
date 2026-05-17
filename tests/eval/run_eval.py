"""Direct ADK eval runner — sidesteps the adk-eval CLI module-loading quirk.

The CLI does `agent_module.agent.root_agent` which forced us to add
`from . import agent` to app/__init__.py, which then claimed specialists
twice and broke. This runner loads root_agent directly and calls
AgentEvaluator, so app/__init__.py stays empty.

Usage:
    uv run python tests/eval/run_eval.py                          # all evalsets
    uv run python tests/eval/run_eval.py basic                    # one evalset by name
    uv run python tests/eval/run_eval.py basic falsifier          # multiple by name

Exit code 0 = all pass. Non-zero = at least one failure.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add repo root so `from app.agent import root_agent` resolves.
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from google.adk.evaluation.agent_evaluator import AgentEvaluator  # noqa: E402
from google.adk.evaluation.eval_config import EvalConfig  # noqa: E402
from google.adk.evaluation.eval_set import EvalSet  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

EVALSETS_DIR = ROOT / "tests" / "eval" / "evalsets"
EVAL_CONFIG_PATH = ROOT / "tests" / "eval" / "eval_config.json"


def load_eval_config() -> EvalConfig:
    with open(EVAL_CONFIG_PATH) as fh:
        return EvalConfig.model_validate(json.load(fh))


def discover_evalsets(names: list[str]) -> list[Path]:
    """If `names` is empty, return all *.evalset.json. Otherwise filter by stem."""
    files = sorted(EVALSETS_DIR.glob("*.evalset.json"))
    if not names:
        return files
    wanted = {n.removesuffix(".evalset.json") for n in names}
    return [f for f in files if f.stem.removesuffix(".evalset") in wanted]


async def run_one(eval_set_path: Path) -> bool:
    log.info("=== %s ===", eval_set_path.name)
    with open(eval_set_path) as fh:
        raw = json.load(fh)
    eval_set = EvalSet.model_validate(raw)
    try:
        await AgentEvaluator.evaluate_eval_set(
            agent_module="app.agent",
            eval_set=eval_set,
            eval_config=load_eval_config(),
            num_runs=1,
            print_detailed_results=True,
        )
        log.info("PASS — %s (%d cases)", eval_set_path.stem, len(eval_set.eval_cases))
        return True
    except AssertionError as e:
        log.error("FAIL — %s: %s", eval_set_path.stem, e)
        return False
    except Exception as e:
        log.error("ERROR — %s: %s: %s", eval_set_path.stem, type(e).__name__, e)
        return False


async def amain() -> int:
    names = sys.argv[1:]
    targets = discover_evalsets(names)
    if not targets:
        log.error("No evalsets matched %r in %s", names, EVALSETS_DIR)
        return 2
    log.info("Running %d evalset(s): %s", len(targets), [t.name for t in targets])
    results: dict[str, bool] = {}
    for t in targets:
        results[t.stem] = await run_one(t)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    log.info("--- SUMMARY: %d/%d passed ---", passed, total)
    return 0 if passed == total else 1


def main() -> int:
    return asyncio.run(amain())


if __name__ == "__main__":
    raise SystemExit(main())
