"""Tests for the synthetic logistics demo (examples/synthetic-logistics-demo/).

These cover the weather-fetch paths, the observation -> intent mapping,
and the baseline-relative derate rules. They live with the demo, not in
the product test suite, because this directory is a synthetic
stress-test domain, not the product.

Run:  python -m pytest examples/synthetic-logistics-demo/tests -q
"""

import json
import logging
import os
import sys
import urllib.error

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import weather_ingest

from world_engine.core import engine
from world_engine.core.engine import (
    SEED_CAPACITY,
    SEED_ENTITY_ID,
    IntentTransaction,
    execute_deterministic_transition,
)


@pytest.fixture()
def demo_db(tmp_path, monkeypatch):
    db = str(tmp_path / "world_demo.db")
    monkeypatch.setenv("WORLD_DB_PATH", db)
    engine.init_db()
    weather_ingest.init_observations()
    return db


# --- weather fetch ----------------------------------------------------------


class _FakeHTTPResponse:
    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _fake_fetch(monkeypatch, payload: dict):
    def _ok(request, timeout=15):
        return _FakeHTTPResponse(json.dumps(payload).encode("utf-8"))

    monkeypatch.setattr(weather_ingest.urllib.request, "urlopen", _ok)


def _sample_payload(wind: float = 80.0) -> dict:
    return {
        "current": {
            "temperature_2m": 9.5,
            "wind_speed_10m": wind,
            "weather_code": 2,
            "time": "2026-09-21T12:00",
        }
    }


def test_fetch_weather_success(monkeypatch):
    _fake_fetch(monkeypatch, _sample_payload())
    raw, synthetic = weather_ingest.fetch_rotterdam_weather()
    assert synthetic is False
    assert raw["current"]["wind_speed_10m"] == 80.0


def test_fetch_weather_offline_fallback_is_labeled(monkeypatch):
    def _down(request, timeout=15):
        raise urllib.error.URLError("no network in test")

    monkeypatch.setattr(weather_ingest.urllib.request, "urlopen", _down)
    raw, synthetic = weather_ingest.fetch_rotterdam_weather()
    assert synthetic is True
    assert raw["current"]["wind_speed_10m"] == 62.0
    assert "_fallback_reason" in raw


# --- CLI --------------------------------------------------------------------


def test_ingest_main_dry_run(demo_db, monkeypatch, caplog):
    _fake_fetch(monkeypatch, _sample_payload(wind=10.0))
    monkeypatch.setattr(sys, "argv", ["weather_ingest", "--dry-run"])
    with caplog.at_level(logging.INFO):
        weather_ingest.main()
    assert "REVENUE_TICK" in caplog.text  # calm weather earns
    assert "DRY_RUN" in caplog.text
    # Dry run writes nothing to the ledger.
    assert engine.get_ledger(limit=10) == []


def test_ingest_main_demo_runs_rogue_attack(demo_db, monkeypatch, caplog):
    _fake_fetch(monkeypatch, _sample_payload(wind=62.0))
    monkeypatch.setattr(sys, "argv", ["weather_ingest", "--demo"])
    with caplog.at_level(logging.INFO):
        weather_ingest.main()
    assert "WIND_DERATE" in caplog.text
    assert "ROGUE AGENT ATTACK" in caplog.text
    assert "ROGUE_DRAIN: REJECTED" in caplog.text


# --- derate rules -----------------------------------------------------------


def test_weather_derate_uses_baseline_not_current_capacity(demo_db):
    # Drain capacity first; the derate must still be computed from the
    # 1000.0 baseline so repeated ticks do not compound geometrically.
    execute_deterministic_transition(
        IntentTransaction("node_rotterdam_hub", "DRAIN", -500.0, 0.0)
    )
    intent = weather_ingest.weather_to_intent({"wind_speed_kmh": 60.0})
    assert intent.action == "WIND_DERATE"
    assert intent.requested_delta_capacity == -round(0.15 * 1000.0, 2)
    assert intent.requested_delta_capacity == -150.0


def test_weather_derate_deterministic():
    obs = {"wind_speed_kmh": 80.0}
    first = weather_ingest.weather_to_intent(obs)
    second = weather_ingest.weather_to_intent(obs)
    assert first.action == second.action == "STORM_DERATE"
    assert first.requested_delta_capacity == second.requested_delta_capacity == -300.0


def test_ingest_baseline_matches_engine_seed():
    assert weather_ingest.BASELINE_CAPACITY == SEED_CAPACITY == 1000.0
    assert weather_ingest.HUB_ENTITY_ID == SEED_ENTITY_ID
