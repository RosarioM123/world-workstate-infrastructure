"""Prompt 4 cross-model handoff: the continuation packet.

Acceptance tests for the provider-neutral bundle a successor agent
continues from. The packet must carry every field Prompt 4 names
(objective, completed work, remaining tasks, decisions with
rationale, evidence, unresolved questions, artifact references,
dependencies, known errors, state version, next action) plus the
assumptions Experiment #003 showed free-text handoffs lose. A
packet pinned to a version must reproduce from that version, and
the text rendering must be deterministic and provider-neutral.
"""

import copy

import pytest

from world import (
    AgentState,
    Decision,
    Evidence,
    Task,
    World,
    continuation_packet,
    packet_from_state,
    render_packet_text,
    save_state,
)
from world.handoff import PACKET_FORMAT, Assumption


def _world_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DIR", str(tmp_path))


def _rich_state() -> AgentState:
    return AgentState(
        objective="Write a sourcing memo on solid-state battery suppliers",
        decisions=[
            Decision(
                text="Use the March teardown dataset as the primary cost source",
                rationale="It is the only dataset with cell-level cost splits",
                id="D1",
                status="superseded",
                evidence_ids=["E1"],
            ),
            Decision(
                text="Use the January teardown refresh as the primary cost source",
                rationale="The refresh corrects the March cathode pricing error",
                id="D3",
                status="accepted",
                supersedes="D1",
                evidence_ids=["E2"],
            ),
        ],
        assumptions=[
            Assumption(
                text="Pilot-line yields reach 80 percent by Q2 2027",
                id="A1",
                confidence="medium",
                status="active",
            ),
            Assumption(
                text="The leading patent holder licenses exclusively",
                id="A2",
                confidence="low",
                status="invalidated",
                validated_by="E2",
            ),
        ],
        evidence=[
            Evidence(
                claim="March teardown: leading cell at 118 USD per kWh",
                source="Supplier data room, March teardown dataset",
                id="E1",
                kind="measurement",
            ),
            Evidence(
                claim="January refresh: leading cell at 104 USD per kWh",
                source="Supplier data room, January teardown refresh",
                id="E2",
                kind="measurement",
            ),
        ],
        open_questions=["Will the leading supplier license its anode process?"],
        next_actions=["Draft the cost-curve section on the refreshed numbers"],
        tasks=[
            Task(
                title="Collect the teardown datasets",
                id="t-collect",
                status="done",
                owner="agent-a",
            ),
            Task(
                title="Draft the cost-curve section",
                id="t-draft",
                status="in_progress",
                owner="agent-b",
                depends_on=["t-collect"],
            ),
            Task(
                title="Interview two cell makers",
                id="t-interview",
                status="blocked",
                owner="agent-b",
                depends_on=["t-draft"],
            ),
        ],
    )


def test_packet_carries_all_prompt4_fields(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    save_state("job-c1", _rich_state(), actor="agent-a")
    packet = continuation_packet("job-c1")
    assert packet["format"] == PACKET_FORMAT
    assert packet["world"] == "job-c1"
    assert packet["state_version"] == 1
    assert packet["objective"].startswith("Write a sourcing memo")
    for key in (
        "completed_work",
        "remaining_tasks",
        "decisions",
        "assumptions",
        "evidence",
        "unresolved_questions",
        "artifacts",
        "dependencies",
        "known_errors",
        "next_action",
    ):
        assert key in packet, f"packet is missing {key!r}"
    assert (
        packet["next_action"] == "Draft the cost-curve section on the refreshed numbers"
    )


def test_packet_completed_work_splits_done_tasks_and_accepted_decisions(
    tmp_path, monkeypatch
):
    _world_dir(tmp_path, monkeypatch)
    save_state("job-c2", _rich_state(), actor="agent-a")
    packet = continuation_packet("job-c2")
    kinds = [(item["kind"], item["id"]) for item in packet["completed_work"]]
    assert ("task", "t-collect") in kinds
    assert ("decision", "D3") in kinds
    assert ("decision", "D1") not in kinds
    assert ("task", "t-draft") not in kinds
    assert ("task", "t-interview") not in kinds


def test_packet_remaining_tasks_carry_status_owner_and_dependencies(
    tmp_path, monkeypatch
):
    _world_dir(tmp_path, monkeypatch)
    save_state("job-c3", _rich_state(), actor="agent-a")
    packet = continuation_packet("job-c3")
    remaining = {t["id"]: t for t in packet["remaining_tasks"]}
    assert set(remaining) == {"t-draft", "t-interview"}
    assert remaining["t-draft"]["status"] == "in_progress"
    assert remaining["t-draft"]["owner"] == "agent-b"
    assert remaining["t-draft"]["depends_on"] == ["t-collect"]
    assert remaining["t-interview"]["status"] == "blocked"
    assert remaining["t-interview"]["depends_on"] == ["t-draft"]


def test_packet_known_errors_cover_blocked_tasks_invalidated_assumptions_and_rejections(
    tmp_path, monkeypatch
):
    _world_dir(tmp_path, monkeypatch)

    def cap(old, new):
        spend = new.get("spend")
        if isinstance(spend, dict) and spend.get("committed_usd", 0) > 100:
            from world import InvariantViolation

            raise InvariantViolation("spend cap 100 exceeded")

    work = World("job-c4", invariants=[cap])
    work.update({"spend": {"committed_usd": 50}}, actor="agent-a", note="book access")
    with pytest.raises(Exception, match="spend cap"):
        work.update(
            {"spend": {"committed_usd": 200}},
            actor="agent-a",
            note="book the full teardown",
        )
    save_state(work, _rich_state(), actor="agent-a")
    packet = continuation_packet(work)
    kinds = [(e["kind"], e.get("id") or e.get("seq")) for e in packet["known_errors"]]
    assert ("blocked_task", "t-interview") in kinds
    assert ("invalidated_assumption", "A2") in kinds
    rejected = [e for e in packet["known_errors"] if e["kind"] == "rejected_proposal"]
    assert len(rejected) == 1
    assert "book the full teardown" in rejected[0]["note"]
    assert "spend cap 100 exceeded" in rejected[0]["note"]
    assert rejected[0]["actor"] == "agent-a"


def test_packet_artifacts_are_deduplicated_evidence_references(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    state = _rich_state()
    state.evidence.append(
        Evidence(
            claim="March teardown, second reading",
            source="Supplier data room, March teardown dataset",
            id="E3",
            kind="measurement",
        )
    )
    save_state("job-c5", state, actor="agent-a")
    packet = continuation_packet("job-c5")
    refs = {a["reference"]: a["evidence_ids"] for a in packet["artifacts"]}
    assert refs["Supplier data room, March teardown dataset"] == ["E1", "E3"]
    assert refs["Supplier data room, January teardown refresh"] == ["E2"]


def test_packet_dependencies_map_task_links_and_supersession(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    save_state("job-c6", _rich_state(), actor="agent-a")
    packet = continuation_packet("job-c6")
    assert packet["dependencies"]["tasks"]["t-draft"] == {
        "parent_id": None,
        "depends_on": ["t-collect"],
    }
    assert packet["dependencies"]["tasks"]["t-interview"]["depends_on"] == ["t-draft"]
    assert packet["dependencies"]["decisions"] == {"D3": {"supersedes": "D1"}}


def test_packet_next_action_falls_back_to_first_remaining_task(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    state = _rich_state()
    state.next_actions = []
    save_state("job-c7", state, actor="agent-a")
    packet = continuation_packet("job-c7")
    assert packet["next_action"] == "Draft the cost-curve section"


def test_packet_next_action_is_none_when_nothing_remains(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    state = AgentState(objective="Done already")
    packet = packet_from_state(state, state_version=0)
    assert packet["next_action"] is None
    assert packet["completed_work"] == []
    assert packet["remaining_tasks"] == []
    assert packet["known_errors"] == []


def test_packet_pinned_to_a_version_reproduces(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    first = _rich_state()
    save_state("job-c8", first, actor="agent-a")
    packet_v1 = continuation_packet("job-c8", version=1)
    second = _rich_state()
    second.decisions.append(
        Decision(
            text="Draft the memo with the refreshed cost curve as the base case",
            rationale="D3 established the refreshed dataset as authoritative",
            id="D4",
            status="accepted",
            evidence_ids=["E2"],
        )
    )
    save_state("job-c8", second, actor="agent-b")
    assert continuation_packet("job-c8")["state_version"] == 2
    assert continuation_packet("job-c8", version=1) == packet_v1


def test_packet_pinned_version_excludes_later_rejections(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)

    def cap(old, new):
        spend = new.get("spend")
        if isinstance(spend, dict) and spend.get("committed_usd", 0) > 100:
            from world import InvariantViolation

            raise InvariantViolation("spend cap 100 exceeded")

    work = World("job-c9", invariants=[cap])
    save_state(work, _rich_state(), actor="agent-a")
    packet_v1 = continuation_packet(work, version=1)
    assert packet_v1["known_errors"] == [
        {
            "kind": "blocked_task",
            "id": "t-interview",
            "title": "Interview two cell makers",
        },
        {
            "kind": "invalidated_assumption",
            "id": "A2",
            "text": "The leading patent holder licenses exclusively",
        },
    ]
    with pytest.raises(Exception, match="spend cap"):
        work.update(
            {"spend": {"committed_usd": 200}},
            actor="agent-a",
            note="late over-cap attempt",
        )
    # The rejection is a seq 2 row; the packet stays a pure function of
    # the pinned committed version, so it appears only once a later
    # committed version exists.
    save_state(work, _rich_state(), actor="agent-a", note="re-save after rejection")
    packet_now = continuation_packet(work)
    assert packet_now["state_version"] == 3
    assert any(
        e["kind"] == "rejected_proposal" and "late over-cap attempt" in e["note"]
        for e in packet_now["known_errors"]
    )
    assert continuation_packet(work, version=1) == packet_v1


def test_packet_projected_compacts_finished_items(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    save_state("job-c10", _rich_state(), actor="agent-a")
    full = continuation_packet("job-c10")
    projected = continuation_packet("job-c10", projected=True)
    assert projected["state_version"] == full["state_version"]
    done = [i for i in projected["completed_work"] if i["kind"] == "task"]
    assert done[0]["title"] == "Collect the teardown datasets"
    assert len(projected["remaining_tasks"]) == len(full["remaining_tasks"])
    assert projected["decisions"][0]["status"] == "superseded"
    assert projected["decisions"][0]["rationale"] == ""
    assert projected["decisions"][0]["evidence_ids"] == []


def test_packet_from_state_is_pure_and_raises_without_handoff(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    state = _rich_state()
    before = copy.deepcopy(state)
    packet_from_state(state, state_version=3, world_name="job-c11")
    assert state == before
    World("job-c11").update({"spend": {"committed_usd": 1}}, actor="agent-a")
    with pytest.raises(KeyError, match="no saved handoff state"):
        continuation_packet("job-c11")


def test_render_packet_text_is_deterministic_and_provider_neutral(
    tmp_path, monkeypatch
):
    _world_dir(tmp_path, monkeypatch)
    save_state("job-c12", _rich_state(), actor="agent-a")
    packet = continuation_packet("job-c12")
    first = render_packet_text(packet)
    second = render_packet_text(packet)
    assert first == second
    for section in (
        "Completed work:",
        "Remaining tasks:",
        "Decisions:",
        "Evidence:",
        "Assumptions:",
        "Unresolved questions:",
        "Artifacts (references only",
        "Dependencies:",
        "Known errors:",
        "Next action:",
    ):
        assert section in first
    assert "[D1, superseded]" in first
    assert "[D3, accepted]" in first
    assert "[A1, confidence medium, active]" in first
    assert "[A2, confidence low, invalidated]" in first
    assert "task t-interview depends on t-draft" in first
    assert "decision D3 supersedes D1" in first
    lowered = first.lower()
    for provider in ("openai", "anthropic", "gpt", "claude", "gemini"):
        assert provider not in lowered
    assert render_packet_text(packet_from_state(_rich_state(), state_version=0)) == (
        render_packet_text(packet_from_state(_rich_state(), state_version=0))
    )


def test_packet_roundtrips_through_json(tmp_path, monkeypatch):
    import json

    _world_dir(tmp_path, monkeypatch)
    save_state("job-c13", _rich_state(), actor="agent-a")
    packet = continuation_packet("job-c13")
    assert json.loads(json.dumps(packet)) == packet
