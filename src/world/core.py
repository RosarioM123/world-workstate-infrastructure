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
import sqlite3
from collections.abc import Callable, Iterable
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import ed25519 as _ed25519

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

    def sign_tip(self, key: bytes | str) -> dict[str, Any]:
        """Sign the chain tip with an HMAC key held outside the database.

        Returns ``{"name", "seq", "hash", "sig"}``. Store it out-of-band
        (a file, a log, another system): anyone holding it can later prove
        the chain was rolled back or rewritten, which ``verify()`` alone
        cannot detect on an unkeyed chain. The key is never written to
        the database; anyone with the key can sign, so protect it like
        a password. For public verifiability (anyone verifies, only the
        signer signs), use :meth:`sign_tip_ed25519` /
        :meth:`verify_tip_ed25519` instead.
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
        }

    def verify_tip(self, key: bytes | str, signed_tip: dict[str, Any]) -> bool:
        """Check a tip signature from :meth:`sign_tip` against this world.

        Returns False when the signature is forged (wrong key or tampered
        fields) or when the chain no longer contains that ``(seq, hash)``
        pair, i.e. the history was rolled back or rewritten after signing.
        """
        raw = key.encode("utf-8") if isinstance(key, str) else bytes(key)
        try:
            name = str(signed_tip["name"])
            seq = int(signed_tip["seq"])
            tip_hash = str(signed_tip["hash"])
            sig = str(signed_tip["sig"])
        except (KeyError, TypeError, ValueError):
            return False
        if name != self._name:
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

    def sign_tip_ed25519(self, private_key: bytes) -> dict[str, Any]:
        """Sign the chain tip with an Ed25519 private key.

        Same ``(name, seq, hash)`` message as :meth:`sign_tip`, but the
        signature is publicly verifiable: anyone holding the *public* key
        can check it, while only the private-key holder can sign. Returns
        ``{"name", "seq", "hash", "sig", "alg": "ed25519"}`` with the
        signature hex-encoded. The private key is never written to the
        database; distribute the public key out-of-band (it is public,
        so a README or DNS record will do). Key generation:
        ``world.ed25519.create_keypair()``.
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
        }

    def verify_tip_ed25519(
        self, public_key: bytes, signed_tip: dict[str, Any]
    ) -> bool:
        """Verify an Ed25519 tip signature against this world.

        The public key must come from out-of-band distribution, never from
        the signed tip itself (otherwise an attacker rewrites the chain
        *and* re-signs with their own key). Returns False for forged
        signatures, tampered fields, algorithm confusion (an HMAC tip
        passed here is rejected), name mismatch, or a chain that no longer
        contains the signed ``(seq, hash)`` pair.
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
        except (KeyError, TypeError, ValueError):
            return False
        if name != self._name:
            return False
        if not _ed25519.checkvalid(
            sig, self._tip_message(name, seq, tip_hash), bytes(public_key)
        ):
            return False
        with closing(self._connect()) as cx:
            row = cx.execute(
                "SELECT hash FROM versions WHERE seq = ?", (seq,)
            ).fetchone()
        return row is not None and str(row["hash"]) == tip_hash

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
