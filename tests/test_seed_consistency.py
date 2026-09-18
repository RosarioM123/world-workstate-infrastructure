"""Seed-consistency invariants between engine.py and ingest.py.

The weather derate rules are computed against BASELINE_CAPACITY; if that
ever drifted from the engine's SEED_CAPACITY, repeated ingestion ticks
would silently derate against the wrong baseline. These tests pin the
shared constants and the seeded entity row so the two modules cannot
silently disagree.
"""

import pytest

import engine
import ingest
from engine import SEED_CAPACITY, SEED_ENTITY_ID, SEED_LIQUIDITY


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "test.db"))
    engine.init_db()
    yield


def test_ingest_baseline_matches_engine_seed():
    assert ingest.BASELINE_CAPACITY == SEED_CAPACITY == 1000.0


def test_seeded_entity_matches_constants():
    entity = engine.get_entity(SEED_ENTITY_ID)
    assert entity is not None
    assert entity["capacity"] == SEED_CAPACITY
    assert entity["available_liquidity"] == SEED_LIQUIDITY
    assert entity["status"] == "ACTIVE"


def test_seed_id_is_stable():
    assert SEED_ENTITY_ID == "node_rotterdam_hub"
    assert ingest.HUB_ENTITY_ID == SEED_ENTITY_ID
