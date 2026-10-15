# WORLD primitive benchmarks

Benchmarks for the current `src/world` primitive (`World`: versioned,
tamper-evident work-state documents). Run with:

```
python tools/bench_world.py [--rows N]   # default N = 5000
```

The database lives in a temp dir; nothing touches `$WORLD_DIR`.

## Results

Measured 2026-10-15. Machine: Linux x86_64, Python 3.12.3.
Workload: 10,000 sequential versions (5,000 plain updates + 5,000
`expected_version` updates), one invariant judged per update.

| operation | ops | total | per-op | throughput |
| --- | ---: | ---: | ---: | ---: |
| update (invariant judged) | 5000 | 3.73s | 0.747 ms | 1339 ops/s |
| update (expected_version) | 5000 | 7.23s | 1.445 ms | 692 ops/s |
| state() latest | 5000 | 1.32s | 0.264 ms | 3794 ops/s |
| state(version=k) historical | 5000 | 1.87s | 0.374 ms | 2673 ops/s |
| verify() full chain | 10000 | 0.05s | 0.005 ms | 200081 ops/s |
| history(limit=all) | 10000 | 0.02s | 0.002 ms | 459710 ops/s |

## Optimistic-concurrency read path (2026-10-15)

The `update (expected_version)` row above is a harness artifact: the
benchmark did a separate `world.version` read (a full connection
lifecycle) only because `state()` does not return its version. The
realistic client loop is read-modify-write. `World.read()` returns
`(state, version)` atomically, cutting the loop from three connection
lifecycles (`state()` + `version` + `update`) to two (`read()` +
`update`). Measured at 3000 loops, same machine:

| operation | ops | total | per-op | throughput |
| --- | ---: | ---: | ---: | ---: |
| rmw old (state+version+update) | 3000 | 2.89s | 0.963 ms | 1039 ops/s |
| rmw new (read+update) | 3000 | 1.87s | 0.624 ms | 1602 ops/s |

**1.54x** on the OCC read-modify-write loop. The commit path is
unchanged, so the model-checked exactly-one-winner property (P4,
1.22M states) still covers it: a stale version aborts with
`ConflictError`, never silently overwrites.

## Notes

- Every `update` opens a fresh connection, judges invariants, hashes the
  new row, and commits inside `BEGIN IMMEDIATE`. There is no batching and
  no caching; handles are stateless by design.
- The `expected_version` row includes one `version` read per op, because
  that is how the optimistic-concurrency path is actually used.
- `verify()` re-hashes the full chain in Python; it scales linearly and
  stays far below update cost at this size.
- Single-threaded. For concurrent-writer behavior see
  `tests/test_world_concurrency.py` (16 threads serialize on
  `expected_version`; exactly one wins).
- Timings are machine-dependent. Re-run on your hardware before quoting.
