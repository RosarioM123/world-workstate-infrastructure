"""Tests for multi-entity support: registration, the /ledger query
endpoint, and rogue attacks pointed at a registered node.

Covers the engine, the API, and the SDK sidecar, since registration is
a contract both backends must honor identically.
"""

import json

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient

from world_engine.api.main import app
from world_engine.core import engine
from world_engine.core.engine import (
    IntentTransaction,
    execute_deterministic_transition,
    get_entity,
    get_ledger,
    register_entity,
    rogue_agent_attack,
    verify_chain,
)
from world_sdk.ledger import LocalLedger


@pytest.fixture()
def api_client(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "world_api.db"))
    with TestClient(app) as c:
        yield c


# --- Engine: registration ------------------------------------------------


def test_register_entity_success(isolated_db):
    result = register_entity("node_alpha", 500.0, 25000.0, actor="ops")
    assert result["entity_id"] == "node_alpha"
    assert result["capacity"] == 500.0
    assert result["available_liquidity"] == 25000.0
    assert result["status"] == "ACTIVE"
    assert isinstance(result["transaction_id"], int)

    entity = get_entity("node_alpha")
    assert entity is not None
    assert entity["capacity"] == 500.0
    assert entity["available_liquidity"] == 25000.0

    rows = get_ledger(entity_id="node_alpha", limit=1)
    assert len(rows) == 1
    assert rows[0]["action"] == "REGISTER_ENTITY"
    assert rows[0]["status"] == "COMMITTED"
    payload = json.loads(rows[0]["payload"])
    assert payload["initial_capacity"] == 500.0
    assert payload["actor"] == "ops"

    assert verify_chain() == (True, None)


def test_register_entity_duplicate_raises(isolated_db):
    register_entity("node_alpha", 500.0, 25000.0)
    with pytest.raises(ValueError, match="already exists"):
        register_entity("node_alpha", 100.0, 1000.0)
    # The failed registration appends nothing.
    assert get_ledger(entity_id="node_alpha", limit=10)[0]["action"] == (
        "REGISTER_ENTITY"
    )
    assert verify_chain() == (True, None)


@pytest.mark.parametrize(
    "entity_id,capacity,liquidity,actor",
    [
        ("", 100.0, 1000.0, None),  # empty id
        ("x" * 65, 100.0, 1000.0, None),  # id too long
        (123, 100.0, 1000.0, None),  # id not a string
        ("node_a", -1.0, 1000.0, None),  # negative capacity
        ("node_a", 100.0, -1.0, None),  # negative liquidity
        ("node_a", float("nan"), 1000.0, None),  # NaN capacity
        ("node_a", 100.0, float("inf"), None),  # infinite liquidity
        ("node_a", True, 1000.0, None),  # bool is not a number
        ("node_a", 100.0, 1000.0, ""),  # empty actor
    ],
)
def test_register_entity_invalid_inputs_raise(
    isolated_db, entity_id, capacity, liquidity, actor
):
    with pytest.raises(ValueError):
        register_entity(entity_id, capacity, liquidity, actor=actor)
    assert get_entity("node_a") is None


def test_intents_against_registered_entity(isolated_db):
    register_entity("node_beta", 1000.0, 50000.0)
    committed = execute_deterministic_transition(
        IntentTransaction(
            "node_beta",
            "ALLOCATE",
            requested_delta_capacity=-200.0,
            requested_delta_cash=5000.0,
        )
    )
    assert committed["status"] == "COMMITTED"
    rejected = execute_deterministic_transition(
        IntentTransaction(
            "node_beta",
            "DRAIN",
            requested_delta_capacity=-999999.0,
            requested_delta_cash=0.0,
        )
    )
    assert rejected["status"] == "REJECTED"
    entity = get_entity("node_beta")
    assert entity["capacity"] == 800.0
    assert entity["available_liquidity"] == 55000.0
    assert verify_chain() == (True, None)


def test_rogue_attack_targets_registered_entity(isolated_db):
    register_entity("node_gamma", 1000.0, 50000.0)
    outcomes = rogue_agent_attack("node_gamma")
    assert len(outcomes) == 3
    assert all(o["verdict"]["status"] == "REJECTED" for o in outcomes)
    targets = {o["intent"]["entity_id"] for o in outcomes}
    assert targets == {"node_gamma", "node_does_not_exist"}
    assert verify_chain() == (True, None)


# --- SDK: registration parity --------------------------------------------


def test_sdk_register_entity_parity(tmp_path):
    ledger = LocalLedger(tmp_path / "sdk.db")
    result = ledger.register_entity("node_delta", 300.0, 9000.0, actor="agent-7")
    assert result["status"] == "ACTIVE"

    verdict = ledger.intent(
        "node_delta", "ALLOC", deltas=(-50.0, 500.0), actor="agent-7"
    )
    assert verdict["status"] == "COMMITTED"

    state = ledger.replay_to(ledger.latest_height)
    assert state["node_delta"]["capacity"] == 250.0
    assert state["node_delta"]["available_liquidity"] == 9500.0
    assert ledger.verify_chain() == (True, None)

    with pytest.raises(ValueError, match="already exists"):
        ledger.register_entity("node_delta", 1.0, 1.0)


def test_sdk_import_rebuilds_registered_entities(tmp_path):
    source = LocalLedger(tmp_path / "source.db")
    source.register_entity("node_epsilon", 400.0, 8000.0)
    source.intent("node_epsilon", "ALLOC", deltas=(-100.0, 0.0))

    target = LocalLedger(tmp_path / "target.db")
    target.import_ledger_rows(source.get_ledger(limit=100))

    entity = target.get_entity("node_epsilon")
    assert entity is not None
    assert entity["capacity"] == 300.0
    state = target.replay_to(target.latest_height)
    assert state["node_epsilon"]["capacity"] == 300.0
    assert target.verify_chain() == (True, None)


# --- API: entity registration --------------------------------------------


def test_api_create_entity_201(api_client):
    r = api_client.post(
        "/api/v1/entities",
        json={"entity_id": "node_zeta", "capacity": 700.0, "liquidity": 7000.0},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["entity_id"] == "node_zeta"
    assert body["status"] == "ACTIVE"

    # The new node is immediately usable through the intent path.
    r = api_client.post(
        "/api/v1/intent",
        json={
            "entity_id": "node_zeta",
            "action": "ALLOCATE",
            "delta_capacity": -100.0,
            "delta_cash": 0.0,
        },
    )
    assert r.json()["status"] == "COMMITTED"


def test_api_create_entity_duplicate_409(api_client):
    payload = {"entity_id": "node_eta", "capacity": 100.0, "liquidity": 1000.0}
    assert api_client.post("/api/v1/entities", json=payload).status_code == 201
    r = api_client.post("/api/v1/entities", json=payload)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "entity_exists"


@pytest.mark.parametrize(
    "payload",
    [
        {"entity_id": "", "capacity": 100.0, "liquidity": 1000.0},
        {"entity_id": "node_x", "capacity": -5.0, "liquidity": 1000.0},
        {"entity_id": "node_x", "capacity": 100.0, "liquidity": -5.0},
    ],
)
def test_api_create_entity_invalid_400(api_client, payload):
    r = api_client.post("/api/v1/entities", json=payload)
    assert r.status_code in (400, 422)
    if r.status_code == 400:
        assert r.json()["error"]["code"] == "invalid_entity"


# --- API: ledger query endpoint ------------------------------------------


def test_api_ledger_pagination(api_client):
    for i in range(5):
        api_client.post(
            "/api/v1/intent",
            json={
                "entity_id": engine.SEED_ENTITY_ID,
                "action": f"PING_{i}",
                "delta_capacity": 0.0,
                "delta_cash": 0.0,
            },
        )
    page1 = api_client.get("/api/v1/ledger", params={"limit": 2}).json()
    assert [r["transaction_id"] for r in page1["ledger"]] == [5, 4]
    assert page1["next_cursor"] == 4

    page2 = api_client.get(
        "/api/v1/ledger", params={"limit": 2, "cursor": page1["next_cursor"]}
    ).json()
    assert [r["transaction_id"] for r in page2["ledger"]] == [3, 2]
    assert page2["next_cursor"] == 2

    page3 = api_client.get(
        "/api/v1/ledger", params={"limit": 2, "cursor": page2["next_cursor"]}
    ).json()
    assert [r["transaction_id"] for r in page3["ledger"]] == [1]
    assert page3["next_cursor"] is None


def test_api_ledger_entity_filter(api_client):
    api_client.post(
        "/api/v1/entities",
        json={"entity_id": "node_theta", "capacity": 100.0, "liquidity": 1000.0},
    )
    api_client.post(
        "/api/v1/intent",
        json={
            "entity_id": "node_theta",
            "action": "PING",
            "delta_capacity": 0.0,
            "delta_cash": 0.0,
        },
    )
    body = api_client.get("/api/v1/ledger", params={"entity_id": "node_theta"}).json()
    assert all(r["entity_id"] == "node_theta" for r in body["ledger"])
    assert {r["action"] for r in body["ledger"]} == {"REGISTER_ENTITY", "PING"}


def test_api_rogue_attack_with_entity_id(api_client):
    api_client.post(
        "/api/v1/entities",
        json={"entity_id": "node_iota", "capacity": 1000.0, "liquidity": 50000.0},
    )
    r = api_client.post("/api/v1/rogue-attack", params={"entity_id": "node_iota"})
    assert r.status_code == 200
    attacks = r.json()["attacks"]
    assert all(a["verdict"]["status"] == "REJECTED" for a in attacks)
    targets = {a["intent"]["entity_id"] for a in attacks}
    assert "node_iota" in targets
