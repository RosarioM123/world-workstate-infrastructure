"""Pure-Python Ed25519 (public-domain construction after Bernstein).

Vendored so ``world`` stays stdlib-only: no ``cryptography``/``nacl``
dependency for signed checkpoints with public verifiability. Implements
signing and verification per RFC 8032; validated against the RFC 8032
section 7.1 test vectors in ``tests/test_world_signing_ed25519.py``.

Do NOT use this for high-throughput signing: it is constant-effort but
not constant-time, and runs at tens of operations per second. For bulk
use, swap in a constant-time backend behind the same function names.
"""

from __future__ import annotations

import hashlib
import os

__all__ = ["create_keypair", "publickey", "signature", "checkvalid", "SCALAR_BYTES"]

SCALAR_BYTES = 32

# Field and group parameters (RFC 8032 section 5.1).
_Q = (1 << 255) - 19
_L = 2**252 + 27742317777372353535851937790883648493
_D = (-121665 * pow(121666, _Q - 2, _Q)) % _Q
_I = pow(2, (_Q - 1) // 4, _Q)
_MASK255 = (1 << 255) - 1


def _sha512(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()


def _xrecover(y: int) -> int:
    xx = (y * y - 1) * pow(_D * y * y + 1, _Q - 2, _Q) % _Q
    x = pow(xx, (_Q + 3) // 8, _Q)
    if (x * x - xx) % _Q != 0:
        x = (x * _I) % _Q
    if x % 2 != 0:
        x = _Q - x
    return x


# Base point, in affine coordinates.
_Bx = _xrecover(4 * pow(5, _Q - 2, _Q) % _Q)
_By = 4 * pow(5, _Q - 2, _Q) % _Q


def _to_extended(pt: tuple[int, int]) -> tuple[int, int, int, int]:
    x, y = pt
    return (x, y, 1, x * y % _Q)


def _edwards(
    p: tuple[int, int, int, int], q: tuple[int, int, int, int]
) -> tuple[int, int, int, int]:
    """Extended-coordinate addition (Hisil-Wong-Carter-Dawson formula)."""
    x1, y1, z1, t1 = p
    x2, y2, z2, t2 = q
    a = (y1 - x1) * (y2 - x2) % _Q
    b = (y1 + x1) * (y2 + x2) % _Q
    c = t1 * 2 * _D % _Q * t2 % _Q
    dd = z1 * 2 * z2 % _Q
    e = (b - a) % _Q
    f = (dd - c) % _Q
    g = (dd + c) % _Q
    h = (b + a) % _Q
    return (e * f % _Q, g * h % _Q, f * g % _Q, e * h % _Q)


_IDENTITY = (0, 1, 1, 0)


def _scalarmult(p: tuple[int, int, int, int], e: int) -> tuple[int, int, int, int]:
    result = _IDENTITY
    while e > 0:
        if e & 1:
            result = _edwards(result, p)
        p = _edwards(p, p)
        e >>= 1
    return result


def _encodepoint(p: tuple[int, int, int, int]) -> bytes:
    x, y, z, _t = p
    zi = pow(z, _Q - 2, _Q)
    x = x * zi % _Q
    y = y * zi % _Q
    return ((y & _MASK255) | ((x & 1) << 255)).to_bytes(32, "little")


def _decodepoint(s: bytes) -> tuple[int, int, int, int]:
    if len(s) != 32:
        raise ValueError("encoded point must be 32 bytes")
    y = int.from_bytes(s, "little")
    sign = y >> 255
    y &= _MASK255
    x = _xrecover(y)
    if (x & 1) != sign:
        x = _Q - x
    if (-x * x + y * y - 1 - _D * x * x * y * y) % _Q != 0:
        raise ValueError("point is not on the curve")
    return _to_extended((x, y))


def _clamp(h: bytes) -> int:
    """Clamp the left half of SHA-512(sk) into the secret scalar."""
    v = int.from_bytes(h[:32], "little")
    v &= ~7
    v &= ~(1 << 255)
    v |= 1 << 254
    return v


def _hint(data: bytes) -> int:
    return int.from_bytes(_sha512(data), "little")


_BASE_EXT = _to_extended((_Bx, _By))


def publickey(secret_key: bytes) -> bytes:
    """Derive the 32-byte public key from a 32-byte secret seed."""
    if len(secret_key) != 32:
        raise ValueError("secret key must be 32 bytes")
    a = _clamp(_sha512(secret_key))
    return _encodepoint(_scalarmult(_BASE_EXT, a))


def signature(message: bytes, secret_key: bytes, public_key: bytes) -> bytes:
    """Sign ``message``; returns the 64-byte signature R || S."""
    if len(secret_key) != 32:
        raise ValueError("secret key must be 32 bytes")
    h = _sha512(secret_key)
    a = _clamp(h)
    r = _hint(h[32:] + message) % _L
    big_r = _scalarmult(_BASE_EXT, r)
    s = (r + _hint(_encodepoint(big_r) + public_key + message) * a) % _L
    return _encodepoint(big_r) + s.to_bytes(32, "little")


def checkvalid(sig: bytes, message: bytes, public_key: bytes) -> bool:
    """Verify a signature. Returns True/False, never raises on bad input."""
    try:
        if len(sig) != 64 or len(public_key) != 32:
            return False
        big_r = _decodepoint(sig[:32])
        a_pt = _decodepoint(public_key)
        s = int.from_bytes(sig[32:], "little")
        if s >= _L:
            return False
        h = _hint(_encodepoint(big_r) + public_key + message)
        # Check S*B == R + h*A in extended coordinates.
        lhs = _scalarmult(_BASE_EXT, s)
        rhs = _edwards(big_r, _scalarmult(a_pt, h))
        x1, y1, z1, _ = lhs
        x2, y2, z2, _ = rhs
        return (x1 * z2 - x2 * z1) % _Q == 0 and (y1 * z2 - y2 * z1) % _Q == 0
    except ValueError:
        return False


def create_keypair(seed: bytes | None = None) -> tuple[bytes, bytes]:
    """Generate a (secret_key, public_key) pair from an optional 32-byte seed."""
    if seed is None:
        seed = os.urandom(32)
    if len(seed) != 32:
        raise ValueError("seed must be 32 bytes")
    sk = bytes(seed)
    return sk, publickey(sk)
