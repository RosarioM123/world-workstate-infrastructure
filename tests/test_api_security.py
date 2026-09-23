"""Security tests: API-key gate on write routes + per-IP rate limiting.

Auth is disabled when WORLD_API_KEY is unset (the local-dev default), so
the existing suite keeps passing untouched. When the key is set, the
state-mutating routes (POST /intent, /entities, /rogue-attack, including
the deprecated /api/* aliases) require it as X-API-Key; reads stay open.
"""

import pytest
from fastapi.testclient import TestClient

from world_engine.api import middleware as mw
from world_engine.api.main import app
from world_engine.core import engine

_TEST_KEY = "demo-key-123"


@pytest.fixture()
def api_client(tmp_path, monkeypatch):
    """No WORLD_API_KEY: the local-dev default, everything open."""
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "world_sec.db"))
    monkeypatch.delenv("WORLD_API_KEY", raising=False)
    monkeypatch.setenv("WORLD_RATE_LIMIT_ENABLED", "1")
    mw.reset_rate_limiter()
    with TestClient(app) as c:
        yield c
    mw.reset_rate_limiter()


@pytest.fixture()
def authed_client(tmp_path, monkeypatch):
    """WORLD_API_KEY set: writes require the key, reads stay open."""
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "world_sec_auth.db"))
    monkeypatch.setenv("WORLD_API_KEY", _TEST_KEY)
    monkeypatch.setenv("WORLD_RATE_LIMIT_ENABLED", "1")
    mw.reset_rate_limiter()
    with TestClient(app) as c:
        yield c
    mw.reset_rate_limiter()


def _intent():
    return {
        "entity_id": engine.SEED_ENTITY_ID,
        "action": "ALLOCATE",
        "delta_capacity": -10.0,
        "delta_cash": 0.0,
    }


def _key_headers(key=_TEST_KEY):
    return {"X-API-Key": key}


# --- Auth: open by default -------------------------------------------------


def test_write_routes_open_without_api_key(api_client):
    assert api_client.post("/api/v1/intent", json=_intent()).status_code == 200
    r = api_client.post(
        "/api/v1/entities",
        json={"entity_id": "node_open", "capacity": 100.0, "liquidity": 100.0},
    )
    assert r.status_code == 201
    assert api_client.post("/api/v1/rogue-attack").status_code == 200


# --- Auth: gate enforced when the key is configured ------------------------


def test_write_routes_reject_missing_key(authed_client):
    for method, path, kwargs in [
        ("post", "/api/v1/intent", {"json": _intent()}),
        (
            "post",
            "/api/v1/entities",
            {"json": {"entity_id": "n", "capacity": 1.0, "liquidity": 1.0}},
        ),
        ("post", "/api/v1/rogue-attack", {}),
        # Deprecated aliases hit the same handlers, so they are gated too.
        ("post", "/api/intent", {"json": _intent()}),
    ]:
        r = authed_client.request(method, path, **kwargs)
        assert r.status_code == 401, path
        error = r.json()["error"]
        assert error["code"] == "unauthorized"
        assert error["request_id"] == r.headers["X-Request-ID"]


def test_write_routes_reject_wrong_key(authed_client):
    r = authed_client.post(
        "/api/v1/intent", json=_intent(), headers=_key_headers("wrong-key")
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "unauthorized"


def test_write_routes_accept_correct_key(authed_client):
    r = authed_client.post("/api/v1/intent", json=_intent(), headers=_key_headers())
    assert r.status_code == 200
    assert r.json()["status"] == "COMMITTED"
    r = authed_client.post(
        "/api/v1/entities",
        json={"entity_id": "node_gated", "capacity": 50.0, "liquidity": 50.0},
        headers=_key_headers(),
    )
    assert r.status_code == 201
    r = authed_client.post("/api/v1/rogue-attack", headers=_key_headers())
    assert r.status_code == 200


def test_read_routes_stay_open_when_key_configured(authed_client):
    assert authed_client.get("/api/v1/state").status_code == 200
    assert authed_client.get("/api/v1/ledger").status_code == 200
    assert authed_client.get("/health").status_code == 200
    assert authed_client.get("/demo").status_code == 200


def test_failed_auth_writes_no_ledger_row(authed_client):
    before = len(engine.get_ledger(limit=1000))
    authed_client.post("/api/v1/intent", json=_intent())  # 401, no key
    after = len(engine.get_ledger(limit=1000))
    assert after == before


# --- Rate limiting ----------------------------------------------------------


def test_rate_limit_blocks_burst_on_rogue_attack(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "world_rl.db"))
    monkeypatch.delenv("WORLD_API_KEY", raising=False)
    monkeypatch.setenv("WORLD_RATE_LIMIT_ROGUE_PER_MIN", "2")
    mw.reset_rate_limiter()
    try:
        with TestClient(app) as c:
            assert c.post("/api/v1/rogue-attack").status_code == 200
            assert c.post("/api/v1/rogue-attack").status_code == 200
            r = c.post("/api/v1/rogue-attack")
            assert r.status_code == 429
            error = r.json()["error"]
            assert error["code"] == "rate_limited"
            assert error["request_id"] == r.headers["X-Request-ID"]
            assert "Retry-After" in r.headers
    finally:
        mw.reset_rate_limiter()


def test_rate_limit_does_not_touch_reads(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "world_rl2.db"))
    monkeypatch.delenv("WORLD_API_KEY", raising=False)
    monkeypatch.setenv("WORLD_RATE_LIMIT_INTENT_PER_MIN", "1")
    mw.reset_rate_limiter()
    try:
        with TestClient(app) as c:
            for _ in range(5):
                assert c.get("/api/v1/state").status_code == 200
            # ...but the write route is now gated by the tiny limit.
            assert c.post("/api/v1/intent", json=_intent()).status_code == 200
            assert c.post("/api/v1/intent", json=_intent()).status_code == 429
    finally:
        mw.reset_rate_limiter()


def test_rate_limit_can_be_disabled(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "world_rl3.db"))
    monkeypatch.delenv("WORLD_API_KEY", raising=False)
    monkeypatch.setenv("WORLD_RATE_LIMIT_ENABLED", "0")
    monkeypatch.setenv("WORLD_RATE_LIMIT_ROGUE_PER_MIN", "1")
    mw.reset_rate_limiter()
    try:
        with TestClient(app) as c:
            for _ in range(3):
                assert c.post("/api/v1/rogue-attack").status_code == 200
    finally:
        mw.reset_rate_limiter()
