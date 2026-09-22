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

- Tests: 115 green. Coverage: 95.47% across `world_engine` + `world_sdk`
  (gate 85%). `ruff check`, `ruff format --check`, `mypy` clean in CI
  (Python 3.11-3.13).
