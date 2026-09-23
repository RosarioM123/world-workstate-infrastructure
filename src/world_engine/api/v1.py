"""WORLD API v1: versioned routes.

The router is mounted twice in main.py: under /api/v1 (canonical) and
under /api (deprecated aliases kept for the dashboard and existing
clients). Route handlers live here exactly once.
"""

import logging
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from world_engine.api.auth import require_api_key
from world_engine.core.engine import (
    INTENT_KIND_INTERNAL,
    IntentTransaction,
    connect_db,
    execute_deterministic_transition,
    get_ledger,
    lock_entity,
    register_entity,
    replay_ledger,
    rogue_agent_attack,
    unlock_entity,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class IntentRequest(BaseModel):
    entity_id: str = Field(max_length=64)
    action: str = Field(max_length=128)
    delta_capacity: float
    delta_cash: float
    note: str = Field(default="", max_length=4000)
    # Multi-agent schema seam: recorded into the ledger payload, unenforced.
    # See docs/adr/0005-multi-agent-conflict-policy.md and
    # docs/adr/0006-auth-rbac-shape.md.
    actor: str | None = Field(default=None, max_length=128)
    kind: str = Field(default=INTENT_KIND_INTERNAL, max_length=32)
    idempotency_key: str | None = Field(default=None, max_length=128)


@router.get("/state")
def get_world_state() -> dict[str, list[dict]]:
    """Current materialized state + recent tamper-evident ledger entries."""
    conn = connect_db()
    try:
        conn.row_factory = sqlite3.Row
        entities = [dict(r) for r in conn.execute("SELECT * FROM entities")]
        ledger = [
            dict(r)
            for r in conn.execute(
                "SELECT transaction_id, timestamp, entity_id, action, status,"
                " record_hash FROM state_ledger"
                " ORDER BY transaction_id DESC LIMIT 10"
            )
        ]
    finally:
        conn.close()
    return {"entities": entities, "recent_ledger": ledger}


@router.post("/intent", dependencies=[Depends(require_api_key)])
def post_intent(req: IntentRequest) -> dict:
    """Any agent (or human) submits an intent; the math engine decides."""
    try:
        intent = IntentTransaction(
            entity_id=req.entity_id,
            action=req.action,
            requested_delta_capacity=req.delta_capacity,
            requested_delta_cash=req.delta_cash,
            note=req.note,
            actor=req.actor,
            kind=req.kind,
            idempotency_key=req.idempotency_key,
        )
        return execute_deterministic_transition(intent)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_intent", "message": str(exc)},
        )


@router.post("/rogue-attack", dependencies=[Depends(require_api_key)])
def trigger_rogue_attack(entity_id: str | None = None) -> dict[str, list[dict]]:
    """Unleash the rogue agent. Every illegal intent must come back REJECTED.

    ``entity_id`` optionally points the drain and withdrawal attacks at a
    registered node instead of the seeded one.
    """
    return {"attacks": rogue_agent_attack(entity_id)}


class EntityRequest(BaseModel):
    entity_id: str = Field(max_length=64)
    capacity: float = Field(ge=0)
    liquidity: float = Field(ge=0)
    # Multi-agent schema seam: recorded into the ledger payload, unenforced.
    actor: str | None = Field(default=None, max_length=128)


@router.post("/entities", status_code=201, dependencies=[Depends(require_api_key)])
def create_entity(req: EntityRequest) -> dict:
    """Register a new node in the world. Duplicate ids come back 409."""
    try:
        return register_entity(
            entity_id=req.entity_id,
            capacity=req.capacity,
            liquidity=req.liquidity,
            actor=req.actor,
        )
    except ValueError as exc:
        message = str(exc)
        if message.startswith("Entity already exists"):
            raise HTTPException(
                status_code=409,
                detail={"code": "entity_exists", "message": message},
            )
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_entity", "message": message},
        )


@router.get("/ledger")
def read_ledger(
    entity_id: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    cursor: int | None = Query(default=None, ge=1),
) -> dict:
    """Page through the tamper-evident ledger, newest first.

    ``cursor`` is an exclusive upper bound on transaction_id: pass back
    ``next_cursor`` to keep walking toward older rows.
    """
    rows = get_ledger(entity_id=entity_id, limit=limit, cursor=cursor)
    next_cursor = rows[-1]["transaction_id"] if len(rows) == limit else None
    return {"ledger": rows, "next_cursor": next_cursor}


@router.get("/replay")
def verify_replay() -> dict:
    """Engine-side deterministic replay, verified live.

    Rebuilds materialized state from the ledger from the genesis seed
    and reports whether replay arrives at the same state as the live
    tables (``divergences`` is [] when it does). Read-only: the database
    is untouched. Repair mode (``replay_ledger(apply=True)``) stays an
    operator-level engine call, not an HTTP endpoint.
    """
    return replay_ledger()


def _lock_error(exc: ValueError) -> HTTPException:
    message = str(exc)
    if message.startswith("Unknown entity"):
        return HTTPException(
            status_code=404,
            detail={"code": "entity_not_found", "message": message},
        )
    return HTTPException(
        status_code=409,
        detail={"code": "lock_conflict", "message": message},
    )


@router.post("/entities/{entity_id}/lock", dependencies=[Depends(require_api_key)])
def lock_node(entity_id: str) -> dict:
    """Lock a node: intents against it are REJECTED until unlocked.

    The flip is a COMMITTED LOCK_ENTITY ledger row, so it is auditable
    and replayable. Unknown ids come back 404, double-locks 409.
    """
    try:
        return lock_entity(entity_id)
    except ValueError as exc:
        raise _lock_error(exc)


@router.post("/entities/{entity_id}/unlock", dependencies=[Depends(require_api_key)])
def unlock_node(entity_id: str) -> dict:
    """Unlock a node locked by POST /entities/{id}/lock."""
    try:
        return unlock_entity(entity_id)
    except ValueError as exc:
        raise _lock_error(exc)
