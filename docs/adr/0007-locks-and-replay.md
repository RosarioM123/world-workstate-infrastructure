# ADR 0007: Node locks and engine-side replay

Date: 2026-09-23
Status: Accepted (built)

## Context

Two README claims were not backed by code:

1. "Node locks are respected" — `check_constraints()` rejected intents
   against `LOCKED` nodes, but no code path could ever set the flag, so
   the branch was unreachable.
2. "Materialized state is rebuilt deterministically from the ledger" —
   replay existed only in the offline SDK; the engine had `verify_chain()`
   (hash integrity) but no way to prove the live tables matched history.

Separately, the transcript importer wrote each item in its own
transaction: a crash mid-import left partial imports, and the dedup
record was committed separately from its ledger row, so a crash between
the two broke idempotency on retry. Two concurrent importers could also
pass the dedup check simultaneously and double-commit.

## Decision

**Locks are ledger events, not side channels.** `lock_entity()` /
`unlock_entity()` flip the entity's `status` flag and append a
COMMITTED `LOCK_ENTITY` / `UNLOCK_ENTITY` row in the same BEGIN
IMMEDIATE transaction. Consequences:

- Locks are auditable and replayable like every other state change.
- Lock/unlock bypass the constraint engine (a separate code path, not an
  intent): otherwise a locked node could never be unlocked, and lock
  attempts on unknown ids raise `ValueError` instead of polluting the
  ledger with nonsense rows.
- Double-lock / unlock-of-active raises `ValueError` — no-op flips would
  spam the ledger. The API maps these to 404 (unknown entity) and 409
  (already in state).

**Replay is verify-by-default, repair-by-operator.** `replay_ledger()`
re-applies every ledger row from the genesis seed in transaction-ID
order and diffs the rebuilt map against the live `entities` table:

- `apply=False` (default, and what `GET /api/v1/replay` exposes) is
  read-only: it proves "any participant can replay history and arrive
  at the same state" without touching the database.
- `apply=True` rewrites the `entities` table from the replay inside one
  transaction. It is an operator-level engine call only — never an HTTP
  endpoint — and it refuses to run on a broken chain.
- Simulation mirrors the writers exactly: COMMITTED intents apply their
  recorded `target_*` values (no recomputation, so floats are
  bit-identical), REJECTED rows are no-ops, REGISTER/LOCK/UNLOCK rows
  apply their structural change.
- Two bootstrap cases: the seed node has no ledger row (init_db inserts
  it directly), so replay seeds it from the `SEED_*` constants; entities
  created outside the ledger (transcript-knowledge) are materialized
  from each row's recorded pre-image (`previous_capacity`/`previous_cash`,
  which lock rows now also carry).

**Imports are one transaction.** `import_transcript()` opens a single
connection, takes BEGIN IMMEDIATE, and runs every item's transition plus
its dedup record through that connection (`execute_deterministic_transition`
grew an optional `conn` seam for this; when omitted it behaves exactly
as before). A crash or error rolls back to zero imported items, and
concurrent importers serialize on the write lock — the loser sees the
winner's hashes and imports nothing new.

## Consequences

- Good: all three claims are now covered by tests (locks, replay
  verify/repair, import atomicity under failure and concurrency).
- Good: no schema migration — locks and replay use the existing ledger
  and entities tables; the idempotency table is unchanged.
- Bad: replay is O(ledger) on every call; fine for a demo ledger, but a
  production-sized history would want incremental checkpoints.
- Bad: `apply=True` is a blunt instrument — it rewrites the whole table.
  Acceptable for corruption repair, not for routine use.
- Revisit when: the ledger grows past comfortable full-replay time, or a
  second real party needs lock/unlock authorization (see ADR 0006).
