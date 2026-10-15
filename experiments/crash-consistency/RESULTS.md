# Results: crash-consistency fault injection

**Date:** 2026-10-15. **Harness:** `worker.py` + `crash_test.py`.
**Test:** `tests/test_crash_consistency.py`.

## Method

A subprocess hammers a WORLD with 256KB updates (deliberately widening
the `BEGIN IMMEDIATE`..`COMMIT` window). The driver SIGKILLs it at a
random moment, then asserts: the world opens cleanly (WAL recovery),
`verify()` is True, every row's state parses as JSON, and `version()`
equals the max COMMITTED seq. The worker prints `start i` / `done i`
markers around each update, so a `start` with no matching `done` proves
the kill landed *inside* a transaction rather than between two.

## Results

15 rounds, 15/15 kills landed mid-transaction, **0 failures**:

- Every kill recovered with `verify()` True: no torn writes, no broken
  hash links, no unparsable rows.
- `version()` always equaled the max COMMITTED seq: the interrupted
  transaction rolled back atomically, never half-applied.

## Reading

The commit protocol's atomicity (assumed by the model checker as
SQLite's `BEGIN IMMEDIATE` serialization guarantee) survives the
harshest client-side failure: the OS killing the process mid-commit.
WAL-mode recovery does its job; the hash chain is never left in a
state `verify()` would reject. Durability is now tested, not asserted.

## Limits

- Single-writer victim: crash-during-contention (kill one of several
  racing writers) is not covered.
- Kill timing is random, not targeted at specific commit phases
  (pre-lock judgment vs. in-transaction append).
- Host-level failures (disk loss, power cut mid-fsync) are out of scope;
  this tests process death only.
