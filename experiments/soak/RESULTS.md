# Soak results: 1.06M-row chain

**Date:** 2026-10-15. **Tool:** `experiments/soak/soak.py`
(`--rows 1000000 --singles 60000`). **Raw:** `results.json`.
Machine: Linux x86_64, Python 3.12.3. Database on tmpfs
(fsync-cheap; the drift measurement is filesystem-independent).

## Protocol

- **Phase 1:** 1,000,000 rows via `update_many` (batches of 2,000).
- **Phase 2:** 60,000 single `update()` calls in 12 chunks of 5,000,
  recording per-chunk p50/p99 per-op latency.
- **Phase 3:** `verify()` over the full 1,060,000-row chain.

## Results

| Phase | Result |
|---|---|
| Bulk build | 69,714 ops/s (14.3s for 1M rows) |
| Sustained singles | 2,473 ops/s (24.3s for 60k) |
| p99 drift, first to last chunk | 0.81 ms to 0.80 ms (**0.99x**, no drift) |
| p50 across all 12 chunks | 0.36-0.39 ms, flat |
| Full-chain verify | 75,921 rows/s (14.0s for 1.06M rows), True |
| Final version | 1,060,000, exact |
| DB size | 217.7 MB (~205 bytes/row) |
| Max RSS | 659 MB |

## Reading

- **No latency drift with chain length.** p50 is flat at ~0.38 ms and
  p99 shows no trend (0.54-1.59 ms noise band) from 1.00M to 1.06M rows.
  The append path (`SELECT ... ORDER BY seq DESC LIMIT 1` on the
  primary key, single-row INSERT) is O(1) as designed.
- **verify() is O(n) time and O(n) memory.** 14 seconds and 659 MB for
  1.06M rows: it `fetchall()`s the chain. Correct at this scale, but a
  future streaming verify (server-side cursor, constant memory) is the
  obvious next step past ~10M rows.
- **Bulk vs single gap persists at scale:** 69.7k ops/s bulk vs
  2.5k ops/s singles, a 28x multiplier, consistent with the 34.9x
  measured at 3k rows in `docs/benchmarks/world-primitive.md`.

## Limits

- tmpfs database: measures algorithmic scaling, not fsync-bound disk
  behavior (singles on real disk are fsync-limited, as expected).
- Single-threaded writer; write contention is profiled separately in
  `docs/benchmarks/contention.md`.
- Documents are small (`{"n": int}`); larger documents grow the
  205 bytes/row figure linearly.
