"""Per-field encryption and cryptographic redaction.

Encrypted fields are opaque in the database (unreadable without the
master key); redaction crypto-shreds the field's data key so even the
master key cannot recover it, while the hash chain (over ciphertext)
stays verifiable throughout.
"""

import json
import sqlite3

import pytest

from world import RedactedError, World, fieldcrypto

MASTER = b"master-key-32-bytes-for-tests-0000"
WRONG = b"wrong-master-key-32-bytes-0000000"


def _sql(w, stmt, params=()):
    cx = sqlite3.connect(w.path)
    try:
        return cx.execute(stmt, params).fetchall()
    finally:
        cx.close()


def test_encrypt_decrypt_roundtrip(tmp_path):
    w = World("vault", dir=str(tmp_path))
    state = {"user": "ada", "payment": {"card": "4111-1111", "cvv": "123"}}
    seq = w.update_encrypted(MASTER, state, ["payment.card", "payment.cvv"])
    assert seq == 1
    stored, _ = w.read()
    # Ciphertext in the DB, plaintext nowhere.
    assert fieldcrypto.is_envelope(stored["payment"]["card"])
    assert stored["user"] == "ada"
    raw = _sql(w, "SELECT state FROM versions")[0][0]
    assert "4111-1111" not in raw and "123" not in json.dumps(stored["payment"])
    assert w.verify()
    # Decrypt restores the exact original values and types.
    back = w.decrypt_fields(MASTER, stored)
    assert back == state


def test_unreadable_without_key(tmp_path):
    w = World("vault", dir=str(tmp_path))
    w.update_encrypted(MASTER, {"secret": "s3cr3t"}, ["secret"])
    stored, _ = w.read()
    env = stored["secret"]
    assert env["__enc"] == "world-enc-v1"
    # No key: the envelope is opaque base64; the secret is not recoverable
    # from the database bytes.
    blob = bytes.fromhex(
        _sql(w, "SELECT hex(state) FROM versions")[0][0]
    ).decode("utf-8", "replace")
    assert "s3cr3t" not in blob


def test_wrong_key_fails_authentication(tmp_path):
    w = World("vault", dir=str(tmp_path))
    w.update_encrypted(MASTER, {"secret": "s3cr3t"}, ["secret"])
    stored, _ = w.read()
    with pytest.raises(fieldcrypto.DecryptionError):
        w.decrypt_fields(WRONG, stored)


def test_tampered_envelope_rejected(tmp_path):
    w = World("vault", dir=str(tmp_path))
    w.update_encrypted(MASTER, {"secret": "s3cr3t"}, ["secret"])
    stored, _ = w.read()
    env = stored["secret"]
    ct = bytearray(fieldcrypto._unb64(env["ct"]))
    ct[0] ^= 0xFF
    env["ct"] = fieldcrypto._b64(bytes(ct))
    with pytest.raises(fieldcrypto.DecryptionError):
        w.decrypt_fields(MASTER, stored)
    # verify() still sees the *stored* chain as intact (we only mutated
    # our in-memory copy).
    assert w.verify()


def test_envelope_transplant_rejected(tmp_path):
    other = World("other", dir=str(tmp_path / "o"))
    state, records = other.encrypt_fields(MASTER, {"secret": "s3cr3t"}, ["secret"])
    other.store_field_keys(records)
    w = World("vault", dir=str(tmp_path / "v"))
    # Copy the escrow row so only the AAD binding is under test.
    w.store_field_keys(records)
    # The AAD binds the world name: another world's envelope fails here.
    with pytest.raises(fieldcrypto.DecryptionError):
        w.decrypt_fields(MASTER, state)
    # And in the world it was made for, it decrypts fine.
    assert other.decrypt_fields(MASTER, state)["secret"] == "s3cr3t"


def test_verify_survives_encryption_and_redaction(tmp_path):
    w = World("vault", dir=str(tmp_path))
    w.update_encrypted(MASTER, {"a": 1, "ssn": "000-00-0000"}, ["ssn"])
    w.update({"a": 2})
    assert w.verify()
    receipt = w.redact(1, "ssn", MASTER)
    assert receipt["field"] == "ssn" and receipt["seq"] == 1
    # The chain is over ciphertext: redaction needs no rewrite.
    assert w.verify()
    assert w.version == 2


def test_redaction_makes_field_unrecoverable(tmp_path):
    w = World("vault", dir=str(tmp_path))
    w.update_encrypted(MASTER, {"ssn": "000-00-0000"}, ["ssn"])
    assert w.redaction_status(1, "ssn") == "active"
    receipt = w.redact(1, "ssn", MASTER)
    assert w.redaction_status(1, "ssn") == "redacted"
    stored, _ = w.read()
    with pytest.raises(RedactedError) as ei:
        w.decrypt_fields(MASTER, stored)
    assert ei.value.key_id == receipt["key_id"]
    assert ei.value.field == "ssn"
    # Receipt is verifiable: the envelope's key fingerprint matches, and
    # no key row remains.
    assert receipt["key_fp"] == stored["ssn"]["key_fp"]
    rows = _sql(w, "SELECT key_id FROM field_keys WHERE key_id = ?",
                (receipt["key_id"],))
    assert rows == []


def test_redact_requires_master_key(tmp_path):
    w = World("vault", dir=str(tmp_path))
    w.update_encrypted(MASTER, {"ssn": "000-00-0000"}, ["ssn"])
    with pytest.raises(fieldcrypto.DecryptionError):
        w.redact(1, "ssn", WRONG)
    # Nothing was deleted: the field still decrypts.
    assert w.redaction_status(1, "ssn") == "active"
    stored, _ = w.read()
    assert w.decrypt_fields(MASTER, stored)["ssn"] == "000-00-0000"


def test_redact_errors(tmp_path):
    w = World("vault", dir=str(tmp_path))
    w.update_encrypted(MASTER, {"ssn": "000-00-0000"}, ["ssn"])
    with pytest.raises(ValueError, match="not encrypted"):
        w.redact(1, "missing", MASTER)
    with pytest.raises(ValueError, match="no committed version"):
        w.redact(99, "ssn", MASTER)
    w.redact(1, "ssn", MASTER)
    with pytest.raises(RedactedError, match="already redacted"):
        w.redact(1, "ssn", MASTER)
    assert w.redaction_status(1, "nope") == "not-encrypted"


def test_redact_field_all_versions(tmp_path):
    w = World("vault", dir=str(tmp_path))
    for i in range(3):
        w.update_encrypted(MASTER, {"n": i, "ssn": f"000-00-000{i}"}, ["ssn"])
    receipts = w.redact_field("ssn", MASTER)
    assert len(receipts) == 3
    assert {r["seq"] for r in receipts} == {1, 2, 3}
    for seq in (1, 2, 3):
        assert w.redaction_status(seq, "ssn") == "redacted"
    assert w.verify()


def test_rejected_proposal_envelopes_stay_decryptable(tmp_path):
    from world import InvariantViolation
    from world.invariants import monotonic

    w = World("vault", dir=str(tmp_path), invariants=[monotonic("n")])
    w.update_encrypted(MASTER, {"n": 1, "ssn": "aaa"}, ["ssn"])
    with pytest.raises(InvariantViolation):
        w.update_encrypted(MASTER, {"n": 0, "ssn": "bbb"}, ["ssn"])
    # The REJECTED row's envelope decrypts: keys were escrowed first.
    # (Committed-only time travel excludes it; proposal() is the audit
    # path for rejected attempts.)
    rejected_state = w.proposal(2)["state"]
    assert w.decrypt_fields(MASTER, rejected_state)["ssn"] == "bbb"
    assert w.verify()


def test_update_encrypted_refuses_idempotency_key(tmp_path):
    w = World("vault", dir=str(tmp_path))
    with pytest.raises(ValueError, match="idempotency_key"):
        w.update_encrypted(MASTER, {"a": 1}, [], idempotency_key="k")


def test_absent_and_already_encrypted_fields_skipped(tmp_path):
    w = World("vault", dir=str(tmp_path))
    state, records = w.encrypt_fields(MASTER, {"a": 1}, ["missing", "a.b"])
    assert state == {"a": 1} and records == []
    state2, records2 = w.encrypt_fields(MASTER, {"s": "x"}, ["s"])
    # Encrypting an envelope is a no-op (no double wrap).
    state3, records3 = w.encrypt_fields(MASTER, state2, ["s"])
    assert state3 == state2 and records3 == []
    assert len(records2) == 1
