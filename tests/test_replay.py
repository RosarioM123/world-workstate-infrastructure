"""Engine-side deterministic replay tests.

replay_ledger() is the function behind the README's "materialized state
is rebuilt deterministically from the ledger" claim: it re-applies every
ledger row from the genesis seed in transaction-ID order and compares
the rebuilt entity map against the live tables. apply=True repairs a
corrupted materialized state from the ledger.
"""

import json
import sqlite3

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient

from world_engine.api.main import app
from world_engine.core import engine
from world_engine.ingestion import transcript as ti


@pytest.fixture()
def rdb(tmp_path, monkeypatch):
    db = str(tmp_path / "world_replay.db")
    monkeypatch.setenv("WORLD_DB_PATH", db)
    engine.init_db()
    return db


def _workload():
    """A mixed history: registration, intents, a lock cycle, a rejection."""
    engine.register_entity("node_alpha", 500.0, 500.0)
    engine.execute_deterministic_transition(
        engine.IntentTransaction("node_alpha", "ALLOCATE", -100.0, 50.0)
    )
    engine.execute_deterministic_transition(
        engine.IntentTransaction(
            engine.SEED_ENTITY_ID, "ALLOCATE", -999999.0, 0.0
        )  # REJECTED
    )
    engine.lock_entity("node_alpha")
    engine.unlock_entity("node_alpha")
    engine.execute_deterministic_transition(
        engine.IntentTransaction("node_alpha", "ALLOCATE", -25.0, 0.0)
    )


def test_replay_verifies_clean_history(rdb):
    _workload()
    report = engine.replay_ledger()
    assert report["chain_ok"] is True
    assert report["bad_transaction_id"] is None
    assert report["rows_replayed"] == len(engine.get_ledger(limit=10000))
    assert report["entities_rebuilt"] == 2  # seed + node_alpha
    assert report["divergences"] == []
    assert report["skipped_actions"] == []
    assert report["applied"] is False


def test_replay_verify_touches_nothing(rdb):
    _workload()
    before = engine.get_entity("node_alpha")
    engine.replay_ledger()
    after = engine.get_entity("node_alpha")
    assert before == after


def test_replay_detects_corrupted_state_and_repairs(rdb):
    _workload()
    with sqlite3.connect(rdb) as conn:
        conn.execute(
            "UPDATE entities SET capacity = 1.0 WHERE entity_id = 'node_alpha'"
        )
        conn.commit()

    report = engine.replay_ledger()
    assert report["chain_ok"] is True
    assert report["applied"] is False
    assert {
        "entity_id": "node_alpha",
        "field": "capacity",
        "live": 1.0,
        "replayed": 375.0,
    } in report["divergences"]

    repair = engine.replay_ledger(apply=True)
    assert repair["applied"] is True
    assert repair["divergences"] == []
    assert engine.get_entity("node_alpha")["capacity"] == 375.0
    # Repair is state-only: the ledger is untouched and still verifies.
    assert engine.verify_chain() == (True, None)
    assert engine.replay_ledger()["divergences"] == []


def test_replay_aborts_on_broken_chain(rdb):
    _workload()
    with sqlite3.connect(rdb) as conn:
        conn.execute("UPDATE state_ledger SET payload = '{}' WHERE transaction_id = 2")
        conn.commit()

    report = engine.replay_ledger()
    assert report["chain_ok"] is False
    assert report["bad_transaction_id"] == 2
    assert report["applied"] is False

    repair = engine.replay_ledger(apply=True)
    assert repair["applied"] is False  # never repair from a broken chain


def test_replay_handles_lock_rows(rdb):
    engine.register_entity("node_beta", 100.0, 100.0)
    engine.lock_entity("node_beta")
    report = engine.replay_ledger()
    assert report["chain_ok"] is True
    assert report["divergences"] == []
    assert engine.get_entity("node_beta")["status"] == "LOCKED"


def test_replay_after_transcript_import(rdb):
    # transcript-knowledge has no REGISTER row: replay must materialize
    # it from each row's recorded pre-image.
    ti.import_transcript("Rosario: Decision: we will ship this week.\n")
    report = engine.replay_ledger()
    assert report["chain_ok"] is True
    assert report["divergences"] == []
    assert report["entities_rebuilt"] == 2  # seed + transcript-knowledge


def test_replay_endpoint_is_public_read(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "world_replay_api.db"))
    monkeypatch.delenv("WORLD_API_KEY", raising=False)
    with TestClient(app) as c:
        r = c.get("/api/v1/replay")
        assert r.status_code == 200
        body = r.json()
        assert body["chain_ok"] is True
        assert body["divergences"] == []
        assert body["applied"] is False


def test_replay_report_json_serializable(rdb):
    _workload()
    json.dumps(engine.replay_ledger())  # must survive the API boundary
