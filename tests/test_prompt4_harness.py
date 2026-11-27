"""Prompt 4 harness: scoring rules and the scripted run.

The harness is the measurement instrument for the cross-model
handoff, so its scoring rules are pinned here. The end-to-end test
runs the scripted Agent A plus the three fresh-process Agent B runs
and asserts the measured ordering: the packet carries every item,
the journal carries the prose facts but no structure, and the
summary loses the most. These are scripted-run numbers (fixed
rule-based readers), not model results; see
experiments/prompt4/PROTOCOL.md.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from world import packet_from_state

ROOT = Path(__file__).resolve().parent.parent
PROMPT4 = ROOT / "experiments" / "prompt4"


def _load(name, path):
    """Import a script module by file path (scripts are not packages)."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def harness():
    return _load("prompt4_harness", PROMPT4 / "handoff_harness.py")


@pytest.fixture(scope="module")
def agent_b():
    return _load("prompt4_agent_b", PROMPT4 / "handoff_agent_b.py")


def _packet_answers(harness, agent_b):
    packet = packet_from_state(
        harness.state_v2(),
        state_version=4,
        world_name="prompt4-handoff",
        rejected=[
            {
                "seq": 3,
                "actor": "agent-a",
                "note": "book the full teardown | REJECTED: spend cap 5000 exceeded",
            }
        ],
    )
    return agent_b._answer_from_packet(packet)


def test_packet_answers_score_perfect(harness, agent_b):
    answers = _packet_answers(harness, agent_b)
    scored = harness.score_answers(answers)
    assert scored["continuation_success"] == 1.0
    assert scored["lost_decisions"] == 0
    assert scored["lost_evidence"] == 0
    assert scored["duplicate_work"] == 0
    assert scored["wrong_assumptions"] == 0
    assert all(score == 1.0 for score in scored["items"].values())


def test_summary_answers_score_lowest_and_lose_evidence(harness, agent_b):
    answers = agent_b._answer_from_summary(harness.build_summary(harness.state_v2()))
    scored = harness.score_answers(answers)
    assert scored["continuation_success"] == 0.3
    assert scored["lost_evidence"] == 2
    assert scored["items"]["supersession"] == 0.0
    assert scored["items"]["evidence"] == 0.0
    assert scored["items"]["known_errors"] == 0.0
    assert scored["items"]["state_version"] == 0.0
    assert scored["items"]["assumptions"] == 0.5


def test_journal_answers_score_between_packet_and_summary(harness, agent_b):
    answers = agent_b._answer_from_journal(harness.JOURNAL_TEXT)
    scored = harness.score_answers(answers)
    assert scored["continuation_success"] == 0.65
    assert scored["lost_evidence"] == 0
    assert scored["items"]["evidence"] == 1.0
    assert scored["items"]["remaining_tasks"] == 1.0
    assert scored["items"]["known_errors"] == 1.0
    assert scored["items"]["supersession"] == 0.0
    assert scored["items"]["state_version"] == 0.0


def test_journal_carries_every_ground_truth_fact(harness):
    journal = harness.JOURNAL_TEXT.lower()
    truth = harness.GROUND_TRUTH
    assert truth["objective"].lower() in journal
    for decision in truth["authoritative_decisions"] + [truth["superseded"]]:
        assert decision["text"].lower() in journal
    for assumption in truth["assumptions"]:
        assert assumption["text"].lower() in journal
    for item in truth["evidence"]:
        assert item["claim"].lower() in journal
        assert item["source"].lower() in journal
    for task in truth["remaining_tasks"] + truth["completed_tasks"]:
        assert task["title"].lower() in journal
    assert truth["next_action"].lower() in journal


def test_summary_carries_no_structure(harness):
    summary = harness.build_summary(harness.state_v2())
    lowered = summary.lower()
    assert "118 usd per kwh" not in lowered
    assert "t-collect" not in lowered
    assert "medium" not in lowered and "low" not in lowered
    assert "superseded" not in lowered
    assert "104 usd per kwh" not in lowered


def test_score_answers_partial_credit_and_wrong_assumptions(harness, agent_b):
    answers = _packet_answers(harness, agent_b)
    answers["decisions"] = [
        {**d, "id": "", "status": "unknown"} for d in answers["decisions"]
    ]
    answers["supersedes"] = []
    scored = harness.score_answers(answers)
    assert scored["items"]["authoritative_decisions"] == 0.5
    assert scored["items"]["supersession"] == 0.0
    assert scored["lost_decisions"] == 0

    answers = _packet_answers(harness, agent_b)
    for d in answers["decisions"]:
        if d["id"] == "D1":
            d["status"] = "accepted"
    scored = harness.score_answers(answers)
    assert scored["items"]["authoritative_decisions"] == 0.0
    assert scored["lost_decisions"] == 1

    answers = _packet_answers(harness, agent_b)
    for a in answers["assumptions"]:
        if a["id"] == "A1":
            a["confidence"] = "high"
        if a["id"] == "A2":
            a["status"] = "active"
    scored = harness.score_answers(answers)
    assert scored["wrong_assumptions"] == 2
    assert scored["items"]["assumptions"] == 0.5

    answers = _packet_answers(harness, agent_b)
    answers["next_task_choice"] = "t-collect"
    scored = harness.score_answers(answers)
    assert scored["duplicate_work"] == 1


def test_harness_end_to_end_writes_results(harness, tmp_path):
    out = tmp_path / "results" / "run-test.json"
    assert harness.main(["--out", str(out)]) == 0
    results = json.loads(out.read_text())
    assert results["run"] == "prompt4-scripted"
    assert results["state_version"] == 4
    conditions = results["conditions"]
    assert set(conditions) == {"packet", "summary", "journal"}
    assert conditions["packet"]["continuation_success"] == 1.0
    assert conditions["journal"]["continuation_success"] == 0.65
    assert conditions["summary"]["continuation_success"] == 0.3
    words = {c: conditions[c]["bundle_words"] for c in conditions}
    assert words["packet"] > words["journal"] > words["summary"]
    assert (tmp_path / "results" / "bundle-packet.txt").exists()
    assert (tmp_path / "results" / "answers-packet.json").exists()
