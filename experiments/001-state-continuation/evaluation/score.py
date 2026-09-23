#!/usr/bin/env python3
"""Deterministic scoring for the state-continuation benchmark.

Scores the pre-registered deterministic (and deterministic-proxy) metrics:

- M2 factual_accuracy (proxy): fraction of ground-truth facts whose
  must_mention phrases all appear in the continuation.
- M3 decision_recovery (primary): fraction of decisions recovered WITH
  correct rationale (must_mention covers text+rationale phrases).
- M4 question_recovery: fraction of open questions carried forward.
- M5 contradiction_rate: must_not_state hits per 100 output words.
  Negation-aware: "not a database outage" does not count as claiming one.
- M6 repeated_work: already_done hits (count). Proposal-aware: mentioning
  completed work as done ("we already rolled back") does not count;
  re-proposing it ("we should roll back") does.
- M7 token_usage: words/chars from the manifest (+ provider tokens if given).

Matching rule (documented limitation — see methodology §8.7):
normalized substring matching (lowercase, punctuation stripped).
For positive items ALL must_mention phrases must appear; for negative
items (must_not_state, already_done) ANY single phrase hit counts.

Judged metrics (M1, and the judged halves of M2/M5/M6) are NOT scored
here; use evaluation/rubric.md + evaluation/judge_prompt.md.

Usage:
    python evaluation/score.py --raw results/pilot/raw \\
        --manifest results/pilot/manifest.json --out results/pilot/scored
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from textutils import contradiction_hit, phrase_match, proposal_sentences

DATASET = HERE.parent / "dataset" / "tasks"


def all_present(phrases: list[str], haystack: str) -> bool:
    return all(phrase_match(p, haystack) for p in phrases)


def any_present(phrases: list[str], haystack: str) -> bool:
    return any(phrase_match(p, haystack) for p in phrases)


def score_continuation(gt: dict, text: str) -> dict:
    hay = text
    words = len(text.split())

    def frac(items: list[dict]) -> float:
        if not items:
            return 1.0
        return sum(1 for i in items if all_present(i["must_mention"], hay)) / len(items)

    decisions = gt["decisions"]
    facts = gt["facts"]
    questions = gt["open_questions"]

    contra_hits = [
        i["id"]
        for i in gt["must_not_state"]
        if any(contradiction_hit(p, text) for p in i["must_mention"])
    ]
    repeat_hay = proposal_sentences(text)
    repeat_hits = [
        i["id"] for i in gt["already_done"] if any_present(i["must_mention"], repeat_hay)
    ]

    return {
        "M2_factual_accuracy_proxy": round(frac(facts), 3),
        "M3_decision_recovery": round(frac(decisions), 3),
        "M4_question_recovery": round(frac(questions), 3),
        "M5_contradiction_hits": contra_hits,
        "M5_contradiction_rate_per_100w": round(len(contra_hits) / max(words, 1) * 100, 3),
        "M6_repeated_work_hits": repeat_hits,
        "M6_repeated_work_count": len(repeat_hits),
        "output_words": words,
        "output_chars": len(text),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, help="dir with <task>__<condition>.md")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    raw = Path(args.raw)
    manifest = json.loads(Path(args.manifest).read_text())
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    for item in manifest["items"]:
        task, condition = item["task"], item["condition"]
        gt = json.loads((DATASET / task / "ground_truth.json").read_text())
        text = (raw / f"{task}__{condition}.md").read_text()
        scored = score_continuation(gt, text)
        scored.update(
            {
                "task": task,
                "condition": condition,
                "prompt_words": item["prompt_words"],
                "prompt_chars": item["prompt_chars"],
                "input_tokens": item["input_tokens"],
                "output_tokens": item["output_tokens"],
            }
        )
        rows.append(scored)

    (out / "scores.json").write_text(json.dumps(rows, indent=2) + "\n")

    headers = [
        "task", "condition", "M2_factual_accuracy_proxy", "M3_decision_recovery",
        "M4_question_recovery", "M5_contradiction_rate_per_100w",
        "M6_repeated_work_count", "prompt_words", "output_words",
    ]
    with open(out / "scores.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Deterministic scores",
        "",
        ("| task | condition | M2 factual | M3 decisions | M4 questions | "
         "M5 contra/100w | M6 repeated | in-words | out-words |"),
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['task']} | {r['condition']} | {r['M2_factual_accuracy_proxy']} | "
            f"{r['M3_decision_recovery']} | {r['M4_question_recovery']} | "
            f"{r['M5_contradiction_rate_per_100w']} | {r['M6_repeated_work_count']} | "
            f"{r['prompt_words']} | {r['output_words']} |"
        )
    (out / "scores.md").write_text("\n".join(lines) + "\n")
    print(f"scored {len(rows)} continuations -> {out}")


if __name__ == "__main__":
    main()
