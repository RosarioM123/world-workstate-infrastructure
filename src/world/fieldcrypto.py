"""Per-field authenticated encryption for WORLD states (stdlib-only).

Construction (documented, not novel):
  - Subkeys: ``k_enc = HMAC(master, b"world-enc-v1")``,
    ``k_mac = HMAC(master, b"world-mac-v1")`` (domain separation).
  - Stream cipher: ``keystream_i = HMAC(k_enc, nonce || i)`` (CTR mode
    with HMAC-SHA256 as the block function), XORed with the plaintext.
  - Authentication: ``tag = HMAC(k_mac, nonce || ciphertext || aad)``
    (encrypt-then-MAC). Decryption rejects forged or transplanted
    envelopes instead of returning garbage.

This is the standard encrypt-then-MAC pattern from the applied-crypto
literature; it is NOT AES-GCM (no AES in the stdlib). The 32-byte
per-block keystream and 256-bit tags give ample margins for field-sized
payloads. Keys are 32 random bytes; generate with ``secrets.token_bytes``.

The envelope binds ``aad`` (associated data, e.g. the world name and
field path) so an encrypted field cannot be silently transplanted into
another world or field.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets

NONCE_BYTES = 16
MAC_BYTES = 32


class DecryptionError(ValueError):
    """The envelope is forged, tampered, or the key is wrong."""


def _subkey(master_key: bytes, label: bytes) -> bytes:
    return hmac.new(bytes(master_key), label, hashlib.sha256).digest()


def _keystream(k_enc: bytes, nonce: bytes, nbytes: int) -> bytes:
    out = bytearray()
    counter = 0
    while len(out) < nbytes:
        out.extend(
            hmac.new(
                k_enc,
                nonce + counter.to_bytes(8, "big"),
                hashlib.sha256,
            ).digest()
        )
        counter += 1
    return bytes(out[:nbytes])


def _b64(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def _unb64(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


def encrypt(master_key: bytes, plaintext: bytes, aad: bytes) -> dict:
    """Encrypt; returns a JSON-serializable envelope dict."""
    master = bytes(master_key)
    if len(master) < 16:
        raise ValueError("master key must be at least 16 bytes")
    k_enc = _subkey(master, b"world-enc-v1")
    k_mac = _subkey(master, b"world-mac-v1")
    nonce = secrets.token_bytes(NONCE_BYTES)
    ct = bytes(a ^ b for a, b in zip(plaintext, _keystream(k_enc, nonce, len(plaintext))))
    tag = hmac.new(k_mac, nonce + ct + bytes(aad), hashlib.sha256).digest()
    return {
        "__enc": "world-enc-v1",
        "nonce": _b64(nonce),
        "ct": _b64(ct),
        "tag": _b64(tag),
    }


def decrypt(master_key: bytes, envelope: dict, aad: bytes) -> bytes:
    """Decrypt; raises DecryptionError on any failure."""
    try:
        if envelope.get("__enc") != "world-enc-v1":
            raise DecryptionError("not a world-enc-v1 envelope")
        nonce = _unb64(str(envelope["nonce"]))
        ct = _unb64(str(envelope["ct"]))
        tag = _unb64(str(envelope["tag"]))
    except (KeyError, TypeError, ValueError) as e:
        raise DecryptionError(f"malformed envelope: {e}") from e
    if len(nonce) != NONCE_BYTES or len(tag) != MAC_BYTES:
        raise DecryptionError("malformed envelope fields")
    master = bytes(master_key)
    k_enc = _subkey(master, b"world-enc-v1")
    k_mac = _subkey(master, b"world-mac-v1")
    expect = hmac.new(k_mac, nonce + ct + bytes(aad), hashlib.sha256).digest()
    if not hmac.compare_digest(expect, tag):
        raise DecryptionError(
            "authentication failed: wrong key, tampered ciphertext, "
            "or transplanted envelope"
        )
    return bytes(a ^ b for a, b in zip(ct, _keystream(k_enc, nonce, len(ct))))


def is_envelope(value) -> bool:
    return isinstance(value, dict) and value.get("__enc") == "world-enc-v1"


def key_fingerprint(key: bytes) -> str:
    return hashlib.sha256(bytes(key)).hexdigest()[:16]


def encode_value(value) -> bytes:
    return json.dumps(value, sort_keys=True).encode("utf-8")


def decode_value(raw: bytes):
    return json.loads(raw.decode("utf-8"))
