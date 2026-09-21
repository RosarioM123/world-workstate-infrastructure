"""Summarize experiment 001 results. Prints failures plainly.

Reads experiments/results/trial_*.json and prints a table with every
trial, its hand-scored outcome, and its failure reason, followed by the
totals INCLUDING the failure rate. This output is pasted verbatim into
the README; it is never paraphrased into something kinder.

Usage: python experiments/summarize.py
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "experiments" / "results"


def load_trials() -> list[dict]:
    trials = []
    for path in sorted(RESULTS_DIR.glob("trial_*.json")):
        trials.append(json.loads(path.read_text(encoding="utf-8")))
    return trials


def main() -> int:
    trials = load_trials()
    if not trials:
        print("No trials yet. Run experiments/handoff_001.py first.")
        return 1

    print(f"{'Trial':<8}{'Success':<10}{'Failure reason'}")
    print("-" * 60)
    successes = 0
    scored = 0
    for t in trials:
        success = t.get("handoff_success")
        if success is True:
            successes += 1
            scored += 1
            label = "True"
        elif success is False:
            scored += 1
            label = "False"
        else:
            label = "UNSCORed"
        reason = t.get("failure_reason") or ""
        print(f"{t['trial_id']:<8}{label:<10}{reason}")
    print("-" * 60)
    if scored:
        rate = successes / scored * 100
        print(
            f"{successes}/{scored} handoffs succeeded "
            f"({rate:.0f}% success, {100 - rate:.0f}% failure rate)"
        )
    else:
        print("0 trials scored so far.")
    unscored = len(trials) - scored
    if unscored:
        print(f"WARNING: {unscored} trial(s) have no hand score yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
