"""Lost-update experiment: two agents, one shared WORLD.

Pilot harness (see PREREGISTRATION.md). Agents are scripted with stochastic
think times (lognormal, median ~1.2s); the think() step is pluggable for the
LLM-agent phase. Each trial uses a fresh world.

    python experiments/lost_update/harness.py [--trials N] [--seed S]

Prints per-condition rates with Wilson 95% CIs and writes
experiments/lost_update/results.jsonl (one row per trial).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from world.core import ConflictError, World  # noqa: E402

RESULTS = os.path.join(os.path.dirname(__file__), "results.jsonl")


def think(agent: str, trial: int, rng: random.Random) -> tuple[str, float]:
    """Scripted stand-in for LLM generation: variable latency, fixed payload."""
    gap = rng.lognormvariate(math.log(1.2), 0.7)
    time.sleep(gap)
    return f"{agent}-finding-t{trial}", gap


def run_trial(trial: int, condition: str, seed: int) -> dict:
    rng = random.Random(seed)
    d = tempfile.mkdtemp(prefix=f"lostupd-t{trial}-")
    w = World(f"race-{trial}", dir=d)
    w.update({"findings": []})
    v0 = w.version
    outcomes: dict[str, dict] = {}

    def agent(name: str) -> None:
        # Staggered starts (no barrier): overlap is emergent, not staged.
        # Some trials race, some don't, as in real deployments.
        time.sleep(rng.uniform(0, 2.0))
        local = World(f"race-{trial}", dir=d)  # separate handle, shared file
        snap = local.state()  # read at loop start (goes stale)
        ver = local.version
        finding, gap = think(name, trial, rng)
        new_doc = {"findings": snap["findings"] + [finding]}
        attempts, conflicted = 0, False
        while True:
            attempts += 1
            try:
                if condition == "A":
                    local.update(new_doc)
                else:
                    # B: optimistic concurrency; retry on conflict.
                    use_ver = ver if attempts == 1 else local.version
                    use_doc = new_doc if attempts == 1 else {
                        "findings": local.state()["findings"] + [finding]}
                    local.update(use_doc, expected_version=use_ver)
                break
            except ConflictError:
                conflicted = True
                if attempts >= 3:
                    break
        outcomes[name] = {"attempts": attempts, "conflicted": conflicted,
                          "finding": finding, "gap": gap}

    threads = [threading.Thread(target=agent, args=(n,)) for n in ("a", "b")]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    final = w.state()["findings"]
    present = {o["finding"] for o in outcomes.values()}
    lost = len(set(final) & present) < 2
    return {
        "trial": trial, "condition": condition, "seed": seed,
        "v0": v0, "final": final,
        "lost_update": lost,
        "conflicts": sum(1 for o in outcomes.values() if o["conflicted"]),
        "max_gap": max(o["gap"] for o in outcomes.values()),
        "total_attempts": sum(o["attempts"] for o in outcomes.values()),
    }


def wilson(hits: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = hits / n
    den = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - m) / den), min(1.0, (c + m) / den))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20261015)
    args = ap.parse_args()

    rows = []
    for cond in ("A", "B"):
        for t in range(args.trials):
            row = run_trial(t, cond, args.seed + t * 2 + (cond == "B"))
            rows.append(row)
            print(f"condition {cond} trial {t}: lost={row['lost_update']} "
                  f"conflicts={row['conflicts']} gap={row['max_gap']:.2f}s",
                  flush=True)

    with open(RESULTS, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")

    for cond in ("A", "B"):
        sub = [r for r in rows if r["condition"] == cond]
        n = len(sub)
        lost = sum(r["lost_update"] for r in sub)
        conf = sum(1 for r in sub if r["conflicts"] > 0)
        lo, hi = wilson(lost, n)
        print(f"\nCondition {cond} (n={n}): lost-update rate "
              f"{lost}/{n} = {lost / n:.2f} (95% CI {lo:.2f}-{hi:.2f}); "
              f"trials with conflicts: {conf}/{n}; "
              f"mean max gap: {sum(r['max_gap'] for r in sub) / n:.2f}s")
    print(f"\nraw trial rows: {RESULTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
