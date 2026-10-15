"""Tests for signed chain tips (HMAC): detecting rollback and rewrite."""

import sqlite3

import pytest

from world import World

KEY = b"test-key-256-bits-0000000000000000"


def _sql(w, stmt, params=()):
    cx = sqlite3.connect(w.path)
    try:
        cx.execute(stmt, params)
        cx.commit()
    finally:
        cx.close()


def test_sign_tip_roundtrip(tmp_path):
    w = World("vault", dir=str(tmp_path))
    w.update({"n": 1})
    w.update({"n": 2})
    signed = w.sign_tip(KEY)
    assert signed["name"] == "vault"
    assert signed["seq"] == 2
    assert w.verify_tip(KEY, signed)


def test_sign_tip_empty_world_raises(tmp_path):
    with pytest.raises(ValueError, match="empty world"):
        World("vault", dir=str(tmp_path)).sign_tip(KEY)


def test_verify_tip_rejects_wrong_key_and_tampering(tmp_path):
    w = World("vault", dir=str(tmp_path))
    w.update({"n": 1})
    signed = w.sign_tip(KEY)
    assert not w.verify_tip(b"wrong-key", signed)
    for field, bad in [("seq", 999), ("hash", "0" * 64),
                       ("sig", "0" * 64), ("name", "other")]:
        mutated = dict(signed, **{field: bad})
        assert not w.verify_tip(KEY, mutated), field
    assert not w.verify_tip(KEY, {"bogus": 1})
    assert not w.verify_tip(KEY, "not-a-dict")  # type: ignore[arg-type]


def test_signed_tip_survives_honest_growth(tmp_path):
    # Signing does not freeze the world: later appends keep the old
    # signed (seq, hash) pair in the chain, so it still verifies.
    w = World("vault", dir=str(tmp_path))
    w.update({"n": 1})
    signed = w.sign_tip(KEY)
    w.update({"n": 2})
    w.update({"n": 3})
    assert w.verify_tip(KEY, signed)


def test_signed_tip_detects_rollback(tmp_path):
    # The attack test_tail_truncation_undetected could not catch: with a
    # signed tip held out-of-band, the rollback is detected.
    w = World("vault", dir=str(tmp_path))
    for i in range(5):
        w.update({"n": i})
    signed = w.sign_tip(KEY)
    _sql(w, "DELETE FROM versions WHERE seq > 3")
    assert w.verify()  # chain still internally consistent...
    assert not w.verify_tip(KEY, signed)  # ...but the tip is gone


def test_signed_tip_detects_rewrite(tmp_path):
    # Full-chain rewrite with recomputed hashes verifies cleanly, but the
    # attacker cannot forge the tip signature without the key.
    from world.core import _genesis_prev_hash, _row_hash

    w = World("vault", dir=str(tmp_path))
    w.update({"n": 1})
    w.update({"n": 2})
    signed = w.sign_tip(KEY)

    cx = sqlite3.connect(w.path)
    try:
        rows = cx.execute(
            "SELECT seq, timestamp, actor, note, state, status FROM versions"
            " ORDER BY seq"
        ).fetchall()
        prev = _genesis_prev_hash("vault")
        for seq, ts, actor, note, _state, status in rows:
            forged = '{"n": 0}'
            h = _row_hash(prev_hash=prev, seq=seq, timestamp=ts, actor=actor,
                          note=note, status=status, state_text=forged)
            cx.execute(
                "UPDATE versions SET state=?, prev_hash=?, hash=? WHERE seq=?",
                (forged, prev, h, seq),
            )
            prev = h
        cx.commit()
    finally:
        cx.close()

    assert w.verify()  # unkeyed chain cannot tell...
    assert not w.verify_tip(KEY, signed)  # ...but the signature can


def test_key_as_str_accepted(tmp_path):
    w = World("vault", dir=str(tmp_path))
    w.update({"n": 1})
    signed = w.sign_tip("a-string-key")
    assert w.verify_tip("a-string-key", signed)
    assert not w.verify_tip(b"a-string-key-wrong", signed)
