# ADR 0003: Single-transaction check-then-act

Date: 2026-09-17
Status: Accepted

## Context

The constraint engine reads current state, checks the policy, then
writes the verdict and the new state. If two writers interleave between
the read and the write, both can pass the checks against the same stale
state and the second commit silently violates the physical or financial
limits (the classic check-then-act race).

## Decision

Run the whole read-check-write sequence inside one `BEGIN IMMEDIATE`
SQLite transaction per `execute_deterministic_transition()` call.
IMMEDIATE (not DEFERRED) takes the write lock up front, so the second
concurrent writer blocks at `BEGIN` instead of racing the checks.

## Consequences

- Good: the invariant "committed state always satisfies the policy" holds
  under concurrency, not just in single-threaded tests. Proven by
  `tests/test_concurrency.py`: 16 threads race to over-drain one node,
  exactly one commits.
- Good: no application-level locking, no lock ordering to get wrong.
- Bad: writers serialize on the single database write lock. Throughput
  tops out around ~1.7k intents/s on a dev VM (see README benchmarks),
  which is plenty for an agent coordination ledger and far below what
  would justify lock striping.
- Bad: lock contention surfaces as latency (bounded by `busy_timeout`),
  not as errors, so a pathological writer can slow others down.
- Revisit when: sustained write load approaches the single-lock ceiling.
  The escape hatch is partitioning entities across databases, not
  weakening the atomicity.
