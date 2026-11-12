"""Compose all Agent B continuation prompts for Experiment #003.

For each task and condition, composes the prompt through the single code
path in prompts.py (system prompt is fixed; the user prompt is the task's
continuation assignment plus one handoff artifact) and writes it to
results/raw/{task}/prompt-{cond}.txt. Prints word and character counts
per artifact. Run only after the parity gate passes for a task.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompts import CONDITION_ARTIFACTS, SYSTEM_PROMPT, compose  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TASKS = ["F1", "F2", "S1", "S2", "R1", "R2", "C1", "C2"]


def words(text: str) -> int:
    return len(text.split())


def main() -> None:
    print("system prompt words:", words(SYSTEM_PROMPT))
    for task in TASKS:
        assignment = (ROOT / "tasks" / task / "continuation.md").read_text()
        for cond, fname in CONDITION_ARTIFACTS.items():
            artifact = (ROOT / "artifacts" / task / fname).read_text()
            prompt = compose(assignment, artifact)
            out = ROOT / "results" / "raw" / task / f"prompt-{cond}.txt"
            out.write_text(prompt)
            print(
                f"{task} {cond}: artifact {words(artifact)} words, "
                f"{len(artifact)} chars; prompt {words(prompt)} words"
            )


if __name__ == "__main__":
    main()
