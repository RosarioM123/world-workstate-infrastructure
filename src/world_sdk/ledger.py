"""Client-owned deterministic ledger for the WORLD SDK.

``LocalLedger`` mirrors ``world_engine.core.engine`` exactly where it
matters for interoperability:

- the ``state_ledger`` table has the same columns in the same order, so a
  row written by the client is byte-compatible with a row written by the
  server;
- the hash material (field order, separator, GENESIS sentinel, payload JSON
  with sorted keys) is identical, so ``verify_chain()`` accepts chains
  built by either side;
- the constraint policy is not copied, it is imported: ``check_constraints``
  comes straight from the engine, so client and server verdicts cannot drift
  apart;
- REJECTED-but-logged semantics are preserved: a failed intent is still
  appended to the chain, and only COMMITTED intents mutate materialized
  state.

What the client ledger deliberately does NOT do: serve HTTP, run an
embedding model, or resolve timestamps. Those live in the sidecar
(``world_sdk.index``) or in ``WorldClient``.
"""

import hashlib
import json
import math
import os
import sqlite3
from collections.abc import Mapping, Sequence
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from world_engine.core.engine import (
    INTENT_KIND_INTERNAL,
    INTENT_KINDS,
    SEED_CAPACITY,
    SEED_ENTITY_ID,
    SEED_LIQUIDITY,
    check_constraints,
)

LEDGER_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS state_ledger (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        action TEXT NOT NULL,
        payload TEXT NOT NULL,
        previous_hash TEXT,
        record_hash TEXT NOT NULL,
        status TEXT NOT NULL
    )
"""

ENTITIES_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS entities (
        entity_id TEXT PRIMARY KEY,
        capacity REAL NOT NULL,
        available_liquidity REAL NOT NULL,
        status TEXT NOT NULL,
        last_updated TEXT NOT NULL
    )
"""

IDEMPOTENCY_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS idempotency_keys (
        idempotency_key TEXT PRIMARY KEY,
        transaction_id INTEGER NOT NULL
    )
"""

# Keys every imported ledger row must carry. Same columns as the server's
# state_ledger table, which is what makes import a plain copy.
LEDGER_ROW_KEYS = frozenset(
    {
        "transaction_id",
        "timestamp",
        "entity_id",
        "action",
        "payload",
        "previous_hash",
        "record_hash",
        "status",
    }
)


def _utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _hash_record(
    timestamp: str,
    entity_id: str,
    action: str,
    payload: str,
    previous_hash: str | None,
    status: str,
) -> str:
    """Hash material identical to the server engine's.

    Kept as a local copy (rather than importing the engine's private
    helper) so the SDK does not reach into server internals; parity is
    pinned by ``test_sdk_hash_matches_engine``.
    """
    material = "|".join(
        [
            timestamp,
            entity_id,
            action,
            payload,
            previous_hash or "GENESIS",
            status,
        ]
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _as_float(value: Any, name: str) -> float:
    """Coerce a delta to float, rejecting bools and non-finite values.

    Mirrors the server's ``_validate_intent`` numeric checks: a bool is not
    a number here, and NaN/Infinity would corrupt stored state.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(  # noqa: TRY004
            f"Invalid intent: {name} must be a number."
        )
    if not math.isfinite(value):
        raise ValueError(f"Invalid intent: {name} must be finite.")
    return float(value)


def normalize_deltas(
    deltas: Mapping[str, Any] | Sequence[Any] | None,
) -> tuple[float, float]:
    """Normalize the ``deltas`` argument of ``WorldClient.intent``.

    Accepts None (no change), a mapping with optional ``"capacity"`` and
    ``"cash"`` keys, or a 2-tuple ``(delta_capacity, delta_cash)``. Missing
    entries default to 0.0. Returns ``(delta_capacity, delta_cash)``.
    """
    if deltas is None:
        return 0.0, 0.0
    if isinstance(deltas, Mapping):
        raw_capacity = deltas.get("capacity", 0.0)
        raw_cash = deltas.get("cash", 0.0)
    elif isinstance(deltas, (tuple, list)) and len(deltas) == 2:
        raw_capacity, raw_cash = deltas
    else:
        raise ValueError(
            "Invalid intent: deltas must be None, a mapping with "
            "'capacity'/'cash' keys, or a (capacity, cash) pair."
        )
    return (
        _as_float(raw_capacity, "requested_delta_capacity"),
        _as_float(raw_cash, "requested_delta_cash"),
    )


class LocalLedger:
    """A client-owned, hash-chained intent ledger.

    ``db_path`` is the client's own SQLite file. The ledger starts with
    the same seed entity as the server so offline validation runs against
    identical initial state.
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
            cursor = conn.cursor()
            cursor.execute(LEDGER_TABLE_DDL)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_sdk_ledger_entity "
                "ON state_ledger(entity_id)"
            )
            cursor.execute(IDEMPOTENCY_TABLE_DDL)
            cursor.execute(ENTITIES_TABLE_DDL)
            cursor.execute("SELECT COUNT(*) FROM entities")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO entities "
                    "(entity_id, capacity, available_liquidity, status, last_updated)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (
                        SEED_ENTITY_ID,
                        SEED_CAPACITY,
                        SEED_LIQUIDITY,
                        "ACTIVE",
                        _utcnow(),
                    ),
                )
            conn.commit()

    @property
    def latest_height(self) -> int:
        """Highest block height (transaction_id) in the ledger, 0 if empty."""
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT MAX(transaction_id) FROM state_ledger"
            ).fetchone()
        return int(row[0]) if row[0] is not None else 0

    def intent(
        self,
        entity_id: str,
        action: str,
        deltas: Mapping[str, Any] | Sequence[Any] | None = None,
        note: str = "",
        actor: str | None = None,
        kind: str = INTENT_KIND_INTERNAL,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Validate an intent locally and append it to the client ledger.

        Same contract as the server's ``execute_deterministic_transition``:
        returns ``{"status": "COMMITTED" | "REJECTED", "details": {...}}``,
        raises ValueError only for malformed intents. The returned dict also
        carries ``transaction_id`` and ``timestamp`` for the appended row so
        callers (e.g. the timestamp sidecar) can index it.

        ``actor`` names the submitter, ``kind`` marks INTERNAL_STATE vs
        EXTERNAL_EFFECT, and ``idempotency_key`` deduplicates retries: a
        second submission with the same key returns the first submission's
        verdict without appending a new row.
        """
        if not isinstance(entity_id, str) or not entity_id:
            raise ValueError("Invalid intent: entity_id must be a non-empty string.")
        if not isinstance(action, str) or not action:
            raise ValueError("Invalid intent: action must be a non-empty string.")
        if not isinstance(note, str):
            raise ValueError(  # noqa: TRY004
                "Invalid intent: note must be a string."
            )
        if actor is not None and (not isinstance(actor, str) or not actor):
            raise ValueError("Invalid intent: actor must be a non-empty string.")
        if not isinstance(kind, str) or kind not in INTENT_KINDS:
            raise ValueError(
                "Invalid intent: kind must be 'INTERNAL_STATE' or 'EXTERNAL_EFFECT'."
            )
        if idempotency_key is not None and (
            not isinstance(idempotency_key, str) or not idempotency_key
        ):
            raise ValueError(
                "Invalid intent: idempotency_key must be a non-empty string."
            )
        delta_capacity, delta_cash = normalize_deltas(deltas)

        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.cursor()

            if idempotency_key:
                cursor.execute(
                    "SELECT transaction_id FROM idempotency_keys "
                    "WHERE idempotency_key = ?",
                    (idempotency_key,),
                )
                seen = cursor.fetchone()
                if seen is not None:
                    replay = cursor.execute(
                        "SELECT transaction_id, timestamp, status, payload "
                        "FROM state_ledger WHERE transaction_id = ?",
                        (seen[0],),
                    ).fetchone()
                    if replay is not None:
                        conn.commit()
                        return {
                            "status": replay[2],
                            "details": json.loads(replay[3]),
                            "transaction_id": replay[0],
                            "timestamp": replay[1],
                        }

            cursor.execute(
                "SELECT capacity, available_liquidity, status FROM entities "
                "WHERE entity_id = ?",
                (entity_id,),
            )
            row = cursor.fetchone()
            timestamp = _utcnow()

            rejection_reason: str | None = None
            if row is None:
                rejection_reason = (
                    f"Unknown entity: {entity_id} is not in the state ledger."
                )
                current_capacity, current_cash, status = None, None, None
                target_capacity, target_cash = None, None
            else:
                current_capacity, current_cash, status = row
                rejection_reason = check_constraints(
                    current_capacity,
                    current_cash,
                    status,
                    delta_capacity,
                    delta_cash,
                )
                target_capacity = current_capacity + delta_capacity
                target_cash = current_cash + delta_cash

            tx_status = "REJECTED" if rejection_reason else "COMMITTED"
            final_payload = {
                "intent": {
                    "entity_id": entity_id,
                    "action": action,
                    "requested_delta_capacity": delta_capacity,
                    "requested_delta_cash": delta_cash,
                    "note": note,
                    "actor": actor,
                    "kind": kind,
                    "idempotency_key": idempotency_key,
                },
                "previous_capacity": current_capacity,
                "previous_cash": current_cash,
                "target_capacity": target_capacity,
                "target_cash": target_cash,
                "reason": rejection_reason if rejection_reason else "Success",
            }
            payload_json = json.dumps(final_payload, sort_keys=True)

            cursor.execute(
                "SELECT record_hash FROM state_ledger "
                "ORDER BY transaction_id DESC LIMIT 1"
            )
            prev = cursor.fetchone()
            previous_hash = prev[0] if prev else None
            record_hash = _hash_record(
                timestamp, entity_id, action, payload_json, previous_hash, tx_status
            )

            cursor.execute(
                "INSERT INTO state_ledger "
                "(timestamp, entity_id, action, payload, previous_hash, "
                " record_hash, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    timestamp,
                    entity_id,
                    action,
                    payload_json,
                    previous_hash,
                    record_hash,
                    tx_status,
                ),
            )
            transaction_id = cursor.lastrowid

            if idempotency_key:
                cursor.execute(
                    "INSERT OR REPLACE INTO idempotency_keys "
                    "(idempotency_key, transaction_id) VALUES (?, ?)",
                    (idempotency_key, transaction_id),
                )

            if tx_status == "COMMITTED":
                cursor.execute(
                    "UPDATE entities SET capacity = ?, available_liquidity = ?, "
                    "last_updated = ? WHERE entity_id = ?",
                    (target_capacity, target_cash, timestamp, entity_id),
                )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        return {
            "status": tx_status,
            "details": final_payload,
            "transaction_id": transaction_id,
            "timestamp": timestamp,
        }

    def verify_chain(self) -> tuple[bool, int | None]:
        """Verify the full hash chain. Same algorithm as the server.

        Returns (True, None) when every record's hash recomputes and every
        previous_hash links correctly, else (False, bad_transaction_id).
        """
        with closing(self._connect()) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT transaction_id, timestamp, entity_id, action, payload,"
                " previous_hash, record_hash, status"
                " FROM state_ledger ORDER BY transaction_id ASC"
            ).fetchall()

        expected_previous: str | None = None
        for row in rows:
            tx_id = row["transaction_id"]
            if row["previous_hash"] != expected_previous:
                return False, tx_id
            recomputed = _hash_record(
                row["timestamp"],
                row["entity_id"],
                row["action"],
                row["payload"],
                row["previous_hash"],
                row["status"],
            )
            if recomputed != row["record_hash"]:
                return False, tx_id
            expected_previous = row["record_hash"]
        return True, None

    def get_ledger(self, entity_id: str | None = None, limit: int = 50) -> list[dict]:
        """Recent ledger rows, newest first. Same shape as the server's."""
        with closing(self._connect()) as conn:
            conn.row_factory = sqlite3.Row
            if entity_id:
                rows = conn.execute(
                    "SELECT * FROM state_ledger WHERE entity_id = ? "
                    "ORDER BY transaction_id DESC LIMIT ?",
                    (entity_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM state_ledger ORDER BY transaction_id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [dict(r) for r in rows]

    def get_entity(self, entity_id: str) -> dict | None:
        """Current materialized state for one entity, or None."""
        with closing(self._connect()) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM entities WHERE entity_id = ?", (entity_id,)
            ).fetchone()
            return dict(row) if row else None

    def replay_to(self, height: int) -> dict[str, dict[str, Any]]:
        """Rebuild materialized state by replaying COMMITTED rows.

        Starts from the seed state and applies every COMMITTED intent with
        ``transaction_id <= height`` in chain order. This is the primitive
        behind time-travel reads: ``state_at_block(N)`` and, via the
        timestamp sidecar, ``state_at_time(T)``.
        """
        if height < 0:
            raise ValueError("height must be non-negative.")
        height = min(height, self.latest_height)

        state: dict[str, dict[str, Any]] = {
            SEED_ENTITY_ID: {
                "entity_id": SEED_ENTITY_ID,
                "capacity": SEED_CAPACITY,
                "available_liquidity": SEED_LIQUIDITY,
                "status": "ACTIVE",
            }
        }
        with closing(self._connect()) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT entity_id, payload FROM state_ledger "
                "WHERE transaction_id <= ? AND status = 'COMMITTED' "
                "ORDER BY transaction_id ASC",
                (height,),
            ).fetchall()
        for row in rows:
            payload = json.loads(row["payload"])
            intent = payload.get("intent") or {}
            entity = state.get(intent.get("entity_id", ""))
            if entity is None:
                continue
            if payload.get("target_capacity") is not None:
                entity["capacity"] = payload["target_capacity"]
            if payload.get("target_cash") is not None:
                entity["available_liquidity"] = payload["target_cash"]
        return state

    def import_ledger_rows(self, rows: Sequence[Mapping[str, Any]]) -> int:
        """Copy server ledger rows into this client ledger.

        Each row must carry the full ``state_ledger`` column set; hashes
        are preserved verbatim, so the imported prefix keeps verifying.
        Existing transaction_ids are skipped, materialized state is rebuilt
        from the merged chain, and the chain is verified before returning.
        Returns the number of rows actually inserted.
        """
        rows = list(rows)
        for row in rows:
            missing = LEDGER_ROW_KEYS - set(row.keys())
            if missing:
                raise ValueError(f"Ledger row is missing keys: {sorted(missing)}")

        inserted_ids: list[int] = []
        with closing(self._connect()) as conn:
            cursor = conn.cursor()
            for row in rows:
                cursor.execute(
                    "INSERT OR IGNORE INTO state_ledger "
                    "(transaction_id, timestamp, entity_id, action, payload, "
                    " previous_hash, record_hash, status) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        row["transaction_id"],
                        row["timestamp"],
                        row["entity_id"],
                        row["action"],
                        row["payload"],
                        row["previous_hash"],
                        row["record_hash"],
                        row["status"],
                    ),
                )
                if cursor.rowcount:
                    inserted_ids.append(int(row["transaction_id"]))
            conn.commit()

        ok, bad_id = self.verify_chain()
        if not ok:
            # Roll back the import so a failed sync leaves the ledger
            # exactly as it was before.
            if inserted_ids:
                placeholders = ",".join("?" for _ in inserted_ids)
                with closing(self._connect()) as conn:
                    conn.execute(
                        "DELETE FROM state_ledger "
                        f"WHERE transaction_id IN ({placeholders})",
                        inserted_ids,
                    )
                    conn.commit()
            raise ValueError(
                f"Imported rows break the hash chain at transaction {bad_id}."
            )

        self._rebuild_entities()
        self._rebuild_idempotency_keys()
        return len(inserted_ids)

    def _rebuild_idempotency_keys(self) -> None:
        """Rebuild the dedup table from the ledger payloads.

        Used after imports so a synced ledger keeps deduplicating retries:
        every row whose payload carries a non-empty ``idempotency_key``
        maps back to its transaction, first occurrence wins. Rows written
        before the schema seam (or with malformed payloads) carry no key
        and are skipped.
        """
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT transaction_id, payload FROM state_ledger "
                "ORDER BY transaction_id"
            ).fetchall()
        mappings: list[tuple[str, int]] = []
        for transaction_id, payload in rows:
            try:
                key = json.loads(payload).get("intent", {}).get("idempotency_key")
            except (json.JSONDecodeError, AttributeError):
                continue
            if isinstance(key, str) and key:
                mappings.append((key, int(transaction_id)))
        with closing(self._connect()) as conn:
            conn.execute("DELETE FROM idempotency_keys")
            conn.executemany(
                "INSERT OR IGNORE INTO idempotency_keys "
                "(idempotency_key, transaction_id) VALUES (?, ?)",
                mappings,
            )
            conn.commit()

    def _rebuild_entities(self) -> None:
        """Reset materialized state to the seed, then replay the chain.

        Used after imports so the entities table always reflects the
        ledger, never the other way around.
        """
        with closing(self._connect()) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM entities")
            cursor.execute(
                "INSERT INTO entities "
                "(entity_id, capacity, available_liquidity, status, last_updated)"
                " VALUES (?, ?, ?, ?, ?)",
                (SEED_ENTITY_ID, SEED_CAPACITY, SEED_LIQUIDITY, "ACTIVE", _utcnow()),
            )
            conn.commit()
        state = self.replay_to(self.latest_height)
        with closing(self._connect()) as conn:
            cursor = conn.cursor()
            for entity_id, entity in state.items():
                cursor.execute(
                    "UPDATE entities SET capacity = ?, available_liquidity = ?, "
                    "status = ?, last_updated = ? WHERE entity_id = ?",
                    (
                        entity["capacity"],
                        entity["available_liquidity"],
                        entity["status"],
                        _utcnow(),
                        entity_id,
                    ),
                )
            conn.commit()


def default_db_path() -> str:
    """Default client ledger location: ``~/.world/world_client.db``."""
    directory = Path(os.path.expanduser("~")) / ".world"
    directory.mkdir(parents=True, exist_ok=True)
    return str(directory / "world_client.db")
