"""Regression tests for the WORLD Day 1 hardening pass.

Covers: non-finite intent rejection, unknown-entity audit logging,
rogue-attack behavior, baseline-relative derates, and ledger hash linkage.

Run:  pytest
Isolation: every test points the engine at a throwaway SQLite file via
WORLD_DB_PATH, so the real world_state.db is never touched.
"""

import math

import pytest

import engine
import ingest
from engine import IntentTransaction, execute_deterministic_transition


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "test.db"))
    engine.init_db()
    ingest.init_observations()
    yield


def test_nan_capacity_delta_rejected_before_constraints():
    with pytest.raises(ValueError, match="must be finite"):
        execute_deterministic_transition(
            IntentTransaction("node_rotterdam_hub", "NAN_PROBE",
                              float("nan"), 0.0)
        )
    # State untouched, nothing half-written.
    entity = engine.get_entity("node_rotterdam_hub")
    assert entity["capacity"] == 1000.0
    assert entity["available_liquidity"] == 50000.0


def test_inf_cash_delta_rejected():
    with pytest.raises(ValueError, match="must be finite"):
        execute_deterministic_transition(
            IntentTransaction("node_rotterdam_hub", "INF_PROBE",
                              0.0, float("inf"))
        )


def test_non_numeric_delta_rejected():
    with pytest.raises(ValueError, match="must be a number"):
        execute_deterministic_transition(
            IntentTransaction("node_rotterdam_hub", "TYPE_PROBE",
                              "100", 0.0)
        )


def test_unknown_entity_rejected_and_logged():
    result = execute_deterministic_transition(
        IntentTransaction("node_does_not_exist", "SPOOF",
                          10.0, 10.0)
    )
    assert result["status"] == "REJECTED"
    assert "Unknown entity" in result["details"]["reason"]
    rows = engine.get_ledger("node_does_not_exist")
    assert len(rows) == 1
    assert rows[0]["status"] == "REJECTED"


def test_rogue_attack_all_rejected_no_exception():
    outcomes = ingest.rogue_agent_attack()
    assert len(outcomes) == 3
    assert all(o["verdict"]["status"] == "REJECTED" for o in outcomes)
    # The spoof attempt is on the ledger, not swallowed by an exception.
    spoof_rows = engine.get_ledger("node_does_not_exist")
    assert len(spoof_rows) == 1


def test_valid_intent_still_commits():
    result = execute_deterministic_transition(
        IntentTransaction("node_rotterdam_hub", "ALLOCATE",
                          -200.0, 5000.0)
    )
    assert result["status"] == "COMMITTED"
    entity = engine.get_entity("node_rotterdam_hub")
    assert entity["capacity"] == 800.0
    assert entity["available_liquidity"] == 55000.0


def test_overspend_rejected_and_state_unchanged():
    result = execute_deterministic_transition(
        IntentTransaction("node_rotterdam_hub", "DRAIN",
                          -5000.0, 0.0)
    )
    assert result["status"] == "REJECTED"
    entity = engine.get_entity("node_rotterdam_hub")
    assert entity["capacity"] == 1000.0


def test_weather_derate_uses_baseline_not_current_capacity():
    # Drain capacity first; the derate must still be computed from the
    # 1000.0 baseline so repeated ticks do not compound geometrically.
    execute_deterministic_transition(
        IntentTransaction("node_rotterdam_hub", "DRAIN",
                          -500.0, 0.0)
    )
    intent = ingest.weather_to_intent({"wind_speed_kmh": 60.0})
    assert intent.action == "WIND_DERATE"
    assert intent.requested_delta_capacity == -round(0.15 * 1000.0, 2)
    assert intent.requested_delta_capacity == -150.0


def test_weather_derate_deterministic():
    obs = {"wind_speed_kmh": 80.0}
    first = ingest.weather_to_intent(obs)
    second = ingest.weather_to_intent(obs)
    assert first.action == second.action == "STORM_DERATE"
    assert (first.requested_delta_capacity ==
            second.requested_delta_capacity == -300.0)


def test_ledger_hash_chain_links():
    execute_deterministic_transition(
        IntentTransaction("node_rotterdam_hub", "A", -10.0, 0.0))
    execute_deterministic_transition(
        IntentTransaction("node_rotterdam_hub", "B", -10.0, 0.0))
    rows = engine.get_ledger("node_rotterdam_hub", limit=2)
    newest, older = rows[0], rows[1]
    assert newest["previous_hash"] == older["record_hash"]
    assert older["previous_hash"] is None  # genesis row
    assert len(newest["record_hash"]) == 64


def test_rejected_attempts_do_not_mutate_state():
    before = engine.get_entity("node_rotterdam_hub")
    execute_deterministic_transition(
        IntentTransaction("node_rotterdam_hub", "DRAIN",
                          -999999.0, -99999999.0))
    after = engine.get_entity("node_rotterdam_hub")
    assert before == after
    assert math.isfinite(after["capacity"])
    assert math.isfinite(after["available_liquidity"])
