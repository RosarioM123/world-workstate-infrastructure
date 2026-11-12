"""Copy each continuation's handoff artifact next to its blind label.

Graders assign metric 5 failure-cause codes by comparing a continuation
to the artifact it was based on. This script reads the private mapping
(graders never see it) and writes results/judged/{task}/artifact-{label}.md
so the grader can do that comparison after scoring, without learning the
condition from a filename. The artifact format itself can still reveal
the condition; that is a declared blinding imperfection in the report.

Run after blind.py. Usage: python3 blind_artifacts.py
"""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT_FILES = {"A": "state.md", "B": "summary.md", "C": "journal.md"}


def main() -> None:
    mapping = json.loads(
        (ROOT / "results" / "judged" / "mapping.private.json").read_text()
    )
    for task, task_map in mapping.items():
        for label, cell in task_map.items():
            src = ROOT / "artifacts" / task / ARTIFACT_FILES[cell["condition"]]
            dst = ROOT / "results" / "judged" / task / f"artifact-{label}.md"
            shutil.copyfile(src, dst)
        print(f"{task}: artifact copies written for {len(task_map)} labels")


if __name__ == "__main__":
    main()
