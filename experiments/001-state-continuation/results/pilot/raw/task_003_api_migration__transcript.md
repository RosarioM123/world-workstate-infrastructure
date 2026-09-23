**Phase-1 migration plan: REST → GraphQL**

**Scope.** Stand up an Apollo Federation gateway (schema-first) as a strangler facade in front of the existing REST services; migrate the mobile launch screen first; define schema governance; train the backend team. REST remains the system of record through Q2 — no breaking changes for v1 REST clients until the enterprise SLA window ends.

**Sequencing.**

1. Mobile platform stands up the federation gateway in staging (due Nov 1).
2. Feed team writes the launch-screen subgraph — the biggest win, collapsing 14 REST calls to 2.
3. Staff eng publishes the schema governance RFC (single team vs council ownership is still open).
4. Eng manager books GraphQL training for backend engineers (no production GraphQL experience on the team today).

**Rollback criteria.** If the GraphQL layer's p95 exceeds 300ms in prod, roll back to direct REST for the affected path — the strangler facade makes this a routing change, not a redeploy. Launch-screen migration does not proceed to prod until staging holds p95 under 300ms.

**Open risks.** N+1 queries: prevention via dataloader discipline or review is undecided — the governance RFC must settle it. Current launch p95 is 1.8s; the 300ms budget is aggressive and leaves no room for chatty subgraphs.
