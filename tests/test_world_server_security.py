"""Security tests for the `world` primitive HTTP server (src/world/server.py).

Prompt 3 F2: authentication fails closed. With no API key configured
and no explicit opt-in, write routes return 401; the pre-Prompt-3
fail-open default (a startup warning, then open writes) is gone.
Reads stay open in every mode. The legacy engine's API in
tests/test_api_security.py has its own env-var gate and is out of
scope here.
"""

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient

from world import World
from world.server import create_app

WRITE_ROUTES = [
    ("/v1/update", {"state": {"a": 1}, "actor": "mallory"}),
    ("/v1/checkpoint", {"name": "cp"}),
    ("/v1/resume", {"name": "cp"}),
]


@pytest.fixture()
def store(tmp_path):
    return str(tmp_path)


def _client(store, **kwargs):
    kwargs.setdefault("dir", store)
    return TestClient(create_app("srv", **kwargs))


def test_no_key_no_flag_writes_fail_closed(store):
    c = _client(store)
    for path, body in WRITE_ROUTES:
        r = c.post(path, json=body)
        assert r.status_code == 401, path
        assert r.json()["error"] == "unauthorized"
    # Nothing was written by the rejected attempts.
    assert World("srv", dir=store).version == 0


def test_no_key_no_flag_reads_stay_open(store):
    World("srv", dir=store).update({"a": 1}, actor="setup")
    c = _client(store)
    assert c.get("/health").status_code == 200
    assert c.get("/v1/state").status_code == 200
    assert c.get("/v1/history").status_code == 200
    assert c.get("/v1/verify").json() == {"ok": True}


def test_no_key_with_flag_preserves_open_writes(store):
    c = _client(store, allow_unauthenticated_writes=True)
    r = c.post("/v1/update", json={"state": {"a": 1}, "actor": "api"})
    assert r.status_code == 200
    assert r.json() == {"seq": 1, "status": "COMMITTED"}
    assert c.post("/v1/checkpoint", json={"name": "cp"}).status_code == 200
    assert c.post("/v1/resume", json={"name": "cp"}).status_code == 200


def test_key_set_still_gates_and_flag_is_irrelevant(store):
    c = _client(store, api_key="secret", allow_unauthenticated_writes=True)
    assert c.post("/v1/update", json={"state": {}}).status_code == 401
    good = {"X-API-Key": "secret"}
    assert (
        c.post("/v1/update", json={"state": {"a": 1}}, headers=good).status_code == 200
    )


def test_fail_closed_attempts_leave_no_verdict_rows(store):
    """A 401 short-circuits in the guard, before judgment: the verdict
    log must not gain REJECTED rows for unauthenticated requests."""
    c = _client(store)
    c.post("/v1/update", json={"state": {"a": 1}})
    assert World("srv", dir=store).history() == []


# --- Prompt 3 F4: server-side actor binding ---------------------------------


def test_configured_actor_overrides_body_actor(store):
    c = _client(store, allow_unauthenticated_writes=True, actor="svc-research")
    r = c.post("/v1/update", json={"state": {"a": 1}, "actor": "mallory"})
    assert r.status_code == 200
    hist = World("srv", dir=store).history()
    assert hist[0]["actor"] == "svc-research"
    # The override covers resume as well.
    c.post("/v1/checkpoint", json={"name": "cp"})
    c.post("/v1/resume", json={"name": "cp", "actor": "mallory"})
    hist = World("srv", dir=store).history()
    assert hist[-1]["actor"] == "svc-research"


def test_unconfigured_actor_preserves_body_actor(store):
    c = _client(store, allow_unauthenticated_writes=True)
    c.post("/v1/update", json={"state": {"a": 1}, "actor": "agent-a"})
    hist = World("srv", dir=store).history()
    assert hist[0]["actor"] == "agent-a"
