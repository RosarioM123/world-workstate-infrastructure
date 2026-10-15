# Deterministic simulation testing

**Artifact:** `spec/detsim.py` (seeded scheduler + simulation harness).
**Tests:** `tests/test_detsim.py`.
**Date:** 2026-10-15.

## Idea

Real OS threads explore only a sliver of interleavings, unreproducibly.
The deterministic simulator runs the *real* `World.update` under a
seeded scheduler: workers block at instrumented yield points and the
scheduler wakes them one at a time, so exactly one worker runs between
yield points. The same seed reproduces the same interleaving exactly
(proven by double-run log equality in `test_detsim_deterministic`).

## Yield points (monkeypatched, scoped, restored)

- `World._latest_committed` yields, except inside the atomic section.
- Each invariant yields before judging (judgment is always lock-free).
- A connection proxy sniffs `BEGIN IMMEDIATE` / `COMMIT` / `ROLLBACK`
  to track the atomic section and assert it is never re-entered.

The re-check must not yield: the worker holds the SQLite write lock
there, and another worker's `BEGIN IMMEDIATE` would block its OS thread
and deadlock the single-logical-thread simulation. Atomic sections
contain no yield points, so SQLite-level serialization is real but
uncontended by construction; the scheduler explores the interleavings
of reads and judgments against commits, which is where the logic lives.

## What is asserted per seed

- `verify()` is True (hash chain intact).
- The recorded history linearizes under `spec/linearizability.py`
  (cross-validating the simulator against the checker).
- 20 seeds, all outcomes (`ok` / `rejected` / `conflict`) observed,
  genuine overlap confirmed (not accidentally sequential).

## Targeted scenario: audit-seq divergence, reproduced deterministically

`test_detsim_audit_seq_divergence` scripts the exact interleaving behind
the linearizability doc's finding, via an explicit grant script
`[0, 1, 1, 0]` (prestart runs each client to its first read; then: A
judge, B judge, B commit, A append):

- A judges `n=3` against v5 with no `expected_version` (REJECTED
  decided; unguarded so the re-check cannot turn it into a conflict).
- B commits `n=10` at `expected_version=5` → version 6, seq 6.
- A appends its REJECTED row → seq 7, *after* B's commit.

Outcome: B `("ok", 6)`, A `("rejected", 7)`, `verify()` True, and the
abstract history still linearizes. The simulator reproduces the rare
interleaving on demand instead of hoping a thread race hits it.

## Limits

- Explores interleavings at yield-point granularity (read / judge /
  commit boundaries), not inside the atomic section, which SQLite
  truly serializes.
- Monkeypatching is test-only; the shipped implementation is untouched.
- Single-process: no network partitions or multi-process clock skew.
  The crash-consistency harness covers process death separately.
