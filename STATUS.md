# WORLD status

Single-pointer dashboard. Updated 2026-09-22.

## Experiments

- **Experiment #001** (memory-format bake-off): complete. Results in
  `docs/experiment-001-results.md`. Headline: governance/decisions survive
  better in structured state; facts survive in every format. Limitations
  disclosed in the writeup (n=1, same-author bias).
- **Experiment #002** (7-day autonomous Disney replication): in progress.
  Daily files live in `docs/experiment-002/`; Day 7 closeout (results
  writeup, dev-log update, commit) runs 2026-09-23 via the scheduled job.
  Do not touch `docs/experiment-002/` or `docs/development-log.md` until
  then.

## Buildout

- **Work Item 1, SDK-local index**: done 2026-09-22
  (`src/world_sdk/`, `docs/SDK.md`). `WorldClient.intent()` with local
  stdlib-only validation, client-owned SQLite sidecar for embeddings and
  the timestamp index. Server untouched, stdlib-pure.
- **Next**: server sidecar + time-travel/search endpoints, then OBSERVE
  intent (schema still open, see README Honest limits).

## Open decisions

- OBSERVE schema (freeform vs structured fields).
- Time-travel canonical key (block height vs timestamp).

## Health

- Tests: 172 green. Coverage: 94.97% across `world_engine` + `world_sdk`
  (gate 85%). `ruff check`, `ruff format --check`, `mypy` clean in CI
  (Python 3.11-3.13), now also covering `examples/` and `experiments/`.
- Multi-agent schema seam (actor, kind, idempotency_key) shipped with
  commit-time dedup; empty keys rejected; dedup mappings rebuilt on
  ledger import; PEP 561 `py.typed` markers so downstream mypy works.
- Multi-entity support: `POST /api/v1/entities` registration (409 on
  duplicate), `GET /api/v1/ledger` with entity/limit/cursor pagination,
  rogue-attack targetable at any node; SDK parity plus hypothesis
  property tests asserting both backends agree on verdicts, state, and
  chain validity.
  See docs/adr/0005-multi-agent-conflict-policy.md and
  docs/adr/0006-auth-rbac-shape.md.
