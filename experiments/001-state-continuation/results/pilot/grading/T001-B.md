**Recommendation: migrate to pgvector on RDS**

**Decision.** Move the support copilot's vector search (2M documents, 50 QPS peak) from Pinecone to pgvector on RDS, migrating via dual-write then cutover.

**Rationale.** pgvector costs ~$0.6k/mo incremental against the $2k/mo budget cap (Pinecone bills $3.1k/mo); it inherits SOC2 Type II from AWS, a hard requirement in our enterprise contracts; the 5 backend engineers are all postgres-fluent, so there is no new operational surface; and measured recall of 0.97 at k=10 clears the 0.95 acceptance threshold. Qdrant was rejected despite better raw performance — nobody on the team has operated it, and at our scale the headroom isn't worth the on-call risk.

**Key risks.** (1) Scale headroom: RDS pgvector is unproven at 10M documents. (2) Ownership of the embedding pipeline post-migration (ML team or backend) is undecided. (3) Dual-write may double embedding API costs during the migration window.

**Before sign-off.** Priya's benchmark at 10M vectors (due Oct 10); Sam's confirmation of the SOC2 inheritance wording with the AWS artifact; filing the Pinecone cancellation before Oct 15 — the contract auto-renews Nov 1; Alex's dual-write cutover plan.
