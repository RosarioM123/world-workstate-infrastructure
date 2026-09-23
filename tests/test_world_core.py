"""Tests for the WORLD v0.2 primitive core (world.core)."""

import json
import os
import sqlite3
import subprocess
import sys
import threading

import pytest

from world import ConflictError, InvariantViolation, World
from world.invariants import no_negative


def make_world(tmp_path, name="proj", **kwargs):
    return World(name, dir=str(tmp_path), **kwargs)


def test_create_empty_world(tmp_path):
    w = make_world(tmp_path)
    assert w.version == 0
    assert w.state() == {}
    assert w.history() == []
    assert w.verify() is True
    assert w.path.exists()


def test_invalid_names_rejected(tmp_path):
    with pytest.raises(ValueError):
        World("bad name!", dir=str(tmp_path))
    with pytest.raises(ValueError):
        World("../escape", dir=str(tmp_path))
    with pytest.raises(ValueError):
        World("", dir=str(tmp_path))


def test_update_returns_seq_and_replaces_document(tmp_path):
    w = make_world(tmp_path)
    assert w.update({"a": 1}, actor="agent-a", note="first") == 1
    assert w.update({"b": 2}) == 2  # full replacement, not a merge
    assert w.state() == {"b": 2}
    assert w.version == 2
    entry = w.history()[0]
    assert entry["actor"] == "agent-a" and entry["note"] == "first"
    assert entry["status"] == "COMMITTED"


def test_update_rejects_non_dict_and_bad_json(tmp_path):
    w = make_world(tmp_path)
    with pytest.raises(TypeError):
        w.update(["not", "a", "dict"])  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        w.update({"x": float("nan")})
    with pytest.raises(ValueError):
        w.update({"x": float("inf")})
    assert w.version == 0  # nothing appended


def test_checkpoint_and_point_in_time_reads(tmp_path):
    w = make_world(tmp_path)
    w.update({"step": 1})
    assert w.checkpoint("v1") == 1
    w.update({"step": 2})
    assert w.state() == {"step": 2}
    assert w.state(checkpoint="v1") == {"step": 1}
    assert w.state(version=1) == {"step": 1}
    assert w.checkpoints() == [
        {"name": "v1", "seq": 1, "timestamp": w.checkpoints()[0]["timestamp"]}
    ]


def test_checkpoint_errors(tmp_path):
    w = make_world(tmp_path)
    with pytest.raises(ValueError, match="empty"):
        w.checkpoint("v1")
    w.update({"a": 1})
    w.checkpoint("v1")
    with pytest.raises(ValueError, match="already exists"):
        w.checkpoint("v1")
    with pytest.raises(ValueError):
        w.checkpoint("bad name!")
    with pytest.raises(KeyError):
        w.state(checkpoint="nope")
    with pytest.raises(KeyError):
        w.state(version=99)
    with pytest.raises(ValueError):
        w.state(version=1, checkpoint="v1")


def test_resume_restores_as_new_version(tmp_path):
    w = make_world(tmp_path)
    w.update({"step": 1})
    w.checkpoint("v1")
    w.update({"step": 2})
    seq = w.resume("v1", actor="agent-b")
    assert seq == 3
    assert w.state() == {"step": 1}  # restored
    assert w.version == 3  # appended, not rewritten
    assert w.history()[-1]["note"] == "resumed from checkpoint 'v1'"
    assert w.history()[-1]["actor"] == "agent-b"
    with pytest.raises(KeyError):
        w.resume("nope")


def test_rejected_attempt_is_recorded_as_evidence(tmp_path):
    w = make_world(tmp_path, invariants=[no_negative("balance")])
    w.update({"balance": 100}, actor="a")
    with pytest.raises(InvariantViolation) as exc_info:
        w.update({"balance": -5}, actor="b", note="oops")
    assert exc_info.value.seq == 2
    assert "no_negative" in exc_info.value.reason
    # Current state is untouched; the attempt is in the log.
    assert w.version == 1
    assert w.state() == {"balance": 100}
    statuses = [h["status"] for h in w.history()]
    assert statuses == ["COMMITTED", "REJECTED"]
    assert w.history()[1]["note"] == "oops | REJECTED: no_negative: balance = -5"
    assert w.state(version=2) == {"balance": -5}  # attempted doc preserved
    assert w.verify() is True


def test_resume_is_judged_by_current_invariants(tmp_path):
    plain = make_world(tmp_path, name="p")
    plain.update({"balance": -10})
    plain.checkpoint("bad")
    guarded = make_world(tmp_path, name="p", invariants=[no_negative("balance")])
    with pytest.raises(InvariantViolation):
        guarded.resume("bad")
    assert guarded.version == 1  # the pre-existing commit stands; nothing new committed
    assert guarded.state() == {"balance": -10}
    assert any(h["status"] == "REJECTED" for h in guarded.history())


def test_non_violation_exceptions_are_not_recorded(tmp_path):
    def boom(old, new):
        raise RuntimeError("invariant bug")

    w = make_world(tmp_path, invariants=[boom])
    with pytest.raises(RuntimeError):
        w.update({"a": 1})
    assert w.version == 0
    assert w.history() == []


def test_idempotent_update(tmp_path):
    w = make_world(tmp_path)
    s1 = w.update({"a": 1}, idempotency_key="k1")
    s2 = w.update({"a": 999}, idempotency_key="k1")
    assert s1 == s2 == 1
    assert w.version == 1
    assert w.state() == {"a": 1}


def test_expected_version_conflict(tmp_path):
    w = make_world(tmp_path)
    w.update({"a": 1})
    with pytest.raises(ConflictError):
        w.update({"a": 2}, expected_version=0)
    assert w.version == 1
    assert w.update({"a": 2}, expected_version=1) == 2


def test_handles_are_stateless_views(tmp_path):
    w1 = make_world(tmp_path, name="shared")
    w2 = make_world(tmp_path, name="shared")
    w1.update({"n": 1})
    # w2 never "refreshes" — every read hits the database.
    assert w2.state() == {"n": 1}
    assert w2.version == 1
    w2.checkpoint("c1")
    assert w1.checkpoints()[0]["name"] == "c1"


def test_fresh_process_loads_previous_state(tmp_path):
    """State persists across processes: a new interpreter sees everything."""
    env = dict(os.environ, WORLD_DIR=str(tmp_path))
    seed = (
        "from world import World; "
        "w = World('xp'); "
        "w.update({'step': 1}, actor='a'); "
        "w.checkpoint('v1'); "
        "print(w.version)"
    )
    r1 = subprocess.run(
        [sys.executable, "-c", seed],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert r1.returncode == 0, r1.stderr
    assert r1.stdout.strip() == "1"

    read = (
        "from world import World; "
        "w = World('xp'); "
        "print(w.version); "
        "print(w.state()['step']); "
        "print(w.checkpoints()[0]['name']); "
        "print(w.verify())"
    )
    r2 = subprocess.run(
        [sys.executable, "-c", read],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert r2.returncode == 0, r2.stderr
    assert r2.stdout.splitlines() == ["1", "1", "v1", "True"]


def test_rejected_attempts_ignore_idempotency_key(tmp_path):
    """Idempotency dedupes COMMITTED updates only; rejections are evidence."""
    w = make_world(tmp_path, invariants=[no_negative("balance")])
    assert w.update({"balance": 100}, idempotency_key="k") == 1
    for _ in range(2):
        with pytest.raises(InvariantViolation):
            w.update({"balance": -1}, idempotency_key="k")
    assert w.version == 1  # nothing new committed
    assert w.state() == {"balance": 100}
    assert [h["status"] for h in w.history()] == [
        "COMMITTED",
        "REJECTED",
        "REJECTED",
    ]


def test_history_limit_returns_oldest_first(tmp_path):
    w = make_world(tmp_path)
    for i in range(1, 4):
        w.update({"i": i})
    limited = w.history(limit=2)
    assert [h["seq"] for h in limited] == [1, 2]
    assert [h["seq"] for h in w.history()] == [1, 2, 3]


def test_checkpoints_listed_in_creation_order(tmp_path):
    w = make_world(tmp_path)
    w.update({"a": 1})
    w.checkpoint("first")
    w.update({"a": 2})
    w.checkpoint("second")
    assert [(c["name"], c["seq"]) for c in w.checkpoints()] == [
        ("first", 1),
        ("second", 2),
    ]


def test_concurrent_updates_serialize(tmp_path):
    w = make_world(tmp_path, name="conc")
    seqs: list[int] = []
    lock = threading.Lock()

    def worker(i: int) -> None:
        seq = make_world(tmp_path, name="conc").update(
            {"i": i}, idempotency_key=f"w{i}"
        )
        with lock:
            seqs.append(seq)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(seqs) == list(range(1, 9))
    assert w.version == 8
    assert w.verify() is True


def test_verify_detects_tampering(tmp_path):
    w = make_world(tmp_path)
    w.update({"a": 1})
    w.update({"b": 2})
    assert w.verify() is True

    cx = sqlite3.connect(w.path)
    cx.execute("UPDATE versions SET state = ? WHERE seq = 1", (json.dumps({"a": 999}),))
    cx.commit()
    cx.close()
    assert w.verify() is False

    # And a broken link (prev_hash) is caught too.
    w2 = make_world(tmp_path, name="p2")
    w2.update({"a": 1})
    cx = sqlite3.connect(w2.path)
    cx.execute("UPDATE versions SET prev_hash = 'tampered' WHERE seq = 1")
    cx.commit()
    cx.close()
    assert w2.verify() is False
