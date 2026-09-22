# ADR 0006: Auth/RBAC shape (deferred, schema prepared)

Date: 2026-09-22
Status: Proposed (not built)

## Context

WORLD currently has no authentication: any caller of `POST /api/v1/intent`
can submit intents as any actor, because the `actor` field is
client-supplied and unenforced. That is acceptable while the only operator
is the repository owner, and the pre-YC plan already defers a full
auth/RBAC system. But the permission model must not require a second
schema migration later, so the shape is recorded now while the `actor`
field is being added.

## Decision

When auth is built, the permission check will be a pure function of three
things, all already present on every ledger row: the authenticated
`actor`, the intent's `action`, and the target `entity_id`. Concretely,
the model will answer "may this actor perform this action on this
entity?" before the constraint engine runs, and a denial will be
REJECTED-but-logged like any other refused intent, so denied attempts stay
auditable. Nothing about the intent schema, the hash chain, or the
verify path will need to change: the only new machinery is proving that
the caller is the actor they claim to be, and storing the actor-to-
permissions mapping.

## Consequences

- Good: the `actor` field added today is the exact join key the future
  permission model needs, so no backfill or schema split when auth lands.
- Good: denied-by-policy attempts remain on the ledger, preserving the
  "every attempt is auditable" invariant for security review.
- Bad: until auth is built, `actor` is self-asserted and proves nothing.
  No consumer should treat it as identity today.
- Revisit when: a second real party (human or service) submits intents.
  That is the trigger for building auth, not a calendar date.
