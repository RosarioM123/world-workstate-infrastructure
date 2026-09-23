**Recommendation memo — vector database**

**Decision:** adopt pgvector on RDS for the support copilot (2M documents, 50 QPS peak), with a dual-write migration and cutover.

**Rationale:** At ~$0.6k/mo incremental, pgvector is the only option under the $2k/mo cap — Pinecone costs $3.1k/mo. SOC2 Type II, a hard enterprise requirement, is inherited from AWS. The team is 5 postgres-fluent backend engineers with no Qdrant or Weaviate operational experience, so pgvector adds no new operational surface. Recall measured 0.97 at k=10, above the 0.95 threshold. Qdrant Cloud was the fastest in testing but we reject Qdrant on operational risk: performance headroom we can't staff isn't an asset.

**Risks:** whether RDS pgvector scales to 10M documents without a re-architecture; undecided ownership of the embedding pipeline (ML team or backend); possible doubling of embedding API costs during dual-write.

**Pre-sign-off checklist:** (1) Priya's benchmark at 10M vectors, due Oct 10. (2) Sam confirms the SOC2 inheritance wording with the AWS artifact. (3) Sam files the Pinecone cancellation before Oct 15 (auto-renews Nov 1); sunset by end of Q4. (4) Alex's dual-write cutover plan — zero downtime is required.
