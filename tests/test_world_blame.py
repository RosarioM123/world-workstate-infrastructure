"""Tests for per-field provenance: World.blame / `world blame`."""

import json

import pytest

from world import InvariantViolation, World
from world.cli import main
from world.invariants import monotonic


def cli(store, *argv):
    return main(["--dir", store, *argv])


def test_blame_finds_last_change(tmp_path):
    w = World("b", dir=str(tmp_path))
    w.update({"a": 1}, actor="ada")
    w.update({"a": 1, "b": 2}, actor="bob")
    w.update({"a": 5, "b": 2}, actor="ada", note="raise a")
    hit = w.blame("a")
    assert hit["seq"] == 3
    assert hit["actor"] == "ada"
    assert hit["note"] == "raise a"
    assert hit["change"] == "modified"
    assert hit["old"] == 1 and hit["new"] == 5


def test_blame_added_removed_nested(tmp_path):
    w = World("b", dir=str(tmp_path))
    w.update({"cfg": {"x": 1}})
    w.update({"cfg": {"x": 2}})
    w.update({"other": True})  # removes cfg.x
    # As of latest, the last change to cfg.x was its removal.
    gone = w.blame("cfg.x")
    assert (gone["seq"], gone["change"], gone["old"], gone["new"]) == (3, "removed", 2, None)
    # As of v2 it was a modification; as of v1 an addition.
    mod = w.blame("cfg.x", version=2)
    assert (mod["seq"], mod["change"], mod["old"], mod["new"]) == (2, "modified", 1, 2)
    assert w.blame("other")["change"] == "added"
    w2 = World("b2", dir=str(tmp_path))
    w2.update({"a": 1})
    w2.update({})
    gone2 = w2.blame("a")
    assert gone2["change"] == "removed" and gone2["old"] == 1 and gone2["new"] is None


def test_blame_never_set_and_empty(tmp_path):
    w = World("b", dir=str(tmp_path))
    w.update({"a": 1})
    assert w.blame("zzz") is None
    assert World("empty", dir=str(tmp_path)).blame("a") is None


def test_blame_ignores_rejected_proposals(tmp_path):
    w = World("b", dir=str(tmp_path), invariants=[monotonic("n")])
    w.update({"n": 1})
    with pytest.raises(InvariantViolation):
        w.update({"n": 0})  # REJECTED row; committed state unchanged
    w.update({"n": 2})
    hit = w.blame("n")
    assert hit["seq"] == 3 and hit["old"] == 1 and hit["new"] == 2


def test_blame_historical_version(tmp_path):
    w = World("b", dir=str(tmp_path))
    w.update({"a": 1})
    w.update({"a": 1})
    w.update({"a": 5})
    hit = w.blame("a", version=2)
    assert hit["seq"] == 1 and hit["change"] == "added"
    with pytest.raises(KeyError):
        w.blame("a", version=999)


def test_cli_blame(tmp_path, capsys):
    store = str(tmp_path)
    w = World("b", dir=store)
    w.update({"a": 1}, actor="ada")
    w.update({"a": 9}, actor="bob")
    assert cli(store, "blame", "b", "a") == 0
    hit = json.loads(capsys.readouterr().out)
    assert hit["seq"] == 2 and hit["actor"] == "bob"
    assert hit["old"] == 1 and hit["new"] == 9
    assert cli(store, "blame", "b", "missing") == 0
    assert json.loads(capsys.readouterr().out) is None
