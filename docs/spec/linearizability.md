# Linearizability of `World.update`

**Artifact:** `spec/linearizability.py` (mini-Knossos checker).
**Tests:** `tests/test_linearizability.py`.
**Date:** 2026-10-15.

## What is being checked

The model checker (`spec/model_check.py`) proves the *protocol design*
correct. This checks the *running implementation*: real OS threads race
`World.update` calls, and the checker searches for a linearization, a
total order extending the real-time order (A before B when A responds
before B is invoked) under which a sequential spec reproduces every
observed result. Five random concurrent histories (6 threads x 8 ops,
fresh/stale/absent `expected_version`, `monotonic("n")` invariant) all
linearize. Two mutation tests prove the checker has teeth.

## The sequential spec (the honest contract)

The abstract state is `(version, n)`. The spec models the
implementation's contract, not the invariant's wish: judgment runs
against a possibly stale fast-path read, so without `expected_version`
a commit may legally land any `k` (documented last-writer-wins).

- `("ok", ret)`: `expected_version` was None or equaled the version at
  the atomic commit point; `ret` (the new version) exceeds the old one.
- `("rejected",)`: `expected_version` was None or equaled the version
  at some point in the interval, and the proposal lost to the `n`
  there. State unchanged.
- `("conflict",)`: `expected_version` was not None and differed from
  the version at the decision point. State unchanged.

## Finding: the audit seq is not linearizable (and that is fine)

The abstract `(version, n)` state linearizes. The audit log's row seq
does not always agree with the linearization order. Concrete case: op O
with `expected_version=5` judges `k=3` against version 5 and is
rejected; concurrently C6 commits `n=10` (version 6). O's REJECTED row
is appended *after* C6's commit, so it carries a higher seq than the
commit it never observed. No single point in O's interval has both
version 5 and log length `seq(O)-1`, so no linearization exists for the
`(seq, version)` pair. Sequential clients never observe this; the row
still truthfully records its proposal, its judgment basis, and its
proposal timestamp. If strict audit ordering were ever required, the
fix would be re-judging inside the write transaction (judgment against
the locked state), at the cost of serializing all judgments.

## Method

Threads share one `World`; a global atomic counter stamps invoke/response
events, so real-time precedence is exact (no wall-clock skew). The
checker is backtracking over linear extensions with dead-end
memoization on `(placed, version, n)` and a response-order candidate
heuristic. Complete for the given history. Instant on 128-op histories
in practice; worst case remains exponential (linearizability is
NP-complete), so CI uses bounded histories.

## Mutation tests

1. Flip a committed unguarded op to `("conflict",)`: rejected, because
   conflicts require a non-None `expected_version`.
2. Deterministic stale-version case (version driven to 5, op with
   `expected_version=3` conflicts; claim it committed): rejected,
   because the version exceeds 3 at every valid position.

## Limits

- Bounded histories (48 ops in CI; instant to 128 in probing).
- No idempotency keys in the workload; that path was model-checked
  separately (P5/P6).
- Workload uses one invariant shape (`monotonic("n")`); the spec's
  contract reasoning is invariant-agnostic.
- Single-process threads: event ordering is exact by construction.
