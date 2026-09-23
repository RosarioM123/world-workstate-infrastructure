"""Agent handoff interface: the first agent-facing API on the WORLD primitive.

Two operations, stdlib only, no LLM provider dependency:

    save_state(world, state, ...) -> int   # returns the committed version
    load_state(world, ...) -> AgentState

The work state is a structured document with five sections — objective,
decisions, evidence, open questions, next actions — stored under the
reserved ``"handoff"`` key of the world's JSON document. A fresh agent
needs nothing but the world name to recover the canonical state:

    state = load_state("research-acme")   # objective, decisions, ...
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .core import World

__all__ = [
    "AgentState",
    "Decision",
    "Evidence",
    "load_state",
    "save_state",
]

#: Reserved top-level key of the world document holding the handoff state.
HANDOFF_KEY = "handoff"


@dataclass
class Decision:
    """A decision the agent made, with the reasoning behind it."""

    text: str
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Decision:
        if not isinstance(data, dict):
            raise TypeError(f"decision must be a dict, got {type(data).__name__}")
        return cls(text=str(data["text"]), rationale=str(data.get("rationale", "")))


@dataclass
class Evidence:
    """A finding backing the work, with where it came from."""

    claim: str
    source: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Evidence:
        if not isinstance(data, dict):
            raise TypeError(f"evidence must be a dict, got {type(data).__name__}")
        return cls(claim=str(data["claim"]), source=str(data.get("source", "")))


@dataclass
class AgentState:
    """Everything a successor agent needs to continue the work.

    All five sections are required for a faithful handoff; the round-trip
    test fails if any of them is lost or altered.
    """

    objective: str
    decisions: list[Decision] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)

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

    Returns the committed version number.
    """
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
