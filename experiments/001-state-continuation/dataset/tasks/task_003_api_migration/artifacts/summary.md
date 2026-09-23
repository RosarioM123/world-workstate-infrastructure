# Handoff summary — REST → GraphQL migration (task_003)

**Strategy: strangler facade.** A GraphQL gateway sits in front of the
existing REST services — no rewrite, no breaking changes for v1 REST
clients untouched until Q2 per the enterprise SLA. Schema-first with Apollo Federation:
subgraph ownership matches the microservice org. REST stays the system
of record through Q2.

**Why:** the app makes 14 REST calls on launch (p95 1.8s); GraphQL
collapses the launch sequence to 2 calls. The new layer must hold p95
under 300ms. The backend team has no production GraphQL experience
(training budgeted).

**Sequencing:** migrate the mobile launch screen first — the biggest
latency win (14 calls collapse to 2) and the earliest end-to-end exercise
of the gateway.

**Open questions:** single-team vs council ownership of federated schema
governance; N+1 prevention via dataloader discipline or review; the
rollback trigger if p95 exceeds 300ms in prod.

**Next:** federation gateway in staging (mobile platform, due Nov 1);
launch-screen subgraph (feed team); schema governance RFC (staff eng);
GraphQL training for backend engineers (eng manager).
