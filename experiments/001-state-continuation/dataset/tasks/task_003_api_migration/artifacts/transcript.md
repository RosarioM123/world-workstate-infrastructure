# Agent A — migration work journal (task_003_api_migration)

## Day 1 — the problem

Traced the mobile launch path: 14 REST calls on launch, p95 1.8s. The
waterfall is the killer — each call waits on the last. A GraphQL layer
would collapse the launch sequence to 2 calls. Constraints are hard:
no breaking changes for v1 REST clients until Q2 (enterprise SLA), the
new layer must hold p95 under 300ms, and the backend team has no
production GraphQL experience — training is budgeted but the learning
curve is real.

## Day 2 — strategy

Two options on the table: a full native rewrite in GraphQL, or a
strangler facade. The rewrite is a non-starter under the SLA freeze, so:
**strangler facade** — a GraphQL gateway in front of the existing REST
services. v1 clients untouched, nothing rewritten. For the gateway I
compared Apollo and Hot Chocolate; going with **Apollo Federation,
schema-first** — subgraph ownership matches our microservice org, so
each team owns its slice of the schema.

Sequencing: migrate the mobile **launch screen first** — biggest latency
win, 14 calls down to 2, and it exercises the whole path early. And per
the SLA, **REST stays the system of record through Q2**.

## Decisions locked

1. **Strangler facade: GraphQL gateway in front of existing REST.**
   Rationale: no rewrite; v1 clients untouched under the SLA freeze.
2. **Schema-first with Apollo Federation.** Rationale: subgraph
   ownership matches the microservice org.
3. **Migrate the mobile launch screen first.** Rationale: biggest win —
   14 calls collapse to 2.
4. **Keep REST as the system of record through Q2.** Rationale: the
   enterprise SLA freezes v1 clients until Q2.

## Open questions

- Who owns federated schema governance — a single team or a council?
- How are N+1 queries prevented: dataloader discipline or review?
- What is the rollback trigger if p95 exceeds 300ms in prod?

## Next actions

- Mobile platform: stand up the federation gateway in staging (due Nov 1).
- Feed team: write the launch-screen subgraph.
- Staff eng: define the schema governance RFC.
- Eng manager: book GraphQL training for backend engineers.

Handing off: the phase-1 migration plan is the next deliverable.
