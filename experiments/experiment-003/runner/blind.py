"""Blind the continuation outputs for grading.

Copies each raw continuation output into results/judged/{task}/ under a
random label ({task}-{letter}{digit}), shuffling which label maps to
which (condition, trial) per task. The mapping is written to
results/judged/mapping.private.json, which graders never see. Seed fixed
and recorded (20261103). Run after all continuations for a task complete.

Usage: python3 blind.py [TASK ...]
"""

import json
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = 20261103


def main() -> None:
    tasks = sys.argv[1:] or ["F1", "F2", "S1", "S2", "R1", "R2", "C1", "C2"]
    mapping_path = ROOT / "results" / "judged" / "mapping.private.json"
    mapping = json.loads(mapping_path.read_text()) if mapping_path.exists() else {}
    rng = random.Random(SEED)
    for task in tasks:
        cells = [
            (cond, trial)
            for cond in ("A", "B", "C")
            for trial in (1, 2, 3)
        ]
        labels = [f"{task}-{chr(ord('A') + i)}{rng.randint(2, 9)}" for i in range(9)]
        rng.shuffle(cells)
        outdir = ROOT / "results" / "judged" / task
        outdir.mkdir(parents=True, exist_ok=True)
        task_map = {}
        for label, (cond, trial) in zip(labels, cells):
            src = ROOT / "results" / "raw" / task / f"output-{cond}-{trial}.md"
            shutil.copyfile(src, outdir / f"{label}.md")
            task_map[label] = {"condition": cond, "trial": trial}
        mapping[task] = task_map
        print(f"{task}: blinded 9 continuations")
    mapping_path.write_text(json.dumps(mapping, indent=2))


if __name__ == "__main__":
    main()
