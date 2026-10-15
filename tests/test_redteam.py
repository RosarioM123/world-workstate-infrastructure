"""Red-team tests: a database-write attacker vs. ``World.verify()``.

The threat model: the attacker holds the SQLite file and can run
arbitrary SQL, bypassing the API entirely. Each test performs one
attack and asserts the *documented* outcome. Tests are split in two:

- ``test_*_detected``: the attack breaks the chain and ``verify()``
  returns False. These pin the tamper-evidence guarantees.
- ``test_*_undetected_documents_limit``: the attack succeeds
  (``verify()`` still returns True). These pin the *limits* of an
  unkeyed hash chain as tested claims: if a future change (e.g. signed
  checkpoints) closes one, the test fails and forces a doc update.

The tested claims are formalized in ``docs/SECURITY.md``.
"""

import json
import shutil
import sqlite3

import pytest

from world.core import (
    InvariantViolation,
    World,
    _genesis_prev_hash,
    _row_hash,
)


@pytest.fixture()
def attacked(tmp_path):
    """A world with 3 committed versions, ready for surgery."""
    w = World("vault", dir=str(tmp_path))
    w.update({"balance": 100}, actor="alice", note="open")
    w.update({"balance": 150}, actor="alice", note="deposit")
    w.update({"balance": 120}, actor="bob", note="withdraw")
    w.checkpoint("audited")
    assert w.verify()
    return w


def _sql(w, stmt, params=()):
    cx = sqlite3.connect(w.path)
    try:
        cx.execute(stmt, params)
        cx.commit()
    finally:
        cx.close()


def _rows(w):
    cx = sqlite3.connect(w.path)
    try:
        return cx.execute(
            "SELECT seq, timestamp, actor, note, state, status,"
            " prev_hash, hash FROM versions ORDER BY seq"
        ).fetchall()
    finally:
        cx.close()


# ---------------------------------------------------------------------------
# Detected: surgical tampering breaks the chain.
# ---------------------------------------------------------------------------


def test_surgical_state_edit_detected(attacked):
    _sql(attacked, "UPDATE versions SET state = ? WHERE seq = 2",
         (json.dumps({"balance": 999999}),))
    assert not attacked.verify()


def test_surgical_status_flip_detected(attacked):
    _sql(attacked, "UPDATE versions SET status = 'REJECTED' WHERE seq = 2")
    assert not attacked.verify()


def test_surgical_note_edit_detected(attacked):
    _sql(attacked, "UPDATE versions SET note = 'forged' WHERE seq = 1")
    assert not attacked.verify()


def test_surgical_actor_spoof_detected(attacked):
    _sql(attacked, "UPDATE versions SET actor = 'mallory' WHERE seq = 3")
    assert not attacked.verify()


def test_timestamp_backdate_detected(attacked):
    _sql(attacked, "UPDATE versions SET timestamp = ? WHERE seq = 2",
         ("2000-01-01T00:00:00+00:00",))
    assert not attacked.verify()


def test_middle_row_deletion_detected(attacked):
    _sql(attacked, "DELETE FROM versions WHERE seq = 2")
    assert not attacked.verify()


def test_row_reorder_detected(attacked):
    # Swap the states of seq 1 and seq 3: links no longer line up.
    rows = _rows(attacked)
    _sql(attacked, "UPDATE versions SET state = ? WHERE seq = 1", (rows[2][4],))
    _sql(attacked, "UPDATE versions SET state = ? WHERE seq = 3", (rows[0][4],))
    assert not attacked.verify()


# ---------------------------------------------------------------------------
# Undetected: documented limits of the unkeyed chain. Each asserts the
# attack SUCCEEDS, pinning the limit as a tested claim.
# ---------------------------------------------------------------------------


def test_tail_truncation_undetected_documents_limit(attacked):
    # Rollback attack: deleting tail rows leaves a shorter but internally
    # consistent chain. verify() cannot tell history was removed.
    # Mitigation: pin the tip hash out-of-band (signed checkpoints).
    _sql(attacked, "DELETE FROM versions WHERE seq >= 3")
    assert attacked.verify()
    assert attacked.version == 2  # history silently lost


def test_full_rewrite_undetected_documents_limit(attacked):
    # A sophisticated attacker recomputes the whole chain with forged
    # history. The hash is unkeyed (ADR 0002), so this verifies cleanly.
    # This is THE fundamental limit: detection requires a key or an
    # external anchor, not a better hash.
    rows = _rows(attacked)
    prev = _genesis_prev_hash("vault")
    for seq, ts, actor, note, state_text, status, _ph, _h in rows:
        forged_state = json.dumps({"balance": 0})  # drain every version
        new_hash = _row_hash(
            prev_hash=prev, seq=seq, timestamp=ts, actor=actor,
            note=note, status=status, state_text=forged_state,
        )
        _sql(
            attacked,
            "UPDATE versions SET state = ?, prev_hash = ?, hash = ? WHERE seq = ?",
            (forged_state, prev, new_hash, seq),
        )
        prev = new_hash
    assert attacked.verify()
    assert attacked.state() == {"balance": 0}  # forgery accepted


def test_checkpoint_repoint_undetected_documents_limit(attacked):
    # The checkpoints table is not hash-chained: repointing a checkpoint
    # is invisible to verify().
    _sql(attacked, "UPDATE checkpoints SET seq = 1 WHERE name = 'audited'")
    assert attacked.verify()
    assert attacked.state(checkpoint="audited") == {"balance": 100}


def test_idempotency_deletion_enables_double_apply_documents_limit(attacked):
    # Exactly-once per key depends on the idempotency table, which is not
    # tamper-evident. Deleting it lets a retried key commit twice; the
    # chain still verifies.
    w = attacked
    seq1 = w.update({"x": 1}, idempotency_key="pay-1")
    _sql(w, "DELETE FROM idempotency WHERE key = 'pay-1'")
    seq2 = w.update({"x": 1}, idempotency_key="pay-1")
    assert seq2 != seq1  # double apply happened
    assert w.verify()  # chain is oblivious


def test_fork_produces_two_valid_chains_documents_limit(tmp_path, attacked):
    # Fork attack: copy the file, extend each copy differently. Both
    # chains verify; only tip comparison reveals the fork.
    fork_dir = tmp_path / "forkdir"
    fork_dir.mkdir()
    shutil.copy(attacked.path, fork_dir / "vault.db")
    mainline, fork = attacked, World("vault", dir=str(fork_dir))
    assert fork.verify() and fork.state() == {"balance": 120}

    mainline.update({"balance": 1000}, actor="alice", note="mainline")
    fork.update({"balance": 0}, actor="mallory", note="forged fork")

    assert mainline.verify() and fork.verify()  # both internally consistent
    assert mainline.state() != fork.state()  # divergent tips
    assert _rows(mainline)[-1][7] != _rows(fork)[-1][7]  # divergent tip hashes


# ---------------------------------------------------------------------------
# API-constrained attacker: the public surface holds.
# ---------------------------------------------------------------------------


def test_api_cannot_commit_invariant_violation(tmp_path):
    from world.invariants import no_negative

    w = World("guarded", dir=str(tmp_path), invariants=[no_negative("balance")])
    w.update({"balance": 100})
    with pytest.raises(InvariantViolation):
        w.update({"balance": -50}, actor="mallory")
    # The attempt is recorded as evidence; the version did not move.
    assert w.version == 1
    assert w.state() == {"balance": 100}
    assert w.history()[-1]["status"] == "REJECTED"
    assert w.verify()


def test_resume_is_append_only(tmp_path):
    w = World("hist", dir=str(tmp_path))
    w.update({"v": 1})
    w.checkpoint("cp1")
    w.update({"v": 2})
    w.update({"v": 3})
    n_before = len(w.history())
    w.resume("cp1")
    # Resume appends a new version; it never rewrites the past.
    assert len(w.history()) == n_before + 1
    assert w.state(version=2) == {"v": 2}  # old versions intact
    assert w.state() == {"v": 1}  # new tip restores the checkpoint
    assert w.verify()
