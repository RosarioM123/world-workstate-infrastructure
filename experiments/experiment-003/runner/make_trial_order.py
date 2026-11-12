"""Generate the randomized execution order for the 72 continuation trials.

Seed is fixed and recorded here (20261102) before any continuation runs,
per the preregistration. Output: runner/trial_order.json, a list of
{task, condition, trial} in execution order. Trial output files are
results/raw/{task}/output-{condition}-{trial}.md.
"""

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = ["F1", "F2", "S1", "S2", "R1", "R2", "C1", "C2"]
CONDITIONS = ["A", "B", "C"]
SEED = 20261102


def main() -> None:
    trials = [
        {"task": task, "condition": cond, "trial": trial}
        for task in TASKS
        for cond in CONDITIONS
        for trial in (1, 2, 3)
    ]
    random.Random(SEED).shuffle(trials)
    out = ROOT / "runner" / "trial_order.json"
    out.write_text(json.dumps(trials, indent=2))
    print(f"wrote {len(trials)} trials, seed {SEED}")


if __name__ == "__main__":
    main()
