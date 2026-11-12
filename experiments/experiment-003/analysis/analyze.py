"""Analysis for Experiment #003.

Reads ground truths, blind-grading scores, and the label mapping, and
computes per-metric results exactly as predeclared in protocol.md:
per task and condition means and standard deviations across the 3 trials,
paired mean differences (A minus B, A minus C) within task and trial slot,
the revision-history subset separately, artifact size statistics, and
preservation per 1,000 words. No significance tests. No composite score.

Outputs: analysis/results.json and analysis/tables.md.
"""

import json
import math
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parent.parent
TASKS = ["F1", "F2", "S1", "S2", "R1", "R2", "C1", "C2"]
CONDITIONS = ["A", "B", "C"]
ARTIFACT_FILES = {"A": "state.md", "B": "summary.md", "C": "journal.md"}
VERDICT = {"full": 1.0, "partial": 0.5, "miss": 0.0}
REVISION_SUBSET = ["R1", "R2", "F1", "S1"]


def frac(verdicts: dict, item_ids: list) -> float | None:
    if not item_ids:
        return None
    vals = [VERDICT[verdicts[i]] for i in item_ids if i in verdicts]
    if not vals:
        return None
    return sum(vals) / len(item_ids)


def load_scores() -> dict:
    """Return {(task, condition, trial): per-continuation computed dict}."""
    mapping = json.loads(
        (ROOT / "results" / "judged" / "mapping.private.json").read_text()
    )
    out = {}
    for task in TASKS:
        scores = json.loads((ROOT / "results" / "scores" / f"{task}.json").read_text())
        gt = json.loads((ROOT / "tasks" / task / "ground_truth.json").read_text())
        dec_ids = [d["id"] for d in gt["decisions"]]
        con_ids = [c["id"] for c in gt["constraints"]]
        asm_ids = [a["id"] for a in gt["assumptions"]]
        ev_ids = [e["id"] for e in gt["evidence"]]
        chain_ids = [c["id"] for c in gt["revision_chains"]]
        for cont in scores["continuations"]:
            cell = mapping[task][cont["label"]]
            key = (task, cell["condition"], cell["trial"])
            chain_scores = {}
            causes = {}
            for cid in chain_ids:
                entry = cont["revision_chains"].get(cid)
                if entry:
                    chain_scores[cid] = sum(entry["elements"]) / 6.0
                    if "cause" in entry:
                        causes[cid] = entry["cause"]
            losses = []
            partials = []
            for group, ids in (
                ("decisions", dec_ids),
                ("constraints", con_ids),
                ("assumptions", asm_ids),
                ("provenance", ev_ids),
            ):
                for i in ids:
                    v = cont[group].get(i)
                    if v == "miss":
                        losses.append(f"{group}:{i}")
                    elif v == "partial":
                        partials.append(f"{group}:{i}")
            for cid in chain_ids:
                if chain_scores.get(cid, 1.0) < 1.0:
                    losses.append(f"revision_chains:{cid}")
            out[key] = {
                "m1_decisions": frac(cont["decisions"], dec_ids),
                "m2_constraints": frac(cont["constraints"], con_ids),
                "m3_assumptions": frac(cont["assumptions"], asm_ids),
                "m4_provenance": frac(cont["provenance"], ev_ids),
                "m5_revision": (mean(chain_scores.values()) if chain_scores else None),
                "chain_scores": chain_scores,
                "chain_causes": causes,
                "m6_contradictions": len(cont["contradictions"]["must_not_state_asserted"])
                + len(cont["contradictions"]["other"]),
                "m7_fabricated": len(cont["unsupported"]["fabricated"]),
                "m7_unverifiable": len(cont["unsupported"]["unverifiable"]),
                "m8_quality": cont["continuation_quality"],
                "hard_failure": bool(cont.get("hard_failure")),
                "loss_count": len(losses),
                "losses": losses,
                "partials": partials,
            }
    return out


def agg(values: list) -> dict:
    vals = [v for v in values if v is not None]
    if not vals:
        return {"n": 0, "mean": None, "sd": None}
    return {
        "n": len(vals),
        "mean": round(mean(vals), 4),
        "sd": round(stdev(vals), 4) if len(vals) > 1 else 0.0,
    }


METRICS = [
    "m1_decisions",
    "m2_constraints",
    "m3_assumptions",
    "m4_provenance",
    "m5_revision",
    "m6_contradictions",
    "m7_fabricated",
    "m8_quality",
    "loss_count",
]


def main() -> None:
    data = load_scores()
    artifact_sizes = {}
    for task in TASKS:
        artifact_sizes[task] = {}
        for cond, fname in ARTIFACT_FILES.items():
            text = (ROOT / "artifacts" / task / fname).read_text()
            artifact_sizes[task][cond] = {"words": len(text.split()), "chars": len(text)}

    results = {"per_task_condition": {}, "per_condition": {}, "paired": {}, "revision_subset": {}}
    lines = ["# Experiment #003: analysis tables", ""]
    lines.append("All results PRELIMINARY, single model family, n = 3 trials per cell. No composite score. No significance tests.")
    lines.append("")

    for task in TASKS:
        results["per_task_condition"][task] = {}
        lines.append(f"## {task}")
        lines.append("")
        lines.append("| Metric | A (WORLD) mean (sd) | B (summary) mean (sd) | C (transcript) mean (sd) |")
        lines.append("|---|---|---|---|")
        for metric in METRICS:
            row = [metric]
            for cond in CONDITIONS:
                vals = [data[(task, cond, t)][metric] for t in (1, 2, 3) if (task, cond, t) in data]
                a = agg(vals)
                results["per_task_condition"][task].setdefault(cond, {})[metric] = a
                row.append("-" if a["mean"] is None else f"{a['mean']:.3f} ({a['sd']:.3f})")
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    for cond in CONDITIONS:
        results["per_condition"][cond] = {}
        for metric in METRICS:
            vals = [v[metric] for (t, c, _), v in data.items() if c == cond]
            results["per_condition"][cond][metric] = agg(vals)
    lines.append("## Per condition (all tasks, all trials)")
    lines.append("")
    lines.append("| Metric | A mean (sd, n) | B mean (sd, n) | C mean (sd, n) |")
    lines.append("|---|---|---|---|")
    for metric in METRICS:
        row = [metric]
        for cond in CONDITIONS:
            a = results["per_condition"][cond][metric]
            row.append("-" if a["mean"] is None else f"{a['mean']:.3f} ({a['sd']:.3f}, n={a['n']})")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    for metric in METRICS:
        for pair, other in (("A-B", "B"), ("A-C", "C")):
            diffs = []
            for task in TASKS:
                for t in (1, 2, 3):
                    a = data.get((task, "A", t), {}).get(metric)
                    b = data.get((task, other, t), {}).get(metric)
                    if a is not None and b is not None:
                        diffs.append(a - b)
            results["paired"].setdefault(metric, {})[pair] = agg(diffs)
    lines.append("## Paired mean differences (within task and trial slot)")
    lines.append("")
    lines.append("| Metric | A-B mean (sd, n pairs) | A-C mean (sd, n pairs) |")
    lines.append("|---|---|---|")
    for metric in METRICS:
        row = [metric]
        for pair in ("A-B", "A-C"):
            a = results["paired"][metric][pair]
            row.append("-" if a["mean"] is None else f"{a['mean']:+.3f} ({a['sd']:.3f}, n={a['n']})")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    lines.append("## Revision-history subset (R1, R2, F1, S1 chains)")
    lines.append("")
    for cond in CONDITIONS:
        chain_vals = []
        causes = {}
        for task in REVISION_SUBSET:
            for t in (1, 2, 3):
                entry = data.get((task, cond, t))
                if entry:
                    chain_vals.extend(entry["chain_scores"].values())
                    for cause in entry["chain_causes"].values():
                        causes[cause] = causes.get(cause, 0) + 1
        results["revision_subset"][cond] = {"chain_score": agg(chain_vals), "causes": causes}
        a = results["revision_subset"][cond]["chain_score"]
        lines.append(f"- Condition {cond}: chain element score mean {a['mean']}, sd {a['sd']}, n chains scored {a['n']}; failure causes {causes}")
    lines.append("")

    lines.append("## Artifact sizes and context efficiency (metric 10)")
    lines.append("")
    lines.append("| Task | A words | B words | C words | A pres/1k | B pres/1k | C pres/1k |")
    lines.append("|---|---|---|---|---|---|---|")
    results["sizes"] = artifact_sizes
    results["efficiency"] = {}
    for task in TASKS:
        row = [task]
        eff = {}
        for cond in CONDITIONS:
            words = artifact_sizes[task][cond]["words"]
            row.append(str(words))
            pres = []
            for t in (1, 2, 3):
                entry = data.get((task, cond, t))
                if entry:
                    parts = [entry[m] for m in ("m1_decisions", "m2_constraints", "m3_assumptions", "m4_provenance", "m5_revision")]
                    parts = [p for p in parts if p is not None]
                    if parts:
                        pres.append(mean(parts))
            eff[cond] = round(mean(pres) / words * 1000, 4) if pres and words else None
        results["efficiency"][task] = eff
        for cond in CONDITIONS:
            row.append("-" if eff[cond] is None else f"{eff[cond]:.3f}")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    hf = {(t, c): sum(1 for (_, cc, _), v in data.items() if cc == c and v["hard_failure"]) for t in TASKS for c in CONDITIONS}
    results["hard_failures"] = {f"{t}/{c}": n for (t, c), n in hf.items() if n}
    lines.append(f"Hard failures (constraint violations): {results['hard_failures'] or 'none'}")
    lines.append("")

    (ROOT / "analysis" / "results.json").write_text(json.dumps(results, indent=2))
    (ROOT / "analysis" / "tables.md").write_text("\n".join(lines))
    print("wrote analysis/results.json and analysis/tables.md")
    print(f"continuations scored: {len(data)}")


if __name__ == "__main__":
    main()
