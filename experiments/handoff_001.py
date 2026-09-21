"""Experiment 001: model-to-model handoff via the WORLD ledger.

Spec: docs/experiment-handoff.md (the investment-research variant is the
full spec; this script runs the manual-first slice of it).

====================================================================
ANTI-CHERRY-PICKING RULE (read before touching this file)
--------------------------------------------------------------------
This experiment exists to produce EVIDENCE, not a good outcome. The
operator scores every trial by hand, including failures, and the raw
JSON in experiments/results/ is the only result that counts.

  - Report the ugly number. If trials come back 2/5, the README ships
    with "2/5 (40%)" and the failure reasons listed plainly.
  - Never "fix" the demo, the task, the transcript, or the scoring to
    make the number look better. A stated 40% with an honest failure
    analysis is a stronger artifact than a suspiciously perfect run
    with no results file behind it.
  - Do not close the tracking issue by declaring success without the
    JSON files. A partial or negative result still closes the issue:
    the goal is evidence, not a good outcome.
====================================================================

Manual-first protocol. Nothing is automated on day one: the operator
plays Model A and Model B across two chat windows.

  1. Model A works the task (see experiments/tasks/task_001.md). The
     operator saves the session transcript to a file.
  2. Run: commits Model A's state to the ledger and writes the trial
     JSON (handoff_success is None until hand-scored).

         python experiments/handoff_001.py run --trial 1 \\
             --task-file experiments/tasks/task_001.md \\
             --transcript experiments/trials/trial_001_a.md

  3. Print the handoff bundle. Paste it into a FRESH Model B session
     (new tab/window, not the same context) followed by the word
     "continue". Nothing else.

         python experiments/handoff_001.py bundle --trial 1

  4. Save Model B's response, then score by hand. Be honest, not
     generous.

         python experiments/handoff_001.py score --trial 1 \\
             --model-b-output experiments/trials/trial_001_b.md \\
             --success true|false --reason "specific failure reason"

  5. After 5 trials: python experiments/summarize.py

State extraction uses the existing deterministic transcript parser
(world_engine.ingestion.transcript), never an LLM. The ledger is the
state store: engine.init_db / import_transcript / verify_chain /
get_ledger are the only engine calls.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from world_engine.core import engine
from world_engine.ingestion import transcript as ti

RESULTS_DIR = REPO_ROOT / "experiments" / "results"

KIND_TO_FIELD = {
    "DECISION": "decisions",
    "ASSUMPTION": "assumptions",
    "QUESTION": "open_questions",
    "CONSTRAINT": "constraints",
    "NOTE": "notes",
}


def _utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _objective_from_task(task_file: Path) -> str:
    """First markdown heading of the task brief is the objective."""
    for line in task_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return task_file.stem


def build_handoff_bundle(items: list[dict], objective: str) -> dict:
    """Group parsed transcript items into the handoff bundle Model B gets.

    This is exactly what a fresh session receives: the objective plus
    every durable item the deterministic parser extracted, grouped by
    kind. Fields the parser cannot derive (e.g. next_action) are absent
    on purpose; Model B must propose them.
    """
    bundle: dict = {
        "objective": objective,
        "decisions": [],
        "assumptions": [],
        "open_questions": [],
        "constraints": [],
        "notes": [],
    }
    for item in items:
        field = KIND_TO_FIELD.get(item["kind"], "notes")
        bundle[field].append({"speaker": item["speaker"], "text": item["text"]})
    return bundle


def format_bundle(bundle: dict, trial_id: int) -> str:
    """Render the bundle as plain text to paste into Model B's session."""
    lines = [
        f"WORLD handoff bundle (trial {trial_id}).",
        "This is the full state from the previous session, extracted",
        "deterministically from its transcript and committed to a",
        "hash-chained ledger. Continue from exactly here.",
        "",
        f"OBJECTIVE: {bundle['objective']}",
    ]
    for field, label in [
        ("decisions", "DECISIONS"),
        ("assumptions", "ASSUMPTIONS"),
        ("open_questions", "OPEN QUESTIONS"),
        ("constraints", "CONSTRAINTS"),
        ("notes", "NOTES"),
    ]:
        entries = bundle[field]
        lines.append("")
        lines.append(f"{label} ({len(entries)}):")
        for e in entries:
            lines.append(f"  - [{e['speaker']}] {e['text']}")
    lines += ["", "continue"]
    return "\n".join(lines)


def _result_path(trial: int) -> Path:
    return RESULTS_DIR / f"trial_{trial:03d}.json"


def cmd_run(args: argparse.Namespace) -> int:
    task_file = Path(args.task_file)
    transcript_text = Path(args.transcript).read_text(encoding="utf-8")
    objective = _objective_from_task(task_file)

    engine.init_db()
    items = ti.parse_transcript(transcript_text)
    report = ti.import_transcript(
        transcript_text, source=f"handoff_001/trial_{args.trial:03d}"
    )
    verified, bad_id = engine.verify_chain()
    bundle = build_handoff_bundle(items, objective)

    result = {
        "trial_id": args.trial,
        "timestamp": _utcnow(),
        "task": str(task_file),
        "objective": objective,
        "transcript_source": str(args.transcript),
        "ledger_verified": verified,
        "bad_transaction_id": bad_id,
        "import_report": {
            "items_found": report["items_found"],
            "committed": report["committed"],
            "rejected": report["rejected"],
            "skipped_duplicate": report["skipped_duplicate"],
        },
        "state_committed": bundle,
        "model_b_output": None,
        "handoff_success": None,
        "failure_reason": None,
        "scored_at": None,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    _result_path(args.trial).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        f"Trial {args.trial}: {report['committed']} items committed "
        f"({report['rejected']} rejected, "
        f"{report['skipped_duplicate']} duplicates skipped), "
        f"ledger_verified={verified}. handoff_success=None (not yet scored)."
    )
    print(f"Wrote {_result_path(args.trial)}. Next: bundle --trial {args.trial}")
    return 0


def cmd_bundle(args: argparse.Namespace) -> int:
    data = json.loads(_result_path(args.trial).read_text(encoding="utf-8"))
    print(format_bundle(data["state_committed"], data["trial_id"]))
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    path = _result_path(args.trial)
    data = json.loads(path.read_text(encoding="utf-8"))
    if args.model_b_output:
        data["model_b_output"] = Path(args.model_b_output).read_text(encoding="utf-8")
    data["handoff_success"] = args.success
    data["failure_reason"] = args.reason
    data["scored_at"] = _utcnow()
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(
        f"Trial {args.trial} scored: handoff_success={args.success} "
        f"reason={args.reason!r}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Experiment 001: manual-first model-to-model handoff."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Commit Model A's transcript to the ledger.")
    p_run.add_argument("--trial", type=int, required=True)
    p_run.add_argument("--task-file", required=True)
    p_run.add_argument("--transcript", required=True)
    p_run.set_defaults(func=cmd_run)

    p_bundle = sub.add_parser(
        "bundle", help="Print the handoff bundle to paste into Model B."
    )
    p_bundle.add_argument("--trial", type=int, required=True)
    p_bundle.set_defaults(func=cmd_bundle)

    p_score = sub.add_parser("score", help="Hand-score a trial (be honest).")
    p_score.add_argument("--trial", type=int, required=True)
    p_score.add_argument("--model-b-output", default=None)
    p_score.add_argument(
        "--success",
        required=True,
        choices=["true", "false"],
        help="'true' only if Model B continued correctly with no re-explaining.",
    )
    p_score.add_argument(
        "--reason",
        default=None,
        help="Specific failure reason. Required when --success false.",
    )
    p_score.set_defaults(func=cmd_score)

    args = parser.parse_args(argv)
    if args.command == "score" and args.success == "false" and not args.reason:
        parser.error("--reason is required when scoring a trial as failed.")
    args.success = (
        {"true": True, "false": False}[args.success]
        if args.command == "score"
        else None
    )
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
