"""WORLD API v1: versioned routes.

The router is mounted twice in main.py: under /api/v1 (canonical) and
under /api (deprecated aliases kept for the dashboard and existing
clients). Route handlers live here exactly once.
"""

import logging
import sqlite3

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from world_engine.core.engine import (
    INTENT_KIND_INTERNAL,
    IntentTransaction,
    connect_db,
    execute_deterministic_transition,
    rogue_agent_attack,
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


@router.post("/intent")
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


@router.post("/rogue-attack")
def trigger_rogue_attack() -> dict[str, list[dict]]:
    """Unleash the rogue agent. Every illegal intent must come back REJECTED."""
    return {"attacks": rogue_agent_attack()}
