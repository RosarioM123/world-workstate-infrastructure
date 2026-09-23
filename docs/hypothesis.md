# WORLD Hypothesis

## Core thesis

> AI can generate work, but current AI systems do not reliably maintain a
> shared, verifiable state of work as that work moves between different
> models, agents, humans, tools, and time.

WORLD is **persistent work-state infrastructure for AI and human work**. It is
the canonical record of a project's state — not any single participant's
memory of it.

## Definitions

- **Work state**: the structured record of everything needed to understand
  and continue a project: context, tasks, decisions, assumptions, evidence,
  artifacts, provenance, actions, state changes, outstanding questions, and
  handoff state. (Full schema: `state-model.md`.)
- **Shared**: readable and writable by any authorized participant — human or
  agent — regardless of which model powers the agent or which tool it uses.
- **Verifiable**: every state change carries provenance (who or what made it,
  when, on the basis of what evidence), so any participant can audit how the
  current state came to be.
- **Canonical**: there is exactly one WORLD state per project. Agent
  conversation histories, scratch files, and tool outputs are *inputs* to it,
  not substitutes for it.

## What WORLD is NOT

- **Not an AI memory system.** Memory systems optimize for recall by one
  agent. WORLD optimizes for *continuity across many agents and humans* —
  different models, different tools, different points in time.
- **Not a database.** PostgreSQL (or any store) is an implementation detail.
  The thesis is about the *state abstraction and handoff semantics*, not the
  storage engine.
- **Not an orchestration framework.** Orchestrators schedule agents; WORLD is
  what those agents read from and write to between steps.
- **Not a chat log.** Conversation history is lossy, model-specific, and
  unverifiable. WORLD state is structured, model-agnostic, and auditable.

## The claim, precisely

For a project that moves between participants, maintaining canonical
structured state with explicit provenance preserves more decision-relevant
information across handoffs — and makes that information more auditable —
than relying on conversation history, summaries, or tool-specific artifacts.

## Success criteria

The prototype succeeds if, in the investment-research handoff experiment
(`docs/experiment-handoff.md`):

1. An agent entering mid-project from WORLD state alone reconstructs the
   project's key facts, decisions, and open questions with measurably less
   information loss than agents given only a transcript or a summary.
2. A human can audit any decision in the state and trace it back to its
   evidence and the agent/human action that recorded it.
3. Two different models, given the same WORLD state, produce substantively
   consistent continuations of the work.

## Falsifiability — what would prove WORLD wrong

The thesis is false, or not useful, if any of the following hold:

1. **Summary parity**: an agent given a plain-language summary of prior work
   retains as much decision-relevant information as an agent given structured
   WORLD state. (Then WORLD is overhead, not infrastructure.)
2. **Tool sufficiency**: Git + a docs folder + an MCP server achieves the
   same handoff fidelity with less complexity. (Then WORLD is a workflow,
   not an abstraction.)
3. **Ontology collapse**: the state schema cannot be defined generically
   enough to work across projects without becoming so vague it is useless —
   i.e., every project needs a bespoke schema, so there is no *shared*
   abstraction.
4. **Verification irrelevance**: in practice, nobody audits provenance, and
   decisions are trusted on the agent's authority anyway. (Then
   "verifiable" is a feature nobody uses.)

If (1) or (2) holds, WORLD should be re-scoped as a convention, not built as
infrastructure. If (3) holds, the project is dead. See
`docs/thesis-challenge.md` for the full adversarial case.
## Experiment #002 verdict (2026-09-23)

Experiment #002 (Intel main run plus Disney replication, blind grading on 14
metrics against a predeclared answer key) partially supports the WORLD
thesis, in a specifically narrowed form.

**Supported:** structured work-state with stable labels preserved
decision-governance items across agent handoffs better than a raw journal or
an independently written summary in both runs (reference means 3.92 vs 3.58
vs 3.33 on Intel; 4.45 vs 4.09 vs 2.82 on Disney). The advantage concentrated
in assumptions with confidence levels, provenance, and supersession records.
The mechanism is label stability: the journal continuation renumbered every
item under its own labels, and that relabeling is where governance items were
lost.

**Not supported:** revision history. The WORLD continuation scored 2 on
revision history in BOTH runs, losing the old-to-new-to-trigger chains the
state was built to preserve. The current state representation does not
transmit revision chains into a continuation. An independent summary came
within 0.36 of the WORLD continuation in the replication, so falsifiability
condition 1 (summary parity) remains open.

**Untested:** success criterion 2 (no human has traced a decision from the
state to its evidence) and criterion 3 (same model family throughout).

The claim is therefore narrowed: WORLD-style stable labeled governance
records help cross-agent handoffs for assumptions, provenance, and
supersession, but the revision mechanism is unproven. The next experiment
should test revision-chain preservation explicitly before any broader
infrastructure claim is made.

