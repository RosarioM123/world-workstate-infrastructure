# WORLD State Model (v0.1; partly implemented, partly draft)

The canonical schema for work state. This is the heart of the WORLD thesis:
if this ontology doesn't hold up across projects, there is no shared
abstraction (see `docs/thesis-challenge.md`, objection 8).

Status, split by entity (updated 2026-11-05, Prompt 6): **implemented**
as handoff types in `src/world/handoff.py`: Decision, Assumption, and
Evidence (see the implementation note below). **Draft only**: Project,
Task, Artifact, Action, StateChange, Question, and Handoff as stored
types. Experiment #003 (2026-11-03) has now run and bore directly on
the implemented fields (its M3 result turned on assumption confidence
and status), so the original framing, that the model becomes real
only after a handoff experiment validates the entities, is partly
satisfied for the implemented subset and still open for the rest.

Field-name mapping (document to code): Decision `statement` is
`text` in code; Decision `supersedes_id` is `supersedes`; Evidence
`summary` is `claim`; Evidence `reference` is `source`. Where this
document and `src/world/handoff.py` disagree on a name, the code is
authoritative.

Implementation status (2026-11-04, Prompt 3 F1): the shipped handoff
schema (`src/world/handoff.py`) now implements this model's Decision
fields (`id`, `status`, `supersedes`, `evidence_ids`; the code names
the link `supersedes` where this document writes `supersedes_id`),
the Assumption entity (`id`, `confidence`, `status`, `validated_by`),
and Evidence `id` and `kind`. `save_state` validates the revision
graph's referential integrity, and `revision_chain` derives a
decision's revision history from committed snapshots. The remaining
entities (Project, Task, Artifact, Action, StateChange as stored
types) are still draft only: core storage remains one opaque JSON
document per version, and Experiment #003's evidence for the fields
above is recorded in `experiments/prompt3/AUDIT.md`.

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
