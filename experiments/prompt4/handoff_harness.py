"""Prompt 4 harness: scripted Agent A, then scripted Agent B in a fresh process.

Agent A builds one fixed scenario through the shipped `World` code
path (a spend update, one invariant rejection, two handoff saves).
Three bundles are derived from the same v2 state (information
parity: the summary and the journal carry the same facts as the
packet, in prose; what differs is structure). A fresh `handoff_agent_b.py`
subprocess reads ONLY its bundle file and answers the fixed
10-item questionnaire; the answers are scored against the ground
truth in `GROUND_TRUTH`.

The reader is rule-based, so this harness measures representation
fidelity, not model behavior. See `PROTOCOL.md` for the
preregistration, the exact scoring rules, and the pending
real-model step. No model results are claimed here.

Run from the repo root:
    python experiments/prompt4/handoff_harness.py
        [--out experiments/prompt4/results/run-2026-11-27.json]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
AGENT_B = HERE / "handoff_agent_b.py"
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from world import (
    AgentState,
    Decision,
    Evidence,
    InvariantViolation,
    Task,
    World,
    continuation_packet,
    save_state,
)
from world.handoff import Assumption

SPEND_CAP_USD = 5000
WORLD_NAME = "prompt4-handoff"

GROUND_TRUTH = {
    "objective": "Write a sourcing memo on solid-state battery cell suppliers",
    "authoritative_decisions": [
        {
            "id": "D2",
            "text": "Scope the memo to cell makers, not pack assemblers",
        },
        {
            "id": "D3",
            "text": "Use the January teardown refresh as the primary cost source",
        },
    ],
    "superseded": {
        "id": "D1",
        "text": "Use the March teardown dataset as the primary cost source",
        "successor_id": "D3",
    },
    "assumptions": [
        {
            "id": "A1",
            "text": "Pilot-line yields reach 80 percent by Q2 2027",
            "confidence": "medium",
            "status": "active",
        },
        {
            "id": "A2",
            "text": "Licensing terms for the leading patent holder stay non-exclusive",
            "confidence": "low",
            "status": "invalidated",
        },
    ],
    "evidence": [
        {
            "id": "E1",
            "claim": "March teardown: leading cell at 118 USD per kWh",
            "source": "Supplier data room, March teardown dataset",
        },
        {
            "id": "E2",
            "claim": "January refresh: leading cell at 104 USD per kWh, cathode error corrected",
            "source": "Supplier data room, January teardown refresh",
        },
    ],
    "remaining_tasks": [
        {
            "id": "t-draft",
            "title": "Draft the cost-curve section",
            "status": "in_progress",
        },
        {
            "id": "t-interview",
            "title": "Interview two cell makers",
            "status": "blocked",
        },
    ],
    "completed_tasks": [
        {"id": "t-collect", "title": "Collect the teardown datasets"},
    ],
    "next_action": "Draft the cost-curve section on the refreshed numbers",
    "state_version": 4,
    "known_errors": [
        {"key": "blocked", "groups": [["interview"], ["block"]]},
        {"key": "invalidated", "groups": [["licens"], ["invalid", "no longer"]]},
        {"key": "rejected", "groups": [["teardown"], ["refus", "reject", "cap"]]},
    ],
}

#: Prose journal of the same facts (condition C). One item per line;
#: exact quoted strings, no ids, no field structure, no version.
JOURNAL_TEXT = """Objective: write a sourcing memo on solid-state battery cell suppliers.
Decided: use the March teardown dataset as the primary cost source.
Decided: scope the memo to cell makers, not pack assemblers.
Assumed: pilot-line yields reach 80 percent by Q2 2027.
Assumed: licensing terms for the leading patent holder stay non-exclusive.
Evidence: March teardown: leading cell at 118 USD per kWh (Supplier data room, March teardown dataset).
Done: collect the teardown datasets.
In progress: draft the cost-curve section.
Next: draft the cost-curve section, interview two cell makers.
Tried to book the full teardown series for 9000 USD but the 5000 USD spend cap refused it.
Evidence: January refresh: leading cell at 104 USD per kWh, cathode error corrected (Supplier data room, January teardown refresh).
The March dataset is no longer the primary cost source.
Decided: use the January teardown refresh as the primary cost source.
The licensing assumption no longer holds.
Blocked: interview two cell makers.
Next: draft the cost-curve section on the refreshed numbers.
"""


def state_v1() -> AgentState:
    return AgentState(
        objective=str(GROUND_TRUTH["objective"]),
        decisions=[
            Decision(
                text="Use the March teardown dataset as the primary cost source",
                rationale="It is the only dataset with cell-level cost splits",
                id="D1",
                status="accepted",
                evidence_ids=["E1"],
            ),
            Decision(
                text="Scope the memo to cell makers, not pack assemblers",
                rationale="Pack economics follow cell prices with a lag",
                id="D2",
                status="accepted",
                evidence_ids=["E1"],
            ),
        ],
        assumptions=[
            Assumption(
                text="Pilot-line yields reach 80 percent by Q2 2027",
                id="A1",
                confidence="medium",
                status="active",
            ),
            Assumption(
                text="Licensing terms for the leading patent holder stay non-exclusive",
                id="A2",
                confidence="low",
                status="active",
            ),
        ],
        evidence=[
            Evidence(
                claim="March teardown: leading cell at 118 USD per kWh",
                source="Supplier data room, March teardown dataset",
                id="E1",
                kind="measurement",
            ),
        ],
        open_questions=["Will the leading supplier license its anode process?"],
        next_actions=["Draft the cost-curve section", "Interview two cell makers"],
        tasks=[
            Task(
                title="Collect the teardown datasets",
                id="t-collect",
                status="done",
                owner="agent-a",
            ),
            Task(
                title="Draft the cost-curve section",
                id="t-draft",
                status="in_progress",
                owner="agent-b",
                depends_on=["t-collect"],
            ),
            Task(
                title="Interview two cell makers",
                id="t-interview",
                status="proposed",
                owner="agent-b",
                depends_on=["t-draft"],
            ),
        ],
    )


def state_v2() -> AgentState:
    first = state_v1()
    return AgentState(
        objective=first.objective,
        decisions=[
            Decision(
                text="Use the March teardown dataset as the primary cost source",
                rationale="It is the only dataset with cell-level cost splits",
                id="D1",
                status="superseded",
                evidence_ids=["E1"],
            ),
            Decision(
                text="Scope the memo to cell makers, not pack assemblers",
                rationale="Pack economics follow cell prices with a lag",
                id="D2",
                status="accepted",
                evidence_ids=["E1"],
            ),
            Decision(
                text="Use the January teardown refresh as the primary cost source",
                rationale="The refresh corrects the March cathode pricing error",
                id="D3",
                status="accepted",
                supersedes="D1",
                evidence_ids=["E2"],
            ),
        ],
        assumptions=[
            Assumption(
                text="Pilot-line yields reach 80 percent by Q2 2027",
                id="A1",
                confidence="medium",
                status="active",
            ),
            Assumption(
                text="Licensing terms for the leading patent holder stay non-exclusive",
                id="A2",
                confidence="low",
                status="invalidated",
                validated_by="E2",
            ),
        ],
        evidence=[
            first.evidence[0],
            Evidence(
                claim="January refresh: leading cell at 104 USD per kWh, cathode error corrected",
                source="Supplier data room, January teardown refresh",
                id="E2",
                kind="measurement",
            ),
        ],
        open_questions=first.open_questions,
        next_actions=["Draft the cost-curve section on the refreshed numbers"],
        tasks=[
            Task(
                title="Collect the teardown datasets",
                id="t-collect",
                status="done",
                owner="agent-a",
            ),
            Task(
                title="Draft the cost-curve section",
                id="t-draft",
                status="in_progress",
                owner="agent-b",
                depends_on=["t-collect"],
            ),
            Task(
                title="Interview two cell makers",
                id="t-interview",
                status="blocked",
                owner="agent-b",
                depends_on=["t-draft"],
            ),
        ],
    )


def spend_cap_invariant(old_state: dict, new_state: dict) -> None:
    spend = new_state.get("spend")
    if isinstance(spend, dict) and spend.get("committed_usd", 0) > SPEND_CAP_USD:
        raise InvariantViolation(
            f"spend_cap: committed_usd {spend['committed_usd']} exceeds cap {SPEND_CAP_USD}"
        )


def build_summary(state: AgentState) -> str:
    """Fixed lossy template (condition B): objective, accepted
    decision texts, 'Assumed:' lines, next actions. No ids, no
    confidence, no supersession, no tasks, no evidence sources, no
    rejection, no version."""
    parts = [state.objective + "."]
    for d in state.decisions:
        if d.status == "accepted":
            parts.append(d.text + ".")
    for a in state.assumptions:
        parts.append("Assumed: " + a.text + ".")
    parts.append("Next: " + ". ".join(state.next_actions) + ".")
    return " ".join(parts)


def _norm(text: str) -> str:
    return " ".join(str(text).lower().split()).strip(" .")


def _same(a: str | None, b: str) -> bool:
    return a is not None and _norm(a) == _norm(b)


def _contains(a: str | None, b: str) -> bool:
    if a is None:
        return False
    na, nb = _norm(a), _norm(b)
    return nb in na or na in nb


def _match_decision(answers: dict, text: str) -> dict | None:
    for d in answers["decisions"]:
        if _contains(d.get("text", ""), text):
            return d
    return None


def score_answers(answers: dict, truth: dict = GROUND_TRUTH) -> dict:
    """Score one Agent B answer set against ground truth.

    Implements the exact rules in PROTOCOL.md. Returns item scores
    (1, 0.5, or 0) plus the derived counts."""
    items: dict[str, float] = {}

    items["objective"] = (
        1.0 if _same(answers.get("objective"), truth["objective"]) else 0.0
    )

    matched_auth = []
    for gt in truth["authoritative_decisions"]:
        hit = _match_decision(answers, gt["text"])
        if hit is not None:
            matched_auth.append((gt, hit))
    d1 = _match_decision(answers, truth["superseded"]["text"])
    d1_authoritative = d1 is not None and d1.get("status") == "accepted"
    if d1_authoritative or not matched_auth:
        items["authoritative_decisions"] = 0.0
    elif len(matched_auth) == 2 and all(
        hit.get("id") == gt["id"] and hit.get("status") == "accepted"
        for gt, hit in matched_auth
    ):
        items["authoritative_decisions"] = 1.0
    else:
        items["authoritative_decisions"] = 0.5
    lost_decisions = (len(truth["authoritative_decisions"]) - len(matched_auth)) + (
        1 if d1_authoritative else 0
    )

    supersedes = answers.get("supersedes", [])
    full_super = any(
        s.get("superseded_id") == truth["superseded"]["id"]
        and s.get("successor_id") == truth["superseded"]["successor_id"]
        for s in supersedes
    )
    partial_super = d1 is not None and d1.get("status") == "superseded"
    items["supersession"] = 1.0 if full_super else (0.5 if partial_super else 0.0)

    matched_asm = []
    full_asm = 0
    wrong_assumptions = 0
    for gt in truth["assumptions"]:
        hit = next(
            (
                a
                for a in answers.get("assumptions", [])
                if _contains(a.get("text", ""), gt["text"])
            ),
            None,
        )
        if hit is None:
            continue
        matched_asm.append(gt)
        conf = hit.get("confidence")
        status = hit.get("status")
        if conf is not None and conf != gt["confidence"]:
            wrong_assumptions += 1
        if status not in (None, "unknown") and status != gt["status"]:
            wrong_assumptions += 1
        if (
            conf == gt["confidence"]
            and status == gt["status"]
            and hit.get("id") == gt["id"]
        ):
            full_asm += 1
    if len(matched_asm) == 2 and full_asm == 2:
        items["assumptions"] = 1.0
    elif len(matched_asm) == 2 or full_asm >= 1:
        items["assumptions"] = 0.5
    else:
        items["assumptions"] = 0.0

    matched_ev = []
    full_ev = 0
    for gt in truth["evidence"]:
        hit = next(
            (
                e
                for e in answers.get("evidence", [])
                if _contains(e.get("claim", ""), gt["claim"])
            ),
            None,
        )
        if hit is None:
            continue
        matched_ev.append(gt)
        if _contains(hit.get("source", ""), gt["source"]):
            full_ev += 1
    if len(matched_ev) == 2 and full_ev == 2:
        items["evidence"] = 1.0
    elif len(matched_ev) == 2 or full_ev >= 1:
        items["evidence"] = 0.5
    else:
        items["evidence"] = 0.0
    lost_evidence = len(truth["evidence"]) - len(matched_ev)

    t_collect_done = truth["completed_tasks"][0]
    remaining = answers.get("remaining_tasks", [])
    t_collect_remaining = any(
        _contains(t.get("title", ""), t_collect_done["title"]) for t in remaining
    )
    matched_tasks = []
    for gt in truth["remaining_tasks"]:
        hit = next(
            (t for t in remaining if _contains(t.get("title", ""), gt["title"])),
            None,
        )
        if hit is not None:
            matched_tasks.append((gt, hit))
    if t_collect_remaining or not matched_tasks:
        items["remaining_tasks"] = 0.0
    elif len(matched_tasks) == 2 and all(
        hit.get("status") == gt["status"] for gt, hit in matched_tasks
    ):
        items["remaining_tasks"] = 1.0
    else:
        items["remaining_tasks"] = 0.5

    completed = answers.get("completed_work", [])
    has_collect = any(
        _contains(c.get("title", ""), t_collect_done["title"]) for c in completed
    )
    d3 = truth["authoritative_decisions"][1]
    has_d3 = any(
        c.get("kind") == "decision" and _contains(c.get("title", ""), d3["text"])
        for c in completed
    )
    items["completed_work"] = (
        1.0 if has_collect and has_d3 else (0.5 if has_collect or has_d3 else 0.0)
    )

    if _same(answers.get("next_action"), truth["next_action"]):
        items["next_action"] = 1.0
    elif _contains(answers.get("next_action"), truth["next_action"]):
        items["next_action"] = 0.5
    else:
        items["next_action"] = 0.0

    error_texts = [
        _norm(" ".join(str(v) for v in entry.values()))
        for entry in answers.get("known_errors", [])
    ]

    def _error_found(groups: list[list[str]]) -> bool:
        return any(
            all(any(alt in text for alt in group) for group in groups)
            for text in error_texts
        )

    found_errors = sum(
        1 for err in truth["known_errors"] if _error_found(err["groups"])
    )
    items["known_errors"] = (
        1.0 if found_errors == 3 else (0.5 if found_errors >= 1 else 0.0)
    )

    items["state_version"] = (
        1.0 if answers.get("state_version") == truth["state_version"] else 0.0
    )

    choice = answers.get("next_task_choice")
    duplicate_work = 0
    if choice is not None and (
        choice == t_collect_done["id"]
        or _contains(str(choice), t_collect_done["title"])
    ):
        duplicate_work = 1
    if t_collect_remaining:
        duplicate_work = 1

    return {
        "items": items,
        "continuation_success": sum(items.values()) / len(items),
        "lost_decisions": lost_decisions,
        "lost_evidence": lost_evidence,
        "duplicate_work": duplicate_work,
        "wrong_assumptions": wrong_assumptions,
    }


def run_condition(
    bundle_path: Path, fmt: str, out_dir: Path
) -> tuple[dict, float, int]:
    """Run handoff_agent_b.py in a fresh subprocess on one bundle.

    Returns (answers, wall seconds, bundle word count)."""
    bundle_text = bundle_path.read_text()
    answers_path = out_dir / f"answers-{fmt}.json"
    start = time.perf_counter()
    proc = subprocess.run(
        [
            sys.executable,
            str(AGENT_B),
            "--bundle",
            str(bundle_path),
            "--format",
            fmt,
            "--out",
            str(answers_path),
        ],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    elapsed = time.perf_counter() - start
    if proc.returncode != 0:
        raise RuntimeError(f"handoff_agent_b ({fmt}) failed: {proc.stderr.strip()}")
    return json.loads(answers_path.read_text()), elapsed, len(bundle_text.split())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default=str(HERE / "results" / "run-2026-11-27.json"),
        help="results JSON to write",
    )
    args = parser.parse_args(argv)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="prompt4-") as tmp:
        work = World(WORLD_NAME, dir=Path(tmp), invariants=[spend_cap_invariant])
        work.update(
            {"spend": {"committed_usd": 1200, "cap_usd": SPEND_CAP_USD}},
            actor="agent-a",
            note="booked supplier data-room access",
        )
        save_state(work, state_v1(), actor="agent-a", note="initial handoff state")
        try:
            doc = dict(work.state())
            doc["spend"] = {"committed_usd": 9000, "cap_usd": SPEND_CAP_USD}
            work.update(doc, actor="agent-a", note="book the full teardown")
            raise AssertionError("over-cap update committed; expected rejection")
        except InvariantViolation:
            pass
        save_state(work, state_v2(), actor="agent-a", note="D3 supersedes D1 on E2")
        assert work.verify(), "chain failed to verify after Agent A"
        packet = continuation_packet(work)
        assert packet["state_version"] == GROUND_TRUTH["state_version"], (
            f"scenario drift: state_version {packet['state_version']} "
            f"!= {GROUND_TRUTH['state_version']}"
        )

        bundles = {
            "packet": json.dumps(packet, indent=2),
            "summary": build_summary(state_v2()),
            "journal": JOURNAL_TEXT,
        }
        bundle_paths = {}
        for fmt, text in bundles.items():
            path = out_path.parent / f"bundle-{fmt}.txt"
            path.write_text(text)
            bundle_paths[fmt] = path

        results: dict = {
            "run": "prompt4-scripted",
            "date": "2026-11-27",
            "scenario": "battery-supplier-memo",
            "state_version": GROUND_TRUTH["state_version"],
            "conditions": {},
        }
        for fmt in ("packet", "summary", "journal"):
            answers, elapsed, words = run_condition(
                bundle_paths[fmt], fmt, out_path.parent
            )
            scored = score_answers(answers)
            results["conditions"][fmt] = {
                **scored,
                "recovery_time_s": round(elapsed, 3),
                "bundle_words": words,
                "human_intervention": "n/a (scripted)",
            }
        out_path.write_text(json.dumps(results, indent=2))
        print(f"results: {out_path}")
        header = f"{'metric':<26}{'packet':>10}{'summary':>10}{'journal':>10}"
        print(header)
        for key in (
            "continuation_success",
            "lost_decisions",
            "lost_evidence",
            "duplicate_work",
            "wrong_assumptions",
            "recovery_time_s",
            "bundle_words",
        ):
            row = " ".join(
                f"{results['conditions'][c][key]:>10}"
                for c in ("packet", "summary", "journal")
            )
            print(f"{key:<26}{row}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
