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
import logging
import math
import os
import sqlite3
import sys
from contextlib import closing
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = str(Path(__file__).with_name("world_state.db"))

# Seed state for the default hub node. ingest.py computes its weather
# derates against SEED_CAPACITY, so the two modules share this constant
# instead of each hard-coding 1000.0 and silently disagreeing one day.
SEED_ENTITY_ID = "node_rotterdam_hub"
SEED_CAPACITY = 1000.0
SEED_LIQUIDITY = 50000.0

# Intent metadata for the multi-agent future (the MIND/REALITY seam).
#
# These fields are schema-level: cheap to add now, expensive to retrofit
# onto existing ledger history later. They are recorded into every intent
# payload (and therefore covered by the hash chain) but not yet enforced
# or acted on. See docs/adr/0005-multi-agent-conflict-policy.md and
# docs/adr/0006-auth-rbac-shape.md for what they will mean once a second
# agent is actually submitting intents.
INTENT_KIND_INTERNAL = "INTERNAL_STATE"
INTENT_KIND_EXTERNAL = "EXTERNAL_EFFECT"
INTENT_KINDS = frozenset({INTENT_KIND_INTERNAL, INTENT_KIND_EXTERNAL})


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
    return datetime.now(UTC).isoformat()


def _hash_record(
    timestamp: str,
    entity_id: str,
    action: str,
    payload: str,
    previous_hash: str | None,
    status: str,
) -> str:
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

        # Idempotency keys map a client-supplied request id to the ledger
        # row of its first submission. A retry with the same key returns
        # the original verdict instead of appending a duplicate row. The
        # table is keyed, not the ledger, so old rows need no migration.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS idempotency_keys (
                idempotency_key TEXT PRIMARY KEY,
                transaction_id INTEGER NOT NULL
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
                (SEED_ENTITY_ID, SEED_CAPACITY, SEED_LIQUIDITY, "ACTIVE", _utcnow()),
            )

        conn.commit()


@dataclass
class IntentTransaction:
    """An agent's proposal. The agent asks; the engine decides.

    ``note`` carries free text (a decision, assumption, or observation)
    into the ledger payload. It never affects the constraint verdict:
    the engine still decides on the numeric deltas alone.

    ``actor`` names who submitted the intent (an agent id, a human, a
    service). Optional and unenforced today; it exists so ledger rows
    written before multi-agent use share one schema with rows written
    after, instead of forcing a backfill or a schema split later.

    ``kind`` marks whether the intent only changes WORLD's own state
    (``INTERNAL_STATE``) or requests an effect outside the ledger
    (``EXTERNAL_EFFECT``, e.g. a future REALITY action whose outcome is
    logged as a follow-up intent). Recorded, not acted on: the constraint
    verdict is identical either way.

    ``idempotency_key`` is a client-supplied request id. When set, a
    second submission with the same key returns the first submission's
    verdict instead of appending a duplicate row, so a retrying agent
    cannot accidentally double-apply an action.
    """

    entity_id: str
    action: str
    requested_delta_capacity: float
    requested_delta_cash: float
    note: str = ""
    actor: str | None = None
    kind: str = INTENT_KIND_INTERNAL
    idempotency_key: str | None = None


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
    if not isinstance(intent.note, str):
        raise ValueError("Invalid intent: note must be a string.")  # noqa: TRY004
    if intent.actor is not None and (
        not isinstance(intent.actor, str) or not intent.actor
    ):
        raise ValueError("Invalid intent: actor must be a non-empty string.")
    if not isinstance(intent.kind, str) or intent.kind not in INTENT_KINDS:
        raise ValueError(
            "Invalid intent: kind must be 'INTERNAL_STATE' or 'EXTERNAL_EFFECT'."
        )
    if intent.idempotency_key is not None and (
        not isinstance(intent.idempotency_key, str) or not intent.idempotency_key
    ):
        raise ValueError("Invalid intent: idempotency_key must be a non-empty string.")
    for name in ("requested_delta_capacity", "requested_delta_cash"):
        value = getattr(intent, name, None)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Invalid intent: {name} must be a number.")  # noqa: TRY004
        if not math.isfinite(value):
            raise ValueError(f"Invalid intent: {name} must be finite.")


def check_constraints(
    current_capacity: float,
    current_cash: float,
    status: str,
    delta_capacity: float,
    delta_cash: float,
) -> str | None:
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
        return "Constraint Violation: Capacity cannot drop below zero (Physical limit)."
    if current_cash + delta_cash < 0:
        return "Constraint Violation: Insufficient liquidity (Financial limit)."
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

        # Idempotent retry: a key seen before returns the original verdict
        # without appending a duplicate row. The key, not the payload,
        # defines identity, so a retried submission gets the first
        # submission's outcome even if the agent changed the fields.
        if intent.idempotency_key:
            cursor.execute(
                "SELECT transaction_id FROM idempotency_keys WHERE idempotency_key = ?",
                (intent.idempotency_key,),
            )
            seen = cursor.fetchone()
            if seen is not None:
                replay = cursor.execute(
                    "SELECT status, payload FROM state_ledger WHERE transaction_id = ?",
                    (seen[0],),
                ).fetchone()
                if replay is not None:
                    conn.commit()
                    return {"status": replay[0], "details": json.loads(replay[1])}
                # Key mapping without a ledger row (manual DB surgery):
                # fall through and re-process; the mapping is repaired below.

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
                current_capacity,
                current_cash,
                status,
                intent.requested_delta_capacity,
                intent.requested_delta_cash,
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
            timestamp,
            intent.entity_id,
            intent.action,
            payload_json,
            previous_hash,
            tx_status,
        )

        # Append to the log regardless, full audit trail.
        cursor.execute(
            """
            INSERT INTO state_ledger
                (timestamp, entity_id, action, payload, previous_hash, record_hash, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                intent.entity_id,
                intent.action,
                payload_json,
                previous_hash,
                record_hash,
                tx_status,
            ),
        )
        transaction_id = cursor.lastrowid

        # Remember the key for idempotent retries.
        if intent.idempotency_key:
            cursor.execute(
                "INSERT OR REPLACE INTO idempotency_keys "
                "(idempotency_key, transaction_id) VALUES (?, ?)",
                (intent.idempotency_key, transaction_id),
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


def verify_chain() -> tuple[bool, int | None]:
    """Verify the full ledger hash chain in transaction-ID order.

    Recomputes every record's hash from its stored fields and checks that
    each record's previous_hash matches the preceding record's hash
    (None for the genesis record). Returns (True, None) when the whole
    chain verifies, otherwise (False, bad_transaction_id) pinpointing the
    first broken record: a tampered payload/timestamp/action/status shows
    up as a record_hash mismatch, a spliced or reordered row as a
    previous_hash mismatch.

    An empty ledger verifies trivially: (True, None).
    """
    with closing(connect_db()) as conn:
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


def rogue_agent_attack() -> list[dict]:
    """Adversarial self-test of the constraint engine.

    A rogue agent proposes illegal state changes (an impossible drain, an
    impossible withdrawal, and a spoofed entity). Every one must come back
    REJECTED by hard code, and every attempt is appended to the ledger for
    the audit trail. The engine never raises for policy violations.
    """
    attacks = [
        IntentTransaction(
            SEED_ENTITY_ID,
            "ROGUE_DRAIN",
            requested_delta_capacity=-999999.0,
            requested_delta_cash=0.0,
        ),
        IntentTransaction(
            SEED_ENTITY_ID,
            "ROGUE_WITHDRAWAL",
            requested_delta_capacity=0.0,
            requested_delta_cash=-99999999.0,
        ),
        IntentTransaction(
            "node_does_not_exist",
            "ROGUE_SPOOF",
            requested_delta_capacity=10.0,
            requested_delta_cash=10.0,
        ),
    ]
    outcomes = []
    for intent in attacks:
        verdict = execute_deterministic_transition(intent)
        outcomes.append({"intent": intent.__dict__, "verdict": verdict})
    return outcomes


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(message)s")
    init_db()
    logger.info("State engine initialized. Testing guardrail constraints...")

    # Test 1: valid intent, allocate resources within physical limits.
    t1 = IntentTransaction(
        entity_id="node_rotterdam_hub",
        action="ALLOCATE_RESOURCES",
        requested_delta_capacity=-200.0,
        requested_delta_cash=5000.0,
    )
    logger.info("Attempt 1 (Valid): %s", execute_deterministic_transition(t1))

    # Test 2: invalid intent, tries to drain more capacity than physics allows.
    t2 = IntentTransaction(
        entity_id="node_rotterdam_hub",
        action="DRAIN_RESOURCES",
        requested_delta_capacity=-5000.0,
        requested_delta_cash=0.0,
    )
    logger.info(
        "Attempt 2 (Invalid, Hallucination Blocked): %s",
        execute_deterministic_transition(t2),
    )

    # Test 3: unknown entity, rejected but still logged for the audit trail.
    t3 = IntentTransaction(
        entity_id="node_does_not_exist",
        action="SPOOF_ATTEMPT",
        requested_delta_capacity=10.0,
        requested_delta_cash=10.0,
    )
    logger.info("Attempt 3 (Unknown entity): %s", execute_deterministic_transition(t3))

    logger.info("Final entity state: %s", get_entity("node_rotterdam_hub"))
