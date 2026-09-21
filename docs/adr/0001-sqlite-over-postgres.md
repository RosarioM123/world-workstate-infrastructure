# ADR 0001: SQLite over Postgres for v0

Date: 2026-09-17
Status: Accepted

## Context

WORLD v0 needs a durable store for the append-only ledger and the
materialized entity state. Candidates were SQLite (embedded file) and
Postgres (server, free tier). The prototype must run with zero setup:
`pip install -e .` and a quickstart that works in 30 seconds, in
Codespaces, and in CI, with no credentials or hosted services.

## Decision

Use SQLite for v0. One file (`world_state.db`), WAL mode for
concurrent readers, `busy_timeout` for transient writer contention.
`WORLD_DB_PATH` overrides the location so tests and demos isolate state.

## Consequences

- Good: zero-dependency deploy story (stdlib `sqlite3` only in the
  kernel), trivial backups (copy the file), deterministic local demos.
- Good: the entire test suite runs against throwaway files with no
  service fixtures.
- Bad: no real multi-process write scaling beyond what a single file
  lock allows; no built-in replication or access control beyond file
  permissions.
- Bad: tamper-evidence rests on application convention, not
  database-enforced immutability (see `docs/SECURITY.md`).
- Revisit when: a deployment needs concurrent writers across machines,
  or row-level access control. The engine's storage calls are funneled
  through `connect_db()`, so a Postgres port is a contained change.
