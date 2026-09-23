You are a senior engineer continuing a colleague's work. You have received a handoff describing what they did and decided. Read it carefully, then complete the task below.

Rules:
- Use ONLY the handoff. Do not invent facts, numbers, owners, or deadlines.
- If the handoff leaves something open, say so explicitly instead of guessing.
- Write directly; no preamble about being an AI.


[Format: structured JSON state]

--- HANDOFF FROM PREVIOUS AGENT ---
{
  "objective": "Plan the REST to GraphQL migration for the mobile app.",
  "decisions": [
    {
      "text": "Strangler facade: a GraphQL gateway in front of the existing REST services.",
      "rationale": "No rewrite; v1 REST clients untouched behind the SLA freeze."
    },
    {
      "text": "Schema-first with Apollo Federation.",
      "rationale": "Subgraph ownership matches the microservice org structure."
    },
    {
      "text": "Migrate the mobile launch screen first.",
      "rationale": "Biggest latency win: 14 calls collapse to 2."
    },
    {
      "text": "Keep REST as the system of record through Q2.",
      "rationale": "Enterprise SLA freezes v1 REST clients until Q2."
    }
  ],
  "evidence": [
    {
      "claim": "The app makes 14 REST calls on launch; p95 is 1.8s.",
      "source": "mobile perf traces"
    },
    {
      "claim": "No breaking changes for v1 REST clients until Q2.",
      "source": "enterprise SLA"
    },
    {
      "claim": "The GraphQL layer must hold p95 under 300ms.",
      "source": "perf budget doc"
    },
    {
      "claim": "The backend team has no production GraphQL experience; training is budgeted.",
      "source": "team skills matrix"
    },
    {
      "claim": "GraphQL would collapse the launch sequence to 2 calls.",
      "source": "schema spike"
    }
  ],
  "open_questions": [
    "Who owns federated schema governance: a single team or a council?",
    "How are N+1 queries prevented: dataloader discipline or review?",
    "What is the rollback trigger if p95 exceeds 300ms in prod?"
  ],
  "next_actions": [
    "Stand up the federation gateway in staging (owner: mobile platform, due Nov 1).",
    "Write the launch-screen subgraph (owner: feed team).",
    "Define the schema governance RFC (owner: staff eng).",
    "Book GraphQL training for backend engineers (owner: eng manager)."
  ]
}

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