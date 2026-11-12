"""Information parity gate for Experiment #003.

For each task, every phrase in ground_truth.json's top-level must_mention
list must appear (after normalization) in all three handoff artifacts:
state.md (Condition A), summary.md (Condition B), journal.md (Condition C).
A task whose artifacts fail parity must not run continuations until the
producing side fixes the artifact; ground truth is never edited to pass.

Usage: python3 parity_gate.py [TASK ...]   (default: all tasks)
Exit code 0 if all checked tasks pass, 1 otherwise.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = {"A": "state.md", "B": "summary.md", "C": "journal.md"}


def normalize(text: str) -> str:
    # Hyphens and whitespace are equivalent for phrase matching: artifacts
    # legitimately write "export-control" or "export control", "step-free"
    # or "step free". Correction logged in protocol.md run log
    # (2026-11-03T03:50Z) after the first gate run produced false positives
    # on exactly these variants; applied uniformly to phrases and texts.
    text = re.sub(r"[\s\-]+", " ", text.lower())
    # One documented alias (R1 erratum addendum, 2026-11-03T03:52Z): the
    # acronym and its spelled-out form are the same content.
    return text.replace("single sign on", "sso")


def check_task(task: str) -> list[str]:
    gt = json.loads((ROOT / "tasks" / task / "ground_truth.json").read_text())
    phrases = gt["must_mention"]
    failures = []
    for cond, fname in ARTIFACTS.items():
        path = ROOT / "artifacts" / task / fname
        if not path.exists():
            failures.append(f"{task}/{cond}: artifact missing ({fname})")
            continue
        text = normalize(path.read_text())
        for phrase in phrases:
            if normalize(phrase) not in text:
                failures.append(f"{task}/{cond}: missing phrase {phrase!r}")
    return failures


def main() -> int:
    tasks = sys.argv[1:] or sorted(
        p.name for p in (ROOT / "tasks").iterdir() if p.is_dir()
    )
    all_failures = []
    for task in tasks:
        failures = check_task(task)
        status = "PASS" if not failures else "FAIL"
        print(f"{task}: {status} ({len(failures)} failures)")
        all_failures.extend(failures)
    for failure in all_failures:
        print("  " + failure)
    return 1 if all_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
