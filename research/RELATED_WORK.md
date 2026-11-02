# Related work

How WORLD sits relative to existing approaches to agent memory,
summarization, event sourcing, persistent execution, checkpointing, and
agent handoffs. This file extends the in-repo survey in
`research/comparisons.md` (which also covers relational databases with
audit logs, Git, and tool protocols) and follows its discipline:
nothing here claims novelty for WORLD. Where a system is described
without a formal citation, the description is of the approach as
publicly documented by its makers; the two academic citations given in
full are ones this project can stand behind.

## Agent memory systems

A large product and research category persists context across sessions
for an agent: Mem0, Zep, Letta (the hosted form of the MemGPT line of
work), Cognee, Supermemory, and the memory built into major agent
frameworks. The reference academic design is MemGPT (Packer et al.,
"MemGPT: Towards LLMs as Operating Systems," 2023), which treats the
context window as a memory hierarchy the model itself pages in and out
of. Zep organizes memory as a temporal knowledge graph; Mem0 extracts
and consolidates facts from conversations into a retrievable store;
Cognee builds knowledge graphs from ingested documents; Letta persists
agent state and memory blocks as first-class server-side objects.

What these systems optimize for is **recall by an agent**: getting the
right fragments back in front of a model at the right time. What they
generally do not provide, and what WORLD targets instead:

- A **canonical, model-agnostic record** of a project's work state that
  is the same object for every participant, rather than a per-agent or
  per-framework store, often tied to embeddings or a specific runtime.
- **Work semantics as schema**: decisions with rationale, assumptions
  with confidence, supersession, constraints, and open questions as
  first-class, labeled entities rather than retrieved text fragments.
- **Write-time judgment**: proposed changes validated against declared
  invariants before they enter the record, with rejections preserved.
- **Verifiable history**: a hash-chained log a third party can check
  without trusting the writer.

Honest boundary: WORLD has no retrieval layer, no embeddings, and no
automatic fact extraction. A memory system answers "what is relevant
now"; WORLD answers "what is the agreed state of this work, and how did
it get that way." They are composable, not substitutes. Generative
Agents (Park et al., "Generative Agents: Interactive Simulacra of
Human Behavior," UIST 2023) is the adjacent research landmark for
memory streams plus reflection; its memory serves believable behavior
of simulated agents, not verifiable shared work state.

## Conversation summarization

The conventional alternative, and the control condition in WORLD's own
experiments: condense the prior conversation or work log into prose,
either by hand or with a model, and hand the successor the summary.
Framework support is widespread (rolling summary buffers, hierarchical
summarize-and-keep-recent schemes). Summarization is cheap, readable,
and model-portable, and Experiment #002 showed a strong independent
summary coming within 0.36 of structured state on the reference mean.

Its structural weaknesses are the ones WORLD is built against: the
summary is written once, by one author, with no schema, so
decision-hood, confidence, and supersession survive only if the author
happens to preserve them; it cannot be mechanically verified against
the source; it carries no write-time constraint checking; and each new
handoff re-summarizes, compounding loss. WORLD's claim is not that
summaries are bad, but that they are unverifiable and unjudged. The
falsifiability condition in `research/HYPOTHESIS.md` (summary parity)
exists precisely because the summary baseline is strong.

## Event sourcing

Event sourcing stores state as an append-only log of events and derives
current state by replay or projection. WORLD deliberately borrows its
mechanics: an append-only verdict log, deterministic replay, state as
a projection of history. The differences are in vocabulary and
boundary. Domain events in event-sourced systems are meaningful inside
one application's bounded context; WORLD's log records proposals and
verdicts (COMMITTED or REJECTED) about a work document, with the
judgment itself (which invariant failed, and why) as part of the
record, and is designed to be read across the boundary between
independent agents and tools that share no codebase. WORLD adds no new
storage theory here and claims none; the delta, if any, is the verdict
semantics and the handoff-oriented state model, not the log.

## Persistent and durable execution state

Durable execution systems (Temporal is the canonical example; also
workflow engines and restate-style runtimes) persist the execution
state of a program or workflow so a crashed or long-running process
resumes exactly where it stopped. LangGraph's checkpointers do the
same at agent-graph scope: thread state is snapshotted at step
boundaries so a run can resume, branch, or be inspected.

These systems persist **execution** state: where the program is. WORLD
persists **work** state: what has been decided, assumed, and left open,
and why. An orchestrator resumes a crashed run of the same program;
WORLD briefs a new participant, possibly a different model in a
different tool, who was never part of the original run. The overlap is
real (both are append-friendly, replayable state), and a serious
deployment would plausibly use both layers. WORLD does not compete on
scheduling, retries, timers, or exactly-once activity execution, and
claims no advantage there.

## Checkpointing

Checkpointing in ML and in agent frameworks means snapshotting state
at a point so work can resume or branch from it. WORLD checkpoints are
the same primitive at document scope: an immutable name-to-version pin,
with `resume()` restoring the pinned document as a new version rather
than rewinding history. Two properties differ from typical framework
checkpoints: the pin targets a human-meaningful work state rather than
a step boundary, and resuming never rewrites the log, so the fact that
a rollback happened is itself part of the auditable record. WORLD's
checkpoints offer no storage-level snapshotting, deduplication, or
cross-machine restore; they are pins in one SQLite file.

## Agent handoff approaches

Handoffs between agents are usually implemented as message passing
within one framework (an orchestrator routes a task and its context to
the next agent), as shared scratchpads or blackboard files, or as
ad hoc prompt stuffing: paste the summary or transcript into the next
agent's context. Multi-agent frameworks standardize the routing, not
the content: what crosses the boundary is whatever the sending side
serialized, in whatever shape it chose, with no shared schema, no
verification, and no record of what was dropped.

WORLD's handoff position is that the boundary object should be the
shared state itself: the successor loads the same named document the
predecessor wrote, with its decisions, assumptions, evidence links,
constraints, and verdict history intact and checkable. The
`AgentState` helpers in `src/world/handoff.py` are a thin typed layer
over that document (decisions, evidence, open questions, next actions)
for the common research-handoff shape. Experiments #001 and #002 are,
to this project's knowledge, an unusual attempt to measure handoff
formats against each other under blind grading with predeclared keys;
that methodological point is stated as an observation about this repo's
own record, not as a literature claim.

## Open research gaps

Specific, and in the order the experiment record raises them:

1. **Revision chains.** Structured state demonstrably fails to transmit
   old-to-new-to-trigger revision history into continuations
   (Experiment #002, both runs). Whether an explicit revision-chain
   schema fixes this, or whether successors simply do not read
   revision structure, is untested anywhere in this repo.
2. **Cross-model handoffs.** All handoff evidence here is same-model-
   family. Whether stable labeled state helps more, less, or
   differently when the successor is a different model is unknown.
3. **Summary parity at scale.** One strong summary nearly matched
   structured state at n=1. A powered comparison (multiple tasks,
   multiple summary writers, multiple graders) does not exist yet, in
   this repo or, as far as the maintainer has verified, as a public
   benchmark.
4. **Human auditability.** No study here or cited here measures whether
   a human can actually trace a decision to its evidence faster or
   more reliably from structured state than from a transcript.
5. **Ontology generality.** The work-state schema has been exercised on
   investment-research tasks only. Coding, operations, and scientific
   workflows may need entities the schema lacks, or may show the
   schema is research-shaped. Untested.
6. **Verification in practice.** Hash chains and signed tips are
   mechanized and fuzz-tested here, but whether any real workflow
   would ever check them (falsifiability condition: verification
   irrelevance) is a behavioral question no benchmark in this repo
   answers.
7. **Write-side behavior.** The experiments test successors reading
   state. Whether requiring agents to write state in the schema (and
   be judged by invariants) changes what they record, for better or
   worse, is untested.
