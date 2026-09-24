#!/usr/bin/env python3
"""Self-test (methodology §5.3): the benchmark must be able to show WORLD losing.

Builds synthetic continuations for task_001 where the WORLD condition is
deliberately the worst, then asserts the scorer ranks it last and flags
its contradictions and repeated work. Also asserts the negation guard
("not a database outage" is not a contradiction) and the proposal guard
("we already rolled back" is not repeated work).

Exit non-zero on any failure. Run before any real benchmark run:
    python evaluation/selftest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from score import score_continuation

GT = json.loads(
    (
        HERE.parent
        / "dataset"
        / "tasks"
        / "task_001_vendor_selection"
        / "ground_truth.json"
    ).read_text()
)


def good_text() -> str:
    """A perfect continuation: every positive key phrase present."""
    parts = []
    for d in GT["decisions"]:
        parts.append(d["text"] + " " + d["rationale"])
    for f in GT["facts"]:
        parts.append(f["text"])
    for q in GT["open_questions"]:
        parts.append(q["text"])
    return " ".join(parts)


def medium_text() -> str:
    """A mediocre continuation: half the decisions, no contradictions."""
    parts = []
    for d in GT["decisions"][:2]:
        parts.append(d["text"] + " " + d["rationale"])
    for f in GT["facts"][:3]:
        parts.append(f["text"])
    return " ".join(parts)


def bad_world_text() -> str:
    """A bad WORLD-condition continuation: misses decisions, contradicts,
    and re-proposes settled work."""
    return (
        "We recommend Qdrant for its superior performance. "
        "SOC2 is not required for this workload. "
        "We should evaluate Qdrant vs Weaviate vs pgvector before deciding."
    )


def main() -> int:
    failures = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        print(
            ("PASS " if cond else "FAIL ")
            + name
            + (f" — {detail}" if detail and not cond else "")
        )
        if not cond:
            failures.append(name)

    s_good = score_continuation(GT, good_text())
    s_med = score_continuation(GT, medium_text())
    s_bad = score_continuation(GT, bad_world_text())

    # WORLD (bad) must rank last on the primary metric.
    check(
        "M3 ranks WORLD last",
        s_good["M3_decision_recovery"]
        > s_med["M3_decision_recovery"]
        > s_bad["M3_decision_recovery"],
        f"good={s_good['M3_decision_recovery']} med={s_med['M3_decision_recovery']} bad={s_bad['M3_decision_recovery']}",
    )
    check(
        "bad WORLD scores M3 == 0",
        s_bad["M3_decision_recovery"] == 0.0,
        f"got {s_bad['M3_decision_recovery']}",
    )
    check(
        "good scores M3 == 1",
        s_good["M3_decision_recovery"] == 1.0,
        f"got {s_good['M3_decision_recovery']}",
    )

    # Contradictions and repeated work are flagged on the bad WORLD run.
    check(
        "bad WORLD contradiction hits == {C1, C2}",
        set(s_bad["M5_contradiction_hits"]) == {"C1", "C2"},
        f"got {s_bad['M5_contradiction_hits']}",
    )
    check(
        "bad WORLD repeated-work hit == {R1}",
        s_bad["M6_repeated_work_hits"] == ["R1"],
        f"got {s_bad['M6_repeated_work_hits']}",
    )
    check(
        "good has no contradiction hits",
        s_good["M5_contradiction_hits"] == [],
        f"got {s_good['M5_contradiction_hits']}",
    )

    # Negation guard: denying a forbidden claim is not a contradiction.
    neg = (
        "We will not recommend Qdrant. The database was never down; "
        "this was pool exhaustion, not a database outage."
    )
    s_neg = score_continuation(GT, neg)
    check(
        "negation guard",
        s_neg["M5_contradiction_hits"] == [],
        f"got {s_neg['M5_contradiction_hits']}",
    )

    # Proposal guard: mentioning completed work as done is not repeated work.
    gt2 = json.loads(
        (
            HERE.parent
            / "dataset"
            / "tasks"
            / "task_002_incident_postmortem"
            / "ground_truth.json"
        ).read_text()
    )
    done = "We already rolled back to v2.13 at 14:20. Root cause is confirmed."
    s_done = score_continuation(gt2, done)
    check(
        "proposal guard (done != re-proposed)",
        s_done["M6_repeated_work_hits"] == [],
        f"got {s_done['M6_repeated_work_hits']}",
    )
    repropose = "Next step: we should roll back to v2.13 to stop the bleeding."
    s_re = score_continuation(gt2, repropose)
    check(
        "proposal guard (re-proposal flagged)",
        s_re["M6_repeated_work_hits"] == ["R1"],
        f"got {s_re['M6_repeated_work_hits']}",
    )

    if failures:
        print(f"\n{len(failures)} self-test failures")
        return 1
    print("\nself-test OK: harness can show WORLD losing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
