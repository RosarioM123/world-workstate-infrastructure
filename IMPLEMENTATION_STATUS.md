# WORLD Implementation Status

**Date:** 2026-11-25 (Mission Day 14, Prompt 1). **Version:** 0.1.0.
**Purpose:** for each feature area, what is implemented, what is documented
but not implemented, and what is designed but not built. Evidence classes:
VERIFIED (traced code path or live run), DOCUMENTED (docs and code agree),
PRELIMINARY (small-n experiment), NEEDS VALIDATION (needs a test or external
check). No em dashes.

## 1. Core primitive (`src/world/`): IMPLEMENTED

| Capability | Evidence | Notes |
|---|---|---|
| Named world as one SQLite file; opaque JSON document | VERIFIED | `src/world/core.py` |
| Invariant judging on every proposal (COMMITTED/REJECTED verdicts) | VERIFIED | `src/world/invariants.py`; judgment runs inside `BEGIN IMMEDIATE` since C-5 |
| SHA-256 hash chain over all verdicts | VERIFIED | `src/world/core.py`; `verify()` streams (Prompt 3 F5) |
| Optimistic concurrency (`expected_version`, exactly one winner) | VERIFIED | Lost-update experiment: 0/50 lost with `expected_version` + retry vs 33/50 unprotected |
| Idempotent retries | VERIFIED | Committed retry returns the original seq. Keys live outside the chain (F3b open, L-6) |
| Checkpoints with pinned hash, verified on read and resume | VERIFIED | Prompt 3 F3a; server path fixed Day 2 (C-1) |
| Committed-only time travel via full snapshots | VERIFIED | `state(version=...)` |
| `blame` (per-field provenance) | VERIFIED | Streaming since Prompt 3 F5 |
| `update_many` batches in a single transaction | VERIFIED | Per-state `idempotency_keys` supported at the core; CLI flag missing (C-11) |
| Atomic `read()` | VERIFIED | `World.read()` |
| Resume from a checkpoint as a new version | VERIFIED | `World.resume` accepts `expected_version` and `idempotency_key`; the HTTP route drops both (C-10) |
| Crash recovery | VERIFIED | 15/15 recorded mid-transaction kills recovered; 39 further rounds (2026-11-02) with zero durability violations |
| Deterministic replay | VERIFIED | Model checker: 1,220,255 states, P1 to P6 hold |
| Concurrent-write serialization | VERIFIED | 16 racing threads test; busy-timeout/retry added Day 10 (C-12) |

## 2. Handoff and structured state (`src/world/handoff.py`): IMPLEMENTED

| Capability | Evidence | Notes |
|---|---|---|
| Typed `AgentState` (decisions, assumptions, evidence, tasks) | VERIFIED | F1 schema upgrade: `Assumption`, decision `id`/`status`/`supersedes`/`evidence_ids` |
| Referential-integrity validation in `save_state` | VERIFIED | Prompt 3 F1 |
| `revision_chain` view | VERIFIED | Follows `supersedes` links |
| `project_state` projection view | VERIFIED | Prompt 3 F6 |
| Decision-to-evidence traceability | VERIFIED | Via `evidence_ids` and `revision_chain` |
| Cross-process handoff (Agent A then B, no shared memory) | VERIFIED | `demo/agent_a.py` then `demo/agent_b.py`, exit 0, `verify(): True`; also `examples/fleet_mission/` |
| Cross-model handoff | PRELIMINARY | Experiments #001/#002/#003 used hand-authored state or the handoff schema, not the shipped `World` class end to end across two genuinely different models. Prompt 4 of the sequence covers this properly. |

## 3. Integrity and confidentiality layers: IMPLEMENTED

| Capability | Evidence | Notes |
|---|---|---|
| Streaming `verify()` and `blame()` | VERIFIED | Peak-RSS delta on a 20,000-version chain 19.7 MB to 0.8 MB (repeat 1.2 MB; see D-10 on the figure spread) |
| HMAC-signed chain tips | VERIFIED | Rollback/rewrite detection |
| Ed25519 signed checkpoints with key rotation | VERIFIED | Rotation ceremony tested (T-5 negative paths) |
| Merkle inclusion proofs | VERIFIED | Verifiable without the database |
| Per-field encryption with crypto-shredding redaction | VERIFIED | Redaction keeps `verify()` green; covers REJECTED rows since C-2; one dot path notation for list-nested fields since C-8/C-15; import carries field keys since C-6 |
| Transcript producer | VERIFIED | `src/world/producers/transcript.py`; lost-update retry since C-7; clean errors since C-14 |

## 4. Surfaces: IMPLEMENTED with gaps

| Surface | Status | Notes |
|---|---|---|
| Python API | IMPLEMENTED | `World`, handoff functions |
| CLI (`world`) | IMPLEMENTED with gaps | `init`, `update`, `update-many`, `state`, `diff`, `blame`, `import`, `export`, `serve`; clean errors since C-9/C-14; `update-many` lacks idempotency keys (C-11) |
| HTTP API (primitive, `world serve`) | IMPLEMENTED with gaps | Writes fail closed by default; `--allow-unauthenticated` is the explicit opt-in; pin verified on reads (C-1); empty world served (C-4); 400s not 500s (C-3); version string wrong (D-7); resume drops keys (C-10) |
| HTTP API (legacy, `world-server`) | IMPLEMENTED with gaps | Versioned `/api/v1/*` plus deprecated `/api/*` aliases; unauthenticated-by-default writes (L-2); GETs unrated and unpaginated (L-7); XFF trust (L-11) |
| SDK (`src/world_sdk/`) | IMPLEMENTED with drift | Re-implements the engine intent path (L-8); replay drops locks (L-5) |
| Dashboard (`static/dashboard.html`) | IMPLEMENTED, stale API | Uses deprecated `/api/*` (L-4/L-14) |
| Landing page (`frontend/`, `static/site/`) | IMPLEMENTED | Uses `/api/v1/*`; build current |

## 5. Documented but NOT implemented

| Claim or design | Where documented | Status |
|---|---|---|
| Persisted invariant registry (database names the rule set that judged a historical version) | STATUS.md open items; MISSION.md priority A | Designed, not built. Invariants are code, not data. |
| Per-actor identity and RBAC | STATUS.md open items; `docs/adr/0006-auth-rbac-shape.md` | Designed, not built. `actor` is self-asserted; the primitive has no auth beyond the API-key gate on HTTP writes. |
| F3b: idempotency keys bound into the row hash | STATUS.md open items; L-6 | Undecided. The idempotency table sits outside the chain. |
| Removal of the deprecated `/api/*` aliases in v0.3.0 | `src/world_engine/api/main.py:16,21-24` | Promised, not done; blocked by L-4 (the dashboard still uses them). |
| `spec/world.tla` as a checked artifact | `spec/world.tla` exists | Never executed through TLC (T-11). The Python model checker is the checked artifact. |
| Release v0.2.0 | `experiments/prompt6/RELEASE_READINESS.md` | Blocked: Prompt 3 and #003 unreviewed; no release approval. |

## 6. Designed but not built (roadmap, not gaps)

| Item | Where designed | Notes |
|---|---|---|
| Streaming verification for large histories | MISSION.md priority A | Partially built: `verify()` and `blame()` stream (F5). Full streaming verification at soak scale not re-run since F5 landed. |
| Versioned schemas with migrations | MISSION.md priorities B/D | Schema is versioned in the handoff layer (F1); no migration framework exists. |
| Provider adapters / agent-framework integrations | MISSION.md priority D | Not built. Deliberate: build only where developer demand is plausible; no superficial integration sprawl. |
| Multi-tenant isolation, encryption at rest, key rotation for the service | MISSION.md priority E | Not built. The primitive is a single-file library, not a hosted multi-tenant service. |
| Export/import portable formats beyond JSONL | MISSION.md priority D | JSONL export/import exists; no other portable format. |
| Legacy `world_engine` retire-or-merge | STATUS.md open items | Roadmap item; needs the L-3 decision first. |

## 7. Evidence status (what backs the claims above)

| Evidence | Status |
|---|---|
| Full suite: 500 passed, 0 failed, 1 warning, 102.69 s, coverage 95.16% (2026-11-25, this run) | VERIFIED |
| Model checker: 1,220,255 states, P1 to P6 hold; mutation test catches injected P4 violation | VERIFIED (Day 1 measurement) |
| Lost-update: 33/50 lost unprotected vs 0/50 with `expected_version` + retry | DOCUMENTED (scripted agents) |
| Crash consistency: 15/15 kills recovered; 39 further rounds, zero violations | DOCUMENTED |
| Soak: 1.06M rows, integrity held; `verify()` 75,921 rows/s, 659 MB RSS (2026-10-15 run) | DOCUMENTED, pre-F5; not re-run at scale since streaming `verify()` |
| Experiment #001: WORLD won on governance, 5/5 decisions, 7/7 assumptions, zero errors | PRELIMINARY, n=1 |
| Experiment #002: WORLD preserved decision governance best in both runs; failed revision history in both runs (2/5) | PRELIMINARY, n=1 per run |
| Experiment #003: assumption retention the one consistent advantage (A 0.721 vs B 0.500 vs C 0.488); revision history tied at ceiling; unverifiable additions only under A (12) | PRELIMINARY, single model family, hand-authored Markdown condition; the `World` class was never exercised |
| Prompt 3 revalidation: first runs through the shipped code path (R1, R2, C1, n=3 per cell) | PRELIMINARY |
| External validation | PENDING: zero external reviewers have completed the protocol (`experiments/prompt6/VALIDATION_PROTOCOL.md`) |
| Deployment | NOT DEPLOYED: no production instance; `render.yaml` cannot start as written (L-1) |
| Production readiness | NOT CLAIMED: no release approval; see `experiments/prompt6/RELEASE_READINESS.md` |

## 8. What changed since the Day 1 audit (Days 2 to 13)

33 of the 56 Day 1 findings were closed in the mission log; the full
reconciliation is in `REPOSITORY_AUDIT.md`. The implementation-relevant
changes: checkpoint pin verification on the HTTP read path (C-1), redaction
coverage for REJECTED rows (C-2), 400s for malformed POST bodies (C-3),
empty-world serving (C-4), README atomicity wording (C-5), field-key
carrying export/import (C-6), transcript-import conflict retry (C-7),
list-nested encryption path notation (C-8/C-15), clean CLI errors (C-9/C-14),
SQLite lock retry and the documented `update_encrypted` crash window
(C-12/C-13), load-insensitive soak gate (T-1), pinned lint tools and extended
lint scope (T-2/T-3), CLI and core negative-path coverage (T-4/T-5/T-12),
extras-import guard and Hypothesis deadlines (T-7/T-8), coverage scope for
`tools/`/`demo`/root shims (T-9), C# verifier CI job (T-6), read-only export
(L-12). Nothing in this list changed the shipped protocol or the storage
schema; all were fixes or test coverage inside the existing architecture.
