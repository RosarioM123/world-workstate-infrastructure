"""Provenance and verification queries over committed handoff state.

Derived views only. Every answer is computed from the committed
snapshots and the verdict log (``World.history`` plus
``World.state(version=)``), so nothing here is a second source of
truth and no stored format changes. In particular this module does
NOT add per-entity provenance fields to the stored entities: Prompt
3 deferred those (docs/DATA_MODEL_PROPOSAL.md section 8.5) and they
still wait for Rosario's review.

Two limits are load-bearing and are stated in the answers, not
hidden:

- ``actor`` is self-asserted everywhere in WORLD, so an
  introduced-by answer names the actor string that recorded the
  change, never a verified human. Human approval is therefore
  reported as unknown (``human_approved`` is None with a reason),
  never inferred from an actor string.
- Evidence ``kind`` is a free-text field (the enum question in
  proposal section 8.4 is still open), so
  :func:`classify_evidence` is a documented heuristic over that
  string, with an ``unclassified`` bucket for anything outside its
  mapping table. It classifies; it does not enforce.

The five Prompt 5 queries map to functions:

- why is this decision in the project: :func:`explain_decision`
- what evidence supports this assumption: :func:`evidence_for_assumption`
- what changed since a previous version: :func:`state_diff`
- which decisions depend on this source or evidence item:
  :func:`decisions_for_evidence`, :func:`decisions_for_source`
- which conclusions are no longer supported:
  :func:`unsupported_conclusions`

:func:`reconstruct_provenance` is the shared derivation underneath:
per entity id, the version, actor, timestamp, and note that first
introduced it, plus every later version where its content changed.
"""

from __future__ import annotations

import json
from typing import Any

from .core import World
from .handoff import (
    AgentState,
    Assumption,
    Decision,
    Evidence,
    load_state,
)

__all__ = [
    "classify_evidence",
    "decisions_for_evidence",
    "decisions_for_source",
    "evidence_for_assumption",
    "explain_decision",
    "reconstruct_provenance",
    "state_diff",
    "unsupported_conclusions",
]

#: Evidence kinds treated as records of the world rather than
#: readings of it. Lowercased, spaces and hyphens normalized to
#: underscores before lookup; see :func:`classify_evidence`.
SOURCE_FACT_KINDS = frozenset(
    {
        "data",
        "dataset",
        "document",
        "filing",
        "measurement",
        "observation",
        "quote",
        "record",
        "source",
        "transcript",
    }
)

#: Evidence kinds treated as a model or analyst reading rather than
#: a record of the world. Same normalization as above.
MODEL_INTERPRETATION_KINDS = frozenset(
    {
        "analysis",
        "estimate",
        "hypothesis",
        "inference",
        "interpretation",
        "judgment",
        "model_output",
        "opinion",
        "summary",
    }
)

#: Decision statuses that count as live conclusions for support checks.
_LIVE_DECISION_STATUSES = ("accepted", "proposed")

_HUMAN_APPROVAL_NOTE = (
    "not recorded: WORLD stores no approval marker, and actor is "
    "self-asserted, so no actor string can prove a human approved "
    "this decision"
)


def _coerce_world(world: World | str) -> World:
    return world if isinstance(world, World) else World(world)


def _snapshots(
    w: World, *, version: int | None = None
) -> list[tuple[int, dict[str, Any], AgentState]]:
    """Committed handoff snapshots oldest to newest, up to ``version``.

    Each entry is ``(seq, history row, state)``. Snapshots without a
    handoff section are skipped: provenance is about handoff
    entities, and a world can hold other keys. REJECTED rows never
    entered the timeline and are skipped with them.
    """
    out: list[tuple[int, dict[str, Any], AgentState]] = []
    for row in w.history():
        if row["status"] != "COMMITTED":
            continue
        seq = int(row["seq"])
        if version is not None and seq > version:
            continue
        doc = w.state(version=seq)
        raw = doc.get("handoff")
        if not isinstance(raw, dict):
            continue
        out.append((seq, row, AgentState.from_dict(raw)))
    return out


def _entities_by_section(
    state: AgentState,
) -> dict[str, dict[str, dict[str, Any]]]:
    """Entity dicts per section, keyed by id; id-less entities skipped."""
    return {
        "decisions": {d.id: d.to_dict() for d in state.decisions if d.id},
        "assumptions": {a.id: a.to_dict() for a in state.assumptions if a.id},
        "evidence": {e.id: e.to_dict() for e in state.evidence if e.id},
        "tasks": {t.id: t.to_dict() for t in state.tasks if t.id},
    }


def reconstruct_provenance(
    world: World | str, *, version: int | None = None
) -> dict[str, dict[str, dict[str, Any]]]:
    """Derive per-entity provenance from the committed snapshots.

    Returns one mapping per section (``decisions``, ``assumptions``,
    ``evidence``, ``tasks``). Each entity id maps to a record with
    ``introduced_seq``, ``introduced_by`` (actor string),
    ``introduced_at`` (timestamp), ``introduced_note``, and
    ``changed_seqs``: the later committed versions where the
    entity's content differed from the previous snapshot. Entities
    without an id cannot be tracked across snapshots and are absent.
    With ``version=``, the derivation stops at that committed
    version, so a pinned version reproduces its own provenance.
    """
    w = _coerce_world(world)
    provenance: dict[str, dict[str, dict[str, Any]]] = {
        "decisions": {},
        "assumptions": {},
        "evidence": {},
        "tasks": {},
    }
    previous: dict[str, dict[str, dict[str, Any]]] = {
        "decisions": {},
        "assumptions": {},
        "evidence": {},
        "tasks": {},
    }
    for seq, row, state in _snapshots(w, version=version):
        current = _entities_by_section(state)
        for section, entities in current.items():
            for entity_id, content in entities.items():
                record = provenance[section].get(entity_id)
                if record is None:
                    provenance[section][entity_id] = {
                        "introduced_seq": seq,
                        "introduced_by": row["actor"],
                        "introduced_at": row["timestamp"],
                        "introduced_note": row["note"],
                        "changed_seqs": [],
                    }
                elif previous[section].get(entity_id) != content:
                    record["changed_seqs"].append(seq)
        previous = current
    return provenance


def classify_evidence(evidence: Evidence) -> str:
    """Classify one evidence item as source fact or interpretation.

    A heuristic over the free-text ``kind`` string, normalized to
    lowercase with spaces and hyphens as underscores. Kinds in
    ``SOURCE_FACT_KINDS`` return ``"source_fact"``; kinds in
    ``MODEL_INTERPRETATION_KINDS`` return ``"model_interpretation"``;
    anything else, including an empty kind, returns
    ``"unclassified"``. This classifies what is recorded; it does
    not enforce a kind enum, which is Rosario's open decision
    (proposal section 8.4).
    """
    kind = evidence.kind.strip().lower().replace(" ", "_").replace("-", "_")
    if kind in SOURCE_FACT_KINDS:
        return "source_fact"
    if kind in MODEL_INTERPRETATION_KINDS:
        return "model_interpretation"
    return "unclassified"


def _support_status(state: AgentState, decision: Decision) -> tuple[str, str]:
    """Support status of one decision in a state.

    Returns ``(status, detail)`` where status is one of
    ``"supported"``, ``"no_evidence"``, ``"evidence_missing"``,
    ``"weakened_by_invalidated_assumption"``. A decision is weakened
    when evidence it cites validated an assumption that is now
    invalidated: the evidence has not changed, but the conclusion
    built on it has lost its backing. Non-live decisions
    (superseded, reversed) are not judged here; callers skip them.
    """
    if not decision.evidence_ids:
        return "no_evidence", "accepted decision cites no evidence"
    evidence_ids = {e.id for e in state.evidence if e.id}
    missing = [eid for eid in decision.evidence_ids if eid not in evidence_ids]
    if missing:
        return (
            "evidence_missing",
            "cited evidence no longer in state: " + ", ".join(missing),
        )
    invalidated = {
        a.validated_by
        for a in state.assumptions
        if a.status == "invalidated" and a.validated_by
    }
    weakened = [eid for eid in decision.evidence_ids if eid in invalidated]
    if weakened:
        return (
            "weakened_by_invalidated_assumption",
            "cited evidence validated an assumption now invalidated: "
            + ", ".join(weakened),
        )
    return "supported", "backed by evidence present in the current state"


def explain_decision(
    world: World | str, decision_id: str, *, version: int | None = None
) -> dict[str, Any]:
    """Why is this decision in the project, and is it still supported?

    Returns the decision's current fields at ``version`` (default:
    latest committed), the provenance record that introduced it, how
    many revisions it has had, the decisions it supersedes and the
    one that supersedes it, its backing evidence with claims,
    sources, and classifications, and its support status.
    ``human_approved`` is always None: WORLD records no approval
    marker, and the note says so. Raises KeyError for an unknown
    decision id.
    """
    w = _coerce_world(world)
    state = load_state(w, version=version)
    decision: Decision | None = None
    for d in state.decisions:
        if d.id == decision_id:
            decision = d
            break
    if decision is None:
        raise KeyError(f"no decision with id {decision_id!r} in world {w.name!r}")
    provenance = reconstruct_provenance(w, version=version)
    introduced = provenance["decisions"].get(decision_id)
    if introduced is None:
        raise KeyError(f"no provenance for decision id {decision_id!r}")
    by_id = {e.id: e for e in state.evidence if e.id}
    evidence = [
        {
            "id": e.id,
            "claim": e.claim,
            "source": e.source,
            "kind": e.kind,
            "classification": classify_evidence(e),
        }
        for eid in decision.evidence_ids
        if (e := by_id.get(eid)) is not None
    ]
    predecessors: list[str] = []
    cur = decision.supersedes
    seen: set[str] = set()
    while cur is not None and cur not in seen:
        seen.add(cur)
        predecessors.append(cur)
        nxt = next((d for d in state.decisions if d.id == cur), None)
        cur = nxt.supersedes if nxt is not None else None
    successor = next(
        (d.id for d in state.decisions if d.supersedes == decision_id), None
    )
    status, detail = _support_status(state, decision)
    return {
        "id": decision.id,
        "text": decision.text,
        "rationale": decision.rationale,
        "status": decision.status,
        "supersedes": decision.supersedes,
        "evidence_ids": list(decision.evidence_ids),
        "evidence": evidence,
        "introduced": dict(introduced),
        "revision_count": 1 + len(introduced["changed_seqs"]),
        "supersession_chain": predecessors,
        "superseded_by": successor,
        "support_status": status,
        "support_detail": detail,
        "human_approved": None,
        "human_approval_note": _HUMAN_APPROVAL_NOTE,
    }


def evidence_for_assumption(
    world: World | str, assumption_id: str, *, version: int | None = None
) -> dict[str, Any]:
    """What evidence supports this assumption, and when was it recorded?

    Returns the assumption, its validating evidence (or None when
    the assumption names none), and the provenance record of the
    version where the assumption first carried that validation link.
    Raises KeyError for an unknown assumption id.
    """
    w = _coerce_world(world)
    state = load_state(w, version=version)
    assumption: Assumption | None = None
    for a in state.assumptions:
        if a.id == assumption_id:
            assumption = a
            break
    if assumption is None:
        raise KeyError(f"no assumption with id {assumption_id!r} in world {w.name!r}")
    evidence: dict[str, Any] | None = None
    validated_at: dict[str, Any] | None = None
    if assumption.validated_by:
        by_id = {e.id: e for e in state.evidence if e.id}
        found = by_id.get(assumption.validated_by)
        if found is not None:
            evidence = {
                "id": found.id,
                "claim": found.claim,
                "source": found.source,
                "kind": found.kind,
                "classification": classify_evidence(found),
            }
        for seq, row, snap in _snapshots(w, version=version):
            match = next((a for a in snap.assumptions if a.id == assumption_id), None)
            if match is not None and match.validated_by == assumption.validated_by:
                validated_at = {
                    "introduced_seq": seq,
                    "introduced_by": row["actor"],
                    "introduced_at": row["timestamp"],
                    "introduced_note": row["note"],
                    "changed_seqs": [],
                }
                break
    return {
        "assumption": assumption.to_dict(),
        "evidence": evidence,
        "validated_at": validated_at,
    }


def decisions_for_evidence(
    world: World | str, evidence_id: str, *, version: int | None = None
) -> list[dict[str, Any]]:
    """Which decisions cite this evidence item, at ``version``.

    The reverse index of ``Decision.evidence_ids``: every decision
    in the state at that version whose evidence links include the
    id, in listed order. An empty list means nothing depends on it.
    """
    w = _coerce_world(world)
    state = load_state(w, version=version)
    return [d.to_dict() for d in state.decisions if evidence_id in d.evidence_ids]


def decisions_for_source(
    world: World | str, source: str, *, version: int | None = None
) -> list[dict[str, Any]]:
    """Which decisions depend on evidence from this source string.

    A decision depends on a source when any evidence item it cites
    has exactly that ``source`` string. Matching is exact, not
    substring: two sources that merely mention each other are
    different sources.
    """
    w = _coerce_world(world)
    state = load_state(w, version=version)
    linked = {e.id for e in state.evidence if e.id and e.source == source}
    return [
        d.to_dict()
        for d in state.decisions
        if any(eid in linked for eid in d.evidence_ids)
    ]


def state_diff(
    world: World | str, from_version: int, to_version: int
) -> dict[str, Any]:
    """What changed in the handoff state between two committed versions.

    Returns, per section (``decisions``, ``assumptions``,
    ``evidence``, ``tasks``), the entities added, removed, and
    changed between the two versions, keyed by id, plus the
    committed versions in between with their actor, timestamp, and
    note. A changed entry carries the before and after dicts.
    Id-less entities are compared by content. Raises ValueError
    when ``from_version`` is after ``to_version``, and KeyError
    for an unknown or non-committed version.
    """
    if from_version > to_version:
        raise ValueError(
            f"from_version {from_version} is after to_version {to_version}"
        )
    w = _coerce_world(world)
    before = load_state(w, version=from_version)
    after = load_state(w, version=to_version)
    versions = [
        {
            "seq": int(row["seq"]),
            "actor": row["actor"],
            "timestamp": row["timestamp"],
            "note": row["note"],
        }
        for row in w.history()
        if row["status"] == "COMMITTED" and from_version < int(row["seq"]) <= to_version
    ]
    diff: dict[str, Any] = {
        "from_version": from_version,
        "to_version": to_version,
        "versions": versions,
    }
    sections = (
        ("decisions", before.decisions, after.decisions),
        ("assumptions", before.assumptions, after.assumptions),
        ("evidence", before.evidence, after.evidence),
        ("tasks", before.tasks, after.tasks),
    )
    for name, before_items, after_items in sections:
        before_by_id = {i.id: i.to_dict() for i in before_items if i.id}
        after_by_id = {i.id: i.to_dict() for i in after_items if i.id}
        added = [after_by_id[i] for i in after_by_id if i not in before_by_id]
        removed = [before_by_id[i] for i in before_by_id if i not in after_by_id]
        changed = [
            {
                "id": i,
                "before": before_by_id[i],
                "after": after_by_id[i],
            }
            for i in after_by_id
            if i in before_by_id and before_by_id[i] != after_by_id[i]
        ]
        before_anon = sorted(
            json.dumps(i.to_dict(), sort_keys=True) for i in before_items if not i.id
        )
        after_anon = sorted(
            json.dumps(i.to_dict(), sort_keys=True) for i in after_items if not i.id
        )
        for content in after_anon:
            if content not in before_anon:
                added.append(json.loads(content))
                before_anon.append(content)
        for content in before_anon:
            if content not in after_anon:
                removed.append(json.loads(content))
        diff[name] = {"added": added, "removed": removed, "changed": changed}
    return diff


def unsupported_conclusions(
    world: World | str, *, version: int | None = None
) -> list[dict[str, Any]]:
    """Which live conclusions are no longer supported, at ``version``.

    One row per accepted or proposed decision whose support fails:
    ``no_evidence`` (it cites nothing), ``evidence_missing`` (a
    cited evidence id is not in the current state), or
    ``weakened_by_invalidated_assumption`` (cited evidence validated
    an assumption that is now invalidated). Superseded and reversed
    decisions are not live conclusions and are skipped. An empty
    list means every live decision is backed by evidence present in
    the state.
    """
    w = _coerce_world(world)
    state = load_state(w, version=version)
    out: list[dict[str, Any]] = []
    for d in state.decisions:
        if d.status not in _LIVE_DECISION_STATUSES:
            continue
        status, detail = _support_status(state, d)
        if status != "supported":
            out.append(
                {
                    "decision_id": d.id,
                    "text": d.text,
                    "kind": status,
                    "detail": detail,
                }
            )
    return out
