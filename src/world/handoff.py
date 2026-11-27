"""Agent handoff interface: the first agent-facing API on the WORLD primitive.

Two operations, stdlib only, no LLM provider dependency:

    save_state(world, state, ...) -> int   # returns the committed version
    load_state(world, ...) -> AgentState

The work state is a structured document with seven sections:
objective, decisions, assumptions, evidence, tasks, open questions,
next actions. It is stored under the reserved ``"handoff"`` key of
the world's JSON document. A fresh agent needs nothing but the world
name to recover the canonical state:

    state = load_state("research-acme")   # objective, decisions, ...

Decisions, assumptions, and evidence carry the research state model's
identity and provenance fields (``docs/state-model.md``): stable ids,
lifecycle status, supersession links, confidence, and evidence links.
``save_state`` validates the revision graph's referential integrity
before proposing, and :func:`revision_chain` derives one decision's
revision history from the committed snapshots.

A successor agent that never saw the conversation continues from a
continuation packet (:func:`continuation_packet`), a provider-neutral
bundle carrying the eleven fields Prompt 4 names (objective,
completed work, remaining tasks, decisions with rationale, evidence,
unresolved questions, artifact references, dependencies, known
errors, state version, next action), available as JSON or as
deterministic plain text (:func:`render_packet_text`).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .core import World

__all__ = [
    "AgentState",
    "Assumption",
    "Decision",
    "Evidence",
    "Task",
    "continuation_packet",
    "load_state",
    "packet_from_state",
    "project_state",
    "render_packet_text",
    "revision_chain",
    "save_state",
    "validate_state",
]

#: Reserved top-level key of the world document holding the handoff state.
HANDOFF_KEY = "handoff"

#: Version of the continuation packet format. The packet is plain JSON
#: plus a plain-text rendering; it names no model provider and uses no
#: provider-specific formatting, so any agent can consume it.
PACKET_FORMAT = "world-continuation/1"

#: Lifecycle states of a decision (docs/state-model.md).
DECISION_STATUSES = ("proposed", "accepted", "superseded", "reversed")
#: Confidence levels of an assumption (docs/state-model.md).
ASSUMPTION_CONFIDENCES = ("low", "medium", "high")
#: Lifecycle states of an assumption (docs/state-model.md).
ASSUMPTION_STATUSES = ("active", "validated", "invalidated", "stale")
#: Lifecycle states of a task (docs/DATA_MODEL_PROPOSAL.md).
TASK_STATUSES = ("proposed", "in_progress", "blocked", "done", "dropped")


@dataclass
class Decision:
    """A decision the agent made, with the reasoning behind it.

    ``id`` is a stable, author-assigned identifier that persists across
    revisions; it is required once revision features are used.
    ``status`` is the lifecycle state (default ``"accepted"``).
    ``supersedes`` names the id of the decision this one replaces, and
    ``evidence_ids`` links to the :class:`Evidence` items backing it.
    """

    text: str
    rationale: str = ""
    id: str = ""
    status: str = "accepted"
    supersedes: str | None = None
    evidence_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.status not in DECISION_STATUSES:
            raise ValueError(
                f"invalid decision status {self.status!r}: "
                f"use one of {', '.join(DECISION_STATUSES)}"
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Decision:
        if not isinstance(data, dict):
            raise TypeError(f"decision must be a dict, got {type(data).__name__}")
        supersedes = data.get("supersedes")
        return cls(
            text=str(data["text"]),
            rationale=str(data.get("rationale", "")),
            id=str(data.get("id", "")),
            status=str(data.get("status", "accepted")),
            supersedes=None if supersedes is None else str(supersedes),
            evidence_ids=[str(e) for e in data.get("evidence_ids", [])],
        )


@dataclass
class Evidence:
    """A finding backing the work, with where it came from.

    ``id`` is a stable, author-assigned identifier that decisions and
    assumptions link to; ``kind`` classifies the basis (for example
    ``"measurement"``, ``"document"``, ``"quote"``).
    """

    claim: str
    source: str = ""
    id: str = ""
    kind: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Evidence:
        if not isinstance(data, dict):
            raise TypeError(f"evidence must be a dict, got {type(data).__name__}")
        return cls(
            claim=str(data["claim"]),
            source=str(data.get("source", "")),
            id=str(data.get("id", "")),
            kind=str(data.get("kind", "")),
        )


@dataclass
class Assumption:
    """Something taken as true without full evidence.

    ``confidence`` is one of ``"low"``, ``"medium"``, ``"high"``;
    ``status`` tracks the lifecycle (``"active"``, ``"validated"``,
    ``"invalidated"``, ``"stale"``). ``validated_by`` names the id of
    the :class:`Evidence` item that validated the assumption, when one
    has. Experiment #003 found that confidence level and
    fact-versus-assumption status are exactly what free-text handoffs
    lose, which is why they are fields here rather than prose.
    """

    text: str
    id: str = ""
    confidence: str = "medium"
    status: str = "active"
    validated_by: str | None = None

    def __post_init__(self) -> None:
        if self.confidence not in ASSUMPTION_CONFIDENCES:
            raise ValueError(
                f"invalid assumption confidence {self.confidence!r}: "
                f"use one of {', '.join(ASSUMPTION_CONFIDENCES)}"
            )
        if self.status not in ASSUMPTION_STATUSES:
            raise ValueError(
                f"invalid assumption status {self.status!r}: "
                f"use one of {', '.join(ASSUMPTION_STATUSES)}"
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Assumption:
        if not isinstance(data, dict):
            raise TypeError(f"assumption must be a dict, got {type(data).__name__}")
        validated_by = data.get("validated_by")
        return cls(
            text=str(data["text"]),
            id=str(data.get("id", "")),
            confidence=str(data.get("confidence", "medium")),
            status=str(data.get("status", "active")),
            validated_by=None if validated_by is None else str(validated_by),
        )


@dataclass
class Task:
    """A unit of work to be done, with lifecycle and ownership.

    The typed form of what ``next_actions`` records as free text
    (docs/DATA_MODEL_PROPOSAL.md). ``id`` is a stable, author-assigned
    identifier; ``status`` is the lifecycle state (default
    ``"proposed"``); ``owner`` names the human or agent responsible
    (self-asserted, like the version log's ``actor``; it is data, not
    a permission). ``parent_id`` links a subtask to its parent task,
    and ``depends_on`` lists task ids that must finish first.
    """

    title: str
    id: str = ""
    status: str = "proposed"
    owner: str = ""
    parent_id: str | None = None
    depends_on: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.status not in TASK_STATUSES:
            raise ValueError(
                f"invalid task status {self.status!r}: "
                f"use one of {', '.join(TASK_STATUSES)}"
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        if not isinstance(data, dict):
            raise TypeError(f"task must be a dict, got {type(data).__name__}")
        parent_id = data.get("parent_id")
        return cls(
            title=str(data["title"]),
            id=str(data.get("id", "")),
            status=str(data.get("status", "proposed")),
            owner=str(data.get("owner", "")),
            parent_id=None if parent_id is None else str(parent_id),
            depends_on=[str(t) for t in data.get("depends_on", [])],
        )


@dataclass
class AgentState:
    """Everything a successor agent needs to continue the work.

    All seven sections are required for a faithful handoff; the
    round-trip test fails if any of them is lost or altered.
    """

    objective: str
    decisions: list[Decision] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    assumptions: list[Assumption] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentState:
        if not isinstance(data, dict):
            raise TypeError(f"handoff state must be a dict, got {type(data).__name__}")
        try:
            objective = data["objective"]
        except KeyError:
            raise KeyError("handoff state is missing 'objective'") from None
        return cls(
            objective=str(objective),
            decisions=[Decision.from_dict(d) for d in data.get("decisions", [])],
            evidence=[Evidence.from_dict(e) for e in data.get("evidence", [])],
            open_questions=[str(q) for q in data.get("open_questions", [])],
            next_actions=[str(a) for a in data.get("next_actions", [])],
            assumptions=[Assumption.from_dict(a) for a in data.get("assumptions", [])],
            tasks=[Task.from_dict(t) for t in data.get("tasks", [])],
        )


def validate_state(state: AgentState) -> None:
    """Check the revision graph's referential integrity.

    Raises ValueError on the first violation found. The rules engage
    only when revision features are used (ids, supersession links,
    evidence links), so plain states without ids validate trivially:

    - non-empty ids are unique within decisions, evidence, assumptions;
    - a decision's ``supersedes`` target exists, and supersession
      chains have no cycles;
    - a decision marked ``"superseded"`` has exactly one successor
      (a ``"reversed"`` decision needs none: reversal is terminal,
      and a successor may still supersede it, as in Experiment #003
      task R2, where the remote-format decision supersedes the
      reversed in-person decision);
    - every ``evidence_ids`` entry resolves to an evidence id;
    - an assumption's ``validated_by`` resolves to an evidence id;
    - non-empty task ids are unique; a task's ``parent_id`` resolves
      to a task in the same state, is not the task itself, and parent
      chains have no cycles; every ``depends_on`` entry resolves, is
      not the task itself, and the dependency graph has no cycles.
    """
    decision_ids: set[str] = set()
    for d in state.decisions:
        if d.id:
            if d.id in decision_ids:
                raise ValueError(f"duplicate decision id {d.id!r}")
            decision_ids.add(d.id)
    evidence_ids: set[str] = set()
    for e in state.evidence:
        if e.id:
            if e.id in evidence_ids:
                raise ValueError(f"duplicate evidence id {e.id!r}")
            evidence_ids.add(e.id)
    assumption_ids: set[str] = set()
    for a in state.assumptions:
        if a.id:
            if a.id in assumption_ids:
                raise ValueError(f"duplicate assumption id {a.id!r}")
            assumption_ids.add(a.id)

    by_id = {d.id: d for d in state.decisions if d.id}
    successors: dict[str, list[str]] = {}
    for d in state.decisions:
        for eid in d.evidence_ids:
            if eid not in evidence_ids:
                raise ValueError(
                    f"decision {d.id or d.text!r} references unknown "
                    f"evidence id {eid!r}"
                )
        if d.supersedes is not None:
            if d.supersedes == d.id and d.id:
                raise ValueError(f"decision {d.id!r} supersedes itself")
            target = by_id.get(d.supersedes)
            if target is None:
                raise ValueError(
                    f"decision {d.id or d.text!r} supersedes unknown "
                    f"decision id {d.supersedes!r}"
                )
            successors.setdefault(d.supersedes, []).append(d.id)
    for d in state.decisions:
        if d.status == "superseded":
            found = successors.get(d.id, [])
            if len(found) != 1:
                raise ValueError(
                    f"decision {d.id!r} is marked 'superseded' but has "
                    f"{len(found)} successors; exactly one decision must "
                    "supersede it (or mark it 'reversed' instead)"
                )
    # Supersession cycles would make "current version" undefined.
    for d in state.decisions:
        seen: set[str] = set()
        cur = d.supersedes
        while cur is not None:
            if cur in seen:
                raise ValueError(f"supersession cycle through decision id {cur!r}")
            seen.add(cur)
            nxt = by_id.get(cur)
            cur = nxt.supersedes if nxt is not None else None
    for a in state.assumptions:
        if a.validated_by is not None and a.validated_by not in evidence_ids:
            raise ValueError(
                f"assumption {a.id or a.text!r} validated_by unknown "
                f"evidence id {a.validated_by!r}"
            )

    task_ids: set[str] = set()
    for t in state.tasks:
        if t.id:
            if t.id in task_ids:
                raise ValueError(f"duplicate task id {t.id!r}")
            task_ids.add(t.id)
    by_task_id = {t.id: t for t in state.tasks if t.id}
    for t in state.tasks:
        if t.parent_id is not None:
            if t.id and t.parent_id == t.id:
                raise ValueError(f"task {t.id!r} cannot be its own parent")
            if t.parent_id not in task_ids:
                raise ValueError(
                    f"task {t.id or t.title!r} has unknown parent "
                    f"task id {t.parent_id!r}"
                )
        for dep in t.depends_on:
            if t.id and dep == t.id:
                raise ValueError(f"task {t.id!r} cannot depend on itself")
            if dep not in task_ids:
                raise ValueError(
                    f"task {t.id or t.title!r} depends on unknown task id {dep!r}"
                )
    # Parent cycles would make the subtask tree undefined.
    for t in state.tasks:
        t_seen: set[str] = set()
        t_cur = t.parent_id
        while t_cur is not None:
            if t_cur in t_seen:
                raise ValueError(f"task parent cycle through task id {t_cur!r}")
            t_seen.add(t_cur)
            t_nxt = by_task_id.get(t_cur)
            t_cur = t_nxt.parent_id if t_nxt is not None else None
    # Dependency cycles would leave every task in the cycle blocked.
    for t in state.tasks:
        d_seen: set[str] = set()
        d_stack = list(t.depends_on)
        while d_stack:
            d_cur = d_stack.pop()
            if t.id and d_cur == t.id:
                raise ValueError(f"task dependency cycle through task id {d_cur!r}")
            if d_cur in d_seen:
                continue
            d_seen.add(d_cur)
            d_nxt = by_task_id.get(d_cur)
            if d_nxt is not None:
                d_stack.extend(d_nxt.depends_on)


def _coerce_world(world: World | str) -> World:
    return world if isinstance(world, World) else World(world)


def save_state(
    world: World | str,
    state: AgentState,
    *,
    actor: str = "agent",
    note: str = "handoff save",
    expected_version: int | None = None,
    idempotency_key: str | None = None,
) -> int:
    """Write the agent's work state into WORLD.

    The state is stored under the reserved ``"handoff"`` key; any other
    keys already in the document are preserved. Every save is a judged,
    hash-chained version like any other update.

    The revision graph is validated first (see :func:`validate_state`);
    a malformed graph raises ValueError before anything is proposed,
    so it never becomes a committed snapshot.

    Returns the committed version number.
    """
    validate_state(state)
    w = _coerce_world(world)
    doc = dict(w.state())
    doc[HANDOFF_KEY] = state.to_dict()
    return w.update(
        doc,
        actor=actor,
        note=note,
        expected_version=expected_version,
        idempotency_key=idempotency_key,
    )


def load_state(
    world: World | str,
    *,
    version: int | None = None,
    checkpoint: str | None = None,
) -> AgentState:
    """Load the canonical handoff state a successor agent continues from.

    Accepts a world name, so a fresh agent needs no prior handle:
    ``load_state("research-acme")``. Pass ``version=`` or ``checkpoint=``
    to load a historical handoff instead of the latest.

    Raises KeyError if no handoff state was ever saved.
    """
    w = _coerce_world(world)
    doc = w.state(version=version, checkpoint=checkpoint)
    try:
        raw = doc[HANDOFF_KEY]
    except KeyError:
        raise KeyError(f"world {w.name!r} has no saved handoff state") from None
    return AgentState.from_dict(raw)


def _one_line(text: str, limit: int = 100) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[: limit - 3] + "..."


def project_state(state: AgentState) -> AgentState:
    """Project a full handoff state into a continuation-ready view.

    Pure function; the input is not mutated. Experiment #003 measured
    full state bundles at 2.7x to 3.3x the words of summaries for
    preservation that was equal on most metrics; this projection is
    the opt-in smaller bundle. The rules are fixed and conservative:

    - decisions marked ``"accepted"`` or ``"proposed"`` are kept in
      full; ``"superseded"`` and ``"reversed"`` decisions are reduced
      to compact entries that keep ``id``, ``status``, the
      ``supersedes`` link, and a one-line text (rationale and evidence
      links are dropped from the compact entry);
    - assumptions marked ``"active"``, ``"validated"``, or ``"stale"``
      are kept in full; ``"invalidated"`` assumptions are compacted
      the same way;
    - evidence is kept when an included full decision references it
      in ``evidence_ids``, when an included full assumption names it
      in ``validated_by``, or when it has no id (anonymous evidence
      cannot be reference-counted, so it is never silently dropped);
    - tasks marked ``"done"`` or ``"dropped"`` are compacted the
      same way (one-line title; ``id``, ``status``, ``owner``,
      ``parent_id``, and ``depends_on`` are kept); all other tasks
      are kept in full;
    - ``objective``, ``open_questions``, and ``next_actions`` pass
      through unchanged.

    A superseded or invalidated item therefore never appears as
    current guidance: it is present only as a compact, explicitly
    status-marked entry. The projection is a reading view, not a
    state to save back (compacted entries intentionally fail
    :func:`validate_state`'s evidence-link rule).
    """
    from copy import deepcopy

    decisions: list[Decision] = []
    referenced: set[str] = set()
    for d in state.decisions:
        if d.status in ("accepted", "proposed"):
            decisions.append(deepcopy(d))
            referenced.update(d.evidence_ids)
        else:
            decisions.append(
                Decision(
                    text=_one_line(d.text),
                    id=d.id,
                    status=d.status,
                    supersedes=d.supersedes,
                )
            )
    assumptions: list[Assumption] = []
    for a in state.assumptions:
        if a.status == "invalidated":
            assumptions.append(
                Assumption(
                    text=_one_line(a.text),
                    id=a.id,
                    confidence=a.confidence,
                    status=a.status,
                    validated_by=a.validated_by,
                )
            )
        else:
            assumptions.append(deepcopy(a))
            if a.validated_by:
                referenced.add(a.validated_by)
    evidence = [deepcopy(e) for e in state.evidence if not e.id or e.id in referenced]
    tasks: list[Task] = []
    for t in state.tasks:
        if t.status in ("done", "dropped"):
            tasks.append(
                Task(
                    title=_one_line(t.title),
                    id=t.id,
                    status=t.status,
                    owner=t.owner,
                    parent_id=t.parent_id,
                    depends_on=list(t.depends_on),
                )
            )
        else:
            tasks.append(deepcopy(t))
    return AgentState(
        objective=state.objective,
        decisions=decisions,
        evidence=evidence,
        open_questions=list(state.open_questions),
        next_actions=list(state.next_actions),
        assumptions=assumptions,
        tasks=tasks,
    )


def revision_chain(world: World | str, decision_id: str) -> list[dict[str, Any]]:
    """Derive one decision's revision history from committed snapshots.

    Walks committed versions oldest to newest (REJECTED rows are
    skipped: they never entered the timeline), extracts the decision
    with ``decision_id`` from each snapshot's handoff section, and
    emits one entry per snapshot where the decision's text, status,
    rationale, supersession link, or evidence links changed. The first
    entry is the decision's first appearance. Each entry carries
    ``seq``, ``timestamp``, ``actor``, ``note``, ``status``, ``text``,
    ``rationale``, ``supersedes``, and ``evidence_ids``: enough to
    answer what the original decision was, what changed, who changed
    it (actor is self-asserted, as everywhere in WORLD), why, on what
    evidence, and which entry is authoritative now (the last one, in
    the latest committed snapshot).

    A snapshot whose handoff section lacks the decision contributes no
    entry: removal is expressed by status (``"superseded"`` or
    ``"reversed"``), not by silently dropping the decision.

    Raises KeyError if no committed snapshot contains the decision.
    """
    w = _coerce_world(world)
    entries: list[dict[str, Any]] = []
    last_key: tuple[Any, ...] | None = None
    for row in w.history():
        if row["status"] != "COMMITTED":
            continue
        doc = w.state(version=int(row["seq"]))
        raw = doc.get(HANDOFF_KEY)
        if not isinstance(raw, dict):
            continue
        match: dict[str, Any] | None = None
        for d in raw.get("decisions", []):
            if isinstance(d, dict) and str(d.get("id", "")) == decision_id:
                match = d
                break
        if match is None:
            continue
        entry = {
            "seq": int(row["seq"]),
            "timestamp": row["timestamp"],
            "actor": row["actor"],
            "note": row["note"],
            "status": str(match.get("status", "accepted")),
            "text": str(match.get("text", "")),
            "rationale": str(match.get("rationale", "")),
            "supersedes": match.get("supersedes"),
            "evidence_ids": [str(e) for e in match.get("evidence_ids", [])],
        }
        key = (
            entry["status"],
            entry["text"],
            entry["rationale"],
            entry["supersedes"],
            tuple(entry["evidence_ids"]),
        )
        if key != last_key:
            entries.append(entry)
            last_key = key
    if not entries:
        raise KeyError(f"no decision with id {decision_id!r} in world {w.name!r}")
    return entries


def packet_from_state(
    state: AgentState,
    *,
    state_version: int,
    world_name: str = "",
    rejected: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the provider-neutral continuation packet for a handoff state.

    Pure function; the input is not mutated. The packet carries the
    eleven fields Prompt 4 names a successor agent needs:
    objective, completed work, remaining tasks, decisions with
    rationale, evidence, unresolved questions, artifacts,
    dependencies, known errors, state version, and next action,
    plus ``assumptions``: Experiment #003 found assumption
    confidence and fact-versus-assumption status is exactly what
    free-text handoffs lose, so a continuation bundle that dropped
    them would repeat that loss.

    Two fields are derived views, not stored entities:

    - ``artifacts`` lists references to external artifacts as recorded
      in evidence ``source`` strings, deduplicated in first-seen order.
      WORLD stores the reference, not the artifact; there is no typed
      Artifact entity (Prompt 3 deferred it, see
      docs/DATA_MODEL_PROPOSAL.md section 8).
    - ``known_errors`` collects blocked tasks, invalidated
      assumptions, and REJECTED proposals (``rejected`` rows from
      ``World.history``, each with ``seq``, ``actor``, ``note``). A
      packet built from a bare state has no verdict log, so its known
      errors carry only the first two kinds.

    ``next_action`` is the first ``next_actions`` entry when one
    exists, else the title of the first remaining task in listed
    order, else None. The packet is a reading view, not a state to
    save back: it is built from the state, never written into it.
    """
    completed: list[dict[str, Any]] = [
        {"kind": "task", "id": t.id, "title": t.title, "owner": t.owner}
        for t in state.tasks
        if t.status == "done"
    ]
    completed.extend(
        {
            "kind": "decision",
            "id": d.id,
            "text": d.text,
            "rationale": d.rationale,
        }
        for d in state.decisions
        if d.status == "accepted"
    )
    remaining = [
        {
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "owner": t.owner,
            "parent_id": t.parent_id,
            "depends_on": list(t.depends_on),
        }
        for t in state.tasks
        if t.status in ("proposed", "in_progress", "blocked")
    ]
    seen_sources: dict[str, list[str]] = {}
    for e in state.evidence:
        if e.source:
            seen_sources.setdefault(e.source, []).append(e.id)
    artifacts = [
        {"reference": source, "evidence_ids": ids}
        for source, ids in seen_sources.items()
    ]
    dependencies: dict[str, Any] = {
        "tasks": {
            t.id: {"parent_id": t.parent_id, "depends_on": list(t.depends_on)}
            for t in state.tasks
            if t.id and (t.parent_id is not None or t.depends_on)
        },
        "decisions": {
            d.id: {"supersedes": d.supersedes}
            for d in state.decisions
            if d.id and d.supersedes is not None
        },
    }
    known_errors: list[dict[str, Any]] = [
        {"kind": "blocked_task", "id": t.id, "title": t.title}
        for t in state.tasks
        if t.status == "blocked"
    ]
    known_errors.extend(
        {"kind": "invalidated_assumption", "id": a.id, "text": a.text}
        for a in state.assumptions
        if a.status == "invalidated"
    )
    for row in rejected or []:
        known_errors.append(
            {
                "kind": "rejected_proposal",
                "seq": int(row["seq"]),
                "actor": str(row.get("actor", "")),
                "note": str(row.get("note", "")),
            }
        )
    if state.next_actions:
        next_action: str | None = state.next_actions[0]
    elif remaining:
        next_action = str(remaining[0]["title"])
    else:
        next_action = None
    return {
        "format": PACKET_FORMAT,
        "world": world_name,
        "state_version": int(state_version),
        "objective": state.objective,
        "completed_work": completed,
        "remaining_tasks": remaining,
        "decisions": [d.to_dict() for d in state.decisions],
        "assumptions": [a.to_dict() for a in state.assumptions],
        "evidence": [e.to_dict() for e in state.evidence],
        "unresolved_questions": list(state.open_questions),
        "artifacts": artifacts,
        "dependencies": dependencies,
        "known_errors": known_errors,
        "next_action": next_action,
    }


def continuation_packet(
    world: World | str,
    *,
    version: int | None = None,
    projected: bool = False,
) -> dict[str, Any]:
    """Build the continuation packet for a world's handoff state.

    Accepts a world name, so a fresh agent needs no prior handle.
    The packet is pinned to the committed version it was built from:
    ``version=`` loads that version (default: latest committed), and
    ``state_version`` in the packet names it, so a successor that
    re-reads at that version reproduces the same packet. REJECTED
    proposals at or before that version are carried in
    ``known_errors``. With ``projected=True`` the packet is built
    from the ``project_state`` view (compacted finished items)
    instead of the full state.

    Raises KeyError if no handoff state was ever saved.
    """
    w = _coerce_world(world)
    state = load_state(w, version=version)
    state_version = version if version is not None else w.version
    if projected:
        state = project_state(state)
    rejected = [
        row
        for row in w.history()
        if row["status"] == "REJECTED" and int(row["seq"]) <= state_version
    ]
    return packet_from_state(
        state,
        state_version=state_version,
        world_name=w.name,
        rejected=rejected,
    )


def render_packet_text(packet: dict[str, Any]) -> str:
    """Render a continuation packet as deterministic plain text.

    Fixed section order, one line per item, no timestamps and no
    provider-specific formatting, so the same packet always renders
    to the same text and any agent can read it. This is the bundle
    the Prompt 4 harness hands a successor agent; the JSON packet is
    the same content in structured form.
    """
    lines = [
        f"WORLD continuation packet ({packet['format']})",
        f"World: {packet['world']} (state version {packet['state_version']})",
        f"Objective: {packet['objective']}",
        "Completed work:",
    ]
    if not packet["completed_work"]:
        lines.append("  (none)")
    for item in packet["completed_work"]:
        if item["kind"] == "task":
            lines.append(
                f"  - [task {item['id']}, done, owner {item['owner']}] {item['title']}"
            )
        else:
            lines.append(
                f"  - [decision {item['id']}, accepted] {item['text']} "
                f"-- why: {item['rationale']}"
            )
    lines.append("Remaining tasks:")
    if not packet["remaining_tasks"]:
        lines.append("  (none)")
    for t in packet["remaining_tasks"]:
        deps = f" (depends on: {', '.join(t['depends_on'])})" if t["depends_on"] else ""
        lines.append(
            f"  - [{t['id']}, {t['status']}, owner {t['owner']}] {t['title']}{deps}"
        )
    lines.append("Decisions:")
    if not packet["decisions"]:
        lines.append("  (none)")
    for d in packet["decisions"]:
        ev = f" (evidence: {', '.join(d['evidence_ids'])})" if d["evidence_ids"] else ""
        lines.append(
            f"  - [{d['id']}, {d['status']}] {d['text']} -- why: {d['rationale']}{ev}"
        )
    lines.append("Evidence:")
    if not packet["evidence"]:
        lines.append("  (none)")
    for e in packet["evidence"]:
        lines.append(
            f"  - [{e['id']}, {e['kind']}] {e['claim']} (source: {e['source']})"
        )
    lines.append("Assumptions:")
    if not packet["assumptions"]:
        lines.append("  (none)")
    for a in packet["assumptions"]:
        validated = (
            f" (validated by: {a['validated_by']})" if a.get("validated_by") else ""
        )
        lines.append(
            f"  - [{a['id']}, confidence {a['confidence']}, {a['status']}] "
            f"{a['text']}{validated}"
        )
    lines.append("Unresolved questions:")
    if not packet["unresolved_questions"]:
        lines.append("  (none)")
    for q in packet["unresolved_questions"]:
        lines.append(f"  - {q}")
    lines.append("Artifacts (references only; WORLD stores references, not the files):")
    if not packet["artifacts"]:
        lines.append("  (none)")
    for a in packet["artifacts"]:
        lines.append(f"  - {a['reference']} (evidence: {', '.join(a['evidence_ids'])})")
    lines.append("Dependencies:")
    if not packet["dependencies"]["tasks"] and not packet["dependencies"]["decisions"]:
        lines.append("  (none)")
    for tid, link in packet["dependencies"]["tasks"].items():
        if link["parent_id"] is not None:
            lines.append(f"  - task {tid} is a subtask of {link['parent_id']}")
        for dep in link["depends_on"]:
            lines.append(f"  - task {tid} depends on {dep}")
    for did, link in packet["dependencies"]["decisions"].items():
        lines.append(f"  - decision {did} supersedes {link['supersedes']}")
    lines.append("Known errors:")
    if not packet["known_errors"]:
        lines.append("  (none)")
    for err in packet["known_errors"]:
        if err["kind"] == "blocked_task":
            lines.append(f"  - [blocked task {err['id']}] {err['title']}")
        elif err["kind"] == "invalidated_assumption":
            lines.append(f"  - [invalidated assumption {err['id']}] {err['text']}")
        else:
            lines.append(
                f"  - [rejected proposal seq {err['seq']} by {err['actor']}] "
                f"{err['note']}"
            )
    lines.append(f"Next action: {packet['next_action'] or 'none recorded'}")
    return "\n".join(lines) + "\n"
