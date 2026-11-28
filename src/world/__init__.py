"""WORLD v0.1: a minimal, verifiable work-state primitive.

A :class:`~world.core.World` is a named, durable unit of work: an opaque JSON
document whose every change is judged by optional invariants, with every
verdict (COMMITTED or REJECTED) appended to a hash-chained log.
"""

from . import ed25519, fieldcrypto
from .core import ConflictError, InvariantViolation, RedactedError, World
from .handoff import (
    AgentState,
    Decision,
    Evidence,
    Task,
    continuation_packet,
    load_state,
    packet_from_state,
    render_packet_text,
    save_state,
)
from .provenance import (
    classify_evidence,
    decisions_for_evidence,
    decisions_for_source,
    evidence_for_assumption,
    explain_decision,
    reconstruct_provenance,
    state_diff,
    unsupported_conclusions,
)

__version__ = "0.1.0"

__all__ = [
    "AgentState",
    "ConflictError",
    "Decision",
    "Evidence",
    "InvariantViolation",
    "RedactedError",
    "Task",
    "World",
    "__version__",
    "classify_evidence",
    "continuation_packet",
    "decisions_for_evidence",
    "decisions_for_source",
    "ed25519",
    "evidence_for_assumption",
    "explain_decision",
    "fieldcrypto",
    "load_state",
    "packet_from_state",
    "reconstruct_provenance",
    "render_packet_text",
    "save_state",
    "state_diff",
    "unsupported_conclusions",
]
