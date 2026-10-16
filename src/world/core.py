"""The WORLD primitive: versioned, tamper-evident work-state documents.

A :class:`World` is a named, durable unit of work. State is an opaque JSON
document; every proposed change is judged by optional invariants, and every
verdict — COMMITTED or REJECTED — is appended to a hash-chained log, so even
rejected attempts are evidence.

Handles are stateless: every read hits the database, so two processes
sharing a world name always see the same state. There is no caching to go
stale and no refresh API.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
from collections.abc import Callable, Iterable
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import ed25519 as _ed25519
from . import fieldcrypto as _fieldcrypto


class RedactedError(ValueError):
    """The field's encryption key was destroyed via :meth:`World.redact`.

    The ciphertext is still in the chain, but it is cryptographically
    unrecoverable. Carries ``key_id`` and ``field``.
    """

    def __init__(self, message: str, *, key_id: str, field: str) -> None:
        super().__init__(message)
        self.key_id = key_id
        self.field = field

__all__ = [
    "ConflictError",
    "Invariant",
    "InvariantViolation",
    "World",
]

#: An invariant judges a proposed transition: ``(old_state, new_state)``.
#: Raise :class:`InvariantViolation` to reject it.
Invariant = Callable[[dict[str, Any], dict[str, Any]], None]

_DEFAULT_DIRNAME = ".world"
_DIR_ENV_VAR = "WORLD_DIR"
_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS versions (
    seq        INTEGER PRIMARY KEY,
    timestamp  TEXT NOT NULL,
    actor      TEXT,
    note       TEXT NOT NULL DEFAULT '',
    state      TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'COMMITTED'
               CHECK (status IN ('COMMITTED', 'REJECTED')),
    prev_hash  TEXT NOT NULL,
    hash       TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS checkpoints (
    name      TEXT PRIMARY KEY,
    seq       INTEGER NOT NULL REFERENCES versions(seq),
    timestamp TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS idempotency (
    key TEXT PRIMARY KEY,
    seq INTEGER NOT NULL REFERENCES versions(seq)
);
CREATE TABLE IF NOT EXISTS field_keys (
    -- Escrow for per-field encryption keys (see encrypt_fields). This
    -- table is key material, not ledger data: it is NOT hash-chained
    -- (like idempotency, and like signing keys held out-of-band).
    -- Deleting a row crypto-shreds the field: the ciphertext stays in
    -- the chain (verify() unaffected) but becomes unrecoverable.
    key_id      TEXT PRIMARY KEY,
    seq         INTEGER,  -- version whose envelope references it (NULL
                          -- when the proposal was rejected)
    field       TEXT NOT NULL,  -- dot-separated path in the state
    wrapped_key TEXT NOT NULL,  -- data key wrapped with the master key
    key_fp      TEXT NOT NULL,  -- SHA-256 fingerprint of the data key
    created_at  TEXT NOT NULL
);
"""


class ConflictError(Exception):
    """Raised when ``expected_version`` does not match the current version."""


class InvariantViolation(Exception):
    """Raised when an invariant rejects a proposed state.

    The rejected attempt is still appended to the log as a REJECTED row;
    :attr:`seq` is that row's sequence number.
    """

    def __init__(self, reason: str, seq: int | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.seq = seq


def _utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _canonical(state: dict[str, Any]) -> str:
    return json.dumps(
        state, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    )


_MISSING: Any = object()  # sentinel: path absent (distinct from JSON null)


def _get_path(doc: Any, path: str) -> Any:
    """Resolve a dot-separated path; ``_MISSING`` when absent."""
    cur = doc
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return _MISSING
        cur = cur[part]
    return cur


def _genesis_prev_hash(name: str) -> str:
    return hashlib.sha256(f"world-genesis:{name}".encode()).hexdigest()


def _row_hash(
    *,
    prev_hash: str,
    seq: int,
    timestamp: str,
    actor: str | None,
    note: str,
    status: str,
    state_text: str,
) -> str:
    payload = "\n".join(
        [prev_hash, str(seq), timestamp, actor or "", note or "", status, state_text]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class World:
    """A named, durable unit of work-state.

    ``World("my-project")`` opens (or creates) the log at
    ``$WORLD_DIR/my-project.db`` (default ``~/.world/``). One name is one
    project: different names never intermingle.
    """

    def __init__(
        self,
        name: str,
        *,
        dir: str | Path | None = None,
        invariants: list[Invariant] | tuple[Invariant, ...] | None = None,
    ) -> None:
        if not _NAME_RE.fullmatch(name):
            raise ValueError(
                f"invalid world name {name!r}: use letters, digits, '-' and '_'"
            )
        self._name = name
        if dir is None:
            dir = os.environ.get(_DIR_ENV_VAR, str(Path.home() / _DEFAULT_DIRNAME))
        base = Path(dir).expanduser()
        base.mkdir(parents=True, exist_ok=True)
        self._path = base / f"{name}.db"
        self._invariants = tuple(invariants or ())
        with closing(self._connect()) as cx:
            cx.executescript(_SCHEMA)

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._path

    def _connect(self) -> sqlite3.Connection:
        cx = sqlite3.connect(self._path)
        cx.execute("PRAGMA journal_mode=WAL")
        cx.row_factory = sqlite3.Row
        return cx

    def _latest_committed(self, cx: sqlite3.Connection) -> sqlite3.Row | None:
        return cx.execute(
            "SELECT seq, state FROM versions "
            "WHERE status = 'COMMITTED' ORDER BY seq DESC LIMIT 1"
        ).fetchone()

    @property
    def version(self) -> int:
        """Sequence number of the latest COMMITTED version (0 when empty)."""
        with closing(self._connect()) as cx:
            row = self._latest_committed(cx)
            return int(row["seq"]) if row is not None else 0

    def state(
        self, *, version: int | None = None, checkpoint: str | None = None
    ) -> dict[str, Any]:
        """Return the document: current, at a committed version, or at a checkpoint.

        Time travel is committed-only. Rejected proposals were never part
        of the timeline, so ``state(version=N)`` for a REJECTED seq raises
        ``KeyError``; audit rejected attempts with :meth:`proposal`.
        """
        if version is not None and checkpoint is not None:
            raise ValueError("pass version or checkpoint, not both")
        with closing(self._connect()) as cx:
            if checkpoint is not None:
                hit = cx.execute(
                    "SELECT seq FROM checkpoints WHERE name = ?", (checkpoint,)
                ).fetchone()
                if hit is None:
                    raise KeyError(f"unknown checkpoint: {checkpoint!r}")
                version = int(hit["seq"])
            if version is None:
                row = self._latest_committed(cx)
            else:
                row = cx.execute(
                    "SELECT state FROM versions WHERE seq = ? AND status = 'COMMITTED'",
                    (version,),
                ).fetchone()
                if row is None:
                    rejected = cx.execute(
                        "SELECT 1 FROM versions WHERE seq = ? AND status = 'REJECTED'",
                        (version,),
                    ).fetchone()
                    if rejected is not None:
                        raise KeyError(
                            f"version {version} was REJECTED and is not part of"
                            " version history; use proposal() to audit it"
                        )
                    raise KeyError(f"unknown version: {version}")
            return json.loads(row["state"]) if row is not None else {}

    def read(self) -> tuple[dict[str, Any], int]:
        """Return ``(document, version)`` atomically.

        One connection, one SELECT of the latest COMMITTED row, so the
        version always describes the returned document. This is the read
        half of the optimistic-concurrency loop: pass the version as
        ``expected_version`` to :meth:`update`; if another writer commits
        in between, the update aborts with :class:`ConflictError` instead
        of silently overwriting. On an empty world returns ``({}, 0)``.
        """
        with closing(self._connect()) as cx:
            row = self._latest_committed(cx)
            if row is None:
                return {}, 0
            return json.loads(row["state"]), int(row["seq"])

    def update(
        self,
        state: dict[str, Any],
        *,
        actor: str | None = None,
        note: str = "",
        expected_version: int | None = None,
        idempotency_key: str | None = None,
    ) -> int:
        """Replace the document with ``state``; return the new version seq.

        The proposal is judged by this handle's invariants. A rejection is
        appended as a REJECTED row (the attempt is evidence) and raised as
        :class:`InvariantViolation`. A stale ``expected_version`` raises
        :class:`ConflictError` before any judgment. A repeated
        ``idempotency_key`` for a committed update returns the original seq
        without appending. Every proposal is judged first, so a rejected
        attempt is always recorded even when its key was seen before — a
        repeated key can never mask a rejection from the audit trail.

        The ``expected_version`` check is re-validated inside the write
        transaction, so concurrent writers racing on the same expected
        version serialize: exactly one commits and the rest raise
        :class:`ConflictError`. Without ``expected_version`` the write is
        last-writer-wins.
        """
        if not isinstance(state, dict):
            raise TypeError(f"state must be a dict, got {type(state).__name__}")
        try:
            state_text = _canonical(state)
        except (TypeError, ValueError) as e:
            raise ValueError(f"state is not JSON-serializable: {e}") from e
        with closing(self._connect()) as cx:
            cur = self._latest_committed(cx)
            cur_seq = int(cur["seq"]) if cur is not None else 0
            old: dict[str, Any] = json.loads(cur["state"]) if cur is not None else {}
            if expected_version is not None and expected_version != cur_seq:
                raise ConflictError(
                    f"expected version {expected_version}, current is {cur_seq}"
                )
            # Judgment stays lock-free: it is a pure function of (old,
            # state), so holding the write lock while judging would only
            # serialize writers for no correctness gain. (The deterministic
            # simulator relies on this: its "judge" yield point fires
            # outside the atomic section.)
            violation: InvariantViolation | None = None
            for inv in self._invariants:
                try:
                    inv(old, state)
                except InvariantViolation as e:
                    violation = e
                    break
            status = "REJECTED" if violation is not None else "COMMITTED"
            if violation is not None:
                final_note = (
                    f"{note} | REJECTED: {violation.reason}"
                    if note
                    else f"REJECTED: {violation.reason}"
                )
            else:
                final_note = note
            # Serialize writers: the version re-check, dedupe-check, and append
            # are one atomic step. The expected_version check before the lock
            # is a fast path only; the re-check inside is what makes optimistic
            # concurrency atomic, closing the read-to-lock race window.
            # Idempotency dedupes committed updates only: every proposal is
            # judged first, so rejected attempts are always recorded.
            cx.execute("BEGIN IMMEDIATE")
            try:
                seq, _ = self._append_guarded(
                    cx,
                    state_text=state_text,
                    actor=actor,
                    note=final_note,
                    status=status,
                    idempotency_key=idempotency_key,
                    recheck_version=expected_version,
                )
            except BaseException:
                cx.rollback()
                raise
            else:
                cx.commit()
        if violation is not None:
            raise InvariantViolation(violation.reason, seq=seq) from violation
        return seq

    def update_many(
        self,
        states: Iterable[dict[str, Any]],
        *,
        actor: str | None = None,
        note: str = "",
        expected_version: int | None = None,
        idempotency_keys: Iterable[str | None] | None = None,
    ) -> list[int]:
        """Apply many whole-document updates in a single transaction.

        ``states`` are judged in order against the evolving document and each
        verdict is appended, exactly as if :meth:`update` had been called
        once per state with the same ``actor``/``note``: the observable log
        is identical, only the per-update connection and transaction
        overhead is amortized away. Returns the seq of each appended row.

        ``expected_version`` guards the whole batch against the version at
        batch start (one optimistic-concurrency check); a stale version
        raises :class:`ConflictError` with nothing appended.
        ``idempotency_keys`` is an optional parallel sequence; duplicates
        (including keys committed earlier in the same batch) return the
        original seq without appending.

        All states are validated before the transaction opens, so a
        malformed item aborts the batch with nothing appended. A rejected
        item mid-batch appends its REJECTED row and raises
        :class:`InvariantViolation` (with ``.seq`` set); earlier items in
        the batch stay committed, matching sequential :meth:`update` calls.
        """
        items = list(states)
        keys = list(idempotency_keys) if idempotency_keys is not None else [None] * len(items)
        if len(keys) != len(items):
            raise ValueError(
                f"idempotency_keys length {len(keys)} != states length {len(items)}"
            )
        validated: list[tuple[dict[str, Any], str]] = []
        for state in items:
            if not isinstance(state, dict):
                raise TypeError(
                    f"state must be a dict, got {type(state).__name__}"
                )
            try:
                validated.append((state, _canonical(state)))
            except (TypeError, ValueError) as e:
                raise ValueError(f"state is not JSON-serializable: {e}") from e
        if not validated:
            return []
        seqs: list[int] = []
        with closing(self._connect()) as cx:
            # One transaction for the whole batch: this is the entire
            # performance win. Judgment happens inside it (the batch holds
            # the write lock throughout), which is why the deterministic
            # simulator's "judgment is lock-free" assumption applies to
            # update(), not to this path.
            cx.execute("BEGIN IMMEDIATE")
            rejected: tuple[str, int] | None = None
            try:
                cur = self._latest_committed(cx)
                old: dict[str, Any] = (
                    json.loads(cur["state"]) if cur is not None else {}
                )
                for (state, state_text), key in zip(validated, keys):
                    violation: InvariantViolation | None = None
                    for inv in self._invariants:
                        try:
                            inv(old, state)
                        except InvariantViolation as e:
                            violation = e
                            break
                    status = "REJECTED" if violation is not None else "COMMITTED"
                    if violation is not None:
                        final_note = (
                            f"{note} | REJECTED: {violation.reason}"
                            if note
                            else f"REJECTED: {violation.reason}"
                        )
                    else:
                        final_note = note
                    seq, committed_new = self._append_guarded(
                        cx,
                        state_text=state_text,
                        actor=actor,
                        note=final_note,
                        status=status,
                        idempotency_key=key,
                        recheck_version=expected_version if not seqs else None,
                    )
                    seqs.append(seq)
                    if violation is not None:
                        rejected = (violation.reason, seq)
                        break
                    # A dedup hit appends nothing, so the next judgment
                    # uses the unchanged doc, exactly as a re-read would.
                    if committed_new:
                        old = state
            except BaseException:
                cx.rollback()
                raise
            else:
                cx.commit()
        if rejected is not None:
            # The REJECTED row is evidence: it was committed with the
            # batch above; now report it.
            raise InvariantViolation(rejected[0], seq=rejected[1])
        return seqs

    def _append_guarded(
        self,
        cx: sqlite3.Connection,
        *,
        state_text: str,
        actor: str | None,
        note: str,
        status: str,
        idempotency_key: str | None,
        recheck_version: int | None,
    ) -> tuple[int, bool]:
        """Re-check version, dedupe, and append one row in the caller's txn.

        The caller must hold ``BEGIN IMMEDIATE``. Returns ``(seq,
        committed_new)``: ``committed_new`` is False on an idempotent
        dedup hit (no row appended). Raises :class:`ConflictError` on a
        stale ``recheck_version``.
        """
        if recheck_version is not None:
            cur = self._latest_committed(cx)
            cur_seq = int(cur["seq"]) if cur is not None else 0
            if recheck_version != cur_seq:
                raise ConflictError(
                    f"expected version {recheck_version}, current is {cur_seq}"
                )
        if status == "COMMITTED" and idempotency_key is not None:
            hit = cx.execute(
                "SELECT seq FROM idempotency WHERE key = ?",
                (idempotency_key,),
            ).fetchone()
            if hit is not None:
                return int(hit["seq"]), False
        seq = self._append(
            cx,
            timestamp=_utcnow(),
            actor=actor,
            note=note,
            state_text=state_text,
            status=status,
        )
        if idempotency_key is not None and status == "COMMITTED":
            cx.execute(
                "INSERT INTO idempotency(key, seq) VALUES (?, ?)",
                (idempotency_key, seq),
            )
        return seq, True

    def _append(
        self,
        cx: sqlite3.Connection,
        *,
        timestamp: str,
        actor: str | None,
        note: str,
        state_text: str,
        status: str,
    ) -> int:
        """Append one hash-chained row. Caller must hold BEGIN IMMEDIATE."""
        latest = cx.execute(
            "SELECT seq, hash FROM versions ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        prev_hash = (
            latest["hash"] if latest is not None else _genesis_prev_hash(self._name)
        )
        seq = int(latest["seq"]) + 1 if latest is not None else 1
        row_hash = _row_hash(
            prev_hash=prev_hash,
            seq=seq,
            timestamp=timestamp,
            actor=actor,
            note=note,
            status=status,
            state_text=state_text,
        )
        cx.execute(
            "INSERT INTO versions(seq, timestamp, actor, note, state, status,"
            " prev_hash, hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (seq, timestamp, actor, note, state_text, status, prev_hash, row_hash),
        )
        return seq

    def checkpoint(self, name: str) -> int:
        """Pin the current version under ``name``. Names are immutable."""
        if not _NAME_RE.fullmatch(name):
            raise ValueError(
                f"invalid checkpoint name {name!r}: use letters, digits, '-' and '_'"
            )
        with closing(self._connect()) as cx:
            cur = self._latest_committed(cx)
            if cur is None:
                raise ValueError("cannot checkpoint an empty world")
            seq = int(cur["seq"])
            cx.execute("BEGIN IMMEDIATE")
            try:
                cx.execute(
                    "INSERT INTO checkpoints(name, seq, timestamp) VALUES (?, ?, ?)",
                    (name, seq, _utcnow()),
                )
            except sqlite3.IntegrityError:
                cx.rollback()
                raise ValueError(f"checkpoint {name!r} already exists") from None
            else:
                cx.commit()
            return seq

    def checkpoints(self) -> list[dict[str, Any]]:
        """List checkpoints in creation order."""
        with closing(self._connect()) as cx:
            rows = cx.execute(
                "SELECT name, seq, timestamp FROM checkpoints ORDER BY rowid"
            ).fetchall()
            return [dict(r) for r in rows]

    def resume(
        self,
        name: str,
        *,
        actor: str | None = None,
        note: str | None = None,
        expected_version: int | None = None,
        idempotency_key: str | None = None,
    ) -> int:
        """Restore a checkpoint's document as a new version.

        History is append-only: resume never rewrites the past, it appends.
        The restore is judged by the current invariants like any transition.
        """
        target = self.state(checkpoint=name)  # KeyError on unknown name
        return self.update(
            target,
            actor=actor,
            note=note if note is not None else f"resumed from checkpoint {name!r}",
            expected_version=expected_version,
            idempotency_key=idempotency_key,
        )

    def proposal(self, seq: int) -> dict[str, Any]:
        """Return one proposal row by seq, whatever its status.

        This is the audit path for REJECTED proposals: the verdict log
        records every attempt, and this returns the attempt's document,
        actor, note, and status. Unlike :meth:`state`, it does not filter
        by status, so it must never be used as time travel.
        """
        with closing(self._connect()) as cx:
            row = cx.execute(
                "SELECT seq, timestamp, actor, note, status, state FROM versions"
                " WHERE seq = ?",
                (seq,),
            ).fetchone()
            if row is None:
                raise KeyError(f"unknown version: {seq}")
            out = dict(row)
            out["state"] = json.loads(out["state"])
            return out

    def history(self, limit: int | None = None) -> list[dict[str, Any]]:
        """The verdict log, oldest first (REJECTED attempts included)."""
        query = (
            "SELECT seq, timestamp, actor, note, status FROM versions ORDER BY seq ASC"
        )
        params: tuple[Any, ...] = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
        with closing(self._connect()) as cx:
            return [dict(r) for r in cx.execute(query, params).fetchall()]

    def blame(self, path: str, *, version: int | None = None) -> dict[str, Any] | None:
        """Who last changed the value at ``path`` (dot-separated).

        Walks committed versions back from ``version`` (default: latest),
        comparing the value at ``path`` between consecutive versions, and
        returns the row that changed it: ``seq``, ``timestamp``,
        ``actor``, ``note``, ``change`` (``added``/``modified``/
        ``removed``), ``old`` and ``new`` values. Returns None when the
        path was never set. Rejected proposals never changed committed
        state, so they are ignored; like :meth:`state`, ``version`` must
        be a committed seq (``KeyError`` otherwise).
        """
        with closing(self._connect()) as cx:
            if version is None:
                latest = self._latest_committed(cx)
                if latest is None:
                    return None
                version = int(latest["seq"])
            else:
                hit = cx.execute(
                    "SELECT status FROM versions WHERE seq = ?", (version,)
                ).fetchone()
                if hit is None or hit["status"] != "COMMITTED":
                    raise KeyError(f"no committed version {version}")
            rows = cx.execute(
                "SELECT seq, timestamp, actor, note, state FROM versions"
                " WHERE status = 'COMMITTED' AND seq <= ?"
                " ORDER BY seq DESC",
                (version,),
            ).fetchall()
            if not rows:
                return None
            # Walk newest to oldest: the first version whose value differs
            # from its predecessor is the one that last changed the path.
            # A predecessor before the oldest version counts as absent, so
            # a removal by the latest version is reported, not hidden.
            vals = [_get_path(json.loads(r["state"]), path) for r in rows]
            for i, r in enumerate(rows):
                older_val = vals[i + 1] if i + 1 < len(vals) else _MISSING
                if vals[i] != older_val:
                    return {
                        "path": path,
                        "seq": int(r["seq"]),
                        "timestamp": r["timestamp"],
                        "actor": r["actor"],
                        "note": r["note"],
                        "change": (
                            "added"
                            if older_val is _MISSING
                            else "removed"
                            if vals[i] is _MISSING
                            else "modified"
                        ),
                        "old": None if older_val is _MISSING else older_val,
                        "new": None if vals[i] is _MISSING else vals[i],
                    }
            return None

    def verify(self) -> bool:
        """Walk the hash chain; True iff every row is intact and linked."""
        prev_hash = _genesis_prev_hash(self._name)
        with closing(self._connect()) as cx:
            rows = cx.execute(
                "SELECT seq, timestamp, actor, note, status, state, prev_hash, hash"
                " FROM versions ORDER BY seq ASC"
            ).fetchall()
            for r in rows:
                if r["prev_hash"] != prev_hash:
                    return False
                expected = _row_hash(
                    prev_hash=r["prev_hash"],
                    seq=int(r["seq"]),
                    timestamp=r["timestamp"],
                    actor=r["actor"],
                    note=r["note"],
                    status=r["status"],
                    state_text=r["state"],
                )
                if r["hash"] != expected:
                    return False
                prev_hash = r["hash"]
        return True

    @staticmethod
    def _tip_mac(key: bytes, name: str, seq: int, tip_hash: str) -> str:
        return hmac.new(
            key, f"{name}:{seq}:{tip_hash}".encode("utf-8"), hashlib.sha256
        ).hexdigest()

    @staticmethod
    def _key_fingerprint(key: bytes) -> str:
        """Short public identifier for a signing key (not secret).

        For Ed25519 this fingerprints the public key; for HMAC the secret
        (only its holder can compute it). Used as the ``kid`` in signed
        tips so verifiers holding several keys can tell which one signed.
        """
        return hashlib.sha256(bytes(key)).hexdigest()[:16]

    def sign_tip(
        self, key: bytes | str, kid: str | None = None
    ) -> dict[str, Any]:
        """Sign the chain tip with an HMAC key held outside the database.

        Returns ``{"name", "seq", "hash", "sig", "kid"}``. Store it
        out-of-band (a file, a log, another system): anyone holding it can
        later prove the chain was rolled back or rewritten, which
        ``verify()`` alone cannot detect on an unkeyed chain. The key is
        never written to the database; anyone with the key can sign, so
        protect it like a password. For public verifiability (anyone
        verifies, only the signer signs), use :meth:`sign_tip_ed25519` /
        :meth:`verify_tip_ed25519` instead.

        ``kid`` labels the key; it defaults to the key fingerprint. It is
        a routing hint, not a security boundary: the signature covers
        ``(name, seq, hash)`` only, so old tips without ``kid`` still
        verify. See :meth:`rotate_ed25519` for the rotation protocol.
        """
        raw = key.encode("utf-8") if isinstance(key, str) else bytes(key)
        with closing(self._connect()) as cx:
            row = cx.execute(
                "SELECT seq, hash FROM versions ORDER BY seq DESC LIMIT 1"
            ).fetchone()
            if row is None:
                raise ValueError("cannot sign the tip of an empty world")
            seq, tip_hash = int(row["seq"]), str(row["hash"])
        return {
            "name": self._name,
            "seq": seq,
            "hash": tip_hash,
            "sig": self._tip_mac(raw, self._name, seq, tip_hash),
            "kid": kid if kid is not None else self._key_fingerprint(raw),
        }

    def verify_tip(
        self,
        key: bytes | str,
        signed_tip: dict[str, Any],
        expected_kid: str | None = None,
    ) -> bool:
        """Check a tip signature from :meth:`sign_tip` against this world.

        Returns False when the signature is forged (wrong key or tampered
        fields), when the tip's ``kid`` does not match the expected key
        identity (the key fingerprint by default, or ``expected_kid`` when
        the signer used a custom label), or when the chain no longer
        contains that ``(seq, hash)`` pair, i.e. the history was rolled
        back or rewritten after signing.
        """
        if not isinstance(signed_tip, dict):
            return False
        raw = key.encode("utf-8") if isinstance(key, str) else bytes(key)
        try:
            name = str(signed_tip["name"])
            seq = int(signed_tip["seq"])
            tip_hash = str(signed_tip["hash"])
            sig = str(signed_tip["sig"])
            tip_kid = signed_tip.get("kid")
        except (KeyError, TypeError, ValueError):
            return False
        if name != self._name:
            return False
        want_kid = (
            expected_kid if expected_kid is not None else self._key_fingerprint(raw)
        )
        if tip_kid is not None and tip_kid != want_kid:
            return False
        if not hmac.compare_digest(
            self._tip_mac(raw, name, seq, tip_hash), sig
        ):
            return False
        with closing(self._connect()) as cx:
            row = cx.execute(
                "SELECT hash FROM versions WHERE seq = ?", (seq,)
            ).fetchone()
        return row is not None and str(row["hash"]) == tip_hash

    @staticmethod
    def _tip_message(name: str, seq: int, tip_hash: str) -> bytes:
        return f"{name}:{seq}:{tip_hash}".encode("utf-8")

    def sign_tip_ed25519(
        self, private_key: bytes, kid: str | None = None
    ) -> dict[str, Any]:
        """Sign the chain tip with an Ed25519 private key.

        Same ``(name, seq, hash)`` message as :meth:`sign_tip`, but the
        signature is publicly verifiable: anyone holding the *public* key
        can check it, while only the private-key holder can sign. Returns
        ``{"name", "seq", "hash", "sig", "alg": "ed25519", "kid"}`` with
        the signature hex-encoded. The private key is never written to the
        database; distribute the public key out-of-band (it is public,
        so a README or DNS record will do). Key generation:
        ``world.ed25519.create_keypair()``. ``kid`` defaults to the
        public-key fingerprint; see :meth:`rotate_ed25519` for rotation.
        """
        if len(bytes(private_key)) != 32:
            raise ValueError("Ed25519 private key must be 32 bytes")
        with closing(self._connect()) as cx:
            row = cx.execute(
                "SELECT seq, hash FROM versions ORDER BY seq DESC LIMIT 1"
            ).fetchone()
            if row is None:
                raise ValueError("cannot sign the tip of an empty world")
            seq, tip_hash = int(row["seq"]), str(row["hash"])
        public_key = _ed25519.publickey(bytes(private_key))
        sig = _ed25519.signature(
            self._tip_message(self._name, seq, tip_hash),
            bytes(private_key),
            public_key,
        )
        return {
            "name": self._name,
            "seq": seq,
            "hash": tip_hash,
            "sig": sig.hex(),
            "alg": "ed25519",
            "kid": kid if kid is not None else self._key_fingerprint(public_key),
        }

    def verify_tip_ed25519(
        self,
        public_key: bytes,
        signed_tip: dict[str, Any],
        expected_kid: str | None = None,
    ) -> bool:
        """Verify an Ed25519 tip signature against this world.

        The public key must come from out-of-band distribution, never from
        the signed tip itself (otherwise an attacker rewrites the chain
        *and* re-signs with their own key). Returns False for forged
        signatures, tampered fields, a ``kid`` that does not match the
        expected key identity (the public-key fingerprint by default, or
        ``expected_kid`` for a custom label), algorithm confusion (an HMAC
        tip passed here is rejected), name mismatch, or a chain that no
        longer contains the signed ``(seq, hash)`` pair.
        """
        if not isinstance(signed_tip, dict):
            return False
        try:
            if signed_tip.get("alg") != "ed25519":
                return False
            name = str(signed_tip["name"])
            seq = int(signed_tip["seq"])
            tip_hash = str(signed_tip["hash"])
            sig = bytes.fromhex(str(signed_tip["sig"]))
            tip_kid = signed_tip.get("kid")
        except (KeyError, TypeError, ValueError):
            return False
        if name != self._name:
            return False
        pub = bytes(public_key)
        want_kid = (
            expected_kid if expected_kid is not None else self._key_fingerprint(pub)
        )
        if tip_kid is not None and tip_kid != want_kid:
            return False
        if not _ed25519.checkvalid(
            sig, self._tip_message(name, seq, tip_hash), pub
        ):
            return False
        with closing(self._connect()) as cx:
            row = cx.execute(
                "SELECT hash FROM versions WHERE seq = ?", (seq,)
            ).fetchone()
        return row is not None and str(row["hash"]) == tip_hash

    def rotate_ed25519(
        self,
        old_private_key: bytes,
        new_private_key: bytes,
        *,
        old_kid: str | None = None,
        new_kid: str | None = None,
    ) -> dict[str, Any]:
        """Rotate the Ed25519 tip-signing key with a verifiable certificate.

        The *old* private key signs a rotation statement binding the new
        public key to the current chain tip, so anyone who trusted the old
        public key can verify the succession without trusting the
        operator's word. Returns ``{"name", "seq", "hash", "old_kid",
        "new_kid", "new_pub", "sig", "alg": "ed25519-rotation"}``.

        After rotation: keep signing new tips with the new key; old tips
        still verify under the old public key (:meth:`verify_tip_ed25519`
        is per-key). Publish the certificate alongside the new public key.
        Rotation bounds *future* forgeries; it cannot un-compromise
        signatures made before the old key leaked.
        """
        old_sk, new_sk = bytes(old_private_key), bytes(new_private_key)
        if len(old_sk) != 32 or len(new_sk) != 32:
            raise ValueError("Ed25519 private keys must be 32 bytes")
        old_pub = _ed25519.publickey(old_sk)
        new_pub = _ed25519.publickey(new_sk)
        old_fp = old_kid if old_kid is not None else self._key_fingerprint(old_pub)
        new_fp = new_kid if new_kid is not None else self._key_fingerprint(new_pub)
        with closing(self._connect()) as cx:
            row = cx.execute(
                "SELECT seq, hash FROM versions ORDER BY seq DESC LIMIT 1"
            ).fetchone()
            if row is None:
                raise ValueError("cannot rotate on an empty world")
            seq, tip_hash = int(row["seq"]), str(row["hash"])
        msg = (
            f"rotate:{self._name}:{seq}:{tip_hash}:"
            f"{old_fp}:{new_fp}:{new_pub.hex()}"
        ).encode("utf-8")
        sig = _ed25519.signature(msg, old_sk, old_pub)
        return {
            "name": self._name,
            "seq": seq,
            "hash": tip_hash,
            "old_kid": old_fp,
            "new_kid": new_fp,
            "new_pub": new_pub.hex(),
            "sig": sig.hex(),
            "alg": "ed25519-rotation",
        }

    def verify_rotation_ed25519(
        self, old_public_key: bytes, cert: dict[str, Any]
    ) -> bool:
        """Verify a rotation certificate from :meth:`rotate_ed25519`.

        Checks the old key's signature over the rotation statement, that
        the kids match the actual keys (no substitution), and that the
        certified ``(seq, hash)`` is still the chain's history (a rotation
        certified before a rollback does not validate a rewritten chain).
        """
        if not isinstance(cert, dict):
            return False
        try:
            if cert.get("alg") != "ed25519-rotation":
                return False
            name = str(cert["name"])
            seq = int(cert["seq"])
            tip_hash = str(cert["hash"])
            old_kid = str(cert["old_kid"])
            new_kid = str(cert["new_kid"])
            new_pub = bytes.fromhex(str(cert["new_pub"]))
            sig = bytes.fromhex(str(cert["sig"]))
        except (KeyError, TypeError, ValueError):
            return False
        if name != self._name:
            return False
        old_pub = bytes(old_public_key)
        if old_kid != self._key_fingerprint(old_pub):
            return False
        if new_kid != self._key_fingerprint(new_pub):
            return False
        msg = (
            f"rotate:{name}:{seq}:{tip_hash}:"
            f"{old_kid}:{new_kid}:{new_pub.hex()}"
        ).encode("utf-8")
        if not _ed25519.checkvalid(sig, msg, old_pub):
            return False
        with closing(self._connect()) as cx:
            row = cx.execute(
                "SELECT hash FROM versions WHERE seq = ?", (seq,)
            ).fetchone()
        return row is not None and str(row["hash"]) == tip_hash

    # ------------------------------------------------------------------
    # Per-field encryption and cryptographic redaction.
    # ------------------------------------------------------------------

    @staticmethod
    def _enc_aad(name: str, field: str, key_id: str) -> bytes:
        return f"{name}:{field}:{key_id}".encode("utf-8")

    def encrypt_fields(
        self,
        master_key: bytes,
        state: dict[str, Any],
        fields: Iterable[str],
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Encrypt fields of a state; returns ``(new_state, key_records)``.

        Each named field (dot-separated path, e.g. ``"payment.card"``)
        is replaced by an authenticated-encryption envelope; the row
        hash is computed over the ciphertext, so :meth:`verify` works
        without the key and encryption composes with tamper-evidence.
        Absent fields are skipped.

        Every field gets a fresh random 32-byte data key, wrapped with
        ``master_key``; the wrapped keys come back as ``key_records``
        for :meth:`store_field_keys`. Persist them (see
        :meth:`update_encrypted`), or the envelopes can never be
        decrypted. ``master_key`` must be at least 16 bytes; it is never
        written to the database.
        """
        import copy

        master = bytes(master_key)
        if len(master) < 16:
            raise ValueError("master key must be at least 16 bytes")
        new_state = copy.deepcopy(state)
        records: list[dict[str, Any]] = []
        for field in fields:
            value = _get_path(new_state, field)
            if value is _MISSING or _fieldcrypto.is_envelope(value):
                continue
            data_key = secrets.token_bytes(32)
            key_id = secrets.token_hex(8)
            aad = self._enc_aad(self._name, field, key_id)
            env = _fieldcrypto.encrypt(
                data_key, _fieldcrypto.encode_value(value), aad
            )
            env["key_id"] = key_id
            env["key_fp"] = _fieldcrypto.key_fingerprint(data_key)
            wrapped = _fieldcrypto.encrypt(
                master, data_key, f"wrap:{key_id}".encode("utf-8")
            )
            # Swap the plaintext for the envelope at the dot path.
            parts = field.split(".")
            node = new_state
            for part in parts[:-1]:
                node = node[part]
            node[parts[-1]] = env
            records.append(
                {
                    "key_id": key_id,
                    "seq": None,
                    "field": field,
                    "wrapped_key": json.dumps(wrapped),
                    "key_fp": _fieldcrypto.key_fingerprint(data_key),
                    "created_at": _utcnow(),
                }
            )
        return new_state, records

    def store_field_keys(
        self, key_records: Iterable[dict[str, Any]], seq: int | None = None
    ) -> None:
        """Persist wrapped field keys from :meth:`encrypt_fields`.

        ``seq`` tags the rows with the version whose envelopes reference
        them (left NULL for rejected proposals, whose evidence rows stay
        decryptable).
        """
        rows = [
            (
                r["key_id"],
                seq if seq is not None else r.get("seq"),
                r["field"],
                r["wrapped_key"],
                r["key_fp"],
                r["created_at"],
            )
            for r in key_records
        ]
        if not rows:
            return
        with closing(self._connect()) as cx:
            cx.executemany(
                "INSERT OR REPLACE INTO field_keys"
                " (key_id, seq, field, wrapped_key, key_fp, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                rows,
            )
            cx.commit()

    def update_encrypted(
        self,
        master_key: bytes,
        state: dict[str, Any],
        fields: Iterable[str],
        **kw: Any,
    ) -> int:
        """Encrypt ``fields`` then :meth:`update`; returns the new seq.

        Key records are escrowed *before* the update so that even a
        REJECTED proposal's envelopes stay decryptable (the attempt is
        evidence). ``idempotency_key`` is refused: an idempotent replay
        would orphan the fresh key records, so combine the two
        explicitly via :meth:`encrypt_fields` instead.
        """
        if kw.get("idempotency_key") is not None:
            raise ValueError(
                "update_encrypted refuses idempotency_key: encrypt the state"
                " with encrypt_fields and manage the replay explicitly"
            )
        new_state, records = self.encrypt_fields(master_key, state, fields)
        self.store_field_keys(records)
        seq = self.update(new_state, **kw)
        with closing(self._connect()) as cx:
            cx.executemany(
                "UPDATE field_keys SET seq = ? WHERE key_id = ?",
                [(seq, r["key_id"]) for r in records],
            )
            cx.commit()
        return seq

    def _field_data_key(
        self, master_key: bytes, key_id: str
    ) -> tuple[bytes, dict[str, Any]]:
        """Unwrap a field key; raises RedactedError/DecryptionError."""
        with closing(self._connect()) as cx:
            row = cx.execute(
                "SELECT field, wrapped_key FROM field_keys WHERE key_id = ?",
                (key_id,),
            ).fetchone()
        if row is None:
            raise RedactedError(
                f"no decryption key for {key_id}"
                " (never escrowed, or already redacted)",
                key_id=key_id,
                field="",
            )
        try:
            data_key = _fieldcrypto.decrypt(
                bytes(master_key),
                json.loads(str(row["wrapped_key"])),
                f"wrap:{key_id}".encode("utf-8"),
            )
        except _fieldcrypto.DecryptionError as e:
            raise _fieldcrypto.DecryptionError(
                f"cannot unwrap field key {key_id}: {e}"
            ) from e
        return data_key, {"field": str(row["field"])}

    def decrypt_fields(
        self, master_key: bytes, state: dict[str, Any]
    ) -> dict[str, Any]:
        """Restore encrypted fields; raises RedactedError/DecryptionError.

        A wrong master key fails the envelope authentication (no silent
        garbage). A shredded key raises :class:`RedactedError` carrying
        the ``key_id`` and ``field``.
        """
        import copy

        out = copy.deepcopy(state)

        def walk(node: Any, path: str) -> None:
            if isinstance(node, dict):
                for k, v in list(node.items()):
                    p = f"{path}.{k}" if path else str(k)
                    if _fieldcrypto.is_envelope(v):
                        key_id = str(v.get("key_id", ""))
                        try:
                            data_key, _ = self._field_data_key(
                                master_key, key_id
                            )
                        except RedactedError as e:
                            raise RedactedError(
                                str(e), key_id=key_id, field=p
                            ) from e
                        aad = self._enc_aad(self._name, p, key_id)
                        try:
                            raw = _fieldcrypto.decrypt(data_key, v, aad)
                        except _fieldcrypto.DecryptionError as e:
                            raise _fieldcrypto.DecryptionError(
                                f"field {p!r}: {e}"
                            ) from e
                        node[k] = _fieldcrypto.decode_value(raw)
                    else:
                        walk(v, p)
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, f"{path}[{i}]")

        walk(out, "")
        return out

    def _envelope_at(self, seq: int, field: str) -> tuple[dict, str]:
        try:
            state = self.state(version=seq)
        except KeyError:
            raise ValueError(f"no committed version {seq}") from None
        value = _get_path(state, field)
        if not _fieldcrypto.is_envelope(value):
            raise ValueError(
                f"field {field!r} is not encrypted at version {seq}"
            )
        return value, str(value.get("key_id", ""))

    def redact(
        self, seq: int, field: str, master_key: bytes
    ) -> dict[str, Any]:
        """Crypto-shred one encrypted field: destroy its data key.

        The ciphertext stays in the chain, so :meth:`verify` keeps
        passing: erasure needs no history rewrite. Afterwards even the
        master key cannot decrypt the field. The unwrapping step
        authorizes the redaction: a wrong master key raises
        :class:`DecryptionError` and nothing is deleted.

        Returns a receipt ``{"seq", "field", "key_id", "key_fp",
        "redacted_at"}``. Anyone with the receipt and DB access can
        verify the redaction: the envelope's key fingerprint matches the
        receipt and no key row exists for the ``key_id``.
        """
        _, key_id = self._envelope_at(seq, field)
        with closing(self._connect()) as cx:
            row = cx.execute(
                "SELECT wrapped_key, key_fp FROM field_keys WHERE key_id = ?",
                (key_id,),
            ).fetchone()
        if row is None:
            raise RedactedError(
                f"field {field!r} at version {seq} is already redacted",
                key_id=key_id,
                field=field,
            )
        # Authorization: only the master-key holder can shred.
        try:
            _fieldcrypto.decrypt(
                bytes(master_key),
                json.loads(str(row["wrapped_key"])),
                f"wrap:{key_id}".encode("utf-8"),
            )
        except _fieldcrypto.DecryptionError as e:
            raise _fieldcrypto.DecryptionError(
                f"redaction refused (wrong master key): {e}"
            ) from e
        with closing(self._connect()) as cx:
            cx.execute("DELETE FROM field_keys WHERE key_id = ?", (key_id,))
            cx.commit()
        return {
            "seq": seq,
            "field": field,
            "key_id": key_id,
            "key_fp": str(row["key_fp"]),
            "redacted_at": _utcnow(),
        }

    def redact_field(
        self, field: str, master_key: bytes
    ) -> list[dict[str, Any]]:
        """Redact ``field`` at every version where it is encrypted.

        Returns one receipt per shredded key. Already-redacted versions
        are skipped.
        """
        receipts: list[dict[str, Any]] = []
        for seq in range(1, self.version + 1):
            try:
                self._envelope_at(seq, field)
            except ValueError:
                continue  # not encrypted here (or not committed)
            try:
                receipts.append(self.redact(seq, field, master_key))
            except RedactedError:
                continue  # already shredded
        return receipts

    def redaction_status(self, seq: int, field: str) -> str:
        """``"active"`` | ``"redacted"`` | ``"not-encrypted"``."""
        try:
            _, key_id = self._envelope_at(seq, field)
        except ValueError:
            return "not-encrypted"
        with closing(self._connect()) as cx:
            row = cx.execute(
                "SELECT 1 FROM field_keys WHERE key_id = ?", (key_id,)
            ).fetchone()
        return "active" if row else "redacted"

    @staticmethod
    def _merkle_parent(left: bytes, right: bytes) -> bytes:
        # Domain-separated: internal nodes can never be confused with
        # leaves (leaves are raw row hashes, never prefixed).
        return hashlib.sha256(b"\x01" + left + right).digest()

    def merkle_root(self) -> str:
        """Merkle root over all row hashes, hex-encoded.

        The leaves are the raw row hashes in seq order; odd levels
        duplicate the last node (Bitcoin-style). Enables selective
        disclosure: publish the root (or sign it via :meth:`sign_tip`
        over a checkpoint), then prove any single row's inclusion with
        :meth:`inclusion_proof` without revealing the other rows. See
        ``docs/research/zk-audit-spike.md`` for why this, and not
        zero-knowledge proofs, is the recommended audit-privacy
        primitive here.
        """
        with closing(self._connect()) as cx:
            leaves = [
                bytes.fromhex(r["hash"])
                for r in cx.execute("SELECT hash FROM versions ORDER BY seq")
            ]
        if not leaves:
            return hashlib.sha256(b"world:empty-merkle-root").hexdigest()
        level = leaves
        while len(level) > 1:
            if len(level) % 2 == 1:
                level = level + [level[-1]]
            level = [
                self._merkle_parent(level[i], level[i + 1])
                for i in range(0, len(level), 2)
            ]
        return level[0].hex()

    def inclusion_proof(self, seq: int) -> dict[str, Any]:
        """Prove row ``seq`` is in the log: leaf, sibling path, root.

        The proof verifies standalone via :meth:`verify_inclusion`,
        without database access: recompute the root from the leaf and
        siblings and compare. ``KeyError`` for an unknown seq.
        """
        with closing(self._connect()) as cx:
            rows = cx.execute(
                "SELECT seq, hash FROM versions ORDER BY seq"
            ).fetchall()
        seqs = [int(r["seq"]) for r in rows]
        if seq not in seqs:
            raise KeyError(f"no row with seq {seq}")
        idx = seqs.index(seq)
        leaves = [bytes.fromhex(r["hash"]) for r in rows]
        siblings: list[dict[str, Any]] = []
        level = leaves
        while len(level) > 1:
            if len(level) % 2 == 1:
                level = level + [level[-1]]
            if idx % 2 == 0:
                siblings.append({"hash": level[idx + 1].hex(), "left": False})
            else:
                siblings.append({"hash": level[idx - 1].hex(), "left": True})
            level = [
                self._merkle_parent(level[i], level[i + 1])
                for i in range(0, len(level), 2)
            ]
            idx //= 2
        return {
            "seq": seq,
            "leaf": leaves[seqs.index(seq)].hex(),
            "siblings": siblings,
            "root": level[0].hex(),
        }

    @staticmethod
    def verify_inclusion(proof: dict[str, Any]) -> bool:
        """Check a proof from :meth:`inclusion_proof` without the database."""
        try:
            cur = bytes.fromhex(str(proof["leaf"]))
            for s in proof["siblings"]:
                sib = bytes.fromhex(str(s["hash"]))
                if s["left"]:
                    cur = World._merkle_parent(sib, cur)
                else:
                    cur = World._merkle_parent(cur, sib)
            return cur.hex() == str(proof["root"])
        except (KeyError, TypeError, ValueError):
            return False
