# Task 003 — REST → GraphQL migration

## Background

The mobile app makes 14 REST calls on launch (p95 1.8s). A GraphQL layer
would collapse that to 2 calls. Hard constraints: no breaking changes
for v1 REST clients until Q2 (enterprise SLA); the new GraphQL layer
must hold p95 under 300ms; the backend team has no production GraphQL
experience (training is budgeted).

## Agent A's prior work

Agent A chose the migration strategy: a strangler facade — a GraphQL
gateway in front of the existing REST services, so v1 clients are
untouched and nothing gets rewritten. Schema-first with Apollo
Federation (subgraph ownership matches the microservice org). The mobile
launch screen migrates first (biggest latency win: 14 calls → 2). REST
remains the system of record through Q2 per the SLA.

## Continuation brief (identical across conditions)

> Draft the phase-1 migration plan: scope, sequencing, owners, and
> rollback criteria. Keep it under 300 words.
