"""Prompt 3 F1: revision_chain derives entity-level revision history.

The scenario mirrors Experiment #003's M5 grading: a decision revised
twice (D1 -> D2 -> D3), with a REJECTED attempt interleaved in the
verdict log. The chain must answer the six M5 questions mechanically:
original decision, what changed, who, why, on what evidence, and which
version is authoritative now. It must also power the #003 loss test: a
superseded decision is recoverable as superseded, never as current.
"""

import pytest

from world import World, load_state, save_state
from world.core import InvariantViolation
from world.handoff import AgentState, Decision, Evidence, revision_chain


def _no_veto(old, new):
    if new.get("veto"):
        raise InvariantViolation("vetoed by reviewer")


def _state_v1() -> AgentState:
    return AgentState(
        objective="Choose the database for the ledger service.",
        decisions=[
            Decision(
                text="Self-host Postgres 15",
                rationale="Team knows it; zero new vendors.",
                id="D1",
                status="accepted",
                evidence_ids=["E1"],
            )
        ],
        evidence=[
            Evidence(
                claim="Team ran Postgres in production for 3 years",
                source="ops review",
                id="E1",
                kind="document",
            )
        ],
    )


def _state_v2() -> AgentState:
    s = _state_v1()
    s.decisions[0].status = "superseded"
    s.decisions.append(
        Decision(
            text="Use managed Postgres",
            rationale="The failover drill took 22 minutes.",
            id="D2",
            status="accepted",
            supersedes="D1",
            evidence_ids=["E1", "E2"],
        )
    )
    s.evidence.append(
        Evidence(
            claim="Failover drill: 22 minutes to promote a replica",
            source="drill report",
            id="E2",
            kind="measurement",
        )
    )
    return s


def _state_v3() -> AgentState:
    s = _state_v2()
    s.decisions[1].status = "superseded"
    s.decisions.append(
        Decision(
            text="Use managed Postgres, pinned to major version 16",
            rationale="Audit requires a pinned, reviewable upgrade path.",
            id="D3",
            status="accepted",
            supersedes="D2",
            evidence_ids=["E2"],
        )
    )
    return s


@pytest.fixture()
def revised_world(tmp_path):
    """Three committed handoff saves with one REJECTED update between
    the first and second: seqs 1 (v1), 2 (REJECTED), 3 (v2), 4 (v3)."""
    w = World("rev", dir=str(tmp_path), invariants=[_no_veto])
    save_state(w, _state_v1(), actor="agent-a", note="initial decision")
    with pytest.raises(InvariantViolation):
        w.update({"veto": True}, actor="agent-b", note="blocked attempt")
    save_state(w, _state_v2(), actor="agent-b", note="drill results landed")
    save_state(w, _state_v3(), actor="agent-a", note="audit follow-up")
    return w


def test_chain_skips_rejected_rows(revised_world):
    seqs = [h["seq"] for h in revised_world.history()]
    assert [h["status"] for h in revised_world.history()] == [
        "COMMITTED",
        "REJECTED",
        "COMMITTED",
        "COMMITTED",
    ]
    chain = revision_chain(revised_world, "D1")
    assert 2 not in [e["seq"] for e in chain]
    assert seqs == [1, 2, 3, 4]


def test_chain_answers_the_six_m5_questions(revised_world):
    w = revised_world
    chain_d1 = revision_chain(w, "D1")
    chain_d2 = revision_chain(w, "D2")
    chain_d3 = revision_chain(w, "D3")

    # 1. What was the original decision?
    assert chain_d1[0]["text"] == "Self-host Postgres 15"
    assert chain_d1[0]["status"] == "accepted"
    assert chain_d1[0]["seq"] == 1

    # 2. What changed? D1 was superseded at the v2 save; D2 at v3.
    assert [e["status"] for e in chain_d1] == ["accepted", "superseded"]
    assert chain_d1[1]["seq"] == 3
    assert [e["status"] for e in chain_d2] == ["accepted", "superseded"]
    assert chain_d2[0]["supersedes"] == "D1"
    assert chain_d3[0]["supersedes"] == "D2"

    # 3. Who changed it? Entry actors come from the verdict log.
    assert chain_d1[0]["actor"] == "agent-a"
    assert chain_d1[1]["actor"] == "agent-b"
    assert chain_d3[0]["actor"] == "agent-a"

    # 4. Why? Rationale on the entry plus the row note of that save.
    assert "failover drill" in chain_d2[0]["rationale"]
    assert chain_d2[0]["note"] == "drill results landed"
    assert "Audit requires" in chain_d3[0]["rationale"]

    # 5. What evidence supported the change?
    assert chain_d2[0]["evidence_ids"] == ["E1", "E2"]
    assert chain_d3[0]["evidence_ids"] == ["E2"]

    # 6. Which version is authoritative now? The latest snapshot marks
    # D1 and D2 superseded and D3 accepted; each chain's last entry
    # agrees with the loaded state.
    current = load_state(w)
    by_id = {d.id: d for d in current.decisions}
    assert by_id["D1"].status == "superseded"
    assert by_id["D2"].status == "superseded"
    assert by_id["D3"].status == "accepted"
    assert chain_d1[-1]["status"] == by_id["D1"].status
    assert chain_d3[-1]["status"] == "accepted"


def test_superseded_decision_not_recoverable_as_current(revised_world):
    """The #003 loss test, mirrored: status and supersession survive
    the handoff, so a successor can tell D1 is history, not guidance."""
    loaded = load_state(revised_world)
    d1 = next(d for d in loaded.decisions if d.id == "D1")
    assert d1.status == "superseded"
    current = [d for d in loaded.decisions if d.status == "accepted"]
    assert [d.id for d in current] == ["D3"]


def test_chain_collapses_unchanged_snapshots(tmp_path):
    """Re-saving an unchanged state appends a version but not a chain
    entry: the chain records changes, not saves."""
    w = World("calm", dir=str(tmp_path))
    save_state(w, _state_v1(), actor="agent-a", note="first")
    save_state(w, _state_v1(), actor="agent-a", note="re-save, no change")
    assert w.version == 2
    chain = revision_chain(w, "D1")
    assert len(chain) == 1
    assert chain[0]["seq"] == 1


def test_chain_unknown_decision_raises(revised_world):
    with pytest.raises(KeyError, match="no decision with id"):
        revision_chain(revised_world, "D99")


def test_chain_tracks_text_revision_of_same_decision(tmp_path):
    """A decision whose text is revised in place (same id) produces a
    second entry with the new text."""
    w = World("edit", dir=str(tmp_path))
    save_state(w, _state_v1(), actor="agent-a")
    s = _state_v1()
    s.decisions[0].text = "Self-host Postgres 16"
    s.decisions[0].rationale = "Version 15 reaches end of life first."
    save_state(w, s, actor="agent-a", note="version bump")
    chain = revision_chain(w, "D1")
    assert [e["text"] for e in chain] == [
        "Self-host Postgres 15",
        "Self-host Postgres 16",
    ]
    assert chain[1]["rationale"].startswith("Version 15")
