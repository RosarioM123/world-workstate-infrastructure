# WORLD State Model (Draft v0.1)

The canonical schema for work state. This is the heart of the WORLD thesis:
if this ontology doesn't hold up across projects, there is no shared
abstraction (see `docs/thesis-challenge.md`, objection 8).

Status: **draft**. It becomes real only after the handoff experiment
validates that these entities — and not a simpler set — are what actually
prevent information loss.

## Design principles

1. **Small core, layered domains.** A handful of generic entities; investment
   research (or any domain) extends them, never replaces them.
2. **Provenance is cross-cutting.** Every entity carries who/what created it,
   when, and on what basis — never as an afterthought.
3. **State is derived from history.** The current state is a projection over
   an immutable log of state changes. Nothing is ever overwritten; it is
   superseded.
4. **Handoff is a first-class concept.** The bundle a new participant needs
   is computable from the state, not assembled by hand.

## Core entities

### Project
The unit of work. Carries the **context**: goal, scope, constraints,
stakeholders, and the definition of done. One WORLD state per project.

Fields: `id`, `name`, `goal`, `scope`, `constraints[]`, `definition_of_done`,
`status` (active | paused | completed | abandoned), provenance.

### Task
A unit of work to be done, with lifecycle. Tasks decompose; they are the
"what's happening" of the project.

Fields: `id`, `project_id`, `title`, `description`, `status`
(proposed | in_progress | blocked | done | dropped), `assignee`
(human or agent id), `parent_task_id?`, `depends_on[]`, provenance.

### Decision
A choice that was made, with its rationale and basis. Decisions are the
highest-value entity for handoffs: a new participant must know *what was
decided and why* without re-deriving it.

Fields: `id`, `project_id`, `statement`, `rationale`, `status`
(proposed | accepted | superseded | reversed), `evidence_ids[]`,
`supersedes_id?`, provenance. A decision never edits in place — it is
superseded by a new decision that references it.

### Assumption
Something taken as true without full evidence. Assumptions are where
projects silently rot: they go stale, and nobody notices.

Fields: `id`, `project_id`, `statement`, `confidence` (low | medium | high),
`status` (active | validated | invalidated | stale), `validated_by_evidence_id?`,
`stale_after?`, provenance.

### Evidence
A verifiable basis for decisions and assumptions: a document, dataset,
quote, measurement, or external source.

Fields: `id`, `project_id`, `kind` (document | data | observation | source),
`reference` (URI or content hash), `summary`, `captured_by`, provenance.
Evidence is immutable once recorded.

### Artifact
A work product: report, model, deck, codebase, dataset. Artifacts are the
*tangible outputs*; decisions are the *reasoning* behind them.

Fields: `id`, `project_id`, `kind`, `location` (URI), `version`,
`produced_by_task_id?`, provenance.

### Action
Anything a participant did: agent tool calls, human edits, approvals,
messages that changed the work. Actions are the raw material from which
state changes are derived.

Fields: `id`, `project_id`, `actor` (human:<id> | agent:<model>:<run>),
`kind`, `summary`, `timestamp`, `references` (task/decision/evidence ids
touched).

### StateChange (the immutable log)
The append-only history. Every mutation of every entity above is recorded
here; current state is a projection over this log.

Fields: `seq` (monotonic), `entity_type`, `entity_id`, `change`
(created | updated | superseded | status_changed), `before?`, `after`,
`actor`, `timestamp`, `reason?`.

### Question (outstanding questions)
What is currently unknown or undecided. This is the single most valuable
entity for a handoff: it tells the next participant where to start.

Fields: `id`, `project_id`, `question`, `status` (open | answered | dropped),
`blocks_task_id?`, `answered_by_decision_id?`, provenance.

### Handoff
A computed bundle: the minimal state a new participant needs to continue
the work. Not hand-written — generated from the entities above.

Fields: `id`, `project_id`, `generated_at`, `for_actor?`,
`includes`: { context snapshot, active tasks, accepted decisions,
active assumptions, open questions, key evidence refs, recent state
changes }, `format_version`.

## Provenance (cross-cutting, on every entity)

`created_by` (human:<id> | agent:<model>:<run_id>), `created_at`,
`source` (what informed it: evidence ids, prior entity versions),
`supersedes` (prior version id, if any). No entity exists without these.

## Open questions about the model itself

- Is `Action` too fine-grained to store, or is it exactly the audit trail
  that makes state "verifiable"? (Candidate: store actions, project only
  summaries into handoffs.)
- Do `Decision` and `Task` (status=done with outcome) overlap? Where is the
  line?
- What is the minimal handoff bundle — can it be generated, or does it need
  human curation? The experiment will tell us.
