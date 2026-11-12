"""Agent handoff interface: the first agent-facing API on the WORLD primitive.

Two operations, stdlib only, no LLM provider dependency:

    save_state(world, state, ...) -> int   # returns the committed version
    load_state(world, ...) -> AgentState

The work state is a structured document with six sections: objective,
decisions, assumptions, evidence, open questions, next actions. It is
stored under the reserved ``"handoff"`` key of the world's JSON
document. A fresh agent needs nothing but the world name to recover
the canonical state:

    state = load_state("research-acme")   # objective, decisions, ...

Decisions, assumptions, and evidence carry the research state model's
identity and provenance fields (``docs/state-model.md``): stable ids,
lifecycle status, supersession links, confidence, and evidence links.
``save_state`` validates the revision graph's referential integrity
before proposing, and :func:`revision_chain` derives one decision's
revision history from the committed snapshots.
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
    "load_state",
    "project_state",
    "revision_chain",
    "save_state",
    "validate_state",
]

#: Reserved top-level key of the world document holding the handoff state.
HANDOFF_KEY = "handoff"

#: Lifecycle states of a decision (docs/state-model.md).
DECISION_STATUSES = ("proposed", "accepted", "superseded", "reversed")
#: Confidence levels of an assumption (docs/state-model.md).
ASSUMPTION_CONFIDENCES = ("low", "medium", "high")
#: Lifecycle states of an assumption (docs/state-model.md).
ASSUMPTION_STATUSES = ("active", "validated", "invalidated", "stale")


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
class AgentState:
    """Everything a successor agent needs to continue the work.

    All six sections are required for a faithful handoff; the round-trip
    test fails if any of them is lost or altered.
    """

    objective: str
    decisions: list[Decision] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    assumptions: list[Assumption] = field(default_factory=list)

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
    - an assumption's ``validated_by`` resolves to an evidence id.
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
    return AgentState(
        objective=state.objective,
        decisions=decisions,
        evidence=evidence,
        open_questions=list(state.open_questions),
        next_actions=list(state.next_actions),
        assumptions=assumptions,
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
