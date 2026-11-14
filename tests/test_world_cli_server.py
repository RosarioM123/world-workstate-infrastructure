"""Tests for the `world` CLI, the HTTP server, and the transcript producer."""

import json
import sqlite3

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
    # No key, but unauthenticated writes explicitly allowed (local dev).
    c = make_client(store, allow_unauthenticated_writes=True)
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
    c = make_client(
        store, invariants=[no_negative("bal")], allow_unauthenticated_writes=True
    )
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
    c = make_client(store, allow_unauthenticated_writes=True)
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


def test_server_checkpoint_pin_verified_over_http(store):
    # C-1: GET /v1/state used to resolve the checkpoint to a seq itself
    # and read by version, skipping the F3a pin check the core performs.
    c = make_client(store, allow_unauthenticated_writes=True)
    c.post("/v1/update", json={"state": {"n": 1}})
    c.post("/v1/checkpoint", json={"name": "c1"})
    c.post("/v1/update", json={"state": {"n": 2}})
    assert c.get("/v1/state", params={"checkpoint": "c1"}).json() == {
        "version": 1,
        "state": {"n": 1},
    }
    # Repoint the checkpoint at seq 2 by direct DB edit, as an attacker
    # with file access would. The core refuses it; the server must too.
    db = sqlite3.connect(f"{store}/srv.db")
    db.execute("UPDATE checkpoints SET seq = 2 WHERE name = 'c1'")
    db.commit()
    db.close()
    r = c.get("/v1/state", params={"checkpoint": "c1"})
    assert r.status_code == 422
    assert r.json()["error"] == "checkpoint_pin_mismatch"
    # Plain version reads are unaffected by the repoint.
    assert c.get("/v1/state", params={"version": 2}).json()["state"] == {"n": 2}


def test_server_state_empty_world(store):
    # C-4: an empty world has no committed row; GET /v1/state used to
    # 404 on version 0 instead of returning the empty document.
    c = make_client(store, allow_unauthenticated_writes=True)
    assert c.get("/v1/state").json() == {"version": 0, "state": {}}


def test_server_rate_limit(store):
    c = make_client(store, write_limit_per_min=2, allow_unauthenticated_writes=True)
    for _ in range(2):
        assert c.post("/v1/update", json={"state": {"a": 1}}).status_code == 200
    r = c.post("/v1/update", json={"state": {"a": 1}})
    assert r.status_code == 429
    assert r.json()["error"] == "rate_limited"
    # Reads are not rate-limited.
    assert c.get("/v1/state").status_code == 200


def test_server_rate_limit_ignores_spoofed_xff_by_default(store):
    c = make_client(store, write_limit_per_min=2, allow_unauthenticated_writes=True)
    for _ in range(2):
        assert c.post("/v1/update", json={"state": {"a": 1}}).status_code == 200
    # X-Forwarded-For is client-controlled: spoofing a fresh IP must not
    # grant a fresh bucket when the proxy trust opt-in is off.
    r = c.post(
        "/v1/update",
        json={"state": {"a": 1}},
        headers={"X-Forwarded-For": "9.9.9.9"},
    )
    assert r.status_code == 429
    assert r.json()["error"] == "rate_limited"


def test_server_rate_limit_trust_forwarded_for_opt_in(store):
    c = make_client(
        store,
        write_limit_per_min=2,
        trust_forwarded_for=True,
        allow_unauthenticated_writes=True,
    )
    for _ in range(2):
        assert c.post("/v1/update", json={"state": {"a": 1}}).status_code == 200
    # With the opt-in behind a trusted proxy, the forwarded IP gets its
    # own bucket.
    r = c.post(
        "/v1/update",
        json={"state": {"a": 1}},
        headers={"X-Forwarded-For": "9.9.9.9"},
    )
    assert r.status_code == 200
    # But the direct client's bucket is still exhausted.
    r = c.post("/v1/update", json={"state": {"a": 1}})
    assert r.status_code == 429


def test_server_state_version_is_committed_only(store):
    c = make_client(
        store, invariants=[no_negative("bal")], allow_unauthenticated_writes=True
    )
    assert c.post("/v1/update", json={"state": {"bal": 10}}).status_code == 200
    r = c.post("/v1/update", json={"state": {"bal": -1}})
    assert r.status_code == 422 and r.json()["status"] == "REJECTED"
    assert c.post("/v1/update", json={"state": {"bal": 20}}).status_code == 200
    # A rejected proposal is not a historical version.
    r = c.get("/v1/state", params={"version": 2})
    assert r.status_code == 404
    assert r.json()["error"] == "not_found"
    # Committed versions still time-travel.
    assert c.get("/v1/state", params={"version": 1}).json()["state"] == {"bal": 10}
    assert c.get("/v1/state", params={"version": 3}).json()["state"] == {"bal": 20}


def test_server_proposal_audits_rejected_attempts(store):
    c = make_client(
        store, invariants=[no_negative("bal")], allow_unauthenticated_writes=True
    )
    c.post("/v1/update", json={"state": {"bal": 10}, "actor": "alice"})
    c.post("/v1/update", json={"state": {"bal": -1}, "actor": "bob"})
    r = c.get("/v1/proposals/2")
    assert r.status_code == 200
    p = r.json()["proposal"]
    assert p["status"] == "REJECTED"
    assert p["state"] == {"bal": -1}
    assert p["actor"] == "bob"
    assert "no_negative" in p["note"]
    r = c.get("/v1/proposals/1")
    assert r.json()["proposal"]["status"] == "COMMITTED"
    assert c.get("/v1/proposals/99").status_code == 404


def test_cli_proposal_audits_any_seq(store, tmp_path, capsys):
    f = tmp_path / "s.json"
    f.write_text('{"bal": 10}')
    cli(store, "init", "t")
    cli(store, "update", "t", "--file", str(f))
    capsys.readouterr()
    assert cli(store, "proposal", "t", "1") == 0
    p = json.loads(capsys.readouterr().out)
    assert p["status"] == "COMMITTED" and p["state"] == {"bal": 10}
    assert cli(store, "proposal", "t", "99") == 1


def test_server_malformed_bodies_are_400_not_500(store):
    # C-3: unvalidated POST bodies used to return 500 (malformed JSON,
    # a JSON array body, a non-string note) or a misleading 409 (a
    # mistyped expected_version). All are client errors: 400.
    c = make_client(store, allow_unauthenticated_writes=True)
    r = c.post(
        "/v1/update",
        content="{not json",
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 400
    assert r.json()["error"] == "bad_request"
    r = c.post("/v1/update", json=[1, 2, 3])
    assert r.status_code == 400
    assert r.json()["error"] == "bad_request"
    for field, bad in [
        ("note", 123),
        ("actor", 123),
        ("expected_version", "x"),
        ("expected_version", True),
        ("idempotency_key", 123),
    ]:
        r = c.post("/v1/update", json={"state": {"a": 1}, field: bad})
        assert r.status_code == 400, field
        assert r.json()["error"] == "bad_request"
    # A string state is still 400 (unchanged behavior), and a valid
    # update still commits.
    assert c.post("/v1/update", json={"state": "nope"}).status_code == 400
    assert c.post("/v1/update", json={"state": {"a": 1}}).status_code == 200
    # The checkpoint and resume routes validate their bodies too.
    assert c.post("/v1/checkpoint", json=[1]).status_code == 400
    assert c.post("/v1/checkpoint", json={"name": 123}).status_code == 400
    assert c.post("/v1/resume", json=[1]).status_code == 400
    assert c.post("/v1/resume", json={"name": "c1", "note": 5}).status_code == 400
    # And a valid checkpoint/resume round trip still works.
    assert c.post("/v1/checkpoint", json={"name": "c1"}).status_code == 200
    assert c.post("/v1/resume", json={"name": "c1"}).status_code == 200
