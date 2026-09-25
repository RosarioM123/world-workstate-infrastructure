# Changelog

All notable changes to WORLD are documented here, in
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.
Versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
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

### Changed
- Python dependencies are now declared only in `pyproject.toml`
  (`requirements.txt` removed); install with `pip install -e ".[test]"`.
- CI test matrix is now Python 3.11, 3.12, and 3.13.

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
