# Pilot results: lost updates in multi-agent operation

**Date:** 2026-10-15. **Design:** `PREREGISTRATION.md`. **Harness:**
`harness.py`. **Raw data:** `results.jsonl` (40 trials).

## Setup

Two scripted agents share one WORLD (`{"findings": []}`, fresh world per
trial). Each agent: staggered start (uniform 0-2s, so overlap is emergent,
not staged), read version, think (lognormal latency, median ~1.2s), append
its finding, write back from the read snapshot. N=20 trials per condition.

- **A:** plain `update()` (last-writer-wins).
- **B:** `update(..., expected_version=v)` with re-read-and-retry (max 3).

## Results

| Condition | Lost-update rate | 95% CI | Trials w/ conflicts |
|---|---|---:|---:|
| A (no control) | **15/20 = 0.75** | 0.53-0.89 | 0/20 (nothing to conflict *with*) |
| B (expected_version) | **0/20 = 0.00** | 0.00-0.16 | 13/20, all retried clean |

## Reading

- **H1 confirmed (pilot):** the lost-update race is real under realistic
  latency: three of four unprotected trials silently drop one agent's
  write. The 5 non-racing trials are the ones where starts staggered
  enough that one agent finished before the other began.
- **H3 confirmed (pilot):** zero silent overwrites with optimistic
  concurrency; every race surfaced as an explicit `ConflictError` and
  every retry converged. No agent needed more than 2 attempts.
- The mechanism the model checker verified (P4, exactly-one-winner)
  is the same mechanism that produced the 0.00 rate here: verification
  and measurement agree.

## Limits of the pilot

- Scripted agents, not LLM agents: timing is stochastic and realistic,
  but finding content and retry decisions are not model-generated. The
  harness's `think()` is pluggable for the LLM-agent phase (N=50 planned).
- The barrier-synchronized variant (all trials race) was tried first and
  discarded as too staged; staggered starts were adopted for ecological
  validity.
- H2 (loss correlation with gap length) needs the full N=50 for power;
  not tested at pilot N.
