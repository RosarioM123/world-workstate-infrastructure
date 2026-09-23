**Recommendation: pgvector on RDS**

**Decision.** Select pgvector on RDS as the vector database for the support copilot; sunset Pinecone by end of Q4; migrate via dual-write then cutover.

**Rationale.** Cheapest ($0.6k/mo incremental vs the $2k/mo cap; Pinecone is $3.1k/mo), SOC2 inherited from AWS (hard requirement), zero new operational burden for a postgres-fluent team, and recall 0.97 at k=10 clears the 0.95 threshold. Qdrant rejected on operational risk despite better raw performance — no one on the team has run it. Pinecone sunset is forced by cost: $3.1k/mo breaks the budget, and the contract auto-renews Nov 1.

**Key risks.** Scale: can RDS pgvector handle 5x growth to 10M documents without a re-architecture? Ownership: who owns the embedding pipeline after migration — ML team or backend? Cost: does dual-write double embedding API costs during the migration window?

**Before sign-off.** Run the pgvector benchmark at 10M vectors (Priya, due Oct 10). Confirm SOC2 inheritance wording with the AWS artifact (Sam). File the Pinecone cancellation before Oct 15 (Sam). Design the dual-write cutover plan (Alex). Zero downtime is required throughout.
