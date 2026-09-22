# ADR 0005: Multi-agent conflict policy

Date: 2026-09-22
Status: Accepted

## Context

WORLD serializes all writes through a single SQLite writer: check-then-act
runs inside one `BEGIN IMMEDIATE` transaction (ADR 0003), so two agents
proposing intents against the same entity cannot both pass the constraint
checks against the same stale state. The second writer's intent is
evaluated against the state the first writer left behind, and if it no
longer satisfies the constraints it is REJECTED but still logged, per the
"every attempt is on the ledger" invariant.

That is correct for a single agent retrying its own work. It is an open
question for MIND, where several agents may propose intents on the same
entity concurrently with genuinely different goals. "First one wins, the
second is rejected and logged" is a conflict-resolution policy only by
accident: it conflates a constraint violation (the state cannot support
this intent) with a coordination failure (two agents wanted the same
resource). A human operator looking at a REJECTED row cannot tell which
one happened, and a silently rejected agent may keep retrying a plan that
was never viable.

## Decision

Keep single-writer serialization and REJECTED-but-logged exactly as they
are. Do not build conflict resolution, intent merging, priority queues,
or human-in-the-loop escalation now.

What changes today is only the schema, so the decision stays deliberate
later: every intent now carries an `actor` field (who submitted it),
a `kind` field (`INTERNAL_STATE` vs `EXTERNAL_EFFECT`), and an
`idempotency_key` (so a retrying agent's duplicate submission is
recognizable as a retry, not a second real action). With those fields on
every row, a future conflict policy can distinguish "same actor retrying"
from "two actors contending" without backfilling history.

## Consequences

- Good: today's behavior stays simple, deterministic, and fully tested.
  No speculative coordination machinery is built before a second real
  agent exists to exercise it.
- Good: when MIND arrives, the ledger already records who proposed what,
  so the conflict question can be answered from data instead of guesses.
- Bad: until a policy is chosen, concurrent multi-agent use will see
  contention surface as ordinary REJECTED rows. Operators must read the
  `actor` field to distinguish contention from constraint violations.
- Revisit when: two real agents contend on the same entity in production.
  The options on the table are: keep first-wins (document it as the
  policy), surface an explicit conflict to a human instead of silently
  rejecting, or add per-entity intent queues. Do not guess which one;
  let the first real contention decide.
