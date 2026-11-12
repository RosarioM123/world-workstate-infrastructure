# Prompt 3 Benchmarks: Before and After

Methodology: `experiments/prompt3/bench.py`, run unchanged before and
after the Prompt 3 changes. Stdlib only. Fresh worlds in a temp dir on
each run. Sizes: 1,000 single updates; one `update_many` batch of
2,000; verify and revision reads on a 20,000-version chain built with
`update_many` in chunks of 500 (document: a counter, a meta block, a
10-item list, and a small handoff section; `meta.owner` flips once at
the midpoint so `blame()` has to walk about 10,000 snapshots).

Environment (both runs): Python 3.12.3, Linux 7.0.0-39-generic x86_64
(glibc 2.39), 4 CPUs, this machine. Peak RSS via
`resource.getrusage(RUSAGE_SELF).ru_maxrss`.

## BEFORE (HEAD cbcbc66, unmodified code), 2026-11-04

| Operation | Result |
|---|---|
| single update | 1,000 updates in 0.415s = 2,407.4 updates/s |
| update_many | 2,000 updates in 0.036s = 55,925.6 updates/s |
| checkpoint create | 0.57 ms |
| resume | 0.97 ms |
| verify (20,000 versions) | ok=True, 0.109s (183,177 rows/s) |
| verify peak RSS | 25.4 MB -> 45.2 MB (delta 19.7 MB) |
| state(version=N) | 0.72 ms |
| history() | 20,000 rows in 45.8 ms |
| blame('meta.owner') | 130.7 ms (seq=10001, modified) |
| large-chain DB size | 8.9 MB for 20,000 versions |

Baseline test suite at the same point: 377 passed
(`python -m pytest tests/ -q`, 70.05s).
Baseline model checker: P1..P6 hold; 165,579 + 935,111 + 119,565 =
1,220,255 explored states across the three configurations; mutation
test detects the injected P4 bug.

## AFTER (Prompt 3 changes F1 to F6 in the working tree), 2026-11-04

Same script, same machine, same sizes.

| Operation | Before | After | Delta |
|---|---|---|---|
| single update | 2,407.4 /s | 1,853.6 /s (first run); 2,352.6 /s (repeat) | within run-to-run variance, see note |
| update_many | 55,925.6 /s | 56,961.3 /s (repeat: 50,936.0 /s) | no material change |
| checkpoint create | 0.57 ms | 0.55 ms | no material change |
| resume | 0.97 ms | 0.89 ms | no material change |
| verify (20,000 versions) | 0.109s (183,177 rows/s) | 0.096s (207,427 rows/s) | about 12 percent faster |
| verify peak RSS delta | 19.7 MB | 0.8 MB (repeat: 1.2 MB) | F5 streaming removes the fetchall blowup at this scale |
| state(version=N) | 0.72 ms | 0.67 ms | no material change |
| history() | 45.8 ms | 47.5 ms | no material change |
| blame('meta.owner') | 130.7 ms | 60.7 ms (repeat: 63.3 ms) | about 2x faster: streaming walk stops at the change instead of parsing every snapshot |
| large-chain DB size | 8.9 MB | 8.9 MB | unchanged |

Note on single update: the first AFTER run read 1,853.6 updates/s,
but a repeat run of the identical script read 2,352.6 updates/s,
statistically indistinguishable from the BEFORE 2,407.4 on this
shared host. No Prompt 3 change touches the update hot path (F3a's
schema check runs once per World construction), so this is recorded
as measurement variance, not a regression. Every other operation is
unchanged within noise except the two F5 targets, verify memory and
blame latency, which improved as designed.

Test suite AFTER: 409 passed (`python -m pytest tests/ -q`, 73.12s),
up from 377 (32 new tests). Model checker AFTER: P1..P6 hold,
1,220,255 explored states, identical to baseline, as predicted:
no change altered the checked transition semantics.
