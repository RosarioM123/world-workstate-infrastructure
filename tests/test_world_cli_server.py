"""Tests for the `world` CLI, the HTTP server, and the transcript producer."""

import json

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient

from world import World
from world.cli import main
from world.invariants import no_negative
from world.producers import import_transcript
from world.server import create_app


@pytest.fixture()
def store(tmp_path):
    return str(tmp_path)


def cli(store, *argv):
    return main(["--dir", store, *argv])


def test_cli_full_roundtrip(tmp_path, store, capsys):
    state_file = tmp_path / "s1.json"
    state_file.write_text('{"tasks": ["a"]}')
    assert cli(store, "init", "demo") == 0
    assert (
        cli(store, "update", "demo", "--file", str(state_file), "--actor", "cli") == 0
    )

    capsys.readouterr()
    assert cli(store, "state", "demo") == 0
    assert json.loads(capsys.readouterr().out) == {"tasks": ["a"]}

    assert cli(store, "checkpoint", "demo", "v1") == 0

    state_file.write_text('{"tasks": []}')
    assert cli(store, "update", "demo", "--file", str(state_file)) == 0
    assert cli(store, "resume", "demo", "v1", "--actor", "cli2") == 0

    capsys.readouterr()
    assert cli(store, "state", "demo") == 0
    assert json.loads(capsys.readouterr().out) == {"tasks": ["a"]}

    assert cli(store, "verify", "demo") == 0
    assert capsys.readouterr().out.strip() == "ok"

    assert cli(store, "history", "demo") == 0
    hist = json.loads(capsys.readouterr().out)
    assert [h["status"] for h in hist] == ["COMMITTED"] * 3
    assert hist[0]["actor"] == "cli"

    assert cli(store, "checkpoints", "demo") == 0
    assert json.loads(capsys.readouterr().out)[0]["name"] == "v1"


def test_cli_update_from_stdin(store, capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", _Stdin('{"k": "v"}'))
    assert cli(store, "init", "s") == 0
    assert cli(store, "update", "s", "--file", "-") == 0
    capsys.readouterr()
    assert cli(store, "state", "s") == 0
    assert json.loads(capsys.readouterr().out) == {"k": "v"}


class _Stdin:
    def __init__(self, text):
        self._text = text

    def read(self):
        return self._text


def test_cli_state_at_checkpoint_and_version(store, tmp_path, capsys):
    f = tmp_path / "s.json"
    cli(store, "init", "t")
    f.write_text('{"n": 1}')
    cli(store, "update", "t", "--file", str(f))
    cli(store, "checkpoint", "t", "c1")
    f.write_text('{"n": 2}')
    cli(store, "update", "t", "--file", str(f))

    capsys.readouterr()
    assert cli(store, "state", "t", "--checkpoint", "c1") == 0
    assert json.loads(capsys.readouterr().out) == {"n": 1}
    assert cli(store, "state", "t", "--version", "1") == 0
    assert json.loads(capsys.readouterr().out) == {"n": 1}
    assert cli(store, "state", "t", "--checkpoint", "nope") == 1


def test_cli_verify_fails_on_tamper(store, tmp_path):
    cli(store, "init", "tamper")
    w = World("tamper", dir=store)
    w.update({"a": 1})
    import sqlite3

    cx = sqlite3.connect(w.path)
    cx.execute("UPDATE versions SET hash = 'forged' WHERE seq = 1")
    cx.commit()
    cx.close()
    assert cli(store, "verify", "tamper") == 1


def test_import_transcript_is_idempotent(store):
    w = World("notes", dir=store)
    text = (
        "Agent A: Decision: we will use sqlite for storage because it is simple "
        "and reliable enough for the prototype.\n"
        "Agent B: Note: remember to add tests for the new module before merging "
        "the changes today.\n"
    )
    seq = import_transcript(w, text, actor="agent-a")
    assert seq == 1
    doc = w.state()
    assert doc["transcript"]["decisions"][0]["speaker"] == "Agent A"
    assert "sqlite" in doc["transcript"]["decisions"][0]["text"]
    assert len(doc["transcript"]["notes"]) == 1
    # Re-importing the same text is a no-op.
    assert import_transcript(w, text, actor="agent-a") == 1
    assert w.version == 1
    assert w.history()[0]["actor"] == "agent-a"


def test_import_transcript_empty_text_is_noop(store):
    w = World("empty", dir=store)
    assert import_transcript(w, "hi") == 0
    assert w.version == 0


def make_client(store, **kwargs):
    kwargs.setdefault("dir", store)
    return TestClient(create_app("srv", **kwargs))


def test_server_health_and_open_writes(store):
    c = make_client(store)  # no key: fail-open
    assert c.get("/health").json() == {"ok": True, "world": "srv", "version": 0}
    r = c.post("/v1/update", json={"state": {"a": 1}, "actor": "api"})
    assert r.status_code == 200
    assert r.json() == {"seq": 1, "status": "COMMITTED"}
    assert c.get("/v1/state").json() == {"version": 1, "state": {"a": 1}}


def test_server_api_key_gate(store):
    c = make_client(store, api_key="secret")
    assert c.post("/v1/update", json={"state": {}}).status_code == 401
    bad = {"X-API-Key": "wrong"}
    assert c.post("/v1/update", json={"state": {}}, headers=bad).status_code == 401
    good = {"X-API-Key": "secret"}
    assert (
        c.post("/v1/update", json={"state": {"a": 1}}, headers=good).status_code == 200
    )
    # Reads stay public.
    assert c.get("/v1/state").status_code == 200
    assert c.get("/v1/verify").json() == {"ok": True}


def test_server_invariant_violation_is_422_with_evidence(store):
    c = make_client(store, invariants=[no_negative("bal")])
    assert c.post("/v1/update", json={"state": {"bal": 10}}).status_code == 200
    r = c.post("/v1/update", json={"state": {"bal": -1}, "note": "oops"})
    assert r.status_code == 422
    body = r.json()
    assert body["status"] == "REJECTED" and body["seq"] == 2
    assert "no_negative" in body["reason"]
    # State untouched; rejection visible in history.
    assert c.get("/v1/state").json()["state"] == {"bal": 10}
    hist = c.get("/v1/history").json()["history"]
    assert [h["status"] for h in hist] == ["COMMITTED", "REJECTED"]


def test_server_conflict_checkpoint_resume(store):
    c = make_client(store)
    c.post("/v1/update", json={"state": {"n": 1}})
    r = c.post("/v1/update", json={"state": {"n": 2}, "expected_version": 0})
    assert r.status_code == 409
    assert c.post("/v1/checkpoint", json={"name": "c1"}).json() == {
        "name": "c1",
        "seq": 1,
    }
    assert c.post("/v1/checkpoint", json={"name": "c1"}).status_code == 400
    c.post("/v1/update", json={"state": {"n": 5}})
    r = c.post("/v1/resume", json={"name": "c1"})
    assert r.json() == {"seq": 3, "status": "COMMITTED"}
    assert c.get("/v1/state", params={"checkpoint": "c1"}).json() == {
        "version": 1,
        "state": {"n": 1},
    }
    assert c.get("/v1/state", params={"version": 2}).json()["state"] == {"n": 5}
    assert c.post("/v1/resume", json={"name": "nope"}).status_code == 404
    assert len(c.get("/v1/checkpoints").json()["checkpoints"]) == 1


def test_server_rate_limit(store):
    c = make_client(store, write_limit_per_min=2)
    for _ in range(2):
        assert c.post("/v1/update", json={"state": {"a": 1}}).status_code == 200
    r = c.post("/v1/update", json={"state": {"a": 1}})
    assert r.status_code == 429
    assert r.json()["error"] == "rate_limited"
    # Reads are not rate-limited.
    assert c.get("/v1/state").status_code == 200
