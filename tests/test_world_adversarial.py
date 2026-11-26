"""Prompt 2 adversarial state-integrity tests for the WORLD primitive.

Day 15 continuation (2026-11-26). Each Prompt 2 scenario was first
checked against the existing suite; scenarios already genuinely
covered are recorded in the mission log instead of being duplicated
here (concurrent writers racing on one expected version:
``test_world_concurrency.py``; sequential duplicate submissions:
``test_world_core.py::test_idempotent_update``; tampered rows:
``test_redteam.py`` and ``test_verify_chain.py``; crash mid-update:
``test_crash_consistency.py``). This file pins only the combinations
and surfaces those tests do not reach:

- the same idempotency key submitted by many threads at once (a
  duplicate that arrives concurrently, not sequentially);
- out-of-order arrival: a write prepared earlier but submitted late
  can only append at the tip, never insert into or rewrite history,
  and a raw mid-chain insertion is refused by the schema;
- a corrupted checkpoint whose pinned row was deleted, or whose pin
  was garbled, is refused at serve time even though ``verify()``
  alone cannot see tail truncation;
- an unauthorized transition through the public surface: an actor
  changing a locked field is judged, rejected, and recorded, with
  the committed document untouched.

No guarantee here is stronger than the implementation: the chain is
tamper-evident, not immutable, and the checkpoint pin lives in the
same database (see ``test_redteam.py`` for the documented limits).
"""

import sqlite3
import threading

import pytest

from world.core import InvariantViolation, World
from world.invariants import respect_locks


def _sql(w, stmt, params=()):
    cx = sqlite3.connect(w.path)
    try:
        cx.execute(stmt, params)
        cx.commit()
    finally:
        cx.close()


def test_concurrent_duplicate_submission_commits_once(tmp_path):
    """Many threads submit the SAME event (same idempotency key) at once.

    Exactly one row may be appended; every submitter gets the original
    seq back. Sequential duplicates are covered in test_world_core.py;
    the race is the gap: the dedup check and the insert must be atomic
    (they are, inside BEGIN IMMEDIATE), or two racing retries could
    both pass the check and double-apply the event.
    """
    n = 8
    d = str(tmp_path / "dup")
    barrier = threading.Barrier(n)
    results: list = [None] * n

    def worker(i: int) -> None:
        try:
            barrier.wait()
            w = World("dup", dir=d)
            results[i] = (
                "ok",
                w.update({"pay": 100}, actor=f"retry-{i}", idempotency_key="pay-1"),
            )
        except Exception as e:  # noqa: BLE001 - record, never hang the barrier
            results[i] = ("error", repr(e))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(r is not None for r in results), f"threads failed: {results}"
    assert not [r for r in results if r[0] == "error"], f"errors: {results}"
    seqs = {r[1] for r in results}
    assert seqs == {1}, f"expected one shared seq, got {seqs}"
    w = World("dup", dir=d)
    assert w.version == 1
    assert len(w.history()) == 1
    assert w.state() == {"pay": 100}
    assert w.verify()


def test_late_arriving_write_appends_at_tip_never_rewrites(tmp_path):
    """Out-of-order arrival: chain order is arrival order, assigned at append.

    Agent A prepares a document against v1. Agent B commits first
    (v2). A's stale document, submitted late and unguarded, becomes
    v3: it cannot land at the position it was prepared for, and B's
    committed v2 stays exactly as written. (The guarded variant of
    this race, where A passes expected_version=1 and is refused, is
    covered in test_world_occ.py.)
    """
    w = World("order", dir=str(tmp_path))
    w.update({"step": "seed"}, actor="seed")
    prepared_by_a = {"step": "a-prepared-against-v1"}
    w.update({"step": "b-committed-first"}, actor="b")
    seq_a = w.update(prepared_by_a, actor="a")
    assert seq_a == 3
    assert [h["seq"] for h in w.history()] == [1, 2, 3]
    assert [h["actor"] for h in w.history()] == ["seed", "b", "a"]
    assert w.state(version=2) == {"step": "b-committed-first"}
    assert w.state() == prepared_by_a
    assert w.verify()


def test_mid_chain_insertion_refused_by_schema(tmp_path):
    """A raw insert at an existing seq (backdated event) cannot land.

    ``versions.seq`` is the primary key, so an out-of-order insertion
    is refused outright and the chain is untouched. Reordering or
    editing existing rows instead is tampering, and is covered by
    test_redteam.py (detected by verify()).
    """
    w = World("insert", dir=str(tmp_path))
    w.update({"n": 1}, actor="a")
    w.update({"n": 2}, actor="a")
    cx = sqlite3.connect(w.path)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            cx.execute(
                "INSERT INTO versions(seq, timestamp, actor, note, state,"
                " status, prev_hash, hash) VALUES (1, '2000-01-01T00:00:00"
                "+00:00', 'mallory', 'backdated', '{\"n\": 999}',"
                " 'COMMITTED', 'x', 'y')"
            )
    finally:
        cx.close()
    assert w.version == 2
    assert w.state() == {"n": 2}
    assert w.verify()


def test_checkpoint_pointing_at_deleted_row_is_refused(tmp_path):
    """Corrupted checkpoint: the pinned row is deleted from the tail.

    Deleting tail rows is the documented limit of verify() alone (the
    shorter chain still verifies; see test_redteam.py). A checkpoint
    that pinned the deleted tip catches this case at serve time: the
    pin check finds no row at the pinned seq, refuses to serve, and
    resume appends nothing.
    """
    w = World("ckpt", dir=str(tmp_path))
    w.update({"n": 1})
    w.update({"n": 2})
    w.update({"n": 3})
    assert w.checkpoint("tip") == 3
    _sql(w, "DELETE FROM versions WHERE seq = 3")
    assert w.verify()  # the known limit: the truncated chain verifies
    with pytest.raises(InvariantViolation, match="repointed"):
        w.state(checkpoint="tip")
    with pytest.raises(InvariantViolation, match="repointed"):
        w.resume("tip")
    assert len(w.history()) == 2  # the refused resume appended nothing


def test_checkpoint_with_garbled_pin_is_refused(tmp_path):
    """Corrupted checkpoint: the stored pin itself is garbled.

    The pin comparison is exact, so a pin that no longer equals the
    pinned row's hash is refused at serve time rather than served
    unverified. (Pre-F3a NULL pins remain served unverified, by
    documented backward compatibility, in test_redteam.py.)
    """
    w = World("ckpt2", dir=str(tmp_path))
    w.update({"n": 1})
    w.checkpoint("good")
    _sql(w, "UPDATE checkpoints SET pinned_hash = 'garbled' WHERE name = 'good'")
    with pytest.raises(InvariantViolation, match="repointed"):
        w.state(checkpoint="good")
    assert w.state() == {"n": 1}  # the document itself is unharmed
    assert w.verify()


def test_locked_field_change_by_another_actor_is_rejected(tmp_path):
    """Unauthorized transition: a different actor edits a locked field.

    The world is guarded by respect_locks. Alice locks the budget;
    Mallory's attempt to move it is judged and rejected: it is
    appended as REJECTED evidence under her own actor name, the
    committed version and document do not move, and the chain still
    verifies. The primitive has no actor allowlist; authorization
    here means the declared invariants, enforced for every actor
    alike (HTTP write auth is a separate, server-side control covered
    in test_world_server_security.py).
    """
    w = World("vault2", dir=str(tmp_path), invariants=[respect_locks()])
    w.update({"budget": 100, "_locks": ["budget"]}, actor="alice")
    with pytest.raises(InvariantViolation, match="respect_locks"):
        w.update({"budget": 0, "_locks": ["budget"]}, actor="mallory")
    assert w.version == 1
    assert w.state() == {"budget": 100, "_locks": ["budget"]}
    last = w.history()[-1]
    assert last["status"] == "REJECTED"
    assert last["actor"] == "mallory"
    assert w.verify()
