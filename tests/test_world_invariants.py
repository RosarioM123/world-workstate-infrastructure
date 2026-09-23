"""Tests for the shipped invariant helpers (world.invariants)."""

import pytest

from world import InvariantViolation
from world.invariants import (
    finite_numbers,
    no_negative,
    require_keys,
    respect_locks,
)


def test_no_negative_ok_and_violation():
    no_negative("a")({}, {"a": 5})
    no_negative("a")({}, {"a": 0})
    with pytest.raises(InvariantViolation, match="no_negative: a = -1"):
        no_negative("a")({}, {"a": -1})


def test_no_negative_wildcard_and_nested():
    inv = no_negative("totals.*")
    with pytest.raises(InvariantViolation):
        inv({}, {"totals": {"q1": 10, "q2": -3}})
    inv({}, {"totals": {"q1": 10, "q2": 0}})  # ok


def test_no_negative_ignores_missing_non_numbers_and_bools():
    no_negative("missing")({}, {"a": 1})
    no_negative("a")({}, {"a": "x"})
    no_negative("a")({}, {"a": True})  # bools are not quantities
    no_negative("a")({}, {"a": None})


def test_no_negative_no_paths_checks_all_leaves():
    with pytest.raises(InvariantViolation, match="a.b"):
        no_negative()({}, {"a": {"b": -2}})
    no_negative()({}, {"a": {"b": 2}, "c": [1, 2]})


def test_no_negative_list_index():
    inv = no_negative("items.0.qty")
    with pytest.raises(InvariantViolation):
        inv({}, {"items": [{"qty": -1}]})
    inv({}, {"items": [{"qty": 3}]})


def test_finite_numbers():
    finite_numbers("x")({}, {"x": 1.5})
    with pytest.raises(InvariantViolation, match="finite_numbers"):
        finite_numbers("x")({}, {"x": float("inf")})
    with pytest.raises(InvariantViolation):
        finite_numbers()({}, {"x": float("-inf")})


def test_require_keys():
    require_keys("a", "b.c")({}, {"a": 1, "b": {"c": 2}})
    with pytest.raises(InvariantViolation, match="require_keys: missing b.c"):
        require_keys("a", "b.c")({}, {"a": 1, "b": {}})
    with pytest.raises(InvariantViolation, match="require_keys: missing a"):
        require_keys("a")({}, {})


def test_respect_locks_blocks_change_and_removal():
    inv = respect_locks()
    old = {"budget": 100, "_locks": ["budget"]}
    with pytest.raises(InvariantViolation, match="respect_locks: budget changed"):
        inv(old, {"budget": 90, "_locks": ["budget"]})
    with pytest.raises(InvariantViolation, match="removed while locked"):
        inv(old, {"_locks": ["budget"]})


def test_respect_locks_allows_unlocked_changes():
    inv = respect_locks()
    inv(
        {"budget": 100, "_locks": ["budget"]},
        {"budget": 100, "note": "hi", "_locks": ["budget"]},
    )


def test_respect_locks_unlock_is_a_versioned_update():
    inv = respect_locks()
    locked = {"budget": 100, "_locks": ["budget"]}
    unlocked = {"budget": 100, "_locks": []}
    inv(locked, unlocked)  # unlocking itself passes
    inv(unlocked, {"budget": 90, "_locks": []})  # then edits pass


def test_respect_locks_ignores_missing_key_and_non_list():
    respect_locks()({}, {"a": 1})
    respect_locks()({"_locks": "budget"}, {"budget": 2})
