# WORLD Data Model Proposal (Prompt 3, Phase 2)

**Date:** 2026-11-26 (Mission Day 15, Prompt 3). **Branch:**
`mission/prompt3-data-model`. **Status:** proposal, with one essential
subset implemented in the same change (section 7). Everything in
section 8 is proposed only and is NOT implemented; it waits for
Rosario's review. No em dashes.

**Method.** The evaluation below was made by reading the shipped code,
not the design docs: `src/world/handoff.py` (the typed handoff layer),
`src/world/core.py` (the storage and judging layer), `src/world/__init__.py`
(the package surface), and `docs/state-model.md` (the v0.1 ontology,
which itself splits entities into implemented and draft-only). Where
this proposal and `docs/state-model.md` disagree, the code is
authoritative today and this proposal says what should change.

## 1. The current model in one paragraph

WORLD has two layers. The core (`src/world/core.py`) stores one opaque
JSON document per world; every version row carries `seq`, `timestamp`,
`actor`, `note`, `state`, `status` (COMMITTED or REJECTED), and the
hash chain. The core knows nothing about entities. The handoff layer
(`src/world/handoff.py`) defines the only typed work-state model:
`AgentState` with `objective` (a string), `decisions`, `assumptions`,
and `evidence` (typed dataclasses with ids, lifecycle status, and
cross-links), plus `open_questions` and `next_actions` as plain lists
of strings. It is stored under the reserved `"handoff"` key of the
document. `save_state` validates referential integrity before
proposing; `revision_chain` derives one decision's history from
committed snapshots; `project_state` projects a continuation-ready
view. The legacy engine (`src/world_engine/`) has its own generic
entity ledger for the frozen demo and is out of scope for this
proposal; the primitive is the product direction (ARCHITECTURE_MAP.md
section 1).

## 2. Entity evaluation

Verdicts: REPRESENTED (a typed, validated form exists), PARTIAL
(exists in a weaker form: free text, an untyped field, or only at the
version level), MISSING (no representation).

| # | Entity or property | Verdict | Evidence |
|---|---|---|---|
| 1 | Projects | PARTIAL | One world is one project by convention; the world name is the project identity. `AgentState` has no project field and no project metadata (goal, scope, constraints, definition of done in `docs/state-model.md`). `src/world/core.py` `World(name)`; `docs/state-model.md` Project is draft only. |
| 2 | Objectives | REPRESENTED | `AgentState.objective: str` is required; `load_state` raises without it. `src/world/handoff.py` `AgentState`. |
| 3 | Tasks | MISSING | No Task type anywhere in `src/world/`. The draft Task in `docs/state-model.md` was never implemented. Work items exist only as `next_actions` strings. |
| 4 | Subtasks | MISSING | Follows from 3: no task, no `parent_task_id`. |
| 5 | Decisions | REPRESENTED | `Decision` with `text`, `rationale`, `id`, `status` (proposed, accepted, superseded, reversed), `supersedes`, `evidence_ids`; validated in `validate_state`. |
| 6 | Decision rationale | REPRESENTED | `Decision.rationale`, carried through `revision_chain` entries. |
| 7 | Assumptions | REPRESENTED | `Assumption` with `id`, `confidence` (low, medium, high), `status` (active, validated, invalidated, stale), `validated_by` evidence link. |
| 8 | Evidence and sources | REPRESENTED | `Evidence` with `claim`, `source`, `id`, `kind`. Note: `kind` is a free string in code; `docs/state-model.md` prescribes an enum (document, data, observation, source) that code does not enforce. |
| 9 | Artifacts | MISSING | No Artifact type. A work product can only be mentioned inside an evidence `source` string or decision text. Draft only in `docs/state-model.md`. |
| 10 | Dependencies | PARTIAL | Decision supersession and assumption validation are dependency-like links, and invariants can lock fields, but task-to-task dependencies do not exist because tasks do not exist (see 3). |
| 11 | Owners and responsible agents | PARTIAL | Every version row records `actor` (who proposed the change) and `revision_chain` surfaces it, but `actor` is self-asserted, and no entity carries an owner or assignee field. Per-entity ownership is missing. |
| 12 | Permissions | MISSING at entity level | No per-entity or per-actor permissions in the primitive. The only gate is the HTTP API key on `world serve` writes (fail-closed since F2) and field locking via invariants. Per-actor identity and RBAC are designed in `docs/adr/0006-auth-rbac-shape.md`, not built (IMPLEMENTATION_STATUS.md section 5). |
| 13 | Open questions | PARTIAL | `AgentState.open_questions: list[str]` round-trips faithfully, but questions have no id, status (open, answered, dropped), or link to the decision that answered them. Draft Question entity in `docs/state-model.md` is richer than the code. |
| 14 | Uncertainty | REPRESENTED for assumptions, PARTIAL overall | `Assumption.confidence` plus lifecycle status is a real, validated representation, and Experiment #003 showed it is exactly what free-text handoffs lose. Decisions and evidence carry no confidence or uncertainty marker. |
| 15 | Historical revisions | REPRESENTED | Full snapshot per version in the hash chain; `state(version=...)` time travel; `revision_chain` for decisions; REJECTED proposals are also recorded. |
| 16 | Current status | REPRESENTED | Latest committed snapshot is the current state; lifecycle status fields on decisions and assumptions; `project_state` separates current guidance from superseded history. |
| 17 | Next actions | PARTIAL | `AgentState.next_actions: list[str]` round-trips, but actions are untyped strings: no owner, no status, no link to a task or decision. This is the free-text shadow of the missing Task entity. |

## 3. The six required capabilities, checked against the model

1. **Queryable current state.** Served today by the latest committed
   snapshot plus `project_state`. Weakened by 3 and 17: "what is
   in progress, who owns it, what is it blocked on" cannot be
   answered from typed data.
2. **Historical reconstruction.** Served: full snapshots, hash chain,
   `revision_chain`. Strongest part of the current model.
3. **Traceability from decisions to evidence.** Served:
   `evidence_ids` validated at save time; assumptions trace via
   `validated_by`. Weakened only when work is tracked as free-text
   actions instead of decisions.
4. **Clear ownership of changes.** Served at version level (`actor`
   on every row, surfaced by `blame` and `revision_chain`), with the
   stated limit that `actor` is self-asserted. Missing at entity
   level (see 11).
5. **Safe state transitions.** Served: invariant judging, optimistic
   concurrency, lifecycle enums validated at construction and at
   save. Task lifecycle transitions do not exist yet (see 3).
6. **Cross-agent continuation.** Served by the handoff round trip,
   and measured by Experiments #001 to #003. The continuation bundle
   is exactly where untyped tasks hurt: a successor agent gets a
   prose to-do list, not a work queue.

## 4. Essential vs deferred decision

**Essential for the first working product: the Task entity.** It is
the only gap that weakens three of the six required capabilities at
once (queryable current state, safe transitions, cross-agent
continuation), it is the entity the draft ontology already specifies,
and `next_actions` proves the demand exists in the current schema:
users already record work items, just without structure. A task needs
an id, a lifecycle status, an owner, a parent link (subtasks), and
dependency links, all validated the same way decision links are
validated today. This is an additive change to the handoff document
format, not a storage change.

**Deferred, with reasons:**

- **Project metadata** (goal, scope, constraints, definition of
  done). One world equals one project is a workable convention for
  the first product; `objective` already carries the goal. Adding a
  Project record inside the document buys little until multi-project
  queries exist. Proposed only (section 8).
- **Artifact entity.** Real gap, but the first product's artifacts
  live outside WORLD (files, URLs) and are already referenceable
  through `Evidence.source`. Typing artifacts matters once a pilot
  workflow (Prompt 6) shows which fields are actually used. Proposed
  only.
- **Question entity upgrade** (ids, status, answered-by links). Open
  questions round-trip today; the upgrade is valuable but not
  blocking, and it changes the stored type of an existing field
  (`list[str]` to a list of objects), which needs a load-time
  migration decision. Proposed only, with the migration sketched in
  section 8.
- **Per-entity permissions and RBAC.** An auth design question
  (ADR 0006), not a data-model gap to close by adding fields.
  Adding an owner field (implemented, as data) is not a permission
  system and must not be described as one.
- **Confidence on decisions and evidence.** Experiment evidence
  supports confidence on assumptions specifically. Extending it
  without evidence invites false precision. Deferred.
- **Action and StateChange as stored types.** Already served by the
  version log itself (`actor`, `note`, status, snapshots); storing
  them again as entities would duplicate the log.
- **Evidence `kind` enum enforcement.** The doc prescribes an enum,
  the code accepts any string. Enforcing it now would reject stored
  states that use other kinds (a backward compatibility break for a
  cosmetic gain). Proposed only.

## 5. Proposed schema (the implemented subset)

One new dataclass in `src/world/handoff.py`, following the exact
patterns of `Decision` and `Assumption`:

```python
TASK_STATUSES = ("proposed", "in_progress", "blocked", "done", "dropped")

@dataclass
class Task:
    title: str
    id: str = ""
    status: str = "proposed"        # one of TASK_STATUSES
    owner: str = ""                  # human or agent id, self-asserted like actor
    parent_id: str | None = None     # subtask link
    depends_on: list[str] = field(default_factory=list)  # task ids
```

`AgentState` gains one section, appended last so existing field
order is untouched:

```python
tasks: list[Task] = field(default_factory=list)
```

Stored form: the handoff dict gains a `"tasks"` key holding a list
of task dicts with the fields above. No core storage change, no new
tables, no change to the hash chain or the version row format.

Validation added to `validate_state`, engaging only when ids are
used (the same opt-in rule the revision graph already follows):

- non-empty task ids are unique;
- `parent_id` resolves to a task in the same state, is not the
  task itself, and parent chains have no cycles;
- every `depends_on` entry resolves to a task in the same state,
  is not the task itself, and the dependency graph has no cycles
  (a cycle would make every task in it permanently blocked).

`project_state` gains a task rule consistent with its existing
rules: tasks marked `done` or `dropped` are compacted to a one-line
title keeping `id`, `status`, `owner`, `parent_id`, and
`depends_on`; all other tasks pass through in full.

`Task` is exported from `world.handoff` and from the top-level
`world` package, next to `Decision` and `Evidence`.

## 6. Migration plan

No migration is required for the implemented subset, and that is a
design constraint, not an accident:

- **Stored worlds:** a handoff dict without a `"tasks"` key loads
  with `tasks == []` (`from_dict` uses `data.get("tasks", [])`, the
  same pattern as every other section). A world written by new code
  read by old code: old `AgentState.from_dict` ignores unknown keys,
  so the tasks section is silently skipped, not an error. Both
  directions are pinned by tests.
- **Core storage:** untouched. No SQLite schema change, no version
  row change, nothing to migrate in existing world files.
- **Rollback:** reverting the code restores the old behavior exactly;
  task data written meanwhile stays in the document as an ignored
  key and reappears if the code is re-applied.

## 7. Implemented in this change (and nothing more)

- `Task` dataclass, `TASK_STATUSES`, `AgentState.tasks`, the
  `validate_state` task rules, the `project_state` task rule, and
  the exports, exactly as section 5 specifies.
- Acceptance tests in `tests/test_handoff_tasks.py` (section 9),
  written before the implementation.
- `docs/state-model.md` status note updated: Task moves from draft
  to implemented (subset: no `project_id`, because one world is one
  project; the field mapping is recorded there).

## 8. Proposed only, NOT implemented (for Rosario's review)

1. **Question entity upgrade.** Replace `open_questions: list[str]`
   with a `Question` dataclass (`text`, `id`, `status` open /
   answered / dropped, `answered_by` decision id, `blocks` task
   id). Stored-format change to an existing field, so it needs a
   load-time coercion: strings in a stored list load as `Question`
   objects with empty ids. Backward compatible on load, lossy on
   save-back through old code. Judgment call; left for review.
2. **Artifact entity.** `Artifact` dataclass (`id`, `kind`,
   `location`, `title`, `produced_by` task id). Additive like
   tasks, but the field set should be decided by the Prompt 6
   pilot's real usage, not guessed now.
3. **Project metadata section.** An optional `project` dict in
   `AgentState` (`name`, `scope`, `constraints`,
   `definition_of_done`). Additive; deferred until multi-project
   queries are a real requirement.
4. **Evidence `kind` enum.** Enforce the `docs/state-model.md`
   enum (document, data, observation, source) or formally accept
   free strings and fix the doc. Either way it is a doc-versus-code
   decision for Rosario; enforcing it is a breaking change for
   states already stored with other kinds.
5. **Per-entity provenance fields** (`created_by`, `created_at` on
   each entity, as `docs/state-model.md` prescribes). Version rows
   already carry actor and timestamp for the change that introduced
   an entity, and `revision_chain` surfaces them for decisions.
   Duplicating provenance inside entities risks divergence between
   the two records. Proposed only, with a recommendation to NOT
   implement unless a concrete query needs it.

## 9. Acceptance criteria and tests

Each essential change has a test in `tests/test_handoff_tasks.py`:

| Criterion | Test |
|---|---|
| Task fields round-trip through save and load unchanged | `test_task_fields_roundtrip_through_save_and_load` |
| A pre-Task stored handoff (no `tasks` key) still loads | `test_old_format_handoff_without_tasks_still_loads` |
| Tasks survive a fresh handle (new process equivalent) | `test_tasks_load_from_fresh_handle` |
| Invalid task status is rejected at construction | `test_invalid_task_status_rejected` |
| Duplicate task ids are rejected at save | `test_validation_duplicate_task_ids_rejected` |
| Unknown, self, and cyclic parent links are rejected | `test_validation_parent_must_resolve`, `test_validation_task_cannot_be_own_parent`, `test_validation_parent_cycle_rejected` |
| Unknown, self, and cyclic dependencies are rejected | `test_validation_depends_on_must_resolve`, `test_validation_task_cannot_depend_on_itself`, `test_validation_dependency_cycle_rejected` |
| A valid subtask and dependency graph saves and loads | `test_subtask_and_dependency_graph_roundtrip` |
| `project_state` compacts finished tasks, keeps active ones full, does not mutate the input | `test_project_state_compacts_finished_tasks` |

Plus the standing criteria: the full suite passes with no
regressions (510 passing at baseline), ruff and mypy are clean on
changed code, and no stored format that loaded before this change
fails to load after it.

## 10. Backward compatibility risks found

- **R-1 (handled):** old stored handoffs have no `tasks` key.
  Handled by the `data.get` default and pinned by test.
- **R-2 (accepted, documented):** new states read by old code lose
  the tasks section silently (old `from_dict` ignores unknown
  keys). Same behavior as every previous additive handoff change
  (the F1 fields had the same property). Acceptable for a library
  at 0.1.0 with no external users yet; noted here so it is a
  decision, not a surprise.
- **R-3 (avoided):** validation strictness. The new task rules
  engage only when task ids are used, matching the existing
  revision-graph rule, so no previously valid state becomes
  invalid. States with tasks but no ids validate trivially.
- **R-4 (avoided):** `project_state` output shape. The projection
  gains a tasks section populated from the input; callers that
  read the other sections are unaffected.
- **R-5 (open, pre-existing):** idempotency keys still sit outside
  the hash chain (L-6 / F3b) and `actor` is still self-asserted.
  This proposal does not change either; `Task.owner` inherits the
  self-asserted limit and the docs say so.

## 11. What Rosario should review or decide

1. The essential-versus-deferred call itself: Task now, the rest
   later (section 4).
2. The Question upgrade (section 8.1): worth the stored-format
   change, or keep questions as strings?
3. Evidence `kind` (section 8.4): enforce the doc's enum, or fix
   the doc to match the code?
4. Whether `Assumption` should also be exported from the top-level
   `world` package while `Task` is added (pre-existing D-8 gap;
   this change adds `Task` only, to stay minimal).
