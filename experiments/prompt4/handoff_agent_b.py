"""Agent B: fresh-process continuer for the Prompt 4 harness.

Reads ONLY the bundle file given on the command line. It never opens
a world file and never imports `world`: everything it knows comes
from the bundle. It answers the fixed 10-item questionnaire and
writes answers JSON. One parser per bundle kind; each parser uses
fixed rules and knows nothing about the scenario.

Run:  python experiments/prompt4/agent_b.py --bundle <file>
        --format packet|summary|journal --out <answers.json>
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _norm(text: str) -> str:
    return " ".join(text.lower().split()).strip(" .")


def _blank_answers() -> dict:
    return {
        "objective": None,
        "decisions": [],
        "supersedes": [],
        "assumptions": [],
        "evidence": [],
        "remaining_tasks": [],
        "completed_work": [],
        "next_action": None,
        "next_task_choice": None,
        "known_errors": [],
        "state_version": None,
    }


def _answer_from_packet(packet: dict) -> dict:
    answers = _blank_answers()
    answers["objective"] = packet["objective"]
    answers["decisions"] = [
        {"id": d["id"], "text": d["text"], "status": d["status"]}
        for d in packet["decisions"]
    ]
    answers["supersedes"] = [
        {"superseded_id": d["supersedes"], "successor_id": d["id"]}
        for d in packet["decisions"]
        if d.get("supersedes")
    ]
    answers["assumptions"] = [
        {
            "id": a["id"],
            "text": a["text"],
            "confidence": a["confidence"],
            "status": a["status"],
        }
        for a in packet["assumptions"]
    ]
    answers["evidence"] = [
        {"id": e["id"], "claim": e["claim"], "source": e["source"]}
        for e in packet["evidence"]
    ]
    answers["remaining_tasks"] = [
        {"id": t["id"], "title": t["title"], "status": t["status"]}
        for t in packet["remaining_tasks"]
    ]
    answers["completed_work"] = [
        {
            "kind": item["kind"],
            "id": item["id"],
            "title": item.get("title") or item.get("text", ""),
        }
        for item in packet["completed_work"]
    ]
    answers["next_action"] = packet["next_action"]
    in_progress = [t for t in packet["remaining_tasks"] if t["status"] == "in_progress"]
    first = in_progress[0] if in_progress else None
    if first is None and packet["remaining_tasks"]:
        first = packet["remaining_tasks"][0]
    answers["next_task_choice"] = first["id"] if first else None
    answers["known_errors"] = list(packet["known_errors"])
    answers["state_version"] = packet["state_version"]
    return answers


def _answer_from_summary(text: str) -> dict:
    answers = _blank_answers()
    sentences = [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]
    if not sentences:
        return answers
    answers["objective"] = sentences[0].rstrip(".")
    for sentence in sentences[1:]:
        sentence = sentence.rstrip(".")
        if sentence.startswith("Assumed: "):
            answers["assumptions"].append(
                {
                    "id": "",
                    "text": sentence[len("Assumed: ") :],
                    "confidence": None,
                    "status": "unknown",
                }
            )
        elif sentence.startswith("Next: "):
            answers["next_action"] = sentence[len("Next: ") :]
        else:
            answers["decisions"].append(
                {"id": "", "text": sentence, "status": "unknown"}
            )
    return answers


def _answer_from_journal(text: str) -> dict:
    answers = _blank_answers()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        if line.startswith("Objective: "):
            answers["objective"] = line[len("Objective: ") :].rstrip(".")
        elif line.startswith("Decided: "):
            answers["decisions"].append(
                {
                    "id": "",
                    "text": line[len("Decided: ") :].rstrip("."),
                    "status": "unknown",
                }
            )
        elif line.startswith("Assumed: "):
            answers["assumptions"].append(
                {
                    "id": "",
                    "text": line[len("Assumed: ") :].rstrip("."),
                    "confidence": None,
                    "status": "unknown",
                }
            )
        elif line.startswith("Evidence: "):
            rest = line[len("Evidence: ") :]
            match = re.match(r"^(.*) \((.*)\)\.?$", rest)
            if match:
                answers["evidence"].append(
                    {"id": "", "claim": match.group(1), "source": match.group(2)}
                )
            else:
                answers["evidence"].append(
                    {"id": "", "claim": rest.rstrip("."), "source": ""}
                )
        elif line.startswith("Done: "):
            answers["completed_work"].append(
                {
                    "kind": "task",
                    "id": "",
                    "title": line[len("Done: ") :].rstrip("."),
                }
            )
        elif line.startswith("In progress: "):
            answers["remaining_tasks"].append(
                {
                    "id": "",
                    "title": line[len("In progress: ") :].rstrip("."),
                    "status": "in_progress",
                }
            )
        elif line.startswith("Blocked: "):
            title = line[len("Blocked: ") :].rstrip(".")
            answers["remaining_tasks"].append(
                {"id": "", "title": title, "status": "blocked"}
            )
            answers["known_errors"].append(
                {"kind": "note", "text": line, "id": "", "title": title}
            )
        elif "no longer holds" in line or "refused" in line or "REJECTED" in line:
            answers["known_errors"].append({"kind": "note", "text": line})
        elif line.startswith("Next: "):
            answers["next_action"] = line[len("Next: ") :].rstrip(".")
    if answers["next_action"]:
        target = _norm(answers["next_action"])
        for task in answers["remaining_tasks"]:
            if _norm(task["title"]) and _norm(task["title"]) in target:
                answers["next_task_choice"] = task["title"]
                break
    return answers


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True, help="bundle file to read")
    parser.add_argument(
        "--format", required=True, choices=["packet", "summary", "journal"]
    )
    parser.add_argument("--out", required=True, help="answers JSON to write")
    args = parser.parse_args(argv)
    bundle_path = Path(args.bundle)
    raw = bundle_path.read_text()
    if args.format == "packet":
        answers = _answer_from_packet(json.loads(raw))
    elif args.format == "summary":
        answers = _answer_from_summary(raw)
    else:
        answers = _answer_from_journal(raw)
    Path(args.out).write_text(json.dumps(answers, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
