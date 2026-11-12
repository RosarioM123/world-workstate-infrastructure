"""Build the raw JSONL run records for Experiment #003.

One record per continuation trial, written to results/raw/records.jsonl.
Fields per protocol.md: experiment id, task id, trial id, condition,
model description, system prompt hash and text, full user prompt,
artifact path with word and character counts, output path, timestamps
(output file mtime, UTC), and errors or retries (none in this run: all
72 trials completed on the first attempt).

Usage: python3 build_records.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import prompts

ROOT = Path(__file__).resolve().parent.parent
TASKS = ["F1", "F2", "S1", "S2", "R1", "R2", "C1", "C2"]
ARTIFACT_FILES = {"A": "state.md", "B": "summary.md", "C": "journal.md"}
MODEL = (
    "in-environment agent (Muse platform subagent), single model family; "
    "exact model version not reported by the platform"
)


def ts(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def main() -> None:
    records = []
    for task in TASKS:
        for cond in ("A", "B", "C"):
            artifact = ROOT / "artifacts" / task / ARTIFACT_FILES[cond]
            atext = artifact.read_text()
            prompt_path = ROOT / "results" / "raw" / task / f"prompt-{cond}.txt"
            user_prompt = prompt_path.read_text()
            for trial in (1, 2, 3):
                out = ROOT / "results" / "raw" / task / f"output-{cond}-{trial}.md"
                records.append(
                    {
                        "experiment_id": "experiment-003",
                        "task_id": task,
                        "trial_id": trial,
                        "condition": cond,
                        "model": MODEL,
                        "system_prompt_sha256": prompts.system_prompt_hash(),
                        "system_prompt": prompts.SYSTEM_PROMPT,
                        "user_prompt": user_prompt,
                        "artifact_path": f"artifacts/{task}/{ARTIFACT_FILES[cond]}",
                        "artifact_words": len(atext.split()),
                        "artifact_chars": len(atext),
                        "output_path": f"results/raw/{task}/output-{cond}-{trial}.md",
                        "output_words": len(out.read_text().split()),
                        "completed_at_utc": ts(out),
                        "errors": None,
                        "retries": 0,
                    }
                )
    out_path = ROOT / "results" / "raw" / "records.jsonl"
    with out_path.open("w") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")
    print(f"wrote {len(records)} records to {out_path}")


if __name__ == "__main__":
    main()
