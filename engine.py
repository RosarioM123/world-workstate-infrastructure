"""
WORLD Day 1, Deterministic State Ledger (engine.py)

The killer demo:
  1. Ingest real-world data (see ingest.py next).
  2. Pipe it through this deterministic, append-only state ledger.
  3. Watch an AI agent try to break the rules, and get blocked by hard code.

Design principles:
  - Agents propose INTENTS. They never write state directly.
  - This engine validates every intent against physical/financial constraints.
  - Every attempt (committed or rejected) is appended to a tamper-evident,
    hash-chained ledger for a complete audit trail. Tamper-evidence is by
    application convention until chain verification and stronger storage
    controls land; the table itself is not database-enforced immutable.
  - Current state is a derived view of the ledger, never edited in place
    except through a validated transition.
  - Check-then-act runs inside a single write transaction (BEGIN IMMEDIATE)
    so concurrent writers cannot both pass the constraint checks.

Zero heavy dependencies: standard library + sqlite3 only.
"""

import hashlib
import json
import math
import os
import sqlite3
from contextlib import closing
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = str(Path(__file__).with_name("world_state.db"))

# Seed state for the default hub node. ingest.py computes its weather
# derates against SEED_CAPACITY, so the two modules share this constant
# instead of each hard-coding 1000.0 and silently disagreeing one day.
SEED_ENTITY_ID = "node_rotterdam_hub"
SEED_CAPACITY = 1000.0
SEED_LIQUIDITY = 50000.0


def _db_path() -> str:
    """Resolve the database file. WORLD_DB_PATH overrides the default so
    tests and demos can isolate state without touching the real ledger."""
    return os.environ.get("WORLD_DB_PATH", DB_PATH)


def connect_db() -> sqlite3.Connection:
    """Open a hardened SQLite connection shared by engine, API, and ingest.

    WAL mode lets readers proceed while a writer holds the lock, and a busy
    timeout turns transient lock contention into a short wait instead of an
    immediate "database is locked" failure under concurrent uvicorn workers.
    """
    conn = sqlite3.connect(_db_path(), timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_record(timestamp: str, entity_id: str, action: str,
                 payload: str, previous_hash: str | None, status: str) -> str:
    material = "|".join([
        timestamp, entity_id, action, payload,
        previous_hash or "GENESIS", status,
    ])
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def init_db() -> None:
    """Initializes the append-only, hash-chained state ledger."""
    with closing(connect_db()) as conn:
        cursor = conn.cursor()

        cursor.execute("""
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
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_state_ledger_entity
            ON state_ledger(entity_id)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                capacity REAL NOT NULL,
                available_liquidity REAL NOT NULL,
                status TEXT NOT NULL,
                last_updated TEXT NOT NULL
            )
        """)

        # Seed a default high-stakes node if empty (e.g. a supply-chain hub).
        cursor.execute("SELECT COUNT(*) FROM entities")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """
                INSERT INTO entities
                    (entity_id, capacity, available_liquidity, status, last_updated)
                VALUES (?, ?, ?, ?, ?)
                """,
                (SEED_ENTITY_ID, SEED_CAPACITY, SEED_LIQUIDITY,
                 "ACTIVE", _utcnow()),
            )

        conn.commit()


@dataclass
class IntentTransaction:
    """An agent's proposal. The agent asks; the engine decides."""
    entity_id: str
    action: str
    requested_delta_capacity: float
    requested_delta_cash: float


def _validate_intent(intent: IntentTransaction) -> None:
    """Reject malformed intents before they reach the constraint engine.

    NaN and Infinity are the critical cases: every comparison against them
    is False, so without this check a NaN delta would sail through the
    constraint checks as if it were valid and then corrupt the stored state
    (SQLite stores NaN as NULL, violating the NOT NULL columns).
    """
    if not isinstance(intent.entity_id, str) or not intent.entity_id:
        raise ValueError("Invalid intent: entity_id must be a non-empty string.")
    if not isinstance(intent.action, str) or not intent.action:
        raise ValueError("Invalid intent: action must be a non-empty string.")
    for name in ("requested_delta_capacity", "requested_delta_cash"):
        value = getattr(intent, name, None)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Invalid intent: {name} must be a number.")
        if not math.isfinite(value):
            raise ValueError(f"Invalid intent: {name} must be finite.")


def check_constraints(current_capacity: float, current_cash: float,
                      status: str, delta_capacity: float,
                      delta_cash: float) -> str | None:
    """The policy itself, as a pure function.

    Takes the entity's current state plus the requested deltas and returns
    a rejection reason, or None if the intent is allowed. No database, no
    I/O, no clock: the same inputs always produce the same verdict, which
    makes the policy unit-testable in isolation and auditable by reading
    one function. Check order is fixed and deterministic: node lock first,
    then the physical limit, then the financial limit.
    """
    if status == "LOCKED":
        return "Node is locked due to active macro shock wave."
    if current_capacity + delta_capacity < 0:
        return ("Constraint Violation: Capacity cannot drop below zero "
                "(Physical limit).")
    if current_cash + delta_cash < 0:
        return ("Constraint Violation: Insufficient liquidity "
                "(Financial limit).")
    return None


def execute_deterministic_transition(intent: IntentTransaction) -> dict:
    """
    The Math Constraint Engine.

    Validates an agent intent against physical/financial limits.
    If it breaks reality, it is REJECTED, but still appended to the
    tamper-evident log so the attempt itself is auditable, including
    attempts that name entities that do not exist.

    The read-check-write sequence runs inside one BEGIN IMMEDIATE
    transaction so two concurrent writers cannot both pass the constraint
    checks against the same stale state.

    Returns {"status": "COMMITTED" | "REJECTED", "details": {...}}.
    Raises ValueError only for malformed intents (see _validate_intent).
    """
    _validate_intent(intent)

    conn = connect_db()
    try:
        # One write transaction for the whole check-then-act sequence.
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT capacity, available_liquidity, status FROM entities WHERE entity_id = ?",
            (intent.entity_id,),
        )
        row = cursor.fetchone()
        timestamp = _utcnow()

        # --- DETERMINISTIC CONSTRAINT CHECKS (hard code, not vibes) ---
        # The policy lives in check_constraints(); this block only handles
        # the unknown-entity case, which needs a DB lookup to detect.
        rejection_reason: str | None = None

        if row is None:
            # Unknown entities are rejected AND logged, preserving the
            # "every attempt is on the ledger" invariant.
            rejection_reason = (
                f"Unknown entity: {intent.entity_id} is not in the state ledger."
            )
            current_capacity, current_cash, status = None, None, None
            target_capacity, target_cash = None, None
        else:
            current_capacity, current_cash, status = row
            rejection_reason = check_constraints(
                current_capacity, current_cash, status,
                intent.requested_delta_capacity, intent.requested_delta_cash,
            )
            target_capacity = current_capacity + intent.requested_delta_capacity
            target_cash = current_cash + intent.requested_delta_cash

        tx_status = "REJECTED" if rejection_reason else "COMMITTED"
        final_payload = {
            "intent": asdict(intent),
            "previous_capacity": current_capacity,
            "previous_cash": current_cash,
            "target_capacity": target_capacity,
            "target_cash": target_cash,
            "reason": rejection_reason if rejection_reason else "Success",
        }
        payload_json = json.dumps(final_payload, sort_keys=True)

        # Hash-chain to the previous ledger record (tamper-evidence).
        cursor.execute(
            "SELECT record_hash FROM state_ledger ORDER BY transaction_id DESC LIMIT 1"
        )
        prev = cursor.fetchone()
        previous_hash = prev[0] if prev else None
        record_hash = _hash_record(
            timestamp, intent.entity_id, intent.action,
            payload_json, previous_hash, tx_status,
        )

        # Append to the log regardless, full audit trail.
        cursor.execute(
            """
            INSERT INTO state_ledger
                (timestamp, entity_id, action, payload, previous_hash, record_hash, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (timestamp, intent.entity_id, intent.action, payload_json,
             previous_hash, record_hash, tx_status),
        )

        # Mutate materialized state ONLY on commit.
        if tx_status == "COMMITTED":
            cursor.execute(
                """
                UPDATE entities
                SET capacity = ?, available_liquidity = ?, last_updated = ?
                WHERE entity_id = ?
                """,
                (target_capacity, target_cash, timestamp, intent.entity_id),
            )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return {"status": tx_status, "details": final_payload}


def get_entity(entity_id: str) -> dict | None:
    with closing(connect_db()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM entities WHERE entity_id = ?", (entity_id,)
        ).fetchone()
        return dict(row) if row else None


def get_ledger(entity_id: str | None = None, limit: int = 50) -> list[dict]:
    with closing(connect_db()) as conn:
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


if __name__ == "__main__":
    init_db()
    print("State engine initialized. Testing guardrail constraints...")

    # Test 1: valid intent, allocate resources within physical limits.
    t1 = IntentTransaction(
        entity_id="node_rotterdam_hub",
        action="ALLOCATE_RESOURCES",
        requested_delta_capacity=-200.0,
        requested_delta_cash=5000.0,
    )
    print("Attempt 1 (Valid):", execute_deterministic_transition(t1))

    # Test 2: invalid intent, tries to drain more capacity than physics allows.
    t2 = IntentTransaction(
        entity_id="node_rotterdam_hub",
        action="DRAIN_RESOURCES",
        requested_delta_capacity=-5000.0,
        requested_delta_cash=0.0,
    )
    print("Attempt 2 (Invalid, Hallucination Blocked):",
          execute_deterministic_transition(t2))

    # Test 3: unknown entity, rejected but still logged for the audit trail.
    t3 = IntentTransaction(
        entity_id="node_does_not_exist",
        action="SPOOF_ATTEMPT",
        requested_delta_capacity=10.0,
        requested_delta_cash=10.0,
    )
    print("Attempt 3 (Unknown entity):", execute_deterministic_transition(t3))

    print("Final entity state:", get_entity("node_rotterdam_hub"))
