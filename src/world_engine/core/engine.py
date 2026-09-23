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


def _append_ledger_row(
    cursor: sqlite3.Cursor,
    timestamp: str,
    entity_id: str,
    action: str,
    payload_json: str,
    status: str,
) -> int:
    """Append one hash-chained row to the ledger. Returns transaction_id.

    The caller owns the transaction: this only runs the SELECT + INSERT
    on the given cursor. Every writer goes through here so the
    chain-linking discipline lives in exactly one place.
    """
    cursor.execute(
        "SELECT record_hash FROM state_ledger ORDER BY transaction_id DESC LIMIT 1"
    )
    prev = cursor.fetchone()
    previous_hash = prev[0] if prev else None
    record_hash = _hash_record(
        timestamp, entity_id, action, payload_json, previous_hash, status
    )
    cursor.execute(
        """
        INSERT INTO state_ledger
            (timestamp, entity_id, action, payload, previous_hash, record_hash, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            entity_id,
            action,
            payload_json,
            previous_hash,
            record_hash,
            status,
        ),
    )
    transaction_id = cursor.lastrowid
    assert transaction_id is not None  # INSERT always yields a rowid
    return transaction_id


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


def execute_deterministic_transition(
    intent: IntentTransaction,
    conn: sqlite3.Connection | None = None,
) -> dict:
    """
    The Math Constraint Engine.

    Validates an agent intent against physical/financial limits.
    If it breaks reality, it is REJECTED, but still appended to the
    tamper-evident log so the attempt itself is auditable, including
    attempts that name entities that do not exist.

    The read-check-write sequence runs inside one BEGIN IMMEDIATE
    transaction so two concurrent writers cannot both pass the constraint
    checks against the same stale state.

    ``conn`` is a seam for batch writers (e.g. the transcript importer):
    pass an open connection already holding a BEGIN IMMEDIATE transaction
    and this call participates in it — no BEGIN/COMMIT/close of its own.
    When omitted, the call manages its own connection exactly as before.

    Returns {"status": "COMMITTED" | "REJECTED", "details": {...}}.
    Raises ValueError only for malformed intents (see _validate_intent).
    """
    _validate_intent(intent)

    own_conn = conn is None
    if own_conn:
        conn = connect_db()
    assert conn is not None
    try:
        if own_conn:
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

        # Hash-chain to the previous ledger record (tamper-evidence) and
        # append to the log regardless: full audit trail.
        transaction_id = _append_ledger_row(
            cursor,
            timestamp,
            intent.entity_id,
            intent.action,
            payload_json,
            tx_status,
        )

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

        if own_conn:
            conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()

    return {"status": tx_status, "details": final_payload}


def get_entity(entity_id: str) -> dict | None:
    with closing(connect_db()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM entities WHERE entity_id = ?", (entity_id,)
        ).fetchone()
        return dict(row) if row else None


def register_entity(
    entity_id: str,
    capacity: float,
    liquidity: float,
    actor: str | None = None,
) -> dict:
    """Register a new entity and log its creation on the ledger.

    The database starts with a single seeded node; this is how a second,
    third, and further nodes join the world. Inputs are validated the same
    way intents are (non-empty id, finite non-negative numbers, a
    non-empty actor when given). Registration runs under BEGIN IMMEDIATE
    so two concurrent registrations of the same id cannot both succeed.

    The creation is appended to the hash-chained ledger as a COMMITTED
    REGISTER_ENTITY row, so entity creation is auditable exactly like
    every other state change. ``actor`` is a plain label, it confers no
    authority.

    Raises ValueError for malformed input. Raises ValueError when the
    entity_id is already registered (the API maps that to HTTP 409).
    """
    if not isinstance(entity_id, str) or not entity_id:
        raise ValueError("Invalid entity: entity_id must be a non-empty string.")
    if len(entity_id) > 64:
        raise ValueError("Invalid entity: entity_id must be at most 64 characters.")
    for name, value in (("capacity", capacity), ("liquidity", liquidity)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(  # noqa: TRY004
                f"Invalid entity: {name} must be a number."
            )
        if not math.isfinite(value):
            raise ValueError(f"Invalid entity: {name} must be finite.")
        if value < 0:
            raise ValueError(f"Invalid entity: {name} must be non-negative.")
    if actor is not None and (not isinstance(actor, str) or not actor):
        raise ValueError("Invalid entity: actor must be a non-empty string.")

    capacity = float(capacity)
    liquidity = float(liquidity)
    conn = connect_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM entities WHERE entity_id = ?", (entity_id,))
        if cursor.fetchone() is not None:
            raise ValueError(f"Entity already exists: {entity_id!r} is registered.")

        timestamp = _utcnow()
        cursor.execute(
            "INSERT INTO entities"
            " (entity_id, capacity, available_liquidity, status, last_updated)"
            " VALUES (?, ?, ?, ?, ?)",
            (entity_id, capacity, liquidity, "ACTIVE", timestamp),
        )

        payload = {
            "action": "REGISTER_ENTITY",
            "entity_id": entity_id,
            "initial_capacity": capacity,
            "initial_liquidity": liquidity,
            "actor": actor,
        }
        payload_json = json.dumps(payload, sort_keys=True)
        transaction_id = _append_ledger_row(
            cursor,
            timestamp,
            entity_id,
            "REGISTER_ENTITY",
            payload_json,
            "COMMITTED",
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return {
        "entity_id": entity_id,
        "capacity": capacity,
        "available_liquidity": liquidity,
        "status": "ACTIVE",
        "transaction_id": transaction_id,
    }


def _set_entity_lock(entity_id: str, locked: bool, actor: str | None = None) -> dict:
    """Core for lock_entity/unlock_entity: flip the status flag and log it.

    The flip is a ledger event (action LOCK_ENTITY / UNLOCK_ENTITY,
    COMMITTED), so locks are auditable and replayable like every other
    state change. Runs under BEGIN IMMEDIATE so two concurrent lock
    attempts serialize instead of double-logging.

    Raises ValueError for an unknown entity or when the node is already
    in the requested state (no-op flips would spam the ledger).
    """
    if not isinstance(entity_id, str) or not entity_id:
        raise ValueError("Invalid entity: entity_id must be a non-empty string.")
    if actor is not None and (not isinstance(actor, str) or not actor):
        raise ValueError("Invalid entity: actor must be a non-empty string.")

    action = "LOCK_ENTITY" if locked else "UNLOCK_ENTITY"
    want_status = "LOCKED" if locked else "ACTIVE"
    conn = connect_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT capacity, available_liquidity, status FROM entities"
            " WHERE entity_id = ?",
            (entity_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"Unknown entity: {entity_id!r} is not registered.")
        if row[2] == want_status:
            raise ValueError(f"Entity {entity_id!r} is already {want_status.lower()}.")
        timestamp = _utcnow()
        cursor.execute(
            "UPDATE entities SET status = ?, last_updated = ? WHERE entity_id = ?",
            (want_status, timestamp, entity_id),
        )
        # The pre-image lets replay_ledger() materialize entities that
        # were created outside the ledger (seed, transcript-knowledge).
        payload_json = json.dumps(
            {
                "action": action,
                "entity_id": entity_id,
                "actor": actor,
                "status": want_status,
                "previous_capacity": row[0],
                "previous_cash": row[1],
            },
            sort_keys=True,
        )
        transaction_id = _append_ledger_row(
            cursor, timestamp, entity_id, action, payload_json, "COMMITTED"
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return {
        "entity_id": entity_id,
        "status": want_status,
        "transaction_id": transaction_id,
    }


def lock_entity(entity_id: str, actor: str | None = None) -> dict:
    """Lock a node: while locked, every intent against it is REJECTED by
    the constraint engine's LOCKED branch ("Node is locked due to active
    macro shock wave."). Unlock with unlock_entity().

    This is what makes the README's "node locks are respected" claim
    true: previously the LOCKED branch in check_constraints() was
    unreachable because no code path could ever set the flag.
    """
    return _set_entity_lock(entity_id, True, actor)


def unlock_entity(entity_id: str, actor: str | None = None) -> dict:
    """Unlock a node locked by lock_entity(). Intents are accepted again."""
    return _set_entity_lock(entity_id, False, actor)


def get_ledger(
    entity_id: str | None = None,
    limit: int = 50,
    cursor: int | None = None,
) -> list[dict]:
    """Read ledger rows newest-first.

    ``cursor`` is an exclusive upper bound on transaction_id: only rows
    older than the cursor are returned. It is the pagination primitive
    behind ``GET /api/v1/ledger``.
    """
    query = "SELECT * FROM state_ledger"
    params: list = []
    clauses = []
    if entity_id:
        clauses.append("entity_id = ?")
        params.append(entity_id)
    if cursor is not None:
        clauses.append("transaction_id < ?")
        params.append(cursor)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY transaction_id DESC LIMIT ?"
    params.append(limit)
    with closing(connect_db()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()
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


def replay_ledger(apply: bool = False) -> dict:
    """Rebuild materialized state from the ledger and compare it (or repair).

    This is the engine-side deterministic replay the README promises:
    starting from the genesis seed, every ledger row is re-applied in
    transaction-ID order and the rebuilt entity map is compared against
    the live ``entities`` table — "any participant can replay history
    and arrive at the same state", as a function you can call.

    - ``apply=False`` (default): verify only. The database is untouched.
    - ``apply=True``: after a clean chain verify, replace the
      ``entities`` table with the rebuilt state inside one transaction
      (repair mode for a corrupted materialized state).

    The hash chain is verified first via verify_chain(); a broken chain
    aborts before any comparison or repair.

    Simulation rules mirror the writers exactly:
    - REGISTER_ENTITY creates the entity (status ACTIVE).
    - LOCK_ENTITY / UNLOCK_ENTITY flip the status flag.
    - COMMITTED intent rows set capacity/liquidity to the recorded
      target_* values; REJECTED rows change nothing.
    - The seed node has no ledger row (init_db inserts it directly), so
      it is bootstrapped from the SEED_* constants.
    - Entities created outside the ledger (transcript-knowledge) are
      materialized from each row's recorded pre-image
      (previous_capacity / previous_cash).

    Returns {"chain_ok", "bad_transaction_id", "rows_replayed",
    "entities_rebuilt", "divergences", "applied", "skipped_actions"}.
    ``divergences`` is [] when replay arrives at the same state.
    """
    chain_ok, bad_tx = verify_chain()
    report: dict = {
        "chain_ok": chain_ok,
        "bad_transaction_id": bad_tx,
        "rows_replayed": 0,
        "entities_rebuilt": 0,
        "divergences": [],
        "applied": False,
        "skipped_actions": [],
    }
    if not chain_ok:
        return report

    with closing(connect_db()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT transaction_id, entity_id, action, payload, status"
            " FROM state_ledger ORDER BY transaction_id ASC"
        ).fetchall()
        live = {
            r["entity_id"]: dict(r)
            for r in conn.execute(
                "SELECT entity_id, capacity, available_liquidity, status FROM entities"
            ).fetchall()
        }

    sim: dict[str, dict] = {
        SEED_ENTITY_ID: {
            "capacity": SEED_CAPACITY,
            "available_liquidity": SEED_LIQUIDITY,
            "status": "ACTIVE",
        }
    }

    def _materialize(entity_id: str, payload: dict) -> None:
        """Bootstrap a ledger-external entity from the row's pre-image."""
        if entity_id not in sim:
            sim[entity_id] = {
                "capacity": payload.get("previous_capacity") or 0.0,
                "available_liquidity": payload.get("previous_cash") or 0.0,
                "status": "ACTIVE",
            }

    skipped: set[str] = set()
    for row in rows:
        payload = json.loads(row["payload"])
        action = row["action"]
        entity_id = row["entity_id"]
        if action == "REGISTER_ENTITY":
            sim[entity_id] = {
                "capacity": payload["initial_capacity"],
                "available_liquidity": payload["initial_liquidity"],
                "status": "ACTIVE",
            }
        elif action in ("LOCK_ENTITY", "UNLOCK_ENTITY"):
            _materialize(entity_id, payload)
            sim[entity_id]["status"] = payload.get(
                "status", "LOCKED" if action == "LOCK_ENTITY" else "ACTIVE"
            )
        elif row["status"] == "COMMITTED":
            _materialize(entity_id, payload)
            if payload.get("target_capacity") is not None:
                sim[entity_id]["capacity"] = payload["target_capacity"]
            if payload.get("target_cash") is not None:
                sim[entity_id]["available_liquidity"] = payload["target_cash"]
        elif row["status"] == "REJECTED":
            pass  # rejected rows never mutate materialized state
        else:  # defensive: an unknown ledger status value
            skipped.add(f"{action}:{row['status']}")

    divergences = []
    for entity_id in sorted(set(sim) | set(live)):
        s, live_row = sim.get(entity_id), live.get(entity_id)
        if s is None:
            divergences.append(
                {
                    "entity_id": entity_id,
                    "field": "entity",
                    "live": "present",
                    "replayed": "absent",
                }
            )
        elif live_row is None:
            divergences.append(
                {
                    "entity_id": entity_id,
                    "field": "entity",
                    "live": "absent",
                    "replayed": "present",
                }
            )
        else:
            for field in ("capacity", "available_liquidity", "status"):
                if s[field] != live_row[field]:
                    divergences.append(
                        {
                            "entity_id": entity_id,
                            "field": field,
                            "live": live_row[field],
                            "replayed": s[field],
                        }
                    )

    report.update(
        rows_replayed=len(rows),
        entities_rebuilt=len(sim),
        divergences=divergences,
        skipped_actions=sorted(skipped),
    )

    if apply:
        with closing(connect_db()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                conn.execute("DELETE FROM entities")
                conn.executemany(
                    "INSERT INTO entities"
                    " (entity_id, capacity, available_liquidity, status,"
                    " last_updated) VALUES (?, ?, ?, ?, ?)",
                    [
                        (
                            entity_id,
                            state["capacity"],
                            state["available_liquidity"],
                            state["status"],
                            _utcnow(),
                        )
                        for entity_id, state in sim.items()
                    ],
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        report["applied"] = True
        report["divergences"] = []  # just wrote sim to the table
    return report


def rogue_agent_attack(entity_id: str | None = None) -> list[dict]:
    """Adversarial self-test of the constraint engine.

    A rogue agent proposes illegal state changes (an impossible drain, an
    impossible withdrawal, and a spoofed entity). Every one must come back
    REJECTED by hard code, and every attempt is appended to the ledger for
    the audit trail. The engine never raises for policy violations.

    ``entity_id`` selects the node the drain and withdrawal attacks are
    pointed at; it defaults to the seeded node. The spoof attack always
    targets a node that does not exist.
    """
    target = entity_id if entity_id is not None else SEED_ENTITY_ID
    attacks = [
        IntentTransaction(
            target,
            "ROGUE_DRAIN",
            requested_delta_capacity=-999999.0,
            requested_delta_cash=0.0,
        ),
        IntentTransaction(
            target,
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
