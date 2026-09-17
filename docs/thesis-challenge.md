# Challenging the WORLD Thesis

This document exists to try to kill the project. Each section is an objection
of the form "WORLD is just X" — the strongest version of the argument that
WORLD is not a genuinely useful abstraction. WORLD only earns continued
investment by surviving these.

## 1. "It's just event sourcing"

**The objection.** An append-only event log in Postgres, with projections for
current state, already gives you ordered, auditable, replayable state. This
is a solved pattern (banking ledgers, CQRS systems). WORLD adds nothing.

**What WORLD must demonstrate.** Event sourcing is a *storage pattern*; it
says nothing about what the events mean across organizational and model
boundaries. WORLD's claim is about the *state schema and handoff semantics*:
a canonical ontology (decision, assumption, evidence, handoff) that any
model can read and write. An event log of opaque blobs does not give you
that. If WORLD's schema turns out to be "a JSON blob per event," the
objection stands and WORLD is just event sourcing with branding.

## 2. "It's just Git"

**The objection.** Git already does provenance (author, timestamp), state
changes (diffs), branching and merging (parallel work), and handoffs (clone,
pull). Teams have coordinated complex work across humans and time with Git
for twenty years.

**What WORLD must demonstrate.** Git versions *files*; WORLD versions
*work-state semantics*. A diff tells you what changed in a document, not
that "Decision D-14 was made by Agent A on the basis of Evidence E-3 and
supersedes Assumption A-7." Git's unit of meaning is the file; WORLD's is
the decision, the task, the question. That said — if the honest thesis is
"Git for agent work-state," say so. That's a defensible position, but the
burden is to show the semantics Git lacks, not to pretend Git doesn't exist.
WORLD should probably *use* Git-like concepts (immutable history,
content-addressing) rather than reinvent them.

## 3. "It's just a database with an audit log"

**The objection.** A `decisions` table with `created_by` and `created_at`
columns is a database with an audit log. Every enterprise CRUD app has one.
There is no new abstraction here.

**What WORLD must demonstrate.** A CRUD app's audit log answers "who changed
this row." WORLD must answer richer questions: "What did Agent B know at the
time it made this decision?", "Which assumptions are still unvalidated?",
"What is the current handoff bundle for a new agent?" If WORLD's queries are
just `SELECT * FROM decisions`, the objection stands. The differentiator has
to be a *queryable model of work* — open questions, assumption validity,
handoff readiness — not row-level auditing.

## 4. "It's just RAG / agent memory"

**The objection.** RAG retrieves relevant context; agent memory systems
(Mem0, Zep, and framework built-ins) already persist state across sessions.
WORLD is a memory system with extra steps.

**What WORLD must demonstrate.** Memory systems optimize for *one agent's
recall*. Their state is model-specific, embedding-specific, and opaque to
humans. WORLD's bet is that cross-participant continuity needs *explicit
structured state*, not retrieved fragments: a new model with no shared
embedding space and no access to the old agent's weights must be able to
pick up the work. If a vector store plus good prompts achieves the same
handoff fidelity in the experiment, WORLD loses this round.

## 5. "It's just MCP"

**The objection.** The Model Context Protocol already standardizes how
models access tools, resources, and state. WORLD could — and should — just
be an MCP server exposing work-state tools. There is no need for a new
thing; there is a need for an MCP implementation.

**What WORLD must demonstrate.** This objection is largely *correct* about
mechanism: WORLD's interface to models probably should be MCP-shaped. The
remaining question is whether the *state model and handoff protocol* are a
genuinely new contribution. "WORLD is a state model + handoff protocol,
exposed over MCP" is a coherent, modest thesis. "WORLD is a new protocol
replacing MCP" is not. This document recommends the former.

## 6. "It's just orchestration"

**The objection.** LangGraph, Temporal, and similar frameworks already
checkpoint agent state, pass it between steps, and resume work. Stateful
orchestration is a solved problem.

**What WORLD must demonstrate.** Orchestrators checkpoint *execution* state:
which step ran, what the variables were. WORLD tracks *work* state: why a
decision was made, what evidence supported it, what's still unknown. An
orchestrator can resume a crashed run; it cannot tell a new human teammate
why the project pivoted last Tuesday. If WORLD can't articulate that
difference crisply, it's orchestration with extra tables.

## 7. The compression objection (the most dangerous one)

**The objection.** Information loss across handoffs is fundamentally a
*compression* problem: Agent A's full context never fits into Agent B's
context, so something is always lost. Structured state is just one more
compression scheme. A well-written summary by a strong model may compress
better than any fixed schema — schemas waste budget on fields nobody reads,
while summaries adapt to what matters.

**What WORLD must demonstrate.** This is the objection the handoff
experiment is designed to test (`docs/experiment-handoff.md`). WORLD wins
only if structured state *measurably* beats a strong-model summary on
decision-relevant retention. If it doesn't, WORLD is overhead. Note the
asymmetry: the summary baseline gets stronger every model generation, while
a fixed schema does not. WORLD's schema must earn its keep against an
improving baseline.

## 8. The ontology objection (the existential one)

**The objection.** "Decision," "assumption," "evidence" sound universal until
you try to define them precisely enough to build on. In investment research
a "decision" is a buy/hold/sell call; in software it's an architecture
choice; in hiring it's a candidate ranking. Either the schema is generic
("a decision has an actor, a timestamp, and a rationale") — in which case
it's too vague to power anything — or it's domain-specific, in which case
there is no *shared* abstraction, just a family of bespoke schemas.

**What WORLD must demonstrate.** That a small core ontology covers the
handoff-critical concepts across domains, with domain specifics layered on
top — not baked in. The state model (`docs/state-model.md`) is where this
lives or dies. If every new project needs a new schema, WORLD is a schema
*framework*, not infrastructure, and should be scoped accordingly.

## Verdict so far

None of these objections is fatal on paper, but (7) and (8) are the ones
that can kill the project empirically. The correct next step is not to build
the app — it is to run the comparisons (`research/comparisons.md`) and then
the handoff experiment. Build only what the experiment justifies.
