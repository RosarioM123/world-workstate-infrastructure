"""Prompt 5 provenance and verification: queries over committed handoff state.

The five Prompt 5 queries must be answerable from what WORLD already
records (version rows with actor, timestamp, note; committed
snapshots; evidence links): why a decision is in the project, what
evidence supports an assumption, what changed since a previous
version, which decisions depend on a source or evidence item, and
which conclusions are no longer supported. Provenance here is a
derived view, not stored per-entity fields (Prompt 3 proposal
section 8.5 stays proposed-only), so reconstruction is verified
after multiple transitions and at a pinned older version.
"""

import pytest

from world import (
    AgentState,
    Decision,
    Evidence,
    Task,
    World,
    save_state,
)
from world.handoff import Assumption
from world.provenance import (
    classify_evidence,
    decisions_for_evidence,
    decisions_for_source,
    evidence_for_assumption,
    explain_decision,
    reconstruct_provenance,
    state_diff,
    unsupported_conclusions,
)


def _world_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DIR", str(tmp_path))


def _v1() -> AgentState:
    return AgentState(
        objective="Write a sourcing memo on solid-state battery suppliers",
        decisions=[
            Decision(
                text="Use the March teardown dataset as the primary cost source",
                rationale="It is the only dataset with cell-level cost splits",
                id="D1",
                status="accepted",
                evidence_ids=["E1"],
            ),
        ],
        assumptions=[
            Assumption(
                text="Pilot-line yields reach 80 percent by Q2 2027",
                id="A1",
                confidence="medium",
                status="active",
                validated_by="E1",
            ),
        ],
        evidence=[
            Evidence(
                claim="March teardown prices cathode at $42 per kWh",
                source="teardown.pdf",
                id="E1",
                kind="document",
            ),
        ],
        tasks=[Task(title="Draft the cost section", id="T1", owner="agent-a")],
    )


def _build_world(tmp_path, monkeypatch) -> World:
    """Three saves, three actors: v1 start, v2 edit plus D2, v3 supersede plus invalidate."""
    _world_dir(tmp_path, monkeypatch)
    w = World("prov-memo")
    v1 = save_state(w, _v1(), actor="agent-a", note="start research")
    assert v1 == 1
    s2 = _v1()
    s2.decisions[
        0
    ].text = "Use the March teardown dataset as the primary cost source (revised)"
    s2.decisions[0].rationale = "Still the only dataset with cell-level splits"
    s2.decisions.append(
        Decision(
            text="Publish the memo without a sensitivity table",
            rationale="No time before the deadline",
            id="D2",
            status="accepted",
        )
    )
    s2.evidence.append(
        Evidence(
            claim="The refresh corrects the March cathode pricing error",
            source="analyst note",
            id="E2",
            kind="interpretation",
        )
    )
    save_state(w, s2, actor="agent-b", note="revise cost source, add D2")
    s3 = _v1()
    s3.decisions[
        0
    ].text = "Use the March teardown dataset as the primary cost source (revised)"
    s3.decisions[0].rationale = "Still the only dataset with cell-level splits"
    s3.decisions[0].status = "superseded"
    s3.decisions.append(
        Decision(
            text="Publish the memo without a sensitivity table",
            rationale="No time before the deadline",
            id="D2",
            status="accepted",
        )
    )
    s3.decisions.append(
        Decision(
            text="Use the January teardown refresh as the primary cost source",
            rationale="The refresh corrects the March cathode pricing error",
            id="D3",
            status="accepted",
            supersedes="D1",
            evidence_ids=["E2"],
        )
    )
    s3.decisions.append(
        Decision(
            text="Treat pilot yields as the binding constraint on cost",
            rationale="The validated yield model drives the cost curve",
            id="D4",
            status="accepted",
            evidence_ids=["E1"],
        )
    )
    s3.assumptions[0].status = "invalidated"
    s3.evidence.append(
        Evidence(
            claim="The refresh corrects the March cathode pricing error",
            source="analyst note",
            id="E2",
            kind="interpretation",
        )
    )
    save_state(w, s3, actor="rosario", note="supersede D1, invalidate A1")
    return w


def test_reconstruct_provenance_tracks_introduction_and_changes(tmp_path, monkeypatch):
    w = _build_world(tmp_path, monkeypatch)
    prov = reconstruct_provenance(w)
    d1 = prov["decisions"]["D1"]
    assert d1["introduced_seq"] == 1
    assert d1["introduced_by"] == "agent-a"
    assert d1["introduced_note"] == "start research"
    assert d1["changed_seqs"] == [2, 3]
    d3 = prov["decisions"]["D3"]
    assert d3["introduced_seq"] == 3
    assert d3["introduced_by"] == "rosario"
    assert d3["changed_seqs"] == []
    e2 = prov["evidence"]["E2"]
    assert e2["introduced_seq"] == 2
    assert e2["introduced_by"] == "agent-b"
    t1 = prov["tasks"]["T1"]
    assert t1["introduced_seq"] == 1
    assert t1["changed_seqs"] == []
    a1 = prov["assumptions"]["A1"]
    assert a1["introduced_seq"] == 1
    assert a1["changed_seqs"] == [3]


def test_reconstruct_provenance_at_pinned_version(tmp_path, monkeypatch):
    w = _build_world(tmp_path, monkeypatch)
    prov = reconstruct_provenance(w, version=2)
    assert "D3" not in prov["decisions"]
    assert prov["assumptions"]["A1"]["changed_seqs"] == []
    assert prov["decisions"]["D1"]["changed_seqs"] == [2]


def test_explain_decision(tmp_path, monkeypatch):
    w = _build_world(tmp_path, monkeypatch)
    out = explain_decision(w, "D3")
    assert out["id"] == "D3"
    assert out["status"] == "accepted"
    assert out["supersedes"] == "D1"
    assert out["introduced"]["introduced_seq"] == 3
    assert out["introduced"]["introduced_by"] == "rosario"
    assert out["revision_count"] == 1
    assert out["supersession_chain"] == ["D1"]
    assert out["support_status"] == "supported"
    assert len(out["evidence"]) == 1
    assert out["evidence"][0]["id"] == "E2"
    assert out["evidence"][0]["source"] == "analyst note"
    assert out["evidence"][0]["classification"] == "model_interpretation"
    assert out["human_approved"] is None
    assert "not recorded" in out["human_approval_note"]


def test_explain_decision_unknown_id_raises(tmp_path, monkeypatch):
    w = _build_world(tmp_path, monkeypatch)
    with pytest.raises(KeyError):
        explain_decision(w, "D9")


def test_evidence_for_assumption(tmp_path, monkeypatch):
    w = _build_world(tmp_path, monkeypatch)
    out = evidence_for_assumption(w, "A1")
    assert out["assumption"]["id"] == "A1"
    assert out["assumption"]["status"] == "invalidated"
    assert out["evidence"]["id"] == "E1"
    assert out["evidence"]["claim"].startswith("March teardown prices cathode")
    assert out["validated_at"]["introduced_seq"] == 1
    assert out["validated_at"]["introduced_by"] == "agent-a"


def test_evidence_for_assumption_unknown_id_raises(tmp_path, monkeypatch):
    w = _build_world(tmp_path, monkeypatch)
    with pytest.raises(KeyError):
        evidence_for_assumption(w, "A9")


def test_decisions_for_evidence_and_source(tmp_path, monkeypatch):
    w = _build_world(tmp_path, monkeypatch)
    by_e1 = decisions_for_evidence(w, "E1")
    assert [d["id"] for d in by_e1] == ["D1", "D4"]
    by_e2 = decisions_for_evidence(w, "E2")
    assert [d["id"] for d in by_e2] == ["D3"]
    assert decisions_for_evidence(w, "E9") == []
    by_source = decisions_for_source(w, "teardown.pdf")
    assert [d["id"] for d in by_source] == ["D1", "D4"]
    assert decisions_for_source(w, "no such source") == []


def test_state_diff_between_versions(tmp_path, monkeypatch):
    w = _build_world(tmp_path, monkeypatch)
    diff = state_diff(w, 1, 3)
    assert diff["from_version"] == 1
    assert diff["to_version"] == 3
    assert [v["seq"] for v in diff["versions"]] == [2, 3]
    assert [v["actor"] for v in diff["versions"]] == ["agent-b", "rosario"]
    added_decisions = [d["id"] for d in diff["decisions"]["added"]]
    assert added_decisions == ["D2", "D3", "D4"]
    assert diff["decisions"]["removed"] == []
    changed = diff["decisions"]["changed"]
    assert [c["id"] for c in changed] == ["D1"]
    assert changed[0]["before"]["status"] == "accepted"
    assert changed[0]["after"]["status"] == "superseded"
    assert [e["id"] for e in diff["evidence"]["added"]] == ["E2"]
    changed_a = diff["assumptions"]["changed"]
    assert [c["id"] for c in changed_a] == ["A1"]
    assert changed_a[0]["after"]["status"] == "invalidated"


def test_state_diff_same_version_is_empty(tmp_path, monkeypatch):
    w = _build_world(tmp_path, monkeypatch)
    diff = state_diff(w, 2, 2)
    assert diff["versions"] == []
    for section in ("decisions", "assumptions", "evidence", "tasks"):
        assert diff[section] == {"added": [], "removed": [], "changed": []}


def test_state_diff_rejects_bad_range(tmp_path, monkeypatch):
    w = _build_world(tmp_path, monkeypatch)
    with pytest.raises(ValueError):
        state_diff(w, 3, 1)
    with pytest.raises(KeyError):
        state_diff(w, 1, 9)


def test_unsupported_conclusions(tmp_path, monkeypatch):
    w = _build_world(tmp_path, monkeypatch)
    out = unsupported_conclusions(w)
    by_id = {row["decision_id"]: row for row in out}
    assert by_id["D2"]["kind"] == "no_evidence"
    assert by_id["D4"]["kind"] == "weakened_by_invalidated_assumption"
    assert "D3" not in by_id
    assert "D1" not in by_id


def test_unsupported_conclusions_dangling_evidence(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    w = World("prov-dangling")
    state = _v1()
    state.decisions[0].evidence_ids = ["E-missing"]
    doc = {"handoff": state.to_dict()}
    w.update(doc, actor="agent-a", note="raw save with dangling link")
    out = unsupported_conclusions(w)
    assert len(out) == 1
    assert out[0]["decision_id"] == "D1"
    assert out[0]["kind"] == "evidence_missing"
    assert "E-missing" in out[0]["detail"]


def test_decision_losing_evidence_becomes_unsupported(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    w = World("prov-lost-support")
    save_state(w, _v1(), actor="agent-a", note="start")
    assert unsupported_conclusions(w) == []
    s2 = _v1()
    s2.decisions[0].evidence_ids = []
    save_state(w, s2, actor="agent-b", note="drop the evidence link")
    out = unsupported_conclusions(w)
    assert [row["decision_id"] for row in out] == ["D1"]
    assert out[0]["kind"] == "no_evidence"
    diff = state_diff(w, 1, 2)
    changed = diff["decisions"]["changed"]
    assert [c["id"] for c in changed] == ["D1"]
    assert changed[0]["before"]["evidence_ids"] == ["E1"]
    assert changed[0]["after"]["evidence_ids"] == []


def test_classify_evidence():
    assert classify_evidence(Evidence(claim="c", kind="document")) == "source_fact"
    assert classify_evidence(Evidence(claim="c", kind="Data")) == "source_fact"
    assert classify_evidence(Evidence(claim="c", kind="measurement")) == "source_fact"
    assert classify_evidence(Evidence(claim="c", kind="observation")) == "source_fact"
    assert (
        classify_evidence(Evidence(claim="c", kind="interpretation"))
        == "model_interpretation"
    )
    assert (
        classify_evidence(Evidence(claim="c", kind="inference"))
        == "model_interpretation"
    )
    assert (
        classify_evidence(Evidence(claim="c", kind="hypothesis"))
        == "model_interpretation"
    )
    assert classify_evidence(Evidence(claim="c", kind="")) == "unclassified"
    assert classify_evidence(Evidence(claim="c", kind="weird-kind")) == "unclassified"


def test_provenance_on_id_less_state(tmp_path, monkeypatch):
    _world_dir(tmp_path, monkeypatch)
    w = World("prov-anon")
    save_state(
        w,
        AgentState(
            objective="Explore",
            decisions=[Decision(text="Go left", rationale="Faster")],
            evidence=[Evidence(claim="Left is faster", source="map")],
        ),
        actor="agent-a",
        note="anonymous entities",
    )
    prov = reconstruct_provenance(w)
    assert prov == {
        "decisions": {},
        "assumptions": {},
        "evidence": {},
        "tasks": {},
    }
    with pytest.raises(KeyError):
        explain_decision(w, "")
    assert unsupported_conclusions(w) == [
        {
            "decision_id": "",
            "text": "Go left",
            "kind": "no_evidence",
            "detail": "accepted decision cites no evidence",
        }
    ]
