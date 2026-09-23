#!/usr/bin/env python3
"""Parity gate (methodology §3): information parity by construction.

Every must_mention key phrase in the POSITIVE ground-truth sections
(decisions, facts, open_questions, next_actions) must appear — after
normalization — in ALL THREE artifacts (transcript.md, summary.md,
world.json).

must_not_state phrases must not be ASSERTED by any artifact (negation-
aware: "not a database outage" is fine, "the database was down" is a
leak). already_done phrases are exempt: completed work is legitimately
mentioned as history; the repeated-work check applies to continuations,
not handoffs.

A task failing parity is excluded from runs until fixed. Exit code is
non-zero on any failure.

Usage:
    python evaluation/check_parity.py [--tasks task_001_vendor_selection]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from textutils import contradiction_hit, normalize, phrase_match

DATASET = HERE.parent / "dataset" / "tasks"

POSITIVE_SECTIONS = ("decisions", "facts", "open_questions", "next_actions")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", nargs="*")
    args = parser.parse_args()

    task_dirs = sorted(p for p in DATASET.iterdir() if p.is_dir())
    if args.tasks:
        task_dirs = [p for p in task_dirs if p.name in args.tasks]

    failures = 0
    for task_dir in task_dirs:
        gt = json.loads((task_dir / "ground_truth.json").read_text())
        artifacts = {
            "transcript": (task_dir / "artifacts" / "transcript.md").read_text(),
            "summary": (task_dir / "artifacts" / "summary.md").read_text(),
            "world": (task_dir / "artifacts" / "world.json").read_text(),
        }
        haystacks = {k: normalize(v) for k, v in artifacts.items()}

        # must_not_state phrases must not be asserted (negation-aware).
        for item in gt["must_not_state"]:
            for name, raw in artifacts.items():
                hits = [p for p in item["must_mention"] if contradiction_hit(p, raw)]
                if hits:
                    print(
                        f"LEAK {task_dir.name}: must_not_state/{item['id']} phrase "
                        f"{hits} asserted in {name}"
                    )
                    failures += 1

        for section in POSITIVE_SECTIONS:
            for item in gt[section]:
                for phrase in item["must_mention"]:
                    for name, hay in haystacks.items():
                        if not phrase_match(phrase, hay):
                            print(
                                f"PARITY {task_dir.name}: {section}/{item['id']} "
                                f"phrase {phrase!r} missing from {name}"
                            )
                            failures += 1

    if failures:
        print(f"\n{failures} parity failures")
        return 1
    print("parity OK: all key phrases present in all three artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
