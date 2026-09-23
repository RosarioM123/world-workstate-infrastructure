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
import json
import os
import re
import sqlite3
from collections.abc import Callable
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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
        """Return the document: current, at a version, or at a checkpoint."""
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
                    "SELECT state FROM versions WHERE seq = ?", (version,)
                ).fetchone()
                if row is None:
                    raise KeyError(f"unknown version: {version}")
            return json.loads(row["state"]) if row is not None else {}

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
        """
        if not isinstance(state, dict):
            raise TypeError(f"state must be a dict, got {type(state).__name__}")
        try:
            state_text = _canonical(state)
        except (TypeError, ValueError) as e:
            raise ValueError(f"state is not JSON-serializable: {e}") from e
        timestamp = _utcnow()
        with closing(self._connect()) as cx:
            cur = self._latest_committed(cx)
            cur_seq = int(cur["seq"]) if cur is not None else 0
            old: dict[str, Any] = json.loads(cur["state"]) if cur is not None else {}
            if expected_version is not None and expected_version != cur_seq:
                raise ConflictError(
                    f"expected version {expected_version}, current is {cur_seq}"
                )
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
            # Serialize writers: dedupe-check and append are one atomic step.
            # Idempotency dedupes committed updates only: every proposal is
            # judged first, so rejected attempts are always recorded.
            cx.execute("BEGIN IMMEDIATE")
            try:
                seq: int | None = None
                if status == "COMMITTED" and idempotency_key is not None:
                    hit = cx.execute(
                        "SELECT seq FROM idempotency WHERE key = ?",
                        (idempotency_key,),
                    ).fetchone()
                    if hit is not None:
                        seq = int(hit["seq"])
                if seq is None:
                    seq = self._append(
                        cx,
                        timestamp=timestamp,
                        actor=actor,
                        note=final_note,
                        state_text=state_text,
                        status=status,
                    )
                    if idempotency_key is not None and status == "COMMITTED":
                        cx.execute(
                            "INSERT INTO idempotency(key, seq) VALUES (?, ?)",
                            (idempotency_key, seq),
                        )
            except BaseException:
                cx.rollback()
                raise
            else:
                cx.commit()
        if violation is not None:
            raise InvariantViolation(violation.reason, seq=seq) from violation
        return seq

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
