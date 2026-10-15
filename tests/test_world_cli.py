"""Tests for the `world` CLI commands that need no server dependencies."""

import json

import pytest

from world import World
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
    assert [r["seq"] for r in rows] == [1, 2, 3]
    assert [r["status"] for r in rows] == ["COMMITTED", "REJECTED", "COMMITTED"]
    assert rows[0]["state"] == {"a": 1}
    assert rows[0]["actor"] == "ann"

    capsys.readouterr()
    assert cli(store, "export", "e") == 0  # stdout form
    assert len(capsys.readouterr().out.strip().splitlines()) == 3


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
