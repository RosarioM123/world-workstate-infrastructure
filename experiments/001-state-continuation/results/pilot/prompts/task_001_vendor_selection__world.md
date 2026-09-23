You are a senior engineer continuing a colleague's work. You have received a handoff describing what they did and decided. Read it carefully, then complete the task below.

Rules:
- Use ONLY the handoff. Do not invent facts, numbers, owners, or deadlines.
- If the handoff leaves something open, say so explicitly instead of guessing.
- Write directly; no preamble about being an AI.


[Format: structured JSON state]

--- HANDOFF FROM PREVIOUS AGENT ---
{
  "objective": "Select a vector database for the support copilot and plan the migration.",
  "decisions": [
    {
      "text": "Select pgvector on RDS as the vector database.",
      "rationale": "Cheapest option at $0.6k/mo incremental, SOC2 inherited from AWS, the team already operates Postgres, and recall 0.97 at k=10 clears the 0.95 threshold."
    },
    {
      "text": "Reject Qdrant despite its better raw performance.",
      "rationale": "Operational risk: nobody on the team has run Qdrant, and the performance headroom is not needed at 2M documents and 50 QPS."
    },
    {
      "text": "Sunset Pinecone by end of Q4; file cancellation before Oct 15.",
      "rationale": "$3.1k/mo exceeds the $2k budget cap, and the contract auto-renews Nov 1."
    },
    {
      "text": "Migrate via dual-write then cutover.",
      "rationale": "Zero downtime is required for the support copilot."
    }
  ],
  "evidence": [
    {
      "claim": "Corpus is 2M documents; peak load is 50 QPS.",
      "source": "capacity planning doc"
    },
    {
      "claim": "Budget cap is $2k/mo; Pinecone costs $3.1k/mo.",
      "source": "infra budget sheet"
    },
    {
      "claim": "SOC2 Type II is a hard requirement from enterprise contracts.",
      "source": "enterprise MSA terms"
    },
    {
      "claim": "Team is 5 backend engineers, all Postgres-fluent, with no Qdrant or Weaviate operational experience.",
      "source": "team skills matrix"
    },
    {
      "claim": "pgvector recall is 0.97 at k=10 on the team's eval set; the acceptance threshold was 0.95.",
      "source": "recall eval notebook"
    },
    {
      "claim": "Weaviate was evaluated and dropped: weakest recall and a GraphQL API the team dislikes.",
      "source": "vendor eval notes"
    }
  ],
  "open_questions": [
    "Can RDS pgvector handle 5x growth to 10M documents without a re-architecture?",
    "Who owns the embedding pipeline after migration: the ML team or backend?",
    "Does dual-write double embedding API costs during the migration window?"
  ],
  "next_actions": [
    "Run the pgvector benchmark at 10M vectors (owner: Priya, due Oct 10).",
    "Confirm SOC2 inheritance wording with the AWS artifact (owner: Sam).",
    "File the Pinecone cancellation before Oct 15 (owner: Sam).",
    "Design the dual-write cutover plan (owner: Alex)."
  ]
}

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