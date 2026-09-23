You are a senior engineer continuing a colleague's work. You have received a handoff describing what they did and decided. Read it carefully, then complete the task below.

Rules:
- Use ONLY the handoff. Do not invent facts, numbers, owners, or deadlines.
- If the handoff leaves something open, say so explicitly instead of guessing.
- Write directly; no preamble about being an AI.


[Format: chronological transcript]

--- HANDOFF FROM PREVIOUS AGENT ---
# Agent A — work journal (task_001_vendor_selection)

## Day 1 — scoping

Kicked off the vector DB selection for the support copilot. Hard numbers
first: the corpus is 2M documents, peak load 50 QPS. The infra budget cap
is $2k/mo and Pinecone is billing $3.1k/mo — so the status quo is already
over budget. SOC2 Type II is a hard requirement from the enterprise MSAs;
anything without it is disqualified on arrival. Team context: 5 backend
engineers, all postgres-fluent, zero operational experience with Qdrant
or Weaviate. That last point matters more than the benchmarks suggest.

## Day 2 — vendor evaluation

Ran the bake-off. Pinecone is out on cost alone ($3.1k/mo vs the $2k/mo
cap), and its contract auto-renews Nov 1, so if we stay we are locked in
— cancellation has to be filed before Oct 15 regardless of the decision.

Qdrant Cloud at $1.4k/mo is SOC2 Type II certified and the fastest thing
I tested. Tempting. But I keep coming back to the team: nobody here has
operated Qdrant, and at 2M documents / 50 QPS we do not need its
performance headroom. I am rejecting Qdrant on operational risk — raw
speed we cannot use is not worth on-call pain we cannot staff.

Weaviate Cloud ($1.8k/mo, SOC2 certified) had the weakest recall of the
three and the team dislikes its GraphQL API. Dropped.

pgvector on RDS came in at ~$0.6k/mo incremental, inherits SOC2 from AWS
(need to confirm the exact inheritance wording with the AWS artifact —
Sam is on it), and the team already runs Postgres in production. Recall
measured 0.97 at k=10 on our eval set against an acceptance threshold of
0.95. It clears the bar with margin.

## Day 3 — decisions

Locked four decisions:

1. **Select pgvector on RDS.** Rationale: cheapest ($0.6k/mo), SOC2 via
   AWS, zero new operational surface for a postgres-fluent team, recall
   0.97 clears the 0.95 threshold.
2. **Reject Qdrant despite better raw performance.** Rationale:
   operational risk the team cannot cover.
3. **Sunset Pinecone by end of Q4; file cancellation before Oct 15.**
   Rationale: $3.1k/mo breaks the budget cap and the contract
   auto-renews Nov 1.
4. **Migrate via dual-write then cutover.** Rationale: zero downtime is
   required for the support copilot.

## Open questions (unresolved)

- Can RDS pgvector handle 5x growth to 10M documents without a
  re-architecture? The 10M-vector benchmark (Priya, due Oct 10) will tell us.
- Who owns the embedding pipeline after migration — the ML team or backend?
- Does dual-write double embedding API costs during the migration window?

## Next actions

- Priya: run the pgvector benchmark at 10M vectors (due Oct 10).
- Sam: confirm SOC2 inheritance wording with the AWS artifact.
- Sam: file the Pinecone cancellation before Oct 15.
- Alex: design the dual-write cutover plan.

Handing off here. The recommendation memo is the next deliverable.

--- END HANDOFF ---

--- YOUR TASK ---
# Task 001 — Vector database selection

## Background

Acme's support copilot searches 2M support documents at a peak of 50 QPS.
The team (5 backend engineers, all fluent in Postgres, none with
Qdrant/Weaviate operational experience) currently pays $3.1k/month for
Pinecone — over the $2k/month infrastructure budget cap. Enterprise
contracts require SOC2 Type II, which rules out any vendor without it.

## Agent A's prior work

Agent A evaluated four options against budget, compliance, operational
risk, and recall quality:

- **Pinecone** (current): $3.1k/mo — over budget. Contract auto-renews
  Nov 1; cancellation deadline Oct 15.
- **Qdrant Cloud**: $1.4k/mo, SOC2 Type II certified, excellent raw
  performance — but nobody on the team has operated it.
- **Weaviate Cloud**: $1.8k/mo, SOC2 Type II certified — but the team
  dislikes its GraphQL API and it is the weakest on recall benchmarks.
- **pgvector on RDS**: ~$0.6k/mo incremental, SOC2 inherited from AWS,
  team already operates Postgres. Recall 0.97 @ k=10 on the team's eval
  set (threshold was 0.95).

Agent A decided: **pgvector on RDS**, rejected Qdrant on operational
risk, set a Pinecone sunset deadline, and chose a dual-write migration
(zero downtime is required for the support copilot).

## Continuation brief (identical across conditions)

> Write the final recommendation memo section for engineering leadership:
> the decision, its rationale, key risks, and what must happen before
> sign-off. Keep it under 300 words.

--- END TASK ---