"""Seed-consistency invariants for the engine's seeded entity row.

These tests pin the seed constants and the seeded entity row so the
initial ledger state cannot silently drift. The weather-derate baseline
check moved with the demo to
``examples/synthetic-logistics-demo/tests/test_weather_ingest.py``.
"""

import pytest

from world_engine.core import engine
from world_engine.core.engine import (
    SEED_CAPACITY,
    SEED_ENTITY_ID,
    SEED_LIQUIDITY,
)


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "test.db"))
    engine.init_db()
    yield


def test_seeded_entity_matches_constants():
    entity = engine.get_entity(SEED_ENTITY_ID)
    assert entity is not None
    assert entity["capacity"] == SEED_CAPACITY
    assert entity["available_liquidity"] == SEED_LIQUIDITY
    assert entity["status"] == "ACTIVE"


def test_seed_id_is_stable():
    assert SEED_ENTITY_ID == "node_rotterdam_hub"
