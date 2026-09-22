"""Client-owned index sidecar for the WORLD SDK.

Two disposable indexes in one sqlite3 file, both derived from the ledger
and both excluded from the integrity path:

- ``embeddings``: block_height -> vector blob. Bring-your-own embeddings:
  the SDK never calls an embedding model or API, the caller supplies
  vectors. Search is cosine similarity in pure Python.
- ``timestamps``: block_height -> block_time. This is the client-side
  timestamp resolution the time-travel design calls for: the server stays
  stdlib-pure and block-height canonical, while the client answers
  "what did we know at time T" by resolving T to a height locally and
  replaying the ledger to that height.

If the sidecar is deleted, nothing of value is lost: rebuild it by
re-adding vectors and re-recording timestamps from the ledger.
"""

import math
import os
import sqlite3
import struct
from collections.abc import Sequence
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _as_vector(values: Sequence[Any], name: str) -> tuple[float, ...]:
    """Validate a vector: non-empty, finite floats, no bools."""
    items = tuple(values)
    if not items:
        raise ValueError(f"Invalid vector: {name} must be non-empty.")
    out: list[float] = []
    for value in items:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(  # noqa: TRY004
                f"Invalid vector: {name} entries must be numbers."
            )
        if not math.isfinite(value):
            raise ValueError(f"Invalid vector: {name} entries must be finite.")
        out.append(float(value))
    return tuple(out)


def _pack(vector: tuple[float, ...]) -> bytes:
    return struct.pack(f"<{len(vector)}d", *vector)


def _unpack(blob: bytes, dim: int) -> tuple[float, ...]:
    return struct.unpack(f"<{dim}d", blob)


def _cosine(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    """Cosine similarity. A zero-norm vector scores 0.0 against anything."""
    norm_a = math.fsum(x * x for x in a)
    norm_b = math.fsum(y * y for y in b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    dot = math.fsum(x * y for x, y in zip(a, b))
    return dot / math.sqrt(norm_a * norm_b)


def _normalize_time(value: str | datetime) -> str:
    """Normalize a timestamp to canonical UTC ISO8601.

    Accepts an ISO8601 string or a datetime. Naive datetimes are rejected:
    an ambiguous wall clock has no place in an audit index. The canonical
    form sorts lexicographically in chronological order, which is what the
    ``resolve`` query relies on.
    """
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value)
    elif isinstance(value, datetime):
        parsed = value
    else:
        raise ValueError(  # noqa: TRY004
            "block_time must be an ISO8601 string or datetime."
        )
    if parsed.tzinfo is None:
        raise ValueError("block_time must be timezone-aware, not naive.")
    return parsed.astimezone(UTC).isoformat()


class EmbeddingSidecar:
    """Disposable vector + timestamp indexes, owned by the client.

    ``db_path`` is the client's own SQLite file, separate from the ledger.
    """

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def _init_db(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS embeddings ("
                " block_height INTEGER PRIMARY KEY,"
                " dim INTEGER NOT NULL,"
                " vector BLOB NOT NULL)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS timestamps ("
                " block_height INTEGER PRIMARY KEY,"
                " block_time TEXT NOT NULL)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_sidecar_timestamps_time"
                " ON timestamps(block_time)"
            )
            conn.commit()

    def _dim(self) -> int | None:
        with closing(self._connect()) as conn:
            row = conn.execute("SELECT dim FROM embeddings LIMIT 1").fetchone()
        return int(row[0]) if row else None

    def add(self, block_height: int, vector: Sequence[Any]) -> None:
        """Store (or replace) the embedding vector for a block height."""
        if isinstance(block_height, bool) or not isinstance(block_height, int):
            raise ValueError(  # noqa: TRY004
                "block_height must be an integer."
            )
        if block_height < 1:
            raise ValueError("block_height must be >= 1.")
        vec = _as_vector(vector, "vector")
        existing_dim = self._dim()
        if existing_dim is not None and len(vec) != existing_dim:
            raise ValueError(
                f"Dimension mismatch: sidecar holds dim {existing_dim}, "
                f"got dim {len(vec)}."
            )
        with closing(self._connect()) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO embeddings "
                "(block_height, dim, vector) VALUES (?, ?, ?)",
                (block_height, len(vec), _pack(vec)),
            )
            conn.commit()

    def search(
        self, query_vector: Sequence[Any], k: int = 5
    ) -> list[tuple[int, float]]:
        """Top-k block heights by cosine similarity, highest score first.

        Ties break by ascending block height so results are deterministic.
        Returns an empty list when the index is empty or k is 0.
        """
        if isinstance(k, bool) or not isinstance(k, int) or k < 0:
            raise ValueError("k must be a non-negative integer.")
        query = _as_vector(query_vector, "query_vector")
        existing_dim = self._dim()
        if existing_dim is None:
            return []
        if len(query) != existing_dim:
            raise ValueError(
                f"Dimension mismatch: sidecar holds dim {existing_dim}, "
                f"query has dim {len(query)}."
            )
        scored: list[tuple[int, float]] = []
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT block_height, dim, vector FROM embeddings"
            ).fetchall()
        for block_height, dim, blob in rows:
            vec = _unpack(blob, dim)
            scored.append((int(block_height), _cosine(query, vec)))
        scored.sort(key=lambda item: (-item[1], item[0]))
        return scored[:k]

    def record_timestamp(self, block_height: int, block_time: str | datetime) -> None:
        """Record the wall-clock time a block was committed.

        Upserts: re-recording a height replaces its timestamp. Timestamps
        are normalized to canonical UTC ISO8601 on write.
        """
        if isinstance(block_height, bool) or not isinstance(block_height, int):
            raise ValueError(  # noqa: TRY004
                "block_height must be an integer."
            )
        if block_height < 1:
            raise ValueError("block_height must be >= 1.")
        canonical = _normalize_time(block_time)
        with closing(self._connect()) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO timestamps "
                "(block_height, block_time) VALUES (?, ?)",
                (block_height, canonical),
            )
            conn.commit()

    def resolve(self, at_time: str | datetime) -> int | None:
        """Resolve a timestamp to the latest block at or before it.

        Returns the max block_height with block_time <= T, or None when no
        block exists at or before T. Equal timestamps resolve to the
        highest block height among them.
        """
        canonical = _normalize_time(at_time)
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT MAX(block_height) FROM timestamps WHERE block_time <= ?",
                (canonical,),
            ).fetchone()
        return int(row[0]) if row[0] is not None else None


def default_index_path() -> str:
    """Default sidecar location: ``~/.world/world_index.db``."""
    directory = Path(os.path.expanduser("~")) / ".world"
    directory.mkdir(parents=True, exist_ok=True)
    return str(directory / "world_index.db")
