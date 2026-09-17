# WORLD vs. Existing Technologies

The competitive survey. Each technology gets: what it already solves, what
it doesn't, and what WORLD would have to add to earn its existence. This is
the research backbone of `docs/thesis-challenge.md`.

## Comparison matrix

| Capability | RDBMS + audit log | Event sourcing | Git | RAG / vector memory | Agent memory products | MCP | Orchestration (LangGraph/Temporal) | WORLD (claimed) |
|---|---|---|---|---|---|---|---|---|
| Ordered, replayable history | Partial | Yes | Yes | No | Partial | No | Yes (execution) | Yes (work semantics) |
| Provenance (who/when/why) | Who/when | Who/when | Who/when | No | Partial | No | Who/when | Who/when/**why** |
| Cross-model portability | Yes | Yes | Yes | No (embedding-tied) | Partial | Yes | Partial | Yes (core claim) |
| Human-readable + auditable | Yes | Partial | Yes | No | No | n/a | Partial | Yes (core claim) |
| Schema for work concepts | No | No | No | No | No | No | No | Yes (core claim) |
| Handoff bundle generation | No | No | No | No | Partial | No | No | Yes (core claim) |
| Assumption lifecycle | No | No | No | No | No | No | No | Yes |
| Outstanding-question tracking | No | No | No | No | No | No | No | Yes |

## Per-technology notes

### Relational DB + audit log
Solves: durable structured storage, who-changed-what-when.
Doesn't solve: *why* — rationale, evidence linkage, and work-semantic
queries (open questions, stale assumptions) are not first-class.
WORLD's delta: the work ontology and handoff semantics, not the storage.

### Event sourcing / CQRS
Solves: append-only history, projections, replay, audit.
Doesn't solve: cross-boundary meaning. Events are opaque without a shared
schema; "DecisionAccepted" means nothing to a new model without the
ontology behind it.
WORLD's delta: the canonical event *vocabulary* for work, plus handoff
projections as a first-class concept. WORLD should steal event sourcing's
mechanics, not compete with them.

### Git
Solves: provenance, diffing, branching/merging, distributed handoff of
*files*.
Doesn't solve: work semantics. A diff shows what changed, not that a
decision was made on evidence and supersedes an assumption.
WORLD's delta: versioning *decisions/tasks/questions*, not files. Git-like
properties (immutable history, content addressing) are features to adopt.

### RAG / vector memory
Solves: retrieving relevant fragments from large corpora.
Doesn't solve: structure, provenance, or cross-model portability —
embeddings are model-tied, retrieval is probabilistic, and "relevant
fragments" are not a work state.
WORLD's delta: explicit structured state instead of retrieved fragments.
The experiment tests whether this actually retains more.

### Agent memory products (Mem0, Zep, framework built-ins)
Solves: persisting context across sessions for *one* agent stack.
Doesn't solve: model-agnostic handoff (state is often embedding- or
framework-tied), human auditability, or a canonical cross-project schema.
WORLD's delta: the *shared* and *verifiable* parts of the thesis — memory
for the team, not the agent.

### MCP (Model Context Protocol)
Solves: standard interface for models to reach tools/resources.
Doesn't solve: what the work-state *means*. MCP is a transport-shaped
answer to a different question.
WORLD's delta: none at the protocol layer — WORLD should likely *be* an
MCP-shaped interface. The contribution, if any, is the state model and
handoff protocol it exposes.

### Orchestration frameworks (LangGraph, Temporal)
Solves: checkpointed, resumable *execution* state across agent steps.
Doesn't solve: *work* state — why decisions were made, what's still
unknown, what a new human teammate needs on day one.
WORLD's delta: work semantics over execution semantics. An orchestrator
resumes a crashed run; WORLD briefs a new participant.

## The honest summary

WORLD's defensible territory is narrow: **a canonical, model-agnostic
ontology for work state + a handoff protocol, likely exposed over
MCP-shaped interfaces, persisted with event-sourced mechanics.** Everything
else on the matrix is either borrowed or out of scope. If the handoff
experiment shows a strong-model summary matches structured state on
retention, even that territory collapses — see `docs/experiment-handoff.md`
for the kill criteria.
