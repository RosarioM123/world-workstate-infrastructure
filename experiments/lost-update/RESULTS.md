# Full-run results: lost updates in multi-agent operation

**Date:** 2026-10-15. **Design:** `PREREGISTRATION.md`. **Harness:**
`harness.py` (`--trials 50 --seed 20261016`; fresh seed, disclosed).
**Analysis:** `analyze.py`. **Raw data:** `results.jsonl` (100 trials).

## Setup

Two scripted agents share one WORLD (`{"findings": []}`, fresh world per
trial). Each agent: staggered start (uniform 0-2s, so overlap is emergent,
not staged), read version, think (lognormal latency, median ~1.2s), append
its finding, write back from the read snapshot. N=50 trials per condition.

- **A:** plain `update()` (last-writer-wins).
- **B:** `update(..., expected_version=v)` with re-read-and-retry (max 3).

## Results

| Condition | Lost-update rate | 95% CI | Trials w/ conflicts |
|---|---|---:|---:|
| A (no control) | **33/50 = 0.66** | 0.52-0.78 | 0/50 (nothing to conflict *with*) |
| B (expected_version) | **0/50 = 0.00** | 0.00-0.07 | 40/50, all retried clean |

H2 (condition A, loss on read-to-write gap): logistic regression
logit(p) = b0 + b1*gap gives **b1 = 0.73, SE 0.33, z = 2.20, p = 0.028**.
Mean gap: 2.46s on lost trials vs 1.56s on kept trials (33 lost, 17 kept).

## Reading

- **H1 confirmed:** the lost-update race is real under realistic latency.
  Two of three unprotected trials silently drop one agent's write; the
  95% CI (0.52-0.78) excludes anything below one-half.
- **H2 confirmed:** loss probability rises with the read-to-write gap
  (p = 0.028). Longer generations widen the race window, exactly as
  hypothesized. Mean gap differs by ~0.9s between lost and kept trials.
- **H3 confirmed:** zero silent overwrites with optimistic concurrency
  across 50 trials (CI upper bound 0.07). Races surfaced as explicit
  `ConflictError`s in 40/50 trials; every retry converged within 3 attempts.
- The mechanism the model checker verified (P4, exactly-one-winner) is the
  same mechanism that produced the 0.00 rate here: verification and
  measurement agree at full power.

## Pilot (superseded)

N=20/condition, seed 20261015: A 15/20 = 0.75 (CI 0.53-0.89); B 0/20 = 0.00
(CI 0.00-0.16), 13/20 conflicts retried clean. The full run replicates the
pilot's direction with tighter intervals and adds the H2 test the pilot
was underpowered for.

## Limits

- Scripted agents, not LLM agents: timing is stochastic and realistic,
  but finding content and retry decisions are not model-generated. The
  harness's `think()` is pluggable for the LLM-agent phase (queued;
  blocked on model API credentials, none available 2026-10-15).
- The barrier-synchronized variant (all trials race) was tried first and
  discarded as too staged; staggered starts were adopted for ecological
  validity.
- Gap is measured as the trial's max think time (preregistered proxy);
  per-agent start offsets are not logged, so the regression captures gap
  length, not the full overlap geometry.
