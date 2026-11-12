"""Prompt 3 revalidation: build A-prime bundles through the new code path.

For each task (R1, R2, C1), the mapped Agent A production in
``mapped/{task}.json`` is loaded into the new ``AgentState`` schema,
saved into a throwaway World via ``save_state`` (which runs the F1
referential-integrity validation), and loaded back via ``load_state``.
Two bundles are rendered from the loaded state with one renderer:

- ``bundles/{task}-full.md``: the full ``load_state`` state;
- ``bundles/{task}-projected.md``: ``project_state`` of that state.

Constraints travel in the world document next to the ``handoff`` key
(the shipped AgentState has no constraints section; see MAPPING.md)
and are rendered identically in both bundles.

Continuation prompts are composed with Experiment #003's own single
prompt code path (``experiments/experiment-003/runner/prompts.py``),
using the task's verbatim continuation assignment.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "src"))

from world import World, load_state, save_state
from world.handoff import AgentState, project_state

spec = importlib.util.spec_from_file_location(
    "exp003_prompts",
    REPO / "experiments" / "experiment-003" / "runner" / "prompts.py",
)
exp003_prompts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exp003_prompts)

TASKS = ["R1", "R2", "C1"]


def render(state: AgentState, constraints: list[str], task: str) -> str:
    lines = [f"# WORLD State Bundle: Task {task}", ""]
    lines += ["## Objective", "", state.objective, ""]
    lines += ["## Decisions", ""]
    if not state.decisions:
        lines += ["(none recorded)", ""]
    for d in state.decisions:
        lines += [
            f"### {d.id or '(no id)'} [status: {d.status}]",
            f"- statement: {d.text}",
            f"- rationale: {d.rationale}",
            f"- supersedes: {d.supersedes or 'none'}",
            f"- evidence_ids: {', '.join(d.evidence_ids) or 'none'}",
            "",
        ]
    lines += ["## Assumptions", ""]
    if not state.assumptions:
        lines += ["(none recorded)", ""]
    for a in state.assumptions:
        lines += [
            f"### {a.id or '(no id)'} [status: {a.status}, confidence: {a.confidence}]",
            f"- statement: {a.text}",
            f"- validated_by: {a.validated_by or 'none'}",
            "",
        ]
    lines += ["## Evidence", ""]
    if not state.evidence:
        lines += ["(none recorded)", ""]
    for e in state.evidence:
        lines += [
            f"### {e.id or '(no id)'} (kind: {e.kind or 'unspecified'})",
            f"- claim: {e.claim}",
            f"- source: {e.source}",
            "",
        ]
    lines += ["## Constraints", ""]
    if constraints:
        lines += [f"- {c}" for c in constraints] + [""]
    else:
        lines += ["(none recorded)", ""]
    lines += ["## Open questions", ""]
    if state.open_questions:
        lines += [f"- {q}" for q in state.open_questions] + [""]
    else:
        lines += ["(none recorded)", ""]
    lines += ["## Next actions", ""]
    if state.next_actions:
        lines += [f"- {a}" for a in state.next_actions] + [""]
    else:
        lines += ["(none recorded)", ""]
    return "\n".join(lines).rstrip() + "\n"


def words(text: str) -> int:
    return len(text.split())


def main() -> int:
    bundles_dir = HERE / "bundles"
    prompts_dir = HERE / "prompts"
    bundles_dir.mkdir(exist_ok=True)
    prompts_dir.mkdir(exist_ok=True)
    counts = {}
    for task in TASKS:
        mapped = json.loads((HERE / "mapped" / f"{task}.json").read_text())
        state = AgentState.from_dict(mapped["state"])
        constraints = mapped["constraints"]
        with tempfile.TemporaryDirectory() as tmp:
            w = World(f"reval-{task.lower()}", dir=tmp)
            if constraints:
                w.update({"constraints": constraints}, actor="agent-a")
            seq = save_state(w, state, actor="agent-a", note="revalidation load")
            loaded = load_state(w)
            assert loaded == state, f"{task}: round trip altered the state"
            doc = w.state()
            assert doc.get("constraints") == constraints
            full = render(loaded, constraints, task)
            projected = render(project_state(loaded), constraints, task)
        (bundles_dir / f"{task}-full.md").write_text(full)
        (bundles_dir / f"{task}-projected.md").write_text(projected)
        assignment = (
            REPO / "experiments" / "experiment-003" / "tasks" / task / "continuation.md"
        ).read_text()
        for kind, bundle in [("full", full), ("projected", projected)]:
            prompt = (
                exp003_prompts.SYSTEM_PROMPT
                + "\n\n----- USER PROMPT -----\n\n"
                + exp003_prompts.compose(assignment, bundle)
            )
            (prompts_dir / f"{task}-{kind}.txt").write_text(prompt)
        counts[task] = {
            "full_words": words(full),
            "projected_words": words(projected),
            "saved_seq": seq,
        }
        print(task, counts[task])
    (HERE / "bundle_sizes.json").write_text(json.dumps(counts, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
