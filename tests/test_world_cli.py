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
