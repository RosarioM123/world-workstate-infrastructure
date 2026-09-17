"""
WORLD Day 1 — Deterministic State Ledger (engine.py)

The killer demo:
  1. Ingest real-world data (see ingest.py next).
  2. Pipe it through this deterministic, append-only state ledger.
  3. Watch an AI agent try to break the rules — and get blocked by hard code.

Design principles:
  - Agents propose INTENTS. They never write state directly.
  - This engine validates every intent against physical/financial constraints.
  - Every attempt (committed or rejected) is appended to an immutable,
    hash-chained ledger for a complete audit trail.
  - Current state is a derived view of the ledger — never edited in place
    except through a validated transition.

Zero heavy dependencies: standard library + sqlite3 only.
"""

import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = str(Path(__file__).with_name("world_state.db"))


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
    conn = sqlite3.connect(DB_PATH)
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
            ("node_rotterdam_hub", 1000.0, 50000.0, "ACTIVE", _utcnow()),
        )

    conn.commit()
    conn.close()


@dataclass
class IntentTransaction:
    """An agent's proposal. The agent asks; the engine decides."""
    entity_id: str
    action: str
    requested_delta_capacity: float
    requested_delta_cash: float


def execute_deterministic_transition(intent: IntentTransaction) -> dict:
    """
    The Math Constraint Engine.

    Validates an agent intent against physical/financial limits.
    If it breaks reality, it is REJECTED — but still appended to the
    immutable log so the attempt itself is auditable.

    Returns {"status": "COMMITTED" | "REJECTED", "details": {...}}.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT capacity, available_liquidity, status FROM entities WHERE entity_id = ?",
        (intent.entity_id,),
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Entity {intent.entity_id} does not exist in state ledger.")

    current_capacity, current_cash, status = row
    timestamp = _utcnow()

    # --- DETERMINISTIC CONSTRAINT CHECKS (hard code, not vibes) ---
    rejection_reason: str | None = None

    target_capacity = current_capacity + intent.requested_delta_capacity
    target_cash = current_cash + intent.requested_delta_cash

    if status == "LOCKED":
        rejection_reason = "Node is locked due to active macro shock wave."
    elif target_capacity < 0:
        rejection_reason = (
            "Constraint Violation: Capacity cannot drop below zero (Physical limit)."
        )
    elif target_cash < 0:
        rejection_reason = (
            "Constraint Violation: Insufficient liquidity (Financial limit)."
        )

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

    # Append to the immutable log regardless — full audit trail.
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
    conn.close()

    return {"status": tx_status, "details": final_payload}


def get_entity(entity_id: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM entities WHERE entity_id = ?", (entity_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_ledger(entity_id: str | None = None, limit: int = 50) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    init_db()
    print("State engine initialized. Testing guardrail constraints...")

    # Test 1: valid intent — allocate resources within physical limits.
    t1 = IntentTransaction(
        entity_id="node_rotterdam_hub",
        action="ALLOCATE_RESOURCES",
        requested_delta_capacity=-200.0,
        requested_delta_cash=5000.0,
    )
    print("Attempt 1 (Valid):", execute_deterministic_transition(t1))

    # Test 2: invalid intent — tries to drain more capacity than physics allows.
    t2 = IntentTransaction(
        entity_id="node_rotterdam_hub",
        action="DRAIN_RESOURCES",
        requested_delta_capacity=-5000.0,
        requested_delta_cash=0.0,
    )
    print("Attempt 2 (Invalid — Hallucination Blocked):",
          execute_deterministic_transition(t2))

    print("Final entity state:", get_entity("node_rotterdam_hub"))
