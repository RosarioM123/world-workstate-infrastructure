"""Per-field encryption and cryptographic redaction.

Encrypted fields are opaque in the database (unreadable without the
master key); redaction crypto-shreds the field's data key so even the
master key cannot recover it, while the hash chain (over ciphertext)
stays verifiable throughout.
"""

import json
import sqlite3

import pytest

from world import ConflictError, RedactedError, World, fieldcrypto

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
    blob = bytes.fromhex(_sql(w, "SELECT hex(state) FROM versions")[0][0]).decode(
        "utf-8", "replace"
    )
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
    rows = _sql(
        w, "SELECT key_id FROM field_keys WHERE key_id = ?", (receipt["key_id"],)
    )
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


def test_redact_field_covers_rejected_rows(tmp_path):
    # C-2: redact_field used to stop at the latest COMMITTED version,
    # so a REJECTED row appended after it kept a decryptable envelope
    # while the receipt implied the field was shredded everywhere.
    from world import InvariantViolation
    from world.invariants import monotonic

    w = World("vault", dir=str(tmp_path), invariants=[monotonic("n")])
    w.update_encrypted(MASTER, {"n": 1, "ssn": "aaa"}, ["ssn"])
    with pytest.raises(InvariantViolation):
        w.update_encrypted(MASTER, {"n": 0, "ssn": "bbb"}, ["ssn"])
    receipts = w.redact_field("ssn", MASTER)
    assert {r["seq"] for r in receipts} == {1, 2}
    assert w.redaction_status(1, "ssn") == "redacted"
    assert w.redaction_status(2, "ssn") == "redacted"
    # The rejected attempt no longer decrypts; the chain still verifies.
    with pytest.raises(RedactedError):
        w.decrypt_fields(MASTER, w.proposal(2)["state"])
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


def test_conflicted_update_encrypted_keys_stay_decryptable(tmp_path, monkeypatch):
    """C-13: keys escrowed before a conflicting update stay decryptable.

    update_encrypted escrows the wrapped keys, then update raises
    ConflictError, so the seq-tagging step never runs. The key rows
    keep seq NULL (audit linkage only), but the envelopes in the
    attempted state still decrypt: lookup is by key_id, not seq.
    The failed update appends nothing.
    """
    w = World("vault", dir=str(tmp_path))
    w.update({"n": 0}, actor="seed")

    captured: dict[str, object] = {}

    def failing_update(self, state, **kw):
        captured["state"] = state
        raise ConflictError("simulated concurrent writer conflict")

    monkeypatch.setattr(World, "update", failing_update)
    with pytest.raises(ConflictError):
        w.update_encrypted(MASTER, {"n": 1, "ssn": "000-00-0000"}, ["ssn"])

    assert w.version == 1
    keys = w.field_keys()
    assert len(keys) == 1
    assert keys[0]["field"] == "ssn"
    assert keys[0]["seq"] is None
    attempted = captured["state"]
    assert isinstance(attempted, dict)
    assert w.decrypt_fields(MASTER, attempted)["ssn"] == "000-00-0000"
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


def test_list_nested_field_roundtrip(tmp_path):
    # C-8: fields nested in lists used to be silently skipped.
    w = World("vault", dir=str(tmp_path))
    state = {"items": [{"secret": "one"}, {"secret": "two"}], "plain": "x"}
    w.update_encrypted(MASTER, state, ["items.0.secret", "items.1.secret"])
    stored = w.state()
    assert stored["plain"] == "x"
    assert fieldcrypto.is_envelope(stored["items"][0]["secret"])
    assert fieldcrypto.is_envelope(stored["items"][1]["secret"])
    assert w.decrypt_fields(MASTER, stored) == state
    assert w.verify()


def test_list_nested_absent_index_skipped(tmp_path):
    w = World("vault", dir=str(tmp_path))
    state, records = w.encrypt_fields(
        MASTER,
        {"items": [{"secret": "x"}]},
        ["items.5.secret", "items.x.secret", "items.-1.secret"],
    )
    assert state == {"items": [{"secret": "x"}]} and records == []


def test_list_nested_decrypt_error_names_dot_path(tmp_path):
    # C-15: the field in the error must match the dot notation used by
    # encrypt_fields and redact_field, not the old "a[0].secret" form.
    # Tamper the envelope ciphertext (not the key) so the failure
    # surfaces at the envelope-decrypt step that names the field.
    w = World("vault", dir=str(tmp_path))
    w.update_encrypted(MASTER, {"items": [{"secret": "x"}]}, ["items.0.secret"])
    stored, _ = w.read()
    env = stored["items"][0]["secret"]
    ct = bytearray(fieldcrypto._unb64(env["ct"]))
    ct[0] ^= 0xFF
    env["ct"] = fieldcrypto._b64(bytes(ct))
    with pytest.raises(fieldcrypto.DecryptionError, match=r"items\.0\.secret"):
        w.decrypt_fields(MASTER, stored)


def test_list_nested_redact_field(tmp_path):
    w = World("vault", dir=str(tmp_path))
    w.update_encrypted(MASTER, {"items": [{"secret": "x"}]}, ["items.0.secret"])
    receipts = w.redact_field("items.0.secret", MASTER)
    assert len(receipts) == 1 and receipts[0]["field"] == "items.0.secret"
    assert w.redaction_status(1, "items.0.secret") == "redacted"
    with pytest.raises(RedactedError) as exc:
        w.decrypt_fields(MASTER, w.state())
    assert exc.value.field == "items.0.secret"
