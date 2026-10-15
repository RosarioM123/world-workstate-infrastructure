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
