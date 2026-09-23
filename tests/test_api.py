"""API integration tests via FastAPI TestClient.

Covers the canonical /api/v1 routes, the deprecated unversioned aliases,
the uniform error envelope, and request-ID propagation. The lifespan hook
initializes the ledger, so WORLD_DB_PATH must be set before the
TestClient context is entered.
"""

import pytest
from fastapi.testclient import TestClient

from world_engine.api.main import app
from world_engine.core import engine


@pytest.fixture()
def api_client(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "world_api.db"))
    with TestClient(app) as c:
        yield c


def _intent(action="ALLOCATE", delta_capacity=-50.0, delta_cash=0.0):
    return {
        "entity_id": engine.SEED_ENTITY_ID,
        "action": action,
        "delta_capacity": delta_capacity,
        "delta_cash": delta_cash,
    }


def test_v1_post_intent_commits_and_lands_in_ledger(api_client):
    r = api_client.post("/api/v1/intent", json=_intent())
    assert r.status_code == 200
    assert r.json()["status"] == "COMMITTED"
    assert "X-Request-ID" in r.headers

    rows = engine.get_ledger(limit=5)
    assert any(
        row["action"] == "ALLOCATE" and row["status"] == "COMMITTED" for row in rows
    )


def test_v1_rejected_intent_is_a_verdict_not_an_error(api_client):
    # Overspending is a REJECTED verdict (200), not an HTTP error: the
    # attempt is on the ledger either way.
    r = api_client.post("/api/v1/intent", json=_intent(delta_cash=-99999999.0))
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "REJECTED"


def test_v1_intent_records_actor_kind_and_idempotency_key(api_client):
    body = _intent()
    body.update(
        {
            "actor": "mind-planner-7",
            "kind": "EXTERNAL_EFFECT",
            "idempotency_key": "api-k1",
        }
    )
    r = api_client.post("/api/v1/intent", json=body)
    assert r.status_code == 200
    assert r.json()["status"] == "COMMITTED"

    # Retry with the same key: same verdict, no new row.
    r2 = api_client.post("/api/v1/intent", json=body)
    assert r2.status_code == 200
    assert r2.json()["status"] == "COMMITTED"

    import json as _json

    rows = engine.get_ledger(limit=5)
    assert len(rows) == 1
    payload = _json.loads(rows[0]["payload"])
    assert payload["intent"]["actor"] == "mind-planner-7"
    assert payload["intent"]["kind"] == "EXTERNAL_EFFECT"
    assert payload["intent"]["idempotency_key"] == "api-k1"


def test_v1_intent_rejects_bad_kind(api_client):
    body = _intent()
    body["kind"] = "SIDE_EFFECT"
    r = api_client.post("/api/v1/intent", json=body)
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "invalid_intent"


def test_v1_malformed_intent_returns_error_envelope(api_client):
    r = api_client.post("/api/v1/intent", json={"entity_id": "x"})
    assert r.status_code == 422
    error = r.json()["error"]
    assert error["code"] == "validation_error"
    assert error["message"]
    assert error["request_id"] == r.headers["X-Request-ID"]


def test_v1_non_finite_delta_returns_invalid_intent_envelope(api_client):
    # NaN sails through JSON and pydantic, so the engine's own finite
    # check is what rejects it: a 400 with the semantic error code.
    r = api_client.post(
        "/api/v1/intent",
        content=(
            '{"entity_id": "' + engine.SEED_ENTITY_ID + '", "action": "X", '
            '"delta_capacity": NaN, "delta_cash": 0.0}'
        ),
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 400
    error = r.json()["error"]
    assert error["code"] == "invalid_intent"
    assert "finite" in error["message"]


def test_v1_get_state(api_client):
    r = api_client.get("/api/v1/state")
    assert r.status_code == 200
    body = r.json()
    assert any(e["entity_id"] == engine.SEED_ENTITY_ID for e in body["entities"])
    assert isinstance(body["recent_ledger"], list)


def test_v1_rogue_attack_all_rejected(api_client):
    r = api_client.post("/api/v1/rogue-attack")
    assert r.status_code == 200
    attacks = r.json()["attacks"]
    assert len(attacks) == 3
    assert all(a["verdict"]["status"] == "REJECTED" for a in attacks)


def test_deprecated_unversioned_alias_still_works(api_client):
    r = api_client.post("/api/intent", json=_intent(action="ALIAS_CHECK"))
    assert r.status_code == 200
    assert r.json()["status"] == "COMMITTED"


def test_unknown_route_returns_error_envelope(api_client):
    r = api_client.get("/api/v1/does-not-exist")
    assert r.status_code == 404
    error = r.json()["error"]
    assert error["code"] == "not_found"
    assert error["request_id"]


def test_request_id_is_echoed_when_supplied(api_client):
    r = api_client.get("/api/v1/state", headers={"X-Request-ID": "demo-123"})
    assert r.headers["X-Request-ID"] == "demo-123"


def test_v1_intent_rejects_empty_idempotency_key(api_client):
    body = _intent()
    body["idempotency_key"] = ""
    r = api_client.post("/api/v1/intent", json=body)
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "invalid_intent"
