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
