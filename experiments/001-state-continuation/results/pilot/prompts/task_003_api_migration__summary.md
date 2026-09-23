You are a senior engineer continuing a colleague's work. You have received a handoff describing what they did and decided. Read it carefully, then complete the task below.

Rules:
- Use ONLY the handoff. Do not invent facts, numbers, owners, or deadlines.
- If the handoff leaves something open, say so explicitly instead of guessing.
- Write directly; no preamble about being an AI.


[Format: written summary]

--- HANDOFF FROM PREVIOUS AGENT ---
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

--- END HANDOFF ---

--- YOUR TASK ---
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

--- END TASK ---