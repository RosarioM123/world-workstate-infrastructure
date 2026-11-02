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

## Evidence classification

Every important quantitative claim and research finding in this
document carries one of three statuses, assigned during the
2026-11-02 audit and its follow-up investigation:

- **VERIFIED**: directly reproduced or checked against executable
  artifacts in the audit. The table below names what was run or read.
- **DOCUMENTED**: supported by project documentation or recorded
  artifacts in the repo, but not independently reproduced in the
  audit. The figure may be exactly right; the audit did not re-derive
  it.
- **NEEDS VALIDATION**: a hypothesis, a preliminary result whose
  design cannot yet carry the general claim, or a claim with no
  executed artifact behind it.

| Claim | Status | Supporting artifact and basis |
|---|---|---|
| Commit protocol model check: 1,220,255 states explored, properties P1 to P6 hold on every reachable state, and a mutation test produces the expected P4 counterexample | VERIFIED | Re-run 2026-11-02: `python3 spec/model_check.py` reproduced the state counts and property results. Writeup `docs/spec/protocol-verification.md`; test entry point `tests/test_protocol_model.py` |
| The TLA+ transcription faithfully models the commit protocol | NEEDS VALIDATION | `spec/world.tla` has never been run through TLC (no JVM in the audit environment). The Python checker is the executed artifact; the transcription is unchecked |
| Test suite: 377 tests pass | VERIFIED | Full suite run three times on 2026-11-02 (default `/tmp`): 377 passed each time. Environment note: the crash-consistency kill timing was filesystem-sensitive until the harness fix recorded in `experiments/crash-consistency/FINDINGS-2026-11-02.md` |
| Hypothesis stateful testing: 1,526 generated operations across 30 examples, zero divergences from the reference model | DOCUMENTED | `docs/spec/stateful-testing.md` (recorded 2026-10-15). The stateful test itself runs inside the suite above; the exact operation counts come from the recorded run and were not re-measured |
| `verify()` tamper fuzzing: 500 of 500 seeded random mutations detected, plus 450 more under alternate seeds | DOCUMENTED | `tests/test_verify_fuzz.py` and its 2026-10-15 commit record; the counts were not re-measured in the audit |
| Crash consistency: 15 of 15 mid-transaction SIGKILLs recovered cleanly | DOCUMENTED as recorded; the underlying property is VERIFIED by re-exercise | Record: `experiments/crash-consistency/RESULTS.md`. Re-exercise: 39 additional rounds run 2026-11-02 with independent checks (`verify()`, `PRAGMA integrity_check`, JSON parse of every row, version consistency), zero durability violations, in `experiments/crash-consistency/FINDINGS-2026-11-02.md` |
| The independent C# verifier accepts valid chains and rejects tampered ones | VERIFIED | `tests/test_csharp_verifier.py` (4 tests: valid mixed-verdict chain accepted; tampered row, broken link, and wrong world name rejected) passed inside the audit's suite runs. Implementation `tools/ChainVerifyWorld/` shares no code with the Python verifier |
| Soak: 1.06M rows, p50 latency flat (0.36 to 0.39 ms), `verify()` at 75,921 rows/s, `verify()` memory is O(n) (659 MB RSS at 1.06M rows) | DOCUMENTED | `experiments/soak/RESULTS.md` and `experiments/soak/results.json` (2026-10-15). Not re-run in the audit |
| Lost-update experiment: 33 of 50 trials lost updates with no control (95% CI 0.52 to 0.78); 0 of 50 with `expected_version` plus retry | DOCUMENTED | `experiments/lost-update/RESULTS.md`; preregistration `experiments/lost-update/PREREGISTRATION.md`. Not re-run in the audit. The agents were scripted, not LLMs |
| Experiment #001 (Block): WORLD state preserved 5/5 decisions and 7/7 assumptions, zero errors | DOCUMENTED | `docs/experiment-001-results.md`. Figures checked against the recorded tables in the audit; the experiment was not re-run. n=1 |
| Experiment #002 (Intel, Disney replication): decision-governance means 3.92 vs 3.58 vs 3.33 (Intel) and 4.45 vs 4.09 vs 2.82 (Disney); the summary came within 0.36 in the replication | DOCUMENTED, preliminary | `docs/experiment-002/results.md` sections 7 and 11, checked against the recorded tables in the audit; the experiment was not re-run. n=1 per run, one model family, exploratory |
| Revision-history preservation: the WORLD continuation scored 2/5 in both #002 runs | DOCUMENTED negative result | `docs/experiment-002/results.md`. This is a demonstrated weakness, not a gap in testing: no current evidence shows WORLD preserving revision history well |
| Benchmark figures in the performance table below (1,339 ops/s and companions) | DOCUMENTED as dated records | `docs/benchmarks/world-primitive.md`, `docs/benchmarks/contention.md`, `experiments/soak/RESULTS.md`; measured 2026-10-15 on one machine |
| Sanity re-run, 2026-11-02: `tools/bench_world.py` measured 2,506 updates/s for `update` on the audit machine | VERIFIED as an order-of-magnitude check only | Audit run 2026-11-02. This machine is faster than the 2026-10-15 record machine; the re-run corroborates the magnitude of the records above and does not replace them |
| CI on the current remote main: test jobs pass on Python 3.11, 3.12, and 3.13; the lint job fails at the Ruff lint step | VERIFIED via API query, 2026-11-02 | GitHub Actions run 41517883400 on commit `ec1a4b27` (2026-11-02): test (3.11, 3.12, 3.13) and frontend jobs succeeded, lint job failed. The same lint failure appears on the previous main commit (run 38841349349, 2026-10-16), so it predates the documentation work. The workflow configuration is `.github/workflows/ci.yml`; configuration alone would be DOCUMENTED, the run records are the evidence |
| WORLD improves AI agent reliability in general, or structured state preserves what a successor needs better than summaries or transcripts beyond the tested tasks | NEEDS VALIDATION | Rests only on Experiments #001 and #002 above: two tasks plus one replication, n=1 per run, one model family, no human evaluation. The handoff hypothesis in `research/HYPOTHESIS.md` states what would falsify it |
| Human auditability of the hash-chained record in practice | NEEDS VALIDATION | No external user has audited a real chain. See `research/LIMITATIONS.md` |

One distinction the statuses exist to protect: the 377 passing tests
(VERIFIED) demonstrate software behavior under tested conditions.
They do not by themselves establish that WORLD improves AI agent
reliability. That claim is NEEDS VALIDATION, and the only evidence
bearing on it is the handoff experiment line above.

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

Four kinds of evidence, in decreasing order of strength. Every claim
made in this section carries a status in the classification table
above; where a section below and the table differ, the table is the
audit's verdict.

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

| Measurement | Result | Source | Status |
|---|---|---|---|
| `update`, invariant judged | 1,339 ops/s | `docs/benchmarks/world-primitive.md` | DOCUMENTED |
| `update` with `expected_version` | 692 ops/s | same | DOCUMENTED |
| `state()` reads | 3,794 ops/s | same | DOCUMENTED |
| `verify()`, full chain | 200,081 rows/s | same | DOCUMENTED |
| `update_many`, batches of 500 | 54,975 ops/s (34.9x sequential) | same | DOCUMENTED |
| Contention, 1 to 16 writer threads | throughput plateaus near 810 ops/s; p99 0.93 ms to 216.70 ms; correctness holds | `docs/benchmarks/contention.md` | DOCUMENTED |
| Soak, 1.06M rows | bulk 69,714 ops/s; singles 2,473 ops/s; p50 flat 0.36 to 0.39 ms; verify 75,921 rows/s | `experiments/soak/RESULTS.md` | DOCUMENTED |

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
