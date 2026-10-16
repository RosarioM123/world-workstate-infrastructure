# Contention profile: OCC latency vs writer threads

Measured 2026-10-15. Machine: Linux x86_64, Python 3.12.3.
Tool: `tools/bench_contention.py`.

Each thread runs 200 read-modify-write loops against one shared WORLD with
the optimistic-concurrency pattern (`read()` then
`update(expected_version=v)`, re-read-and-retry on `ConflictError`).
Per-op latency covers the whole loop including retries. Every level ends
with an exact version check (`version == 1 + threads * ops`) and a clean
`verify()`.

| threads | throughput | p50 | p90 | p99 | conflict rate | correct |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1585 ops/s | 0.61 ms | 0.69 ms | 0.93 ms | 0.000 | yes |
| 2 | 1247 ops/s | 0.70 ms | 3.81 ms | 13.68 ms | 0.195 | yes |
| 4 | 1276 ops/s | 0.79 ms | 8.41 ms | 22.37 ms | 0.433 | yes |
| 8 | 812 ops/s | 1.62 ms | 26.82 ms | 88.58 ms | 0.642 | yes |
| 16 | 810 ops/s | 2.35 ms | 53.86 ms | 216.70 ms | 0.697 | yes |

## Reading

- **The median lies; the tail tells the truth.** p50 degrades gracefully
  (0.61 to 2.35 ms, 3.9x) while p99 explodes (0.93 to 216.70 ms, 233x).
  Under contention, most operations still win the race on the first try;
  the losers retry, and retries stack into the tail.
- **Conflict rate saturates near 0.70**, not 1.00: even with 16 writers
  racing, three in ten attempts still commit first-try. The race window
  (read to `BEGIN IMMEDIATE`) stays small relative to scheduling quanta.
- **Aggregate throughput plateaus near 810 ops/s** past 8 threads:
  SQLite serializes writers on one lock, so more threads add retries,
  not commits. This is the expected single-node ceiling, not a bug.
- **Correctness holds at every level**: exact final versions, clean
  `verify()`, zero lost updates. Contention costs latency, never
  correctness, which is the whole point of the OCC design.

## Limits

- Threads on one machine, not distributed clients; network latency would
  widen the race window and raise conflict rates.
- No artificial think time between read and write: this profiles the
  primitive's raw contention, not an agentic workload (see
  `experiments/lost-update` for realistic gaps).
- One document shape (`{"n": int}`); larger documents shift the per-op
  cost but not the shape of the curve.
