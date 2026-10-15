"""Tests for World.read() and the optimistic-concurrency loop it enables."""

import pytest

from world import ConflictError, World


def test_read_returns_state_and_version_atomically(tmp_path):
    w = World("occ", dir=str(tmp_path))
    assert w.read() == ({}, 0)  # empty world
    w.update({"n": 1})
    w.update({"n": 2})
    state, version = w.read()
    assert (state, version) == ({"n": 2}, 2)


def test_read_version_matches_latest_committed_row(tmp_path):
    w = World("occ", dir=str(tmp_path))
    for i in range(1, 6):
        w.update({"n": i})
    state, version = w.read()
    assert version == w.version == 5
    assert state == w.state(version=version)


def test_occ_loop_commits(tmp_path):
    w = World("occ", dir=str(tmp_path))
    w.update({"n": 0})
    doc, ver = w.read()
    doc["n"] += 1
    seq = w.update(doc, expected_version=ver)
    assert seq == 2
    assert w.read() == ({"n": 1}, 2)


def test_occ_loop_stale_read_aborts(tmp_path):
    # The race read() exists to survive: read v, another writer commits,
    # then update with the stale v must abort, never silently overwrite.
    w = World("occ", dir=str(tmp_path))
    w.update({"n": 0})
    doc, ver = w.read()  # v = 1
    w.update({"n": 99})  # concurrent writer moves to v = 2
    doc["n"] += 1
    with pytest.raises(ConflictError):
        w.update(doc, expected_version=ver)
    assert w.state() == {"n": 99}  # no silent overwrite


def test_occ_loop_retry_converges(tmp_path):
    w = World("occ", dir=str(tmp_path))
    w.update({"n": 0})
    for _ in range(3):  # three sequential read-modify-write cycles
        for _ in range(3):  # inner: the canonical client retry loop
            doc, ver = w.read()
            doc["n"] += 1
            try:
                w.update(doc, expected_version=ver)
                break
            except ConflictError:
                continue
    assert w.state() == {"n": 3}
