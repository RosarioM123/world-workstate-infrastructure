# WORLD status

Single-pointer dashboard. Updated 2026-11-02. Every number below was
verified against code, artifacts, or a fresh run on that date; the
audit trail is in the commit "docs: strengthen research positioning
and technical documentation".

## Current state

- **Version:** 0.1.0 (`src/world/__init__.py`). Working prototype, not
  deployed, not production-ready. No external users.
- **Tests:** 377 passing, 0 failing (full suite run locally
  2026-11-02, Python 3.12.3). CI runs pytest plus ruff and mypy on
  Python 3.11, 3.12, and 3.13.
- **License:** MIT (`LICENSE`).

## Experiments

- **Experiment #001** (Block, 2026-09-17): complete. Structured state
  won on governance (5/5 decisions with rationale, 7/7 assumptions with
  confidence, zero errors); n=1. `docs/experiment-001-results.md`.
- **Experiment #002** (Intel main run plus Disney replication,
  2026-09-17 to 23): complete. WORLD-state continuation preserved
  decision governance best in both runs (reference means: Intel 3.92
  vs 3.58 vs 3.33; Disney 4.45 vs 4.09 vs 2.82), narrowly; the summary
  came within 0.36 in the replication; the WORLD continuation failed
  revision history (2 of 5) in both runs. Thesis partially supported,
  narrowly scoped. `docs/experiment-002/results.md`.
- **Lost-update experiment**: complete, preregistered. Scripted
  agents: 33 of 50 lost updates with no control, 0 of 50 with
  `expected_version` plus retry. LLM-agent replication still blocked
  on model API credentials. `experiments/lost-update/`.
- **Crash consistency**: complete. 15 of 15 mid-transaction SIGKILLs
  recovered cleanly. `experiments/crash-consistency/`.
- **Soak**: complete. 1.06M rows, no latency drift; `verify()` is
  O(n) memory (659 MB RSS at 1.06M rows), the known scaling limit.
  `experiments/soak/`.

## Verification

- **Protocol model checker** (`spec/model_check.py`): 1,220,255
  states explored across three bounded workloads; properties P1 to P6
  hold on every reachable state; mutation test (re-validation removed)
  produces the P4 counterexample. Re-run and confirmed 2026-11-02.
  The TLA+ transcription has not been run through TLC (no JVM in the
  environment); the Python checker is authoritative.
- **Property and fuzz testing**: Hypothesis stateful differential
  testing (1,526 operations, zero divergences); `verify()` fuzzing
  detected 500 of 500 seeded mutations (plus 450 under alternate
  seeds); red-team suite documents detected and undetected attack
  classes (`docs/SECURITY.md`).
- **Independent C# verifier** (`tools/ChainVerifyWorld/`): no shared
  code with the Python implementation; accepts valid chains, rejects
  tampered rows, broken links, and wrong world names.

## Shipped in the primitive since 0.1.0

Batch updates (`update_many`, 54,975 ops/s at batch 500 in the
2026-10-15 benchmark record); atomic `read()` for the OCC loop;
HMAC and Ed25519 signed tips with key rotation; per-field encryption
with crypto-shredding redaction; Merkle inclusion proofs; per-field
blame; committed-only time travel with `proposal(seq)` audit access;
log export/import via CLI. Benchmarks: `docs/benchmarks/`.

## Open items

- **Revision history** is the demonstrated failure from #002 and the
  next experiment the record calls for, ahead of any broader claim.
- **Cross-model handoffs** and **human auditability** (success criteria
  3 and 2 in `docs/hypothesis.md`) remain untested.
- **Persisted invariant registry** (the DB naming the rules that
  judged each version) and **streaming verify** are designed gaps, not
  built.
- **External validation**: zero customer or user conversations to
  date. Whether to prioritize validation conversations over the next
  build item is an open decision for the maintainer.
- The legacy `world_engine` demo remains in the repo, frozen as a
  demo; the `world` primitive is the direction.

## Research documentation

`research/RESEARCH_OVERVIEW.md`, `research/HYPOTHESIS.md`,
`research/LIMITATIONS.md`, `research/RELATED_WORK.md`, and the survey
in `research/comparisons.md`.
