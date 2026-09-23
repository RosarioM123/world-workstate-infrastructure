"""Node lock tests: the LOCKED constraint branch is now reachable.

check_constraints() has always rejected intents against LOCKED nodes,
but no code path could ever set the flag. lock_entity/unlock_entity
close that gap: the flip is a ledger-logged COMMITTED row, intents on a
locked node come back REJECTED with the lock reason, and the HTTP
routes expose the same behavior behind the API-key gate.
"""

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient

from world_engine.api.main import app
from world_engine.core import engine

TEST_KEY = "lock-test-key"


@pytest.fixture()
def ldb(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "world_lock.db"))
    engine.init_db()
    return str(tmp_path / "world_lock.db")


@pytest.fixture()
def lock_client(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "world_lock_api.db"))
    monkeypatch.setenv("WORLD_API_KEY", TEST_KEY)
    with TestClient(app) as c:
        yield c


def _intent(delta=-10.0):
    return engine.IntentTransaction(
        entity_id=engine.SEED_ENTITY_ID,
        action="ALLOCATE",
        requested_delta_capacity=delta,
        requested_delta_cash=0.0,
    )


def test_lock_rejects_intents_with_lock_reason(ldb):
    engine.lock_entity(engine.SEED_ENTITY_ID)
    entity = engine.get_entity(engine.SEED_ENTITY_ID)
    assert entity["status"] == "LOCKED"

    outcome = engine.execute_deterministic_transition(_intent())
    assert outcome["status"] == "REJECTED"
    assert "locked" in outcome["details"]["reason"].lower()

    # The rejection is still on the ledger: attempts stay auditable.
    rows = engine.get_ledger(limit=10)
    assert rows[0]["status"] == "REJECTED"


def test_unlock_restores_commits(ldb):
    engine.lock_entity(engine.SEED_ENTITY_ID)
    assert engine.execute_deterministic_transition(_intent())["status"] == "REJECTED"
    result = engine.unlock_entity(engine.SEED_ENTITY_ID)
    assert result["status"] == "ACTIVE"
    assert engine.get_entity(engine.SEED_ENTITY_ID)["status"] == "ACTIVE"
    assert engine.execute_deterministic_transition(_intent())["status"] == "COMMITTED"


def test_lock_unlock_are_ledger_events(ldb):
    lock_tx = engine.lock_entity(engine.SEED_ENTITY_ID, actor="ops")["transaction_id"]
    unlock_tx = engine.unlock_entity(engine.SEED_ENTITY_ID)["transaction_id"]
    actions = {r["transaction_id"]: r["action"] for r in engine.get_ledger(limit=10)}
    assert actions[lock_tx] == "LOCK_ENTITY"
    assert actions[unlock_tx] == "UNLOCK_ENTITY"
    assert engine.verify_chain() == (True, None)


def test_lock_unknown_entity_raises(ldb):
    with pytest.raises(ValueError, match="Unknown entity"):
        engine.lock_entity("node_does_not_exist")


def test_double_lock_and_unlock_of_active_raise(ldb):
    engine.lock_entity(engine.SEED_ENTITY_ID)
    with pytest.raises(ValueError, match="already locked"):
        engine.lock_entity(engine.SEED_ENTITY_ID)
    engine.unlock_entity(engine.SEED_ENTITY_ID)
    with pytest.raises(ValueError, match="already active"):
        engine.unlock_entity(engine.SEED_ENTITY_ID)


def test_lock_api_routes_gated_and_functional(lock_client):
    headers = {"X-API-Key": TEST_KEY}
    # No key -> 401 even though the route exists.
    assert (
        lock_client.post(f"/api/v1/entities/{engine.SEED_ENTITY_ID}/lock").status_code
        == 401
    )

    r = lock_client.post(
        f"/api/v1/entities/{engine.SEED_ENTITY_ID}/lock", headers=headers
    )
    assert r.status_code == 200
    assert r.json()["status"] == "LOCKED"

    # Intent through the API is REJECTED while locked (HTTP 200: the
    # engine never raises for policy violations).
    r = lock_client.post(
        "/api/v1/intent",
        json={
            "entity_id": engine.SEED_ENTITY_ID,
            "action": "ALLOCATE",
            "delta_capacity": -10.0,
            "delta_cash": 0.0,
        },
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "REJECTED"

    # Double-lock -> 409, unknown entity -> 404.
    r = lock_client.post(
        f"/api/v1/entities/{engine.SEED_ENTITY_ID}/lock", headers=headers
    )
    assert r.status_code == 409
    r = lock_client.post("/api/v1/entities/nope/lock", headers=headers)
    assert r.status_code == 404

    r = lock_client.post(
        f"/api/v1/entities/{engine.SEED_ENTITY_ID}/unlock", headers=headers
    )
    assert r.status_code == 200
    assert r.json()["status"] == "ACTIVE"
