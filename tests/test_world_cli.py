"""Tests for the `world` CLI commands that need no server dependencies."""

import json
import sqlite3
import sys

import pytest

from world import ConflictError, InvariantViolation, World
from world.cli import main


@pytest.fixture()
def store(tmp_path):
    return str(tmp_path)


def cli(store, *argv):
    return main(["--dir", store, *argv])


def _update(store, name, doc, **kw):
    w = World(name, dir=store)
    return w.update(doc, **kw)


def test_cli_diff(store, capsys):
    _update(store, "d", {"a": 1, "b": {"x": 1}, "gone": True})
    _update(store, "d", {"a": 2, "b": {"x": 1, "y": 2}, "new": [1]})
    assert cli(store, "diff", "d", "--from", "1", "--to", "2") == 0
    changes = {c["path"]: c for c in json.loads(capsys.readouterr().out)}
    assert changes["a"] == {"path": "a", "change": "modified", "old": 1, "new": 2}
    assert changes["b.y"]["change"] == "added"
    assert changes["gone"]["change"] == "removed"
    assert changes["new"]["change"] == "added"
    assert "b.x" not in changes  # unchanged


def test_cli_diff_defaults_to_latest(store, capsys):
    _update(store, "d", {"n": 1})
    _update(store, "d", {"n": 2})
    _update(store, "d", {"n": 3})
    assert cli(store, "diff", "d", "--from", "1") == 0
    changes = json.loads(capsys.readouterr().out)
    assert changes == [{"path": "n", "change": "modified", "old": 1, "new": 3}]


def test_cli_diff_no_changes(store, capsys):
    _update(store, "d", {"a": [1, 2]})
    assert cli(store, "diff", "d", "--from", "1", "--to", "1") == 0
    assert json.loads(capsys.readouterr().out) == []


def test_cli_export_roundtrip(store, tmp_path, capsys):
    from world import InvariantViolation

    def reject_negative(old, new):
        if new.get("a", 0) < 0:
            raise InvariantViolation("no negatives")

    w = World("e", dir=store)
    w.update({"a": 1}, actor="ann", note="first")
    with pytest.raises(InvariantViolation):
        World("e", dir=store, invariants=[reject_negative]).update({"a": -1})
    w.update({"a": 2}, actor="bob")

    out_file = tmp_path / "dump.jsonl"
    assert cli(store, "export", "e", "--file", str(out_file)) == 0
    rows = [json.loads(line) for line in out_file.read_text().splitlines()]
    assert rows[0] == {"type": "world", "name": "e"}
    proposals = rows[1:]
    assert [r["seq"] for r in proposals] == [1, 2, 3]
    assert [r["status"] for r in proposals] == ["COMMITTED", "REJECTED", "COMMITTED"]
    assert proposals[0]["state"] == {"a": 1}
    assert proposals[0]["actor"] == "ann"

    capsys.readouterr()
    assert cli(store, "export", "e") == 0  # stdout form
    assert len(capsys.readouterr().out.strip().splitlines()) == 4


def test_cli_import_rebuilds_committed_timeline(store, tmp_path, capsys):
    w = World("src", dir=store)
    w.update({"a": 1}, actor="ann", note="first")
    w.update({"a": 2}, actor="bob", note="second")

    dump = tmp_path / "dump.jsonl"
    assert cli(store, "export", "src", "--file", str(dump)) == 0

    capsys.readouterr()
    assert cli(store, "import", "dst", "--file", str(dump)) == 0
    assert "imported 2 versions, skipped 0 rejected" in capsys.readouterr().out

    dst = World("dst", dir=store)
    assert dst.state() == {"a": 2}
    assert dst.state(version=1) == {"a": 1}
    assert dst.verify()
    assert "imported seq 1" in dst.proposal(1)["note"]


def test_cli_import_skips_rejected(store, tmp_path, capsys):
    from world import InvariantViolation

    def reject_negative(old, new):
        if new.get("a", 0) < 0:
            raise InvariantViolation("no negatives")

    w = World("src", dir=store)
    w.update({"a": 1})
    with pytest.raises(InvariantViolation):
        World("src", dir=store, invariants=[reject_negative]).update({"a": -1})

    dump = tmp_path / "dump.jsonl"
    assert cli(store, "export", "src", "--file", str(dump)) == 0
    capsys.readouterr()
    assert cli(store, "import", "dst", "--file", str(dump)) == 0
    assert "imported 1 versions, skipped 1 rejected" in capsys.readouterr().out
    assert World("dst", dir=store).version == 1


def test_cli_read_returns_version_and_state(store, capsys):
    w = World("r", dir=store)
    assert cli(store, "read", "r") == 0
    assert json.loads(capsys.readouterr().out) == {"version": 0, "state": {}}
    w.update({"a": 1})
    w.update({"a": 2})
    assert cli(store, "read", "r") == 0
    assert json.loads(capsys.readouterr().out) == {"version": 2, "state": {"a": 2}}


MASTER = b"master-key-32-bytes-for-tests-0000"


def _encrypted_world(store, name, state, fields):
    w = World(name, dir=store)
    w.update_encrypted(MASTER, state, fields)
    return w


def test_cli_export_import_carries_field_keys(tmp_path, capsys):
    """C-6: export/import restores decryptability in a same-named world."""
    from world import fieldcrypto

    src_dir, dst_dir = str(tmp_path / "src"), str(tmp_path / "dst")
    state = {"user": "ada", "payment": {"card": "4111-1111", "cvv": "123"}}
    _encrypted_world(src_dir, "vault", state, ["payment.card", "payment.cvv"])

    dump = tmp_path / "dump.jsonl"
    assert cli(src_dir, "export", "vault", "--file", str(dump)) == 0
    lines = [json.loads(line) for line in dump.read_text().splitlines()]
    assert lines[0] == {"type": "world", "name": "vault"}
    key_lines = [r for r in lines if r.get("type") == "field_key"]
    assert len(key_lines) == 2
    assert {r["field"] for r in key_lines} == {"payment.card", "payment.cvv"}

    capsys.readouterr()
    assert cli(dst_dir, "import", "vault", "--file", str(dump)) == 0
    captured = capsys.readouterr()
    out, err = captured.out, captured.err
    assert "imported 1 versions, skipped 0 rejected, 2 field keys" in out
    assert "warning" not in err

    dst = World("vault", dir=dst_dir)
    assert dst.verify()
    assert dst.decrypt_fields(MASTER, dst.state()) == state
    # Keys are re-tagged with the new seq of the imported version.
    assert {r["seq"] for r in dst.field_keys()} == {1}
    assert {r["field"] for r in dst.field_keys()} == {
        "payment.card",
        "payment.cvv",
    }
    assert fieldcrypto.is_envelope(dst.state()["payment"]["card"])


def test_cli_import_warns_on_orphaned_envelope(tmp_path, capsys):
    """C-6: an export without keys imports but warns, and stays orphaned."""
    from world import RedactedError

    src_dir, dst_dir = str(tmp_path / "src"), str(tmp_path / "dst")
    _encrypted_world(src_dir, "vault", {"ssn": "000-00-0000"}, ["ssn"])

    dump = tmp_path / "dump.jsonl"
    assert cli(src_dir, "export", "vault", "--file", str(dump)) == 0
    # Simulate a pre-fix export: proposal rows only, no header, no keys.
    legacy = [line for line in dump.read_text().splitlines() if '"status"' in line]
    assert len(legacy) == 1
    (tmp_path / "legacy.jsonl").write_text("\n".join(legacy) + "\n")

    capsys.readouterr()
    assert (
        cli(dst_dir, "import", "vault", "--file", str(tmp_path / "legacy.jsonl")) == 0
    )
    captured = capsys.readouterr()
    out, err = captured.out, captured.err
    assert "imported 1 versions, skipped 0 rejected" in out
    assert "field keys" not in out
    assert "warning: field 'ssn'" in err
    assert "no escrowed key" in err

    dst = World("vault", dir=dst_dir)
    assert dst.state()["ssn"]["key_id"]  # envelope present, key absent
    with pytest.raises(RedactedError, match="never escrowed"):
        dst.decrypt_fields(MASTER, dst.state())


def test_cli_import_warns_on_world_name_mismatch(tmp_path, capsys):
    """C-6: keys carry, but envelopes stay bound to the source world name."""
    from world import fieldcrypto

    src_dir, dst_dir = str(tmp_path / "src"), str(tmp_path / "dst")
    _encrypted_world(src_dir, "vault", {"ssn": "000-00-0000"}, ["ssn"])

    dump = tmp_path / "dump.jsonl"
    assert cli(src_dir, "export", "vault", "--file", str(dump)) == 0
    capsys.readouterr()
    assert cli(dst_dir, "import", "vault-copy", "--file", str(dump)) == 0
    captured = capsys.readouterr()
    out, err = captured.out, captured.err
    assert "imported 1 versions, skipped 0 rejected, 1 field keys" in out
    assert "warning: this export is from world 'vault'" in err
    assert "world is 'vault-copy'" in err

    dst = World("vault-copy", dir=dst_dir)
    assert dst.verify()
    # The key is escrowed, but the AAD binds the envelope to "vault".
    assert len(dst.field_keys()) == 1
    with pytest.raises(fieldcrypto.DecryptionError):
        dst.decrypt_fields(MASTER, dst.state())


def test_cli_diff_unknown_version_is_clean_error(store, capsys):
    # C-9: an unknown --from version must print `error: ...` and exit 1,
    # not leak a traceback.
    _update(store, "d", {"a": 1})
    assert cli(store, "diff", "d", "--from", "99") == 1
    captured = capsys.readouterr()
    assert "error:" in captured.err and "unknown version: 99" in captured.err
    assert "Traceback" not in captured.err
    assert cli(store, "diff", "d", "--from", "1", "--to", "99") == 1
    assert "unknown version: 99" in capsys.readouterr().err


def test_cli_diff_rejected_version_is_clean_error(store, capsys):
    # C-9: a REJECTED seq is not a version either; same clean error.
    def reject_negative(old, new):
        if new.get("a", 0) < 0:
            raise InvariantViolation("no negatives")

    w = World("d", dir=store)
    w.update({"a": 1})
    with pytest.raises(InvariantViolation):
        World("d", dir=store, invariants=[reject_negative]).update({"a": -1})
    assert cli(store, "diff", "d", "--from", "2") == 1
    captured = capsys.readouterr()
    assert "error:" in captured.err
    assert "version 2 was REJECTED" in captured.err
    assert "Traceback" not in captured.err


def test_cli_blame_unknown_version_is_clean_error(store, capsys):
    # C-9: blame at an unknown version must fail cleanly, like cmd_state.
    _update(store, "d", {"a": 1})
    assert cli(store, "blame", "d", "a", "--version", "99") == 1
    captured = capsys.readouterr()
    assert "error:" in captured.err
    assert "no committed version 99" in captured.err
    assert "Traceback" not in captured.err


def test_cli_state_repointed_checkpoint_is_clean_error(store, tmp_path, capsys):
    # C-9 (same class): a repointed checkpoint raises InvariantViolation
    # in the core; the CLI must report it, not print a traceback.
    w = World("t", dir=store)
    w.update({"n": 1})
    w.checkpoint("c1")
    w.update({"n": 2})
    cx = sqlite3.connect(w.path)
    cx.execute("UPDATE checkpoints SET seq = 2 WHERE name = 'c1'")
    cx.commit()
    cx.close()
    assert cli(store, "state", "t", "--checkpoint", "c1") == 1
    captured = capsys.readouterr()
    assert "error: checkpoint 'c1' does not match the chain" in captured.err
    assert "Traceback" not in captured.err


@pytest.mark.parametrize(
    ("exc", "fragment"),
    [
        (InvariantViolation("no negatives", seq=99), "was rejected (seq 99)"),
        (ConflictError("stale"), "conflict on row seq 2"),
    ],
)
def test_cli_import_aborts_cleanly_on_update_error(
    store, tmp_path, capsys, monkeypatch, exc, fragment
):
    # C-9: a failing replay row aborts the import with a clear message
    # noting the rows already imported, instead of a traceback.
    src = World("src", dir=store)
    src.update({"a": 1}, actor="ann", note="first")
    src.update({"a": 2}, actor="bob", note="second")
    dump = tmp_path / "dump.jsonl"
    assert cli(store, "export", "src", "--file", str(dump)) == 0

    real_update = World.update
    calls = {"n": 0}

    def flaky_update(self, state, **kw):
        calls["n"] += 1
        if calls["n"] == 2:
            raise exc
        return real_update(self, state, **kw)

    monkeypatch.setattr(World, "update", flaky_update)
    capsys.readouterr()
    assert cli(store, "import", "dst", "--file", str(dump)) == 1
    captured = capsys.readouterr()
    assert "error: import aborted" in captured.err
    assert fragment in captured.err
    assert "1 versions were already imported" in captured.err
    assert "Traceback" not in captured.err
    assert World("dst", dir=store).state() == {"a": 1}


def test_cli_import_transcript_without_world_engine_is_clean_error(
    store, tmp_path, capsys, monkeypatch
):
    # C-14: with the world_engine package absent, import-transcript must
    # print a clean error naming the missing dependency (exit 2, like
    # `world serve` without its extra), not a ModuleNotFoundError traceback.
    for mod in (
        "world_engine",
        "world_engine.ingestion",
        "world_engine.ingestion.transcript",
    ):
        monkeypatch.setitem(sys.modules, mod, None)
    transcript = tmp_path / "t.txt"
    transcript.write_text("Rosario: Decision: we will ship this week.\n")
    assert cli(store, "import-transcript", "probe", "--file", str(transcript)) == 2
    captured = capsys.readouterr()
    assert "error: `world import-transcript` needs the world_engine package" in (
        captured.err
    )
    assert "Traceback" not in captured.err


# --- Day 11 (T-4): CLI coverage for the error and serve paths ---------------


def test_cli_update_non_object_json_is_clean_error(store, tmp_path, capsys):
    # T-4: _load_json_file rejects a non-object top level; main() turns the
    # TypeError into `error: ...` (exit 1), not a traceback.
    doc = tmp_path / "doc.json"
    doc.write_text("[1, 2]")
    assert cli(store, "update", "d", "--file", str(doc)) == 1
    assert "error: top-level JSON must be an object" in capsys.readouterr().err


def test_cli_update_conflict_is_clean_error(store, tmp_path, capsys):
    _update(store, "d", {"a": 1})
    doc = tmp_path / "doc.json"
    doc.write_text(json.dumps({"a": 2}))
    assert (
        cli(store, "update", "d", "--file", str(doc), "--expected-version", "99") == 1
    )
    captured = capsys.readouterr()
    assert "conflict:" in captured.err
    assert "Traceback" not in captured.err
    assert World("d", dir=store).state() == {"a": 1}


def test_cli_update_rejected_is_clean_error(store, tmp_path, capsys, monkeypatch):
    def rejected_update(self, state, **kw):
        raise InvariantViolation("no negatives", seq=2)

    monkeypatch.setattr(World, "update", rejected_update)
    doc = tmp_path / "doc.json"
    doc.write_text(json.dumps({"a": -1}))
    assert cli(store, "update", "d", "--file", str(doc)) == 1
    captured = capsys.readouterr()
    assert "rejected (seq 2): no negatives" in captured.err
    assert "Traceback" not in captured.err


def test_cli_update_many_happy_path(store, tmp_path, capsys):
    # T-4: update-many had zero CLI coverage; drive the happy path through
    # main() and check the printed seq list.
    lines = tmp_path / "states.jsonl"
    lines.write_text('{"a": 1}\n{"a": 2}\n')
    assert cli(store, "update-many", "d", "--file", str(lines)) == 0
    assert json.loads(capsys.readouterr().out) == [1, 2]
    assert World("d", dir=store).state() == {"a": 2}


def test_cli_update_many_conflict_is_clean_error(store, tmp_path, capsys):
    _update(store, "d", {"a": 1})
    lines = tmp_path / "states.jsonl"
    lines.write_text('{"a": 2}\n')
    assert (
        cli(
            store,
            "update-many",
            "d",
            "--file",
            str(lines),
            "--expected-version",
            "99",
        )
        == 1
    )
    captured = capsys.readouterr()
    assert "conflict:" in captured.err
    assert "Traceback" not in captured.err


def test_cli_update_many_rejected_is_clean_error(store, tmp_path, capsys, monkeypatch):
    def rejected_update_many(self, states, **kw):
        raise InvariantViolation("no negatives", seq=2)

    monkeypatch.setattr(World, "update_many", rejected_update_many)
    lines = tmp_path / "states.jsonl"
    lines.write_text('{"a": -1}\n')
    assert cli(store, "update-many", "d", "--file", str(lines)) == 1
    captured = capsys.readouterr()
    assert "rejected (seq 2): no negatives" in captured.err
    assert "Traceback" not in captured.err


def test_cli_checkpoint_bad_name_is_clean_error(store, capsys):
    _update(store, "d", {"a": 1})
    assert cli(store, "checkpoint", "d", "bad name!") == 1
    assert "error: invalid checkpoint name" in capsys.readouterr().err


def test_cli_resume_unknown_checkpoint_is_clean_error(store, capsys):
    assert cli(store, "resume", "d", "nope") == 1
    assert "error:" in capsys.readouterr().err


def test_cli_resume_rejected_is_clean_error(store, capsys, monkeypatch):
    _update(store, "d", {"a": 1})
    World("d", dir=store).checkpoint("cp1")

    def rejected_resume(self, name, **kw):
        raise InvariantViolation("no negatives", seq=2)

    monkeypatch.setattr(World, "resume", rejected_resume)
    assert cli(store, "resume", "d", "cp1") == 1
    captured = capsys.readouterr()
    assert "rejected (seq 2): no negatives" in captured.err
    assert "Traceback" not in captured.err


def test_cli_diff_list_changes(store, capsys):
    # T-4: _diff_values list branches (added, removed) had no coverage.
    _update(store, "d", {"items": [1, 2, 3]})
    _update(store, "d", {"items": [1, 9]})
    _update(store, "d", {"items": [1, 9, 8, 7]})
    assert cli(store, "diff", "d", "--from", "1", "--to", "2") == 0
    changes = {c["path"]: c for c in json.loads(capsys.readouterr().out)}
    assert changes["items.1"] == {
        "path": "items.1",
        "change": "modified",
        "old": 2,
        "new": 9,
    }
    assert changes["items.2"]["change"] == "removed"
    assert cli(store, "diff", "d", "--from", "2", "--to", "3") == 0
    changes = {c["path"]: c for c in json.loads(capsys.readouterr().out)}
    assert changes["items.2"]["change"] == "added"
    assert changes["items.3"]["change"] == "added"


def test_cli_export_import_list_nested_envelope(store, tmp_path, capsys):
    # T-4: _envelope_key_ids walks lists; exercise it through an
    # export/import round trip of a list-nested encrypted field.
    master = b"master-key-32-bytes-for-tests-0000"
    w = World("src", dir=store)
    w.update_encrypted(
        master,
        {"items": [{"secret": "s1"}, {"secret": "s2"}]},
        ["items.0.secret", "items.1.secret"],
    )
    dump = tmp_path / "dump.jsonl"
    assert cli(store, "export", "src", "--file", str(dump)) == 0
    assert "field_key" in dump.read_text()
    capsys.readouterr()
    # Envelopes are bound to the source world name (AAD), so the honest
    # restore path is an import into a world with the same name.
    other = tmp_path / "other-store"
    assert main(["--dir", str(other), "import", "src", "--file", str(dump)]) == 0
    imported = World("src", dir=str(other))
    assert imported.decrypt_fields(master, imported.state()) == {
        "items": [{"secret": "s1"}, {"secret": "s2"}]
    }


def test_cli_import_skips_blank_lines(store, tmp_path, capsys):
    # T-4: blank lines in an export file are skipped, not parsed.
    _update(store, "src", {"a": 1})
    dump = tmp_path / "dump.jsonl"
    assert cli(store, "export", "src", "--file", str(dump)) == 0
    dump.write_text("\n" + dump.read_text() + "\n\n")
    capsys.readouterr()
    assert cli(store, "import", "dst", "--file", str(dump)) == 0
    assert "imported 1 versions" in capsys.readouterr().out
    assert World("dst", dir=store).state() == {"a": 1}


@pytest.mark.parametrize(
    ("line", "fragment"),
    [
        ("42", "export line must be a JSON object"),
        ('{"type": "world"}', "malformed export header"),
        (
            '{"type": "field_key", "key_id": "x"}',
            "malformed field_key record: missing 'field'",
        ),
        ('{"type": "weird"}', "unknown export line type 'weird'"),
    ],
)
def test_cli_import_malformed_lines_are_clean_errors(
    store, tmp_path, capsys, line, fragment
):
    # T-4: malformed typed lines fail loudly with a message, not a traceback.
    dump = tmp_path / "dump.jsonl"
    dump.write_text(line + "\n")
    assert cli(store, "import", "dst", "--file", str(dump)) == 1
    captured = capsys.readouterr()
    assert f"error: {fragment}" in captured.err
    assert "Traceback" not in captured.err


def test_cli_import_transcript_happy_path(store, tmp_path, capsys):
    # T-4: the import-transcript success path had no CLI coverage.
    transcript = tmp_path / "t.txt"
    transcript.write_text("Rosario: Decision: we will ship this week.\n")
    assert cli(store, "import-transcript", "probe", "--file", str(transcript)) == 0
    assert capsys.readouterr().out.strip() == "1"
    doc = World("probe", dir=store).state()
    assert doc["transcript"]["decisions"][0]["text"] == "we will ship this week."


def _fake_uvicorn(monkeypatch):
    """Install a stub ``uvicorn`` module recording ``run()`` calls."""
    import types

    calls: list[dict] = []

    def run(app, host=None, port=None, **kw):
        calls.append({"app": app, "host": host, "port": port, **kw})

    monkeypatch.setitem(sys.modules, "uvicorn", types.SimpleNamespace(run=run))
    return calls


def test_cli_serve_runs_uvicorn_with_app(store, capsys, monkeypatch):
    # T-4/T-12: cmd_serve builds the app and hands it to uvicorn.run.
    calls = _fake_uvicorn(monkeypatch)
    assert cli(store, "serve", "d", "--port", "8123") == 0
    assert len(calls) == 1
    assert calls[0]["host"] == "127.0.0.1"
    assert calls[0]["port"] == 8123
    assert calls[0]["app"].routes  # a real FastAPI app, not a stub


def test_cli_serve_with_invariants_and_api_key(store, capsys, monkeypatch, tmp_path):
    # T-4: _load_invariants resolves module:attribute, and the api key and
    # rate limit reach create_app. Verified behaviorally through the app
    # handed to uvicorn.run: writes without the key are 401, and a
    # negative update is 422 under the loaded invariant.
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient

    mod = tmp_path / "probe_invariants.py"
    mod.write_text(
        "from world import InvariantViolation\n\n"
        "def reject_negative(old, new):\n"
        "    if new.get('a', 0) < 0:\n"
        "        raise InvariantViolation('no negatives')\n\n"
        "INVS = [reject_negative]\n"
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    calls = _fake_uvicorn(monkeypatch)
    assert (
        cli(
            store,
            "serve",
            "d",
            "--invariants",
            "probe_invariants:INVS",
            "--api-key",
            "secret",
            "--rate-limit",
            "5",
        )
        == 0
    )
    assert len(calls) == 1
    with TestClient(calls[0]["app"]) as client:
        assert client.post("/v1/update", json={"state": {"a": 1}}).status_code == 401
        good = {"X-API-Key": "secret"}
        r = client.post("/v1/update", json={"state": {"a": -1}}, headers=good)
        assert r.status_code == 422
        assert r.json()["status"] == "REJECTED"
        assert "no negatives" in r.json()["reason"]
        assert (
            client.post("/v1/update", json={"state": {"a": 1}}, headers=good)
            .json()
            .get("seq")
            == 2  # the rejected attempt above consumed seq 1
        )


def test_cli_serve_bad_invariants_spec_is_clean_error(store, capsys, monkeypatch):
    # T-4: a --invariants value without module:attribute is a ValueError,
    # reported by main() as `error: ...` (exit 1).
    _fake_uvicorn(monkeypatch)
    assert cli(store, "serve", "d", "--invariants", "nosuchcolon") == 1
    assert "error: use --invariants module:attribute" in capsys.readouterr().err


def test_cli_serve_missing_uvicorn_is_clean_error(store, capsys, monkeypatch):
    # T-4: with the uvicorn import failing, serve exits 2 naming the
    # server extra, instead of a ModuleNotFoundError traceback. Forcing
    # the ImportError via sys.modules keeps this true even where uvicorn
    # happens to be installed.
    monkeypatch.setitem(sys.modules, "uvicorn", None)
    assert cli(store, "serve", "d") == 2
    captured = capsys.readouterr()
    assert "error: `world serve` needs the server extra" in captured.err
    assert "Traceback" not in captured.err


def test_main_keyboard_interrupt_returns_130(store, monkeypatch):
    # T-4: main() maps KeyboardInterrupt to exit code 130.
    def boom(args):
        raise KeyboardInterrupt

    monkeypatch.setattr("world.cli.cmd_init", boom)
    assert main(["--dir", store, "init", "d"]) == 130
