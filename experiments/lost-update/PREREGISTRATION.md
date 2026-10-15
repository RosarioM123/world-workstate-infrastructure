# Preregistration: lost updates in multi-agent LLM systems

**Date:** 2026-10-15
**Status:** pilot running (scripted agents); LLM-agent phase queued.

## Research question

WORLD's commit protocol was mechanically verified to give exactly-one-winner
under optimistic concurrency (`docs/spec/protocol-verification.md`, P4).
But verification proves the mechanism *can* prevent lost updates, not that
the failure mode *actually manifests* in agentic operation, nor that agents
use the mechanism correctly. This experiment measures both.

## Design

Two agents share one WORLD holding `{"findings": []}`. Each agent loops:
read version v, "think" (latency drawn from a lognormal distribution fit to
rough LLM generation times, median ~1.2s), append its finding to the list,
write back using the snapshot read at loop start (modeling the real
read-to-write gap of generation).

- **Condition A (no control):** plain `update()`. Last-writer-wins.
- **Condition B (optimistic concurrency):** `update(..., expected_version=v)`.
  On `ConflictError`, re-read and retry (max 3 attempts).

Agents are **scripted** in the pilot (deterministic findings, stochastic
timing); the harness exposes a pluggable `think()` so the LLM-agent phase
can substitute real model generation and real retry decisions.

## Conditions and N

- Pilot: N=20 trials per condition, fresh world per trial (independence).
- Full run (queued): N=50 per condition.

## Metrics

- **A:** lost-update rate = fraction of trials where the final document is
  missing at least one agent's finding (silent overwrite).
- **B:** conflict rate (fraction of writes raising ConflictError), retry
  success rate, completeness (both findings present).
- Auxiliary: distribution of read-to-write gaps; correlation of gap length
  with loss in A.

## Predictions

- H1: Condition A shows a nonzero lost-update rate (the race is real under
  realistic latency, not just in the model checker).
- H2: In A, loss probability increases with the read-to-write gap (longer
  generations widen the race window).
- H3: Condition B shows zero silent overwrites; conflicts surface as
  explicit errors and retries converge.

## Falsification

- If Condition A shows zero lost updates across the full N=50, H1 is
  rejected: the failure mode is rarer than hypothesized under these
  latencies, and the mechanism's value is preventive rather than corrective.
- If Condition B shows any silent overwrite, the implementation (not just
  the model) has a bug: stop and investigate.

## Analysis plan

Report rates with Wilson 95% confidence intervals; logistic regression of
loss on gap length in A. All code and raw trial logs committed alongside.
