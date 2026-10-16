"""Preregistered analysis for the lost-update experiment.

Reads experiments/lost-update/results.jsonl and reports:

- per-condition lost-update rates with Wilson 95% CIs (H1, H3),
- condition B conflict rate and retry convergence (H3),
- H2: logistic regression of loss on read-to-write gap in condition A,
  fit by iteratively reweighted least squares (stdlib only), with a
  Wald z-test on the gap coefficient.

Usage: python experiments/lost-update/analyze.py [--jsonl PATH]
"""

from __future__ import annotations

import argparse
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def wilson(hits: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = hits / n
    den = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - m) / den), min(1.0, (c + m) / den))


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def logistic_fit(xs: list[float], ys: list[int]) -> dict:
    """IRLS fit of logit(p) = b0 + b1*x. Returns coef, SE, z, p-value."""
    b0, b1 = 0.0, 0.0
    for _ in range(100):
        g0 = g1 = 0.0
        h00 = h01 = h11 = 0.0
        for x, y in zip(xs, ys):
            p = 1.0 / (1.0 + math.exp(-(b0 + b1 * x)))
            w = p * (1.0 - p)
            r = y - p
            g0 += r
            g1 += r * x
            h00 += w
            h01 += w * x
            h11 += w * x * x
        det = h00 * h11 - h01 * h01
        if det <= 0:
            break
        d0 = (h11 * g0 - h01 * g1) / det
        d1 = (h00 * g1 - h01 * g0) / det
        b0 += d0
        b1 += d1
        if abs(d0) < 1e-10 and abs(d1) < 1e-10:
            break
    # standard errors from the inverse Hessian at convergence
    h00 = h01 = h11 = 0.0
    for x, y in zip(xs, ys):
        p = 1.0 / (1.0 + math.exp(-(b0 + b1 * x)))
        w = p * (1.0 - p)
        h00 += w
        h01 += w * x
        h11 += w * x * x
    det = h00 * h11 - h01 * h01
    se1 = math.sqrt(h00 / det) if det > 0 else float("nan")
    z = b1 / se1 if se1 == se1 and se1 > 0 else float("nan")
    pval = 2.0 * (1.0 - norm_cdf(abs(z))) if z == z else float("nan")
    return {"b0": b0, "b1": b1, "se_b1": se1, "z": z, "p_value": pval}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", default=os.path.join(HERE, "results.jsonl"))
    args = ap.parse_args()
    rows = [json.loads(line) for line in open(args.jsonl) if line.strip()]
    out: dict = {"n_total": len(rows), "conditions": {}}
    for cond in ("A", "B"):
        sub = [r for r in rows if r["condition"] == cond]
        n = len(sub)
        lost = sum(r["lost_update"] for r in sub)
        conf = sum(1 for r in sub if r["conflicts"] > 0)
        lo, hi = wilson(lost, n)
        out["conditions"][cond] = {
            "n": n,
            "lost": lost,
            "lost_rate": lost / n if n else 0.0,
            "wilson_95": [lo, hi],
            "trials_with_conflicts": conf,
            "mean_max_gap_s": sum(r["max_gap"] for r in sub) / n if n else 0.0,
        }
    # H2: loss ~ gap in condition A
    a_rows = [r for r in rows if r["condition"] == "A"]
    xs = [r["max_gap"] for r in a_rows]
    ys = [int(r["lost_update"]) for r in a_rows]
    fit = logistic_fit(xs, ys)
    lost_gaps = [x for x, y in zip(xs, ys) if y == 1]
    kept_gaps = [x for x, y in zip(xs, ys) if y == 0]
    fit["mean_gap_lost_s"] = sum(lost_gaps) / len(lost_gaps) if lost_gaps else 0.0
    fit["mean_gap_kept_s"] = sum(kept_gaps) / len(kept_gaps) if kept_gaps else 0.0
    fit["n_lost"] = len(lost_gaps)
    fit["n_kept"] = len(kept_gaps)
    out["h2_logistic_loss_on_gap_A"] = fit
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
