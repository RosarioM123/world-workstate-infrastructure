"""Tests for the tip-signing key rotation ceremony.

Covers: kid labeling on HMAC and Ed25519 tips (and kid-mismatch
rejection), old kidless tips still verifying (backward compatibility),
the Ed25519 rotation certificate roundtrip, tamper resistance, and the
end-to-end story: old tips verify under the old key after rotation,
new tips verify under the new key.
"""

import sqlite3

import pytest

from world import World, ed25519

HMAC_KEY = b"hmac-key-for-rotation-tests-000000"


def _world(tmp_path):
    w = World("vault", dir=str(tmp_path))
    w.update({"n": 1})
    w.update({"n": 2})
    return w


def _sql(w, stmt, params=()):
    cx = sqlite3.connect(w.path)
    try:
        cx.execute(stmt, params)
        cx.commit()
    finally:
        cx.close()


def test_kid_defaults_to_key_fingerprint(tmp_path):
    w = _world(tmp_path)
    sk, pk = ed25519.create_keypair()
    hmac_tip = w.sign_tip(HMAC_KEY)
    ed_tip = w.sign_tip_ed25519(sk)
    assert hmac_tip["kid"] == World._key_fingerprint(HMAC_KEY)
    assert ed_tip["kid"] == World._key_fingerprint(pk)
    assert hmac_tip["kid"] != ed_tip["kid"]
    assert w.verify_tip(HMAC_KEY, hmac_tip)
    assert w.verify_tip_ed25519(pk, ed_tip)


def test_kid_mismatch_rejected(tmp_path):
    w = _world(tmp_path)
    sk, pk = ed25519.create_keypair()
    _, other_pk = ed25519.create_keypair()
    ed_tip = w.sign_tip_ed25519(sk)
    # Right signature, but the tip names a different key.
    assert not w.verify_tip_ed25519(other_pk, ed_tip)
    hmac_tip = w.sign_tip(HMAC_KEY)
    assert not w.verify_tip(b"a-different-hmac-key-0000000000", hmac_tip)
    # Custom kids also roundtrip when the verifier pins the label.
    custom = w.sign_tip_ed25519(sk, kid="2026-q4")
    assert custom["kid"] == "2026-q4"
    assert w.verify_tip_ed25519(pk, custom, expected_kid="2026-q4")
    assert not w.verify_tip_ed25519(pk, custom)  # fingerprint expected
    hmac_custom = w.sign_tip(HMAC_KEY, kid="ops-key-7")
    assert w.verify_tip(HMAC_KEY, hmac_custom, expected_kid="ops-key-7")


def test_kidless_tips_still_verify(tmp_path):
    # Backward compatibility: tips signed before kid existed.
    w = _world(tmp_path)
    sk, pk = ed25519.create_keypair()
    ed_tip = w.sign_tip_ed25519(sk)
    hmac_tip = w.sign_tip(HMAC_KEY)
    del ed_tip["kid"]
    del hmac_tip["kid"]
    assert w.verify_tip_ed25519(pk, ed_tip)
    assert w.verify_tip(HMAC_KEY, hmac_tip)


def test_rotation_certificate_roundtrip(tmp_path):
    w = _world(tmp_path)
    old_sk, old_pk = ed25519.create_keypair()
    new_sk, new_pk = ed25519.create_keypair()
    cert = w.rotate_ed25519(old_sk, new_sk)
    assert cert["alg"] == "ed25519-rotation"
    assert cert["old_kid"] == World._key_fingerprint(old_pub := old_pk)
    assert cert["new_kid"] == World._key_fingerprint(new_pk)
    assert cert["new_pub"] == new_pk.hex()
    assert w.verify_rotation_ed25519(old_pk, cert)


def test_rotation_certificate_tamper_resistance(tmp_path):
    w = _world(tmp_path)
    old_sk, old_pk = ed25519.create_keypair()
    new_sk, new_pk = ed25519.create_keypair()
    _, attacker_pk = ed25519.create_keypair()
    cert = w.rotate_ed25519(old_sk, new_sk)
    # Attacker substitutes their own key.
    evil = dict(cert, new_pub=attacker_pk.hex())
    assert not w.verify_rotation_ed25519(old_pk, evil)
    # Wrong old key.
    assert not w.verify_rotation_ed25519(attacker_pk, cert)
    # Swapped kids.
    swapped = dict(cert, old_kid=cert["new_kid"], new_kid=cert["old_kid"])
    assert not w.verify_rotation_ed25519(old_pk, swapped)
    # Garbage.
    assert not w.verify_rotation_ed25519(old_pk, {"bogus": 1})
    assert not w.verify_rotation_ed25519(old_pk, "nope")  # type: ignore[arg-type]


def test_rotation_end_to_end_old_and_new_tips(tmp_path):
    w = _world(tmp_path)
    old_sk, old_pk = ed25519.create_keypair()
    new_sk, new_pk = ed25519.create_keypair()
    old_tip = w.sign_tip_ed25519(old_sk)
    cert = w.rotate_ed25519(old_sk, new_sk)
    assert w.verify_rotation_ed25519(old_pk, cert)
    w.update({"n": 3})
    new_tip = w.sign_tip_ed25519(new_sk)
    # Old tips verify under the old key; new tips under the new key.
    assert w.verify_tip_ed25519(old_pk, old_tip)
    assert w.verify_tip_ed25519(new_pk, new_tip)
    # Cross-key verification fails (kids differ).
    assert not w.verify_tip_ed25519(new_pk, old_tip)
    assert not w.verify_tip_ed25519(old_pk, new_tip)


def test_rotation_detects_rollback(tmp_path):
    w = _world(tmp_path)
    old_sk, old_pk = ed25519.create_keypair()
    new_sk, new_pk = ed25519.create_keypair()
    cert = w.rotate_ed25519(old_sk, new_sk)
    new_tip = w.sign_tip_ed25519(new_sk)
    _sql(w, "DELETE FROM versions WHERE seq > 1")
    assert not w.verify_tip_ed25519(new_pk, new_tip)
    assert not w.verify_rotation_ed25519(old_pk, cert)


def test_rotation_empty_world_raises(tmp_path):
    w = World("empty", dir=str(tmp_path))
    old_sk, _ = ed25519.create_keypair()
    new_sk, _ = ed25519.create_keypair()
    with pytest.raises(ValueError, match="empty world"):
        w.rotate_ed25519(old_sk, new_sk)
    with pytest.raises(ValueError, match="32 bytes"):
        w.rotate_ed25519(b"short", new_sk)
