# Research overview

WORLD is a research prototype of a persistent work-state primitive for
AI agents: a named, durable JSON document whose every proposed change
is judged by declared invariants and recorded, verdict included, in a
SHA-256 hash-chained log on SQLite. It exists to test one question:
whether explicit structured work-state preserves more of what a
successor needs across an agent handoff than the conventional
alternatives (a natural-language summary or a raw transcript), and
whether the record of that work can be made verifiable enough to audit
after the fact.

This file is the map of the research program. The hypothesis is in
`research/HYPOTHESIS.md`, the negative results and limits in
`research/LIMITATIONS.md`, and the positioning against other approaches
in `research/RELATED_WORK.md`.

## The system in one paragraph

One world is one SQLite file. Writers (agents, humans, the CLI, or the
optional HTTP server) propose whole-document updates. Each proposal is
judged by the invariants declared for that handle; the verdict,
COMMITTED or REJECTED, is appended to the hash chain either way, so
rejected work is evidence, not silence. `expected_version` gives
optimistic concurrency, `idempotency_key` makes committed retries
safe, checkpoints pin immutable names to versions, and `resume()`
restores a checkpoint as a new version rather than rewriting history.
Time travel is committed-only: `state(version=N)` returns committed
history, and rejected proposals are auditable separately through
`proposal(seq)`. Optional layers add HMAC or Ed25519 signed tips (with
key rotation), per-field encryption with cryptographic redaction
(crypto-shredding that keeps `verify()` green), Merkle inclusion
proofs for selective disclosure, and a typed agent-handoff layer
(`AgentState`: objective, decisions, evidence, open questions, next
actions) stored under a reserved document key. The design rationale is
in `docs/adr/0008-world-primitive.md`; the state model the handoff
experiments used is in `docs/state-model.md`.

## Evidence base

Four kinds of evidence, in decreasing order of strength:

1. **Mechanized verification of the commit protocol.**
   `spec/model_check.py` exhaustively explores the two-phase commit
   protocol over bounded configurations (2 to 3 writers, 2 to 3
   operations): 1,220,255 states, with properties P1 to P6 (seq
   integrity, chain integrity, committed-only version,
   exactly-one-winner, idempotency, judgment recorded) holding on every
   reachable state. A mutation test (atomic re-validation removed)
   produces the expected P4 counterexample, so the checker can fail.
   Writeup: `docs/spec/protocol-verification.md`. The TLA+
   transcription (`spec/world.tla`) has not been run through TLC.
2. **Property, fuzz, and fault-injection testing.** Hypothesis
   stateful testing differentially compares `World` against a
   reference model (1,526 generated operations across 30 examples,
   zero divergences, recorded 2026-10-15); `verify()` detected 500 of
   500 seeded random in-place mutations (plus 450 under alternate
   seeds); crash-consistency injection recovered cleanly in 15 of 15
   mid-transaction SIGKILLs; an independent C# verifier with no shared
   code accepts valid chains and rejects tampered ones. A 1.06M-row
   soak found no latency drift and one honest scaling limit
   (`verify()` is O(n) memory). Artifacts: `docs/spec/`,
   `experiments/crash-consistency/`, `experiments/soak/`,
   `tools/ChainVerifyWorld/`.
3. **A preregistered concurrency experiment.** Scripted agents racing
   read-modify-write cycles lost updates in 33 of 50 trials with no
   control (95% CI 0.52 to 0.78) and 0 of 50 with `expected_version`
   plus retry. Preregistration and raw data:
   `experiments/lost-update/`. The agents were scripted, not LLMs.
4. **Handoff experiments (the core research question).** Experiments
   #001 (Block) and #002 (Intel, with a Disney replication) handed the
   same Agent A research output to a successor in three conditions
   (structured WORLD state, independent summary, raw journal), with
   blind X/Y/Z labels and grading by an independent evaluator against
   a predeclared 14-metric answer key. WORLD state preserved decision
   governance best in all three runs, narrowly; it failed revision
   history in both #002 runs; a strong summary came within 0.36 of it
   in the replication. n=1 per run, one model family, exploratory.
   Full records: `docs/experiment-001-results.md`,
   `docs/experiment-002/results.md`, scoreboard in
   `docs/benchmarks/head-to-head-scoreboard.md`.

## Performance records (dated, single machine)

Measured 2026-10-15, Linux x86_64, Python 3.12.3, with
`tools/bench_world.py` unless noted. These are records of specific
runs, not guarantees; re-run before quoting.

| Measurement | Result | Source |
|---|---|---|
| `update`, invariant judged | 1,339 ops/s | `docs/benchmarks/world-primitive.md` |
| `update` with `expected_version` | 692 ops/s | same |
| `state()` reads | 3,794 ops/s | same |
| `verify()`, full chain | 200,081 rows/s | same |
| `update_many`, batches of 500 | 54,975 ops/s (34.9x sequential) | same |
| Contention, 1 to 16 writer threads | throughput plateaus near 810 ops/s; p99 0.93 ms to 216.70 ms; correctness holds | `docs/benchmarks/contention.md` |
| Soak, 1.06M rows | bulk 69,714 ops/s; singles 2,473 ops/s; p50 flat 0.36 to 0.39 ms; verify 75,921 rows/s | `experiments/soak/RESULTS.md` |

## What is demonstrated, and what is not

Demonstrated: the commit protocol is correct over the checked
configurations; the implementation keeps its stated guarantees under
property tests, fuzzing, crash injection, tamper fuzzing, and
million-row soak; structured labeled state preserved decision
governance better than summary or transcript in three small blinded
handoff runs; optimistic concurrency eliminates the measured lost
updates for scripted agents.

Not demonstrated: anything about real multi-agent deployments, real
users, cross-model handoffs, or production workloads; human
auditability in practice; revision-history preservation (currently a
failure, not a gap in testing); statistical generality of the handoff
results. See `research/LIMITATIONS.md` for the full list, kept
deliberately unedited by optimism.

## Reproduction

- Full test suite: `pip install -e ".[test]"` then
  `python -m pytest tests/ -q`.
- Model checker: `python3 spec/model_check.py` (full exploration plus
  mutation test); CI entry point
  `python3 -m pytest tests/test_protocol_model.py -q`.
- Benchmarks: `python tools/bench_world.py`,
  `python tools/bench_contention.py`.
- Experiments: harnesses and raw outputs live in `experiments/` and
  `docs/experiment-002/`; protocols were predeclared in
  `docs/experiment-002/protocol.md` and
  `experiments/lost-update/PREREGISTRATION.md` respectively.
