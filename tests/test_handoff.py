"""Agent handoff: Agent A saves, disappears; Agent B loads and continues.

The critical property: every section of the work state — objective,
decisions, evidence, open questions, next actions — must survive the
round trip exactly. If any section is lost or altered, these tests fail.
"""

import json
import os
import subprocess
import sys

import pytest

from world import AgentState, Decision, Evidence, World, load_state, save_state


def _agent_a_state() -> AgentState:
    """The work Agent A performed before its session ended."""
    return AgentState(
        objective="Draft the Q3 foundry memo: buy/hold/sell with a credit stress case.",
        decisions=[
            Decision(
                text="Source 18A yield data from SEC filings only",
                rationale="Press releases round yields up; filings give quarterly granularity.",
            ),
            Decision(
                text="No buy thesis without a stress case",
                rationale="Binding guardrail from the investment committee.",
            ),
        ],
        evidence=[
            Evidence(
                claim="18A defect density improved 2x quarter over quarter",
                source="https://www.sec.gov/ ... 10-Q Q2 2026",
            ),
            Evidence(
                claim="Foundry operating margin still negative at -8%",
                source="Q2 2026 earnings call transcript",
            ),
        ],
        open_questions=[
            "Foundry breakeven date?",
            "Does the CHIPS disbursement schedule constrain capex?",
        ],
        next_actions=[
            "Build the DCF with the filed capex numbers",
            "Run the credit-cycle stress case before any recommendation",
        ],
    )


def _world_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DIR", str(tmp_path))


def test_handoff_roundtrip_preserves_every_section(tmp_path, monkeypatch):
    """save -> load returns the identical work state, section by section."""
    _world_dir(tmp_path, monkeypatch)
    saved = _agent_a_state()

    seq = save_state("job-001", saved, actor="agent-a", note="end of session")
    assert seq == 1

    # Agent A disappears: drop every reference to its objects.
    del saved

    # Agent B starts with nothing but the world name.
    loaded = load_state("job-001")
    expected = _agent_a_state()

    assert loaded.objective == expected.objective, "objective lost in handoff"
    assert loaded.decisions == expected.decisions, "decisions lost in handoff"
    assert loaded.evidence == expected.evidence, "evidence lost in handoff"
    assert loaded.open_questions == expected.open_questions, (
        "open questions lost in handoff"
    )
    assert loaded.next_actions == expected.next_actions, "next actions lost in handoff"
    assert loaded == expected


def test_handoff_across_fresh_processes(tmp_path):
    """Two separate interpreters: nothing survives except the WORLD file."""
    env = dict(os.environ, WORLD_DIR=str(tmp_path))
    state_file = tmp_path / "state.json"
    state_file.write_text(json.dumps(_agent_a_state().to_dict()))

    save_code = (
        "import json; "
        "from world import AgentState, save_state; "
        f"state = AgentState.from_dict(json.loads(open({str(state_file)!r}).read())); "
        "seq = save_state('job-002', state, actor='agent-a'); "
        "print(seq)"
    )
    r1 = subprocess.run(
        [sys.executable, "-c", save_code],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert r1.returncode == 0, r1.stderr
    assert r1.stdout.strip() == "1"

    # Agent B: a brand-new interpreter that only knows the world name.
    load_code = (
        "import json; "
        "from world import load_state; "
        "print(json.dumps(load_state('job-002').to_dict(), sort_keys=True))"
    )
    r2 = subprocess.run(
        [sys.executable, "-c", load_code],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert r2.returncode == 0, r2.stderr
    assert json.loads(r2.stdout) == _agent_a_state().to_dict()


def test_load_state_without_save_raises(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    World("empty-job")  # create the world, save nothing
    with pytest.raises(KeyError, match="no saved handoff state"):
        load_state("empty-job")


def test_load_state_historical_version_and_checkpoint(tmp_path, monkeypatch):
    """Agent B can resume from an earlier handoff, not just the latest."""
    _world_dir(tmp_path, monkeypatch)
    v1 = _agent_a_state()
    save_state("job-003", v1, actor="agent-a", note="phase 1")

    v2 = _agent_a_state()
    v2.objective = "Phase 2: valuation modeling (supersedes phase 1 scope)"
    v2.next_actions = ["Build the DCF"]
    save_state("job-003", v2, actor="agent-a", note="phase 2")

    assert load_state("job-003").objective == v2.objective
    assert load_state("job-003", version=1).objective == v1.objective

    # A checkpoint pins the current version (2 here); the checkpoint path
    # loads the same handoff a name would resolve to.
    World("job-003").checkpoint("phase-2")
    assert load_state("job-003", checkpoint="phase-2").objective == v2.objective


def test_save_state_preserves_other_document_keys(tmp_path, monkeypatch):
    """The handoff namespace must not clobber the agent's other state."""
    _world_dir(tmp_path, monkeypatch)
    w = World("job-004")
    w.update({"scratch": {"tokens_used": 1234}}, actor="agent-a")

    save_state(w, _agent_a_state(), actor="agent-a")

    doc = w.state()
    assert doc["scratch"] == {"tokens_used": 1234}
    assert doc["handoff"]["objective"] == _agent_a_state().objective


def test_save_state_records_verdict_in_history(tmp_path, monkeypatch):
    """A handoff save is an ordinary judged version: visible in history."""
    _world_dir(tmp_path, monkeypatch)
    seq = save_state("job-005", _agent_a_state(), actor="agent-a", note="handoff")
    history = World("job-005").history()
    assert [(h["seq"], h["status"], h["note"]) for h in history] == [
        (seq, "COMMITTED", "handoff")
    ]


def test_handoff_empty_sections_roundtrip(tmp_path, monkeypatch):
    """A sparse handoff (objective only) round-trips without KeyErrors."""
    _world_dir(tmp_path, monkeypatch)
    saved = AgentState(objective="Spike: can WORLD hold a 10MB doc?")
    save_state("job-006", saved, actor="agent-a")
    loaded = load_state("job-006")
    assert loaded == saved
    assert loaded.decisions == []
    assert loaded.evidence == []
    assert loaded.open_questions == []
    assert loaded.next_actions == []


def test_handoff_rejects_malformed_state(tmp_path, monkeypatch):
    """Corruption surfaces loudly instead of loading a partial state."""
    _world_dir(tmp_path, monkeypatch)
    w = World("job-007")
    w.update({"handoff": {"decisions": []}}, actor="agent-a")  # no objective
    with pytest.raises(KeyError, match="objective"):
        load_state("job-007")


# ---------------------------------------------------------------------------
# Prompt 3 F1: research-schema fields (ids, status, supersession,
# assumptions with confidence) round-trip and validate.
# ---------------------------------------------------------------------------

from world.handoff import Assumption


def _rich_state() -> AgentState:
    """A state using every F1 field: a supersession chain, linked
    evidence, and assumptions with confidence and validation links."""
    return AgentState(
        objective="Pick the storage engine for the ledger service.",
        decisions=[
            Decision(
                text="Self-host Postgres 15",
                rationale="Team knows it; zero new vendors.",
                id="D1",
                status="superseded",
            ),
            Decision(
                text="Use managed Postgres",
                rationale="Nightly backups and failover are not optional.",
                id="D2",
                status="accepted",
                supersedes="D1",
                evidence_ids=["E1", "E2"],
            ),
            Decision(
                text="Pin the connection budget at 40",
                rationale="Load test showed saturation at 55.",
                id="D3",
                status="proposed",
                evidence_ids=["E2"],
            ),
        ],
        evidence=[
            Evidence(
                claim="Self-hosted failover took 22 minutes in the drill",
                source="drill report 2026-10-02",
                id="E1",
                kind="measurement",
            ),
            Evidence(
                claim="Managed tier includes nightly PITR backups",
                source="vendor docs",
                id="E2",
                kind="document",
            ),
        ],
        open_questions=["Does the managed tier allow logical replication?"],
        next_actions=["Draft the migration runbook"],
        assumptions=[
            Assumption(
                text="Traffic stays under 2k rps through Q2",
                id="A1",
                confidence="medium",
                status="active",
            ),
            Assumption(
                text="The vendor region supports PITR",
                id="A2",
                confidence="high",
                status="validated",
                validated_by="E2",
            ),
            Assumption(
                text="A second region is required this year",
                id="A3",
                confidence="low",
                status="invalidated",
            ),
        ],
    )


def test_f1_fields_roundtrip_through_save_and_load(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    saved = _rich_state()
    save_state("job-101", saved, actor="agent-a")
    loaded = load_state("job-101")
    assert loaded == saved
    d2 = loaded.decisions[1]
    assert d2.id == "D2" and d2.supersedes == "D1"
    assert d2.evidence_ids == ["E1", "E2"]
    assert loaded.decisions[0].status == "superseded"
    assert loaded.evidence[0].kind == "measurement"
    a2 = loaded.assumptions[1]
    assert (a2.confidence, a2.status, a2.validated_by) == (
        "high",
        "validated",
        "E2",
    )


def test_f1_fields_survive_resume(tmp_path, monkeypatch):
    """The revision graph is part of the document, so a checkpoint
    resume carries it intact."""
    _world_dir(tmp_path, monkeypatch)
    w = World("job-102")
    save_state(w, _rich_state(), actor="agent-a")
    w.checkpoint("rich")
    changed = _rich_state()
    changed.objective = "Changed objective"
    save_state(w, changed, actor="agent-a")
    w.resume("rich")
    loaded = load_state(w)
    assert loaded == _rich_state()


def test_f1_old_format_handoff_still_loads(tmp_path, monkeypatch):
    """States stored before F1 (no ids, no assumptions key) load with
    defaults instead of failing."""
    _world_dir(tmp_path, monkeypatch)
    w = World("job-103")
    w.update(
        {
            "handoff": {
                "objective": "Legacy handoff",
                "decisions": [{"text": "Old decision", "rationale": "then"}],
                "evidence": [{"claim": "Old claim", "source": "memory"}],
                "open_questions": [],
                "next_actions": [],
            }
        },
        actor="agent-a",
    )
    loaded = load_state(w)
    assert loaded.decisions[0].id == ""
    assert loaded.decisions[0].status == "accepted"
    assert loaded.decisions[0].supersedes is None
    assert loaded.decisions[0].evidence_ids == []
    assert loaded.evidence[0].id == "" and loaded.evidence[0].kind == ""
    assert loaded.assumptions == []


def test_f1_invalid_enum_values_rejected():
    with pytest.raises(ValueError, match="decision status"):
        Decision(text="x", status="maybe")
    with pytest.raises(ValueError, match="confidence"):
        Assumption(text="x", confidence="certain")
    with pytest.raises(ValueError, match="assumption status"):
        Assumption(text="x", status="forgotten")


def _assert_save_rejected(tmp_path, monkeypatch, state, match):
    _world_dir(tmp_path, monkeypatch)
    w = World("job-104")
    with pytest.raises(ValueError, match=match):
        save_state(w, state, actor="agent-a")
    # Validation fires before proposing: nothing was appended.
    assert w.version == 0
    assert w.history() == []


def test_f1_validation_supersedes_unknown_target(tmp_path, monkeypatch):
    state = _rich_state()
    state.decisions[1].supersedes = "D99"
    _assert_save_rejected(tmp_path, monkeypatch, state, "supersedes unknown")


def test_f1_validation_evidence_link_must_resolve(tmp_path, monkeypatch):
    state = _rich_state()
    state.decisions[1].evidence_ids = ["E1", "E99"]
    _assert_save_rejected(tmp_path, monkeypatch, state, "unknown evidence")


def test_f1_validation_superseded_needs_exactly_one_successor(tmp_path, monkeypatch):
    state = _rich_state()
    state.decisions[1].supersedes = None
    state.decisions[1].status = "accepted"
    # D1 is still marked superseded, but nothing supersedes it now.
    _assert_save_rejected(tmp_path, monkeypatch, state, "exactly one")


def test_f1_validation_successor_may_supersede_reversed_decision(tmp_path, monkeypatch):
    """Experiment #003 task R2's shape: the in-person format decision
    is marked reversed, and the remote decision supersedes it. The
    approved validation spec requires only that the target exists;
    reversal is a terminal status that a successor may still point
    at. (An earlier draft of this validation also required the target
    to be marked 'superseded', which rejects R2's legitimate graph;
    that stricter rule was not in the spec and was removed.)"""
    _world_dir(tmp_path, monkeypatch)
    state = AgentState(
        objective="o",
        decisions=[
            Decision(text="In-person sessions", id="D1", status="reversed"),
            Decision(
                text="Remote sessions",
                id="D2",
                status="accepted",
                supersedes="D1",
            ),
        ],
    )
    assert save_state("job-106", state, actor="agent-a") == 1
    assert load_state("job-106") == state


def test_f1_validation_duplicate_ids_rejected(tmp_path, monkeypatch):
    state = _rich_state()
    state.evidence[1].id = "E1"
    _assert_save_rejected(tmp_path, monkeypatch, state, "duplicate evidence")


def test_f1_validation_assumption_validated_by_must_resolve(tmp_path, monkeypatch):
    state = _rich_state()
    state.assumptions[1].validated_by = "E99"
    _assert_save_rejected(tmp_path, monkeypatch, state, "validated_by unknown")


def test_f1_reversed_decision_needs_no_successor(tmp_path, monkeypatch):
    """Reversal is terminal: a reversed decision validates without a
    successor pointing at it."""
    _world_dir(tmp_path, monkeypatch)
    state = AgentState(
        objective="o",
        decisions=[
            Decision(text="Adopt the vendor SDK", id="D1", status="reversed"),
            Decision(text="Build in house", id="D2", status="accepted"),
        ],
    )
    seq = save_state("job-105", state, actor="agent-a")
    assert seq == 1
    assert load_state("job-105") == state
