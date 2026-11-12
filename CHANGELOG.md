# Changelog

All notable changes to WORLD are documented here, in
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.
Versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Experiment #003 (2026-11-03, preregistered): 8 tasks, 3 conditions,
  72 continuations, blind graded. Assumption retention was the one
  consistent structured-state advantage (A 0.721 vs B 0.500 vs
  C 0.488); revision history tied at ceiling; unverifiable additions
  only under A (12). PRELIMINARY. Full record:
  `experiments/experiment-003/REPORT.md`.
- Prompt 6 release-preparation artifacts (2026-11-05):
  `REPRODUCE.md` (verified reproduction workflow and clean-install
  test), `research/PAPER.md` (unpublished manuscript draft),
  `research/EVIDENCE_REGISTER.md`, `docs/architecture.md` and
  `docs/architecture.mmd`, `demo/` (two-process demonstration), and
  the audit, release-readiness, and validation-protocol documents
  in `experiments/prompt6/`. Nothing in this entry is a release.
- Versioned API under `/api/v1` with deprecated `/api/*` aliases,
  uniform JSON error envelope, and request-ID plus structured logging
  middleware.
- Claim-proving tests: concurrent-write serialization (16 racing
  threads), hash-chain property tests (hypothesis), FastAPI TestClient
  integration tests.
- Coverage gate: pytest-cov enforced at 85% in CI.
- Architecture decision records in `docs/adr/`.
- `docs/SECURITY.md` threat model for the hash-chained ledger.
- `tools/bench.py` ledger benchmarks with published numbers.
- `docs/demo-script.md`: the 2-minute demo script.
- `docs/VISION.md`: the one-page thesis.
- `CONTRIBUTING.md`, issue and pull request templates, Dependabot.
- Multi-entity support for the ledger service: entity registration
  and a paginated ledger query API.
- Multi-agent intent schema: `actor`, `kind`, and `idempotency_key`
  fields on intents.
- The `src/world` primitive: a named, durable JSON document whose
  proposed updates are judged by declared invariants and recorded,
  COMMITTED or REJECTED, in a SHA-256 hash-chained SQLite log, with
  `expected_version` optimistic concurrency.
- Agent handoff interface: typed `AgentState` with `save_state` and
  `load_state`.
- Fleet mission example (`examples/`): WORLD as the shared mission
  layer across processes.
- Invariant helpers `monotonic`, `immutable_fields`, and
  `type_stable`, plus invariant composition with `all_of` and
  documented composition semantics (`docs/spec/`).
- `world diff`, `world export`, and `world import` CLI commands.
- `World.read()` for one-round-trip optimistic concurrency, and
  `World.update_many` batch updates in a single transaction.
- `World.blame`: per-field provenance for the current document.
- HMAC-signed chain tips, Ed25519 signed checkpoints, and a key
  rotation ceremony for tip signing.
- Merkle inclusion proofs for selective disclosure of individual
  versions. A ZK audit spike was evaluated and not adopted.
- Per-field encryption with cryptographic redaction: crypto-shredding
  a field keeps `verify()` green.
- Mechanized verification of the commit protocol: explicit-state
  model checker (`spec/model_check.py`, 1,220,255 explored states,
  properties P1 to P6), a TLA+ transcription, and the writeup in
  `docs/spec/protocol-verification.md`.
- Red-team test suite (database-write attacker vs `verify()`),
  Hypothesis stateful testing against a reference model, `verify()`
  mutation fuzzing, a linearizability checker for `World.update`,
  deterministic simulation testing, and a crash-consistency
  fault-injection harness (`experiments/crash-consistency/`).
- Preregistered lost-update experiment (`experiments/lost-update/`):
  scripted agents lost 33 of 50 updates with no control and 0 of 50
  with `expected_version` plus retry.
- Soak test at 1.06M chained rows (`experiments/soak/`).
- Independent C# chain verifier for the primitive
  (`tools/ChainVerifyWorld/`), sharing no code with the Python
  implementation.
- Primitive benchmarks (`tools/bench_world.py`,
  `tools/bench_contention.py`) with dated records in
  `docs/benchmarks/`.
- Research documentation: rewritten README research framing,
  `research/RESEARCH_OVERVIEW.md`, `research/HYPOTHESIS.md`,
  `research/LIMITATIONS.md`, `research/RELATED_WORK.md`, and a
  refreshed `STATUS.md`.
- Prompt 3 (2026-11-04): handoff schema brought up to the research
  state model. `AgentState` gains an `assumptions` section;
  `Decision` gains `id`, `status`, `supersedes`, and `evidence_ids`;
  `Evidence` gains `id` and `kind`; a new `Assumption` type carries
  `confidence`, `status`, and `validated_by`. `save_state` validates
  the revision graph's referential integrity before proposing.
  All additive: pre-F1 stored handoffs load with defaults.
- Prompt 3 (2026-11-04): `world.handoff.revision_chain(world,
  decision_id)` derives one decision's revision history (original,
  changes, actor, reason, evidence links, current status) from the
  committed snapshots.
- Prompt 3 (2026-11-04): `world.handoff.project_state(state)` builds
  a continuation-ready projection: live decisions and assumptions in
  full, superseded/reversed/invalidated items as compact
  status-marked entries, evidence filtered to referenced items.
- Prompt 3 (2026-11-04): checkpoints record the pinned row's hash;
  `state(checkpoint=...)` and `resume()` verify it before serving
  and refuse repointed checkpoints (`InvariantViolation`). Existing
  databases gain the column additively; pre-F3a checkpoints carry no
  pin and are served unverified.
- Prompt 3 (2026-11-04): the HTTP server accepts a fixed `actor`
  configuration that overrides body-supplied actor labels on writes.

### Changed
- Python dependencies are now declared only in `pyproject.toml`
  (`requirements.txt` removed); install with `pip install -e ".[test]"`.
- CI test matrix is now Python 3.11, 3.12, and 3.13.
- License switched to MIT.
- `docs/SECURITY.md` expanded with a tested threat model for the
  `src/world` primitive, and updated again when signed checkpoints
  closed its top two stated limits.
- Prompt 3 (2026-11-04): the HTTP server fails closed. With no API
  key configured, write routes return 401 unless unauthenticated
  writes were explicitly allowed (`allow_unauthenticated_writes` /
  `world serve --allow-unauthenticated`). The previous fail-open
  default (startup warning, then open writes) is removed.
- Prompt 3 (2026-11-04): `World.verify()` and `World.blame()` stream
  rows instead of materializing the chain; verification memory no
  longer grows with chain length.

### Fixed
- `World.update` re-validates `expected_version` inside the write
  transaction, closing a lost-update race where two writers that both
  passed the pre-lock check could overwrite each other. Without
  `expected_version` the write remains last-writer-wins (now documented).
- The HTTP rate limiter no longer trusts `X-Forwarded-For` by default:
  the header is client-controlled, so any client could spoof a fresh IP
  per request and bypass the limit. Opt in with
  `trust_forwarded_for=True` only behind a trusted reverse proxy, and the
  per-IP hit table is now bounded by periodic eviction of stale entries.
- `World.state(version=N)` is now committed-only: a REJECTED proposal's
  seq raises `KeyError` instead of returning the rejected document as if
  it were history. Rejected attempts stay auditable through the new
  `World.proposal(seq)`, also exposed as `GET /v1/proposals/{seq}` and the
  `world proposal` CLI command.
- `fleet_mission` example: `execute_mission` now uses its
  `mission_name` parameter.
- Crash-consistency harness: the SIGKILL now waits for the worker's
  first committed update instead of racing worker startup. The old
  timing made the test fail deterministically on a real disk with no
  durability violation; investigation and evidence in
  `experiments/crash-consistency/FINDINGS-2026-11-02.md`.

## [0.1.0] - 2026-09-21

### Added
- Deterministic append-only state ledger: intents validated by a
  constraint engine (COMMITTED/REJECTED), every attempt hash-chained
  (SHA-256) into a tamper-evident SQLite ledger.
- `verify_chain()`: full chain verification naming the first broken
  record.
- Transcript importer: deterministic stdlib-only parsing of chat
  transcripts into ledger intents (decisions, assumptions, questions,
  constraints, notes), idempotent re-imports.
- FastAPI backend with live dashboard, live Open-Meteo ingestion, and
  rogue-attack simulation.
- `src/` packaging (`world_engine`) with root compatibility shims.
- Independent C# chain verifier (`tools/ChainVerify`).
- 45-test suite, CI on Python 3.12/3.13, ruff + mypy enforcement.
