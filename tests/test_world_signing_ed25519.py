"""Tests for Ed25519 signed chain tips: public verifiability.

RFC 8032 section 7.1 vectors pin the vendored primitive; the World-level
tests mirror the HMAC suite, plus algorithm-confusion rejection.
"""

import sqlite3
import time

import pytest

from world import World, ed25519

# RFC 8032 section 7.1, TEST 1-3 (secret, public, message, signature).
RFC_VECTORS = [
    (
        "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
        "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a",
        "",
        "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
        "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b",
    ),
    (
        "4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
        "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c",
        "72",
        "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da"
        "085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00",
    ),
    (
        "c5aa8df43f9f837bedb7442f31dcb7b166d38535076f094b85ce3a2e0b4458f7",
        "fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025",
        "af82",
        "6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac"
        "18ff9b538d16f290ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a",
    ),
]


def _sql(w, stmt, params=()):
    cx = sqlite3.connect(w.path)
    try:
        cx.execute(stmt, params)
        cx.commit()
    finally:
        cx.close()


@pytest.mark.parametrize("skh,pkh,mh,sigh", RFC_VECTORS)
def test_rfc8032_vectors(skh, pkh, mh, sigh):
    sk, pk, msg, sig = (
        bytes.fromhex(skh),
        bytes.fromhex(pkh),
        bytes.fromhex(mh),
        bytes.fromhex(sigh),
    )
    assert ed25519.publickey(sk) == pk
    assert ed25519.signature(msg, sk, pk) == sig
    assert ed25519.checkvalid(sig, msg, pk)


def test_checkvalid_rejects_garbage():
    sk, pk = ed25519.create_keypair()
    sig = ed25519.signature(b"m", sk, pk)
    assert not ed25519.checkvalid(b"\x00" * 64, b"m", pk)
    assert not ed25519.checkvalid(sig, b"other", pk)
    assert not ed25519.checkvalid(sig, b"m", b"\x00" * 32)
    assert not ed25519.checkvalid(b"short", b"m", pk)


def _world(tmp_path):
    w = World("vault", dir=str(tmp_path))
    w.update({"n": 1})
    w.update({"n": 2})
    return w


def test_sign_tip_ed25519_roundtrip(tmp_path):
    w = _world(tmp_path)
    sk, pk = ed25519.create_keypair()
    signed = w.sign_tip_ed25519(sk)
    assert signed["alg"] == "ed25519"
    assert signed["name"] == "vault" and signed["seq"] == 2
    assert w.verify_tip_ed25519(pk, signed)


def test_sign_tip_ed25519_key_validation(tmp_path):
    w = _world(tmp_path)
    with pytest.raises(ValueError):
        w.sign_tip_ed25519(b"too-short")
    with pytest.raises(ValueError, match="empty world"):
        World("empty", dir=str(tmp_path)).sign_tip_ed25519(b"\x01" * 32)
    with pytest.raises(ValueError):
        ed25519.create_keypair(b"too-short")


def test_verify_tip_ed25519_rejects_forgery_and_tampering(tmp_path):
    w = _world(tmp_path)
    sk, pk = ed25519.create_keypair()
    _, other_pk = ed25519.create_keypair()
    signed = w.sign_tip_ed25519(sk)
    assert not w.verify_tip_ed25519(other_pk, signed)  # wrong key
    for field, bad in [("seq", 999), ("hash", "0" * 64), ("sig", "00" * 64),
                       ("name", "other"), ("alg", "hmac-sha256")]:
        assert not w.verify_tip_ed25519(pk, dict(signed, **{field: bad})), field
    assert not w.verify_tip_ed25519(pk, {"bogus": 1})
    assert not w.verify_tip_ed25519(pk, "not-a-dict")  # type: ignore[arg-type]


def test_verify_tip_ed25519_rejects_hmac_tip(tmp_path):
    # Algorithm confusion: an HMAC-signed tip must not verify here.
    w = _world(tmp_path)
    sk, pk = ed25519.create_keypair()
    hmac_tip = w.sign_tip(b"x" * 32)
    assert "alg" not in hmac_tip
    assert not w.verify_tip_ed25519(pk, hmac_tip)


def test_signed_tip_ed25519_survives_honest_growth(tmp_path):
    w = _world(tmp_path)
    sk, pk = ed25519.create_keypair()
    signed = w.sign_tip_ed25519(sk)
    w.update({"n": 3})
    assert w.verify_tip_ed25519(pk, signed)


def test_signed_tip_ed25519_detects_rollback(tmp_path):
    w = _world(tmp_path)
    sk, pk = ed25519.create_keypair()
    w.update({"n": 3})
    w.update({"n": 4})
    signed = w.sign_tip_ed25519(sk)  # tip at seq 4
    _sql(w, "DELETE FROM versions WHERE seq > 2")
    assert not w.verify_tip_ed25519(pk, signed)


def test_signed_tip_ed25519_detects_rewrite(tmp_path):
    # Full-chain rewrite with recomputed hashes: verify() stays clean,
    # but the attacker cannot re-sign the tip without the private key.
    from world.core import _genesis_prev_hash, _row_hash

    w = _world(tmp_path)
    sk, pk = ed25519.create_keypair()
    signed = w.sign_tip_ed25519(sk)
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
    assert w.verify()  # the rewrite is internally consistent...
    assert not w.verify_tip_ed25519(pk, signed)  # ...but the tip catches it


def test_ed25519_keypair_is_deterministic_from_seed():
    sk1, pk1 = ed25519.create_keypair(b"\x42" * 32)
    sk2, pk2 = ed25519.create_keypair(b"\x42" * 32)
    assert (sk1, pk1) == (sk2, pk2)
    assert ed25519.publickey(sk1) == pk1


def test_ed25519_throughput_floor(tmp_path):
    # Pure-Python backend: tens of ops/s is expected; this floor only
    # catches catastrophic slowdowns (e.g. accidental O(n^2)).
    w = _world(tmp_path)
    sk, pk = ed25519.create_keypair()
    t0 = time.perf_counter()
    for _ in range(4):
        tip = w.sign_tip_ed25519(sk)
        assert w.verify_tip_ed25519(pk, tip)
    elapsed = time.perf_counter() - t0
    assert elapsed < 4 / 20, f"sign+verify too slow: {elapsed:.2f}s for 4 rounds"
