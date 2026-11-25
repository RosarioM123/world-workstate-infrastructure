# WORLD Architecture Map

**Date:** 2026-11-25 (Mission Day 14, Prompt 1). **Version:** 0.1.0.
**Scope:** the repo as it exists on `mission/day-14`. Complements
`docs/architecture.md` (the component diagram) and `docs/architecture.mmd`
(the editable diagram source); this map covers the whole repo, including the
legacy package, the surfaces, and the deployment wiring that
`docs/architecture.md` explicitly excludes.

## 1. The two systems in one repo

The repo contains two systems with different status. This split is the single
most important fact about the codebase.

| System | Location | Status | Deploys? |
|---|---|---|---|
| The primitive (the product direction) | `src/world/` | Shipped, tested, actively hardened (Days 1 to 13) | No. `world serve` is local only. |
| The legacy engine (the demo) | `src/world_engine/`, `src/world_sdk/` | Frozen prototype per `docs/architecture.md:7`, but still the only runnable service | Yes. `render.yaml:7` runs `uvicorn app:app` (legacy). |

Nothing deploys the primitive. The legacy service is the one with the live
auth, rate-limit, and deploy gaps (L-1, L-2, L-3, L-7). Any architecture
decision that assumes one system must name which one; see
`REPOSITORY_AUDIT.md` item 10.1 and `TECHNICAL_DEBT.md` L-1/L-2/L-3.

## 2. The primitive (`src/world/`)

One named world is one SQLite file. Stateless handles; an opaque JSON
document; every proposed update is judged by declared invariants and appended
to a SHA-256 hash chain as COMMITTED or REJECTED. Optimistic concurrency with
`expected_version`; idempotent retries; checkpoints; committed-only time
travel via full snapshots.

| Module | File | Role |
|---|---|---|
| Package surface | `src/world/__init__.py` | Exports `World`, `AgentState`, `Decision`, `Evidence`, `load_state`, `save_state`, `ed25519`, `fieldcrypto`, `__version__ = "0.1.0"`. Does NOT export `Assumption`, `project_state`, `revision_chain`, `validate_state` (D-8). |
| Core protocol | `src/world/core.py` | `World`: update, `update_many`, `read`, checkpoints, resume, `verify`, `blame`, `state(version=...)` / `state(checkpoint=...)`. Judging runs inside `BEGIN IMMEDIATE` (C-5 fix). `resume` accepts `expected_version` and `idempotency_key` (C-10: the HTTP route does not forward them). |
| Invariants | `src/world/invariants.py` | `monotonic`, `immutable_fields`, `type_stable`, composition with `all_of`. |
| Handoff API | `src/world/handoff.py` | Typed `AgentState` (`Assumption`, `Decision` with `id`/`status`/`supersedes`/`evidence_ids`, `Evidence`); `save_state`, `load_state`, `validate_state`, `project_state`, `revision_chain`. Referential-integrity validation in `save_state` (Prompt 3 F1). |
| HTTP server | `src/world/server.py` | FastAPI app, `world serve`. Writes gated by API key, fails closed by default. Reports version "0.2.0" (D-7) against package 0.1.0. `GET /v1/state` verifies the checkpoint pin (C-1 fix) and serves the empty document (C-4 fix). POST bodies validated to 400, not 500 (C-3 fix). |
| CLI | `src/world/cli.py` | `world` entry point: `init`, `update`, `update-many`, `state`, `diff`, `blame`, `import`, `export`, `serve`. Ordinary errors print clean messages, no tracebacks (C-9/C-14 fix). `update-many` has no `--idempotency-key` flag (C-11). |
| Signing | `src/world/ed25519.py` | Ed25519 signed checkpoints, key rotation ceremony. |
| Field crypto | `src/world/fieldcrypto.py` | Per-field encryption with crypto-shredding redaction; redaction covers REJECTED rows too (C-2 fix); one dot path notation for list-nested fields (C-8/C-15 fix). |
| Transcript producer | `src/world/producers/transcript.py` | Imports transcripts as intents with `expected_version` retry (C-7 fix). |
| Merkle proofs | (in `core.py`) | Merkle root and inclusion proofs, verifiable without the database. |

### Storage schema (one SQLite file per world)

| Table | Columns (essence) |
|---|---|
| `versions` | `seq`, `timestamp`, `actor`, `note`, `state`, `status` (COMMITTED/REJECTED), `prev_hash`, `hash` |
| `checkpoints` | `name`, `seq`, `pinned_hash` (verified on read and resume, Prompt 3 F3a) |
| `idempotency` | `key`, `seq` (sits outside the chain; binding it into the row hash is the open F3b decision, L-6) |
| `field_keys` | wrapped per-field data keys (master key never stored) |

### Request flows

- **Python API:** caller holds a `World` handle, declares invariants once,
  calls `update(state, expected_version=..., idempotency_key=...)`. The core
  judges, revalidates `expected_version` inside `BEGIN IMMEDIATE`, appends the
  verdict to the hash chain, and returns the seq. A retried idempotency key
  returns the original seq.
- **Handoff:** Agent A calls `save_state` (validates referential integrity,
  records decisions with rationale and evidence links). Agent B, in a new
  process with no conversation history, calls `load_state`, then
  `revision_chain` for a decision's history and `project_state` for the
  current projection.
- **CLI:** thin wrapper over the Python API; `world serve` starts the HTTP
  server; `world export` / `world import` move JSONL (field keys travel with
  the export since C-6).
- **HTTP:** one `World` handle per app; writes require the API key unless
  `--allow-unauthenticated` is passed (explicit local-development opt-in,
  Prompt 3 F2).

## 3. The legacy engine (`src/world_engine/`, `src/world_sdk/`)

| Module | File | Role |
|---|---|---|
| Core engine | `src/world_engine/core/engine.py` | Deterministic intent execution, hash-chained ledger, `replay_ledger` (honors `LOCK_ENTITY`/`UNLOCK_ENTITY`), orphan idempotency-key repair. |
| API | `src/world_engine/api/main.py` | FastAPI app (`app.py` shim re-exports it). Warns, but does not fail, when `WORLD_API_KEY` is unset (L-2). |
| API v1 | `src/world_engine/api/v1.py` | Versioned routes under `/api/v1/*`; deprecated `/api/*` aliases promised for removal in v0.3.0. `GET /api/v1/state` returns every entity, no pagination (L-7). |
| Auth | `src/world_engine/api/auth.py` | `require_api_key` silently returns when the key is unset (L-2). |
| Middleware | `src/world_engine/api/middleware.py` | Per-IP rate limits on POST writes only (120/60/5 per min); GETs unrated (L-7); trusts the first `X-Forwarded-For` entry (L-11). |
| Ingestion | `src/world_engine/ingestion/transcript.py` | Transcript import (`world-import` console script). |
| SDK | `src/world_sdk/ledger.py` | `LocalLedger.intent` re-implements the engine intent path (~120 lines, drifted by one branch, L-8); `replay_to` drops node locks and ledger-external entities (L-5). |
| SDK client/index | `src/world_sdk/client.py`, `src/world_sdk/index.py` | Client and index over the ledger. |

## 4. Surfaces and entry points

| Surface | Entry point | Backend |
|---|---|---|
| Python API (primitive) | `from world import World` | `src/world/core.py` |
| Handoff API | `from world.handoff import ...` | `src/world/handoff.py` |
| CLI | `world` console script (`world.cli:main`) | `src/world/cli.py` |
| HTTP (primitive) | `world serve` | `src/world/server.py` |
| HTTP (legacy) | `world-server` console script; `uvicorn app:app` | `src/world_engine/api/main.py` via `app.py` |
| Transcript import | `world-import` console script | `src/world_engine/ingestion/transcript.py` |
| Root shims | `app.py`, `engine.py`, `import_transcript.py` | Re-export the packages. The documented `ingest.py` shim does not exist (L-9). |
| Dashboard (legacy UI) | `static/dashboard.html` | Calls deprecated `/api/*` (L-4/L-14). |
| Landing page (React) | `frontend/src/`, built to `static/site/` | Calls `/api/v1/*`. Current with `frontend/src/` (both last touched by `e66ee58`, 2026-09-22). |

## 5. Tests, spec, and verification

| Area | Location | Notes |
|---|---|---|
| Test suite | `tests/` (51 files, 453 test functions, 500 tests) | Primitive, legacy, SDK, API, security, concurrency, crash consistency, soak, property tests. Coverage 95.16% over the expanded scope (package plus `tools/`, `demo/`, root shims). |
| Model checker | `spec/model_check.py` | 1,220,255 states, properties P1 to P6 hold; mutation test catches an injected P4 violation. |
| TLA+ spec | `spec/world.tla` | Never executed through TLC (T-11). |
| Determinism / linearizability | `spec/detsim.py`, `spec/linearizability.py` | Supporting harnesses. |
| Independent verifier | C# verifier (`tests/test_csharp_verifier.py`) | Reproduces chain verification with no shared code; CI fails unless its 4 tests run (T-6 fix). |
| CI | `.github/workflows/ci.yml` | pytest on Python 3.11, 3.12, 3.13; ruff and mypy pinned (T-2 fix) in a separate lint job; coverage gate 85%; `csharp-verifier` job. |

## 6. Tools, demo, examples

| Area | Location | Notes |
|---|---|---|
| Tools | `tools/` | `export_ledger.py` (refuses to create a ledger, fails clearly when missing, L-12 fix), `bench.py`, `bench_world.py`, `bench_contention.py`, `guardrail_audit.py`, `staleness.py`, `write_cost.py`. All covered by smoke tests since T-9. |
| Demo | `demo/` | Two-process agent A then B handoff; `demo/common.py:22` holds `DEMO_TIP_KEY` in source (L-13). Spend-cap invariant tested. |
| Examples | `examples/` | `quickstart.py`, `fleet_mission/`, `synthetic-logistics-demo/`. |
| Experiments | `experiments/` | Prompt 3 bench, #001/#002/#003 handoff experiments, prompt6 validation and release-readiness docs, `mission-90/` (Day 1 audit and daily log). |
| Research | `research/` | `PAPER.md` manuscript draft, `EVIDENCE_REGISTER.md`, `RESEARCH_OVERVIEW.md`. |
| Docs | `docs/` | `architecture.md`, `state-model.md`, `SECURITY.md`, `SDK.md`, `VISION.md`, `demo-script.md`, `adr/` (decision records), `spec/`, `benchmarks/`. |

## 7. Deployment wiring (as written)

`render.yaml` builds with `pip install -e .` and starts `uvicorn app:app`
with a 1 GB persistent disk at `/var/data` and `WORLD_DB_PATH` pointing at it.
As written it cannot start (L-1: fastapi/uvicorn are only in the `[server]`
extra) and, if fixed to start, would serve unauthenticated writes when
`WORLD_API_KEY` is left unset (L-2: the key is declared with `sync: false`
and no value). No deployment targets the primitive. Fixing either line is a
deployment change and needs Rosario's approval.

## 8. What the map deliberately leaves out

- `build/` is a tracked build artifact holding a stale copy of
  `src/world/server.py` (F-2); it is not part of the architecture and should
  be untracked.
- `__pycache__` directories and `.egg-info` are build noise, not components.
