# Protocol verification: the WORLD commit protocol

**Status:** mechanized and green (2026-10-15).
**Artifacts:** `spec/model_check.py` (executable, CI-checked),
`spec/world.tla` (TLA+ transcription for the toolbox),
`tests/test_protocol_model.py` (CI entry point).

## What was verified and why

`World.update` (`src/world/core.py`) is the trust root of WORLD: every
state change, every invariant judgment, every optimistic-concurrency
decision flows through it. The subtle part is the read-to-lock race: the
latest committed version is read *outside* the write transaction, so two
writers can both observe version V, both pass judgment, and then
serialize at `BEGIN IMMEDIATE`. Correctness rests entirely on the
re-validation *inside* the atomic section. This verification proves the
protocol correct given SQLite's `BEGIN IMMEDIATE` serialization, across
all interleavings and all possible invariant verdicts.

## The transition system

Each `update` is two atomic transitions:

- **READ_JUDGE**: read latest committed seq and snapshot; fast-path
  `expected_version` check (stale here ends the op with `ConflictError`
  before judgment, appending nothing); adversarial invariant verdict
  (the checker branches pass/fail); record pending.
  READ and JUDGE are fused because neither touches shared state: every
  interleaving the three-phase model distinguishes is preserved (a
  COMMIT can still land between another writer's READ_JUDGE and COMMIT).
- **ATOMIC_COMMIT**: one indivisible step: re-validate
  `expected_version` against the latest committed row, apply the
  idempotency dedupe, append exactly one hash-chained row (or none, on
  the idempotent short-circuit or a re-validation conflict).

`resume()` delegates to `update()`, so it is covered. Checkpoints are
out of scope (they only pin seqs, they never mutate the log).

## Abstractions

| Abstracted | Justification | What could be missed |
|---|---|---|
| Documents are opaque tokens | Verdicts are adversarially nondeterministic, so no document content could change control flow | An invariant whose verdict depends on *which* writer proposed (not modeled; invariants see only `(old, new)`) |
| Hashes are symbolic tuples | Only chain linkage is a safety property; preimage resistance is a crypto assumption, not a protocol property | Nothing protocol-level |
| Timestamps, actors, notes, canonical JSON | Do not influence control flow | A crash between timestamp generation and commit (durability, not protocol correctness; see future work) |
| `BEGIN IMMEDIATE` is one atomic step | This *is* SQLite's documented serialization guarantee | A storage engine that does not serialize writers (out of scope by architecture) |
| Bounded workloads (2-3 writers, 2-3 ops) | Bugs in this class (races, lost updates, double winners) show with 2 writers; 3 writers confirm no pairwise assumption | A bug requiring 4+ distinct writers (no known mechanism) |

## Properties

- **P1** seq integrity: row seqs are dense 1..N, unique, append-only.
- **P2** chain integrity: every row's `prev_hash` equals the previous
  row's `hash`, over *all* rows by seq (REJECTED rows included).
- **P3** committed-only version: `version()` equals the max COMMITTED
  seq (0 if none); REJECTED rows never contribute.
- **P4** exactly-one-winner: for each expected version V, at most one op
  commits with `expected_version=V`. Each COMMITTED append strictly
  increases the committed version, so a second contender necessarily
  fails the atomic re-validation. This is the property the whole
  exercise exists to prove.
- **P5** idempotency: the idempotency table always maps each key to the
  seq of its latest COMMITTED use; a short-circuit returns exactly that
  seq and appends no row.
- **P6** judgment recorded: every op that reaches JUDGE appends exactly
  one row, except the idempotent short-circuit which appends none.
  (`ConflictError` before JUDGE appends nothing: the attempt was never
  judged, so there is nothing to record.)

## Results (2026-10-15)

| Workload | States | Transitions | Time |
|---|---|---:|---:|
| 2 writers x 2 ops, full domains (ev x key x verdict) | 165,579 | 331,404 | 2.8s |
| 3 writers x 2 ops, race-focused | 935,111 | 1,911,456 | 19.5s |
| 2 writers x 3 ops, sequential | 119,565 | 193,680 | 2.2s |

All properties hold on every reachable state: **1,220,255 states** total.

## Mutation testing

A checker that cannot fail proves nothing. With the atomic
re-validation removed (`inject_bug=True`), the checker finds the P4
violation and prints the counterexample trace:

```
P4 violated: second winner for expected_version=0 (w1/op0)
```

Two writers racing on the same freshly-read version both commit: the
lost-update race from `cbddc01`, resurrected. The verification has
teeth.

## Limits

- Bounded, not unbounded: this is exhaustive *model checking* of small
  configurations, not a proof for all N. The standard justification
  applies (the "small scope hypothesis"): protocol bugs of this kind
  manifest with 2-3 participants.
- The TLA+ transcription (`spec/world.tla`) was written action-by-action
  against the Python mechanization but has not been run through TLC
  (no JVM in this environment). The Python checker is the authoritative
  mechanized artifact; the TLA+ is provided for independent toolbox
  checking.
- Crash consistency (kill -9 mid-transaction) and Byzantine writers are
  separate verification tasks, queued as future work.

## Running it

```
python3 spec/model_check.py          # full exploration + mutation test
python3 -m pytest tests/test_protocol_model.py -q   # CI entry point (~25s)
```
