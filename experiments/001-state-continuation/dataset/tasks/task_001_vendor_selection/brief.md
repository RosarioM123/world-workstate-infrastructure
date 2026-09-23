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
