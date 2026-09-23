You are a senior engineer continuing a colleague's work. You have received a handoff describing what they did and decided. Read it carefully, then complete the task below.

Rules:
- Use ONLY the handoff. Do not invent facts, numbers, owners, or deadlines.
- If the handoff leaves something open, say so explicitly instead of guessing.
- Write directly; no preamble about being an AI.


[Format: written summary]

--- HANDOFF FROM PREVIOUS AGENT ---
# Handoff summary — vector DB selection (task_001)

**Decision: migrate the support copilot (2M documents, 50 QPS peak) to
pgvector on RDS.** At ~$0.6k/mo incremental it is the cheapest option,
inherits SOC2 Type II from AWS (a hard requirement from enterprise
contracts), adds no new operational surface for the 5 backend engineers (all postgres-fluent), and measured recall of 0.97 at k=10 clears the 0.95
acceptance threshold.

**Rejected:** Qdrant Cloud ($1.4k/mo, SOC2 certified, fastest in testing).
We reject Qdrant on operational risk — nobody on the team has run it, and its
performance headroom is unneeded at our scale. Weaviate had the weakest
recall and an unpopular GraphQL API. Pinecone ($3.1k/mo) exceeds the
$2k/mo budget cap; we will sunset Pinecone by end of Q4, with cancellation filed
before Oct 15 (contract auto-renews Nov 1).

**Migration:** dual-write then cutover, because zero downtime is required.

**Open questions:** Can RDS pgvector scale to 10M documents without a
re-architecture (benchmark at 10M vectors due Oct 10, owner Priya)? Who owns the
embedding pipeline post-migration — ML team or backend? Does dual-write
double embedding API costs during the window?

**Before sign-off:** Priya's benchmark at 10M vectors; Sam's confirmation of
the SOC2 inheritance wording with the AWS artifact; the Pinecone
cancellation filing; Alex's dual-write cutover plan.

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