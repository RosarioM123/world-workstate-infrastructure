"""Prompt 3 F6: project_state builds the continuation-ready view.

Completeness is the safety property: every live item (accepted or
proposed decision, non-invalidated assumption) survives intact, and
no superseded, reversed, or invalidated item is presented as current.
"""

import json

from world.handoff import (
    AgentState,
    Assumption,
    Decision,
    Evidence,
    project_state,
)


def _state() -> AgentState:
    long_rationale = (
        "This rationale is deliberately verbose because real handoff "
        "rationales are verbose, and the words in dead decisions are "
        "exactly the words a successor should not have to pay for."
    )
    return AgentState(
        objective="Continue the storage engine evaluation.",
        decisions=[
            Decision(
                text="Self-host Postgres 15",
                rationale=long_rationale,
                id="D1",
                status="superseded",
            ),
            Decision(
                text="Use managed Postgres",
                rationale="Failover drill took 22 minutes.",
                id="D2",
                status="accepted",
                supersedes="D1",
                evidence_ids=["E1"],
            ),
            Decision(
                text="Pin the connection budget at 40",
                rationale="Load test saturation.",
                id="D3",
                status="proposed",
                evidence_ids=["E2"],
            ),
            Decision(
                text="Adopt the vendor SDK",
                rationale=long_rationale,
                id="D4",
                status="reversed",
            ),
        ],
        evidence=[
            Evidence(claim="Drill timing", source="drill", id="E1", kind="measurement"),
            Evidence(claim="Load test", source="bench", id="E2", kind="measurement"),
            Evidence(
                claim="Unreferenced market survey",
                source="survey",
                id="E3",
                kind="document",
            ),
        ],
        open_questions=["Replication support?"],
        next_actions=["Draft the runbook"],
        assumptions=[
            Assumption(
                text="Traffic stays under 2k rps",
                id="A1",
                confidence="medium",
                status="active",
            ),
            Assumption(
                text="A second region is required this year, per the "
                "board deck and the capacity plan that legal reviewed",
                id="A2",
                confidence="low",
                status="invalidated",
            ),
            Assumption(
                text="Vendor region supports PITR",
                id="A3",
                confidence="high",
                status="validated",
                validated_by="E1",
            ),
        ],
    )


def _words(state: AgentState) -> int:
    return len(json.dumps(state.to_dict()).split())


def test_projection_keeps_every_live_item_intact():
    s = _state()
    p = project_state(s)
    by_id = {d.id: d for d in p.decisions}
    assert by_id["D2"] == s.decisions[1]  # accepted, full fidelity
    assert by_id["D3"] == s.decisions[2]  # proposed, full fidelity
    a_by_id = {a.id: a for a in p.assumptions}
    assert a_by_id["A1"] == s.assumptions[0]  # active, intact
    assert a_by_id["A3"] == s.assumptions[2]  # validated, intact
    assert p.objective == s.objective
    assert p.open_questions == s.open_questions
    assert p.next_actions == s.next_actions


def test_projection_never_presents_dead_items_as_current():
    p = project_state(_state())
    current = [d for d in p.decisions if d.status in ("accepted", "proposed")]
    assert [d.id for d in current] == ["D2", "D3"]
    # Dead decisions remain present, but compact and status-marked.
    dead = {d.id: d for d in p.decisions if d.status in ("superseded", "reversed")}
    assert set(dead) == {"D1", "D4"}
    assert dead["D1"].rationale == "" and dead["D1"].evidence_ids == []
    assert dead["D1"].supersedes is None
    assert dead["D4"].status == "reversed"
    # The supersession link from the live side is preserved.
    assert next(d for d in p.decisions if d.id == "D2").supersedes == "D1"
    inv = next(a for a in p.assumptions if a.id == "A2")
    assert inv.status == "invalidated" and len(inv.text) <= 100


def test_projection_keeps_referenced_evidence_only():
    p = project_state(_state())
    assert [e.id for e in p.evidence] == ["E1", "E2"]  # E3 unreferenced


def test_projection_reduces_word_count():
    s = _state()
    p = project_state(s)
    assert _words(p) < _words(s)
    # The reduction comes from dead weight, so it is substantial here.
    assert _words(p) <= 0.8 * _words(s)


def test_projection_does_not_mutate_input():
    s = _state()
    before = json.dumps(s.to_dict(), sort_keys=True)
    project_state(s)
    assert json.dumps(s.to_dict(), sort_keys=True) == before


def test_projection_of_plain_state_is_identity_like():
    """Old-format states (no ids, default statuses) project to
    themselves: everything is accepted or active, nothing compacts."""
    s = AgentState(
        objective="o",
        decisions=[Decision(text="only decision", rationale="why")],
        evidence=[Evidence(claim="c", source="s")],
        open_questions=["q"],
        next_actions=["n"],
    )
    assert project_state(s) == s
