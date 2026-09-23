**Phase-1 migration plan**

**Scope.** Strangler facade: a GraphQL gateway in front of the existing REST services — v1 clients untouched, nothing rewritten. Schema-first with Apollo Federation. REST remains the system of record through Q2 per the enterprise SLA (no breaking changes for v1 REST clients until Q2).

**Sequencing.**

1. Stand up the federation gateway in staging (mobile platform, due Nov 1).
2. Write the launch-screen subgraph (feed team) — migrate the launch screen first: 14 calls collapse to 2, the biggest latency win.
3. Define the schema governance RFC (staff eng).
4. Book GraphQL training for backend engineers (eng manager) — the team has no production GraphQL experience; training is budgeted.

**Rollback criteria.** The GraphQL layer must hold p95 under 300ms. If p95 exceeds 300ms in prod, roll back the affected path to REST. Staging must demonstrate sustained p95 under 300ms before any prod cutover.

**Open questions carried forward.** Who owns federated schema governance — a single team or a council? How are N+1 queries prevented — dataloader discipline or review? What exactly is the rollback trigger if p95 exceeds 300ms in prod (automatic or manual)?
