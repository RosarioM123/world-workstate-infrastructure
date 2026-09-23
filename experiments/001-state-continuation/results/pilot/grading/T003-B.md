**Phase-1 plan — GraphQL migration**

**Scope:** Apollo Federation gateway (schema-first) as a strangler facade over existing REST services. No rewrite, no breaking changes for v1 clients until Q2; REST stays the system of record through Q2.

**Sequencing & owners:**

1. Federation gateway in staging — mobile platform, due Nov 1.
2. Launch-screen subgraph — feed team. First migration target: 14 calls collapse to 2, the largest latency win and the first end-to-end exercise of the gateway.
3. Schema governance RFC — staff eng. Must answer: single-team or council ownership? N+1 prevention — dataloader discipline or review?
4. GraphQL training — eng manager. The team has no production GraphQL experience.

**Rollback criteria:** p95 over 300ms in prod triggers rollback of the affected path to direct REST (a routing change behind the facade). No prod migration for the launch screen until staging sustains p95 under 300ms.

**Watch-outs:** the 300ms budget against today's 1.8s p95 leaves little margin; governance must land before subgraph proliferation, or the federated schema will fragment.
