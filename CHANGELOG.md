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
- CLI commands no longer leak tracebacks on ordinary errors (Mission
  Day 9, audit findings C-9 and C-14): `world diff` and `world blame`
  catch `KeyError`/`ValueError` for unknown or rejected versions and
  print `error: ...` with exit 1, as `world state` already did;
  `world import` catches `InvariantViolation`/`ConflictError` from a
  replay row and aborts with a message naming the row and how many
  versions were already imported; `world import-transcript` catches
  `ImportError` when the `world_engine` package is absent and prints a
  clean error naming the missing package with the install command
  (exit 2, mirroring `world serve` without its extra). `world state
  --checkpoint` also catches `InvariantViolation`, so a repointed
  checkpoint reports cleanly instead of tracing. Seven new tests
  cover the unknown-version, rejected-version, repointed-checkpoint,
  import-abort (both exception types), and missing-`world_engine`
  cases; all seven fail on the pre-fix code.
- Dated reports no longer read as current state on the commit
  question (Mission Day 8, audit findings D-3 and D-11): dated
  addenda appended (bodies untouched) to
  `experiments/prompt3/REPORT.md`, `experiments/prompt6/REPORT.md`,
  `experiments/prompt6/RELEASE_READINESS.md`,
  `experiments/experiment-003/REPORT.md`, and
  `research/EVIDENCE_REGISTER.md`, recording that Experiment #003,
  Prompt 3, and Prompt 6 were committed locally 2026-11-11
  (`0dca725`, `8288dd4`, `9ef3591`) and the same content pushed to
  remote main (`44b0ff2`, `db5b477`, `5e38886`). The release-readiness
  blocker stays open: the work is still unreviewed with no release
  approval.
- `world export` now carries wrapped field keys and `world import`
  stores them, so encrypted fields survive an export/import round trip
  (Mission Day 7, audit finding C-6): the export gains a first line
  naming the source world plus one `{"type": "field_key", ...}` line per
  escrowed key, and import re-tags each key with the new seq of the
  first imported version whose state holds its envelope. Wrapped keys
  are useless without the master key, which is never stored in the
  world and must be carried separately. Import warns on stderr when an
  imported envelope has no escrowed key (a pre-fix export, or a field
  redacted in the source) and when the export comes from a differently
  named world (envelopes are bound to the source world name, so they
  will not decrypt in the new name by design). Three new tests cover
  the same-name round trip, the orphan warning on a legacy export, and
  the name-mismatch warning. `World.field_keys()` lists the escrow.
- Transcript import no longer has a lost-update race (Mission Day 6,
  audit finding C-7): `import_transcript` now runs the optimistic
  concurrency loop, reading `(state, version)` with `World.read()` and
  passing `expected_version=version` to `update()`, re-reading and
  retrying (bounded at 10 attempts) on `ConflictError`. Two different
  transcripts imported concurrently both land; previously the second
  writer silently overwrote the first's merged items. Three new tests
  cover the retry after an injected conflict, a two-thread concurrent
  import of different transcripts, and bounded-retry exhaustion.
- Field paths now use one dot notation with numeric parts for list
  indices (`"items.0.secret"`) across encrypt, decrypt, redact, and
  blame (Mission Day 5, audit findings C-8 and C-15): `_get_path`
  descends through lists, `encrypt_fields` swaps envelopes via a new
  `_set_path` helper instead of a dict-only loop, and
  `decrypt_fields` builds list paths as `items.0.secret` instead of
  `items[0].secret`, so the AAD matches encryption and the `field` in
  decrypt errors matches the identifier `redact_field` expects.
  Previously `encrypt_fields` silently skipped list-nested fields and
  a hand-built list-nested envelope failed authentication on decrypt.
  Five new tests cover the list-nested roundtrip, out-of-range and
  non-numeric indices, the dot-form error name, redaction, and blame.
- CI lint tools are now pinned and the lint scope covers the whole repo
  (Mission Day 4, audit findings T-2 and T-3): the lint job installs
  `ruff==0.17.5` and `mypy==2.4.1` instead of floating latest, and
  `ruff check`, `ruff format --check`, and `mypy` now run over `spec/`,
  `tools/`, `demo/`, and the root shims (`app.py`, `engine.py`,
  `import_transcript.py`) in addition to `src/`, `tests/`, `examples/`,
  and `experiments/`. The build dependency is pinned as
  `setuptools==84.2.1` in `pyproject.toml`. The newly covered scope
  needed 46 ruff findings fixed plus formatting, and 4 mypy errors
  fixed. The preserved `experiments/prompt3/bench.py` is excluded from
  mypy because it shares the module name `bench` with `tools/bench.py`
  in one run (same pattern as the existing Experiment #003 exclusion).
- `Scheduler` in `spec/detsim.py` no longer closes over loop variables
  (Mission Day 4, audit finding T-3, B023): the two `wait_for`
  predicates that captured the loop variables `cid` and `nxt` are now a
  `_wait_for` helper taking the client id as a parameter.
- `test_soak_no_latency_drift` is now load-insensitive (Mission Day 3,
  audit finding T-1): latencies are measured with `time.process_time()`
  (per-process CPU time) instead of wall clock, and the drift check is a
  row-count scaling check (per-update cost at a 20k-row chain within 5x
  of the cost at a 2k-row chain) instead of a same-window comparison
  that could not catch linear growth. The old test failed 2 of 3 runs
  under two concurrent suites; the new test passed 3 of 3 under the
  same load, and a scratch simulation of an O(n) append path (a full
  history scan per update) trips the scaling gate at 5.9x.
- Malformed POST bodies on `/v1/update`, `/v1/checkpoint`, and
  `/v1/resume` now return 400 `bad_request` instead of 500 (Mission
  Day 3, audit finding C-3): malformed JSON, a non-object JSON body,
  and mistyped `actor`, `note`, `idempotency_key`, `name`, or
  `expected_version` fields (including a boolean `expected_version`,
  which used to surface as a misleading 409) are validated before
  reaching the core.
- `GET /v1/state?checkpoint=...` now verifies the checkpoint pin (Prompt 3
  F3a) through `World.state(checkpoint=...)` instead of resolving the
  checkpoint to a seq and reading by version, which served repointed
  checkpoints silently over HTTP. A mismatched pin returns 422
  `checkpoint_pin_mismatch`. (Mission Day 2, audit finding C-1.)
- `GET /v1/state` on an empty world returns `{"version": 0, "state": {}}`
  instead of 404. (Mission Day 2, audit finding C-4.)
- `World.redact_field` now shreds encrypted fields in REJECTED rows too:
  it stopped at the latest committed version, so a rejected attempt's
  envelope stayed decryptable while the receipt implied the field was
  shredded everywhere. `World.redact` and `World.redaction_status`
  resolve envelopes through `proposal(seq)` for the same reason.
  (Mission Day 2, audit finding C-2.)
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
