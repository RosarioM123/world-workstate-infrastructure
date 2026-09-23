# ADR 0008: The `world` primitive — versioned documents with judged transitions

Date: 2026-09-23
Status: Accepted (built)

## Context

The audit (AUDIT.md) concluded the repo's solid core is the deterministic
ledger kernel — hash chain, verdicts, atomicity, idempotency — while the
supply-chain entity model, narrative docs, and SDK duplication are
aspirational or dead weight. The v0.1 design sketch then over-corrected:
it kept the log but dropped *judgment* ("records everything, judges
nothing"), which was the old engine's actual differentiator.

## Decision

**A `World` is a named, durable, versioned JSON document.** One name is one
project (`~/.world/<name>.db`, overridable). The API is nine methods
(`update`, `state`, `checkpoint`, `checkpoints`, `resume`, `history`,
`verify`, `version`, plus the constructor). Handles are stateless — every
read hits SQLite, so no staleness, no refresh API.

**Every state change is judged; rejections are evidence.** `World` accepts
optional invariant callables `(old, new) -> None`. `update()` (and
`resume()`, which is a state change) runs them; a violation appends a
REJECTED row carrying the *attempted* document and raises
`InvariantViolation` with the row's seq. `state()`/`version` resolve to the
latest COMMITTED row. Shipped helpers (`no_negative`, `finite_numbers`,
`require_keys`, `respect_locks`) are plain functions — no rule DSL, no
engine branch. Locks are a document convention (`_locks` list), not a
status flag; lock/unlock are ordinary versioned updates.

**Uniform enforcement lives in the server.** In-process callables cannot
bind other processes, so `world serve` (new document-model routes,
API-key gate and per-IP rate limiting carried over) is where invariants
are declared once for all remote writers. This matches how the old
architecture actually behaved, now stated instead of implied.

**Producers, not core, ingest the outside world.** The transcript importer
is a thin producer: deterministic parse, merge into `state["transcript"]`,
one `update()` with a content-hash idempotency key — the old dedup table
dissolves into the idempotency key.

## Consequences

- Good: the old engine's real strengths (verdicts, rejection-as-evidence,
  atomicity, idempotency, auth, rate limits) survive in generalized form;
  the hardcoded capacity/liquidity domain, numeric routes,
  `/rogue-attack`, the duplicated SDK ledger, and replay/repair (nothing
  to diverge from the log anymore) are gone.
- Good: 37 new tests, 88%+ coverage on the package; full suite (235)
  green, ruff + mypy clean. The old `world_engine` package is untouched.
- Bad: invariants are code, not data — "which rules judged version N?"
  is answered by convention (the reason string names the rule), not schema.
- Bad: two packages ship in one repo for now (`world_engine` legacy,
  `world` primitive). Deliberate: no silent retrofit of a live branch.
- Revisit when: a real second deployment needs cross-process invariant
  agreement (persist rule specs), or the legacy engine is retired.
