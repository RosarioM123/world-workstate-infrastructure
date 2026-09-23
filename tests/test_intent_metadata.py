"""Tests for the multi-agent intent schema seam.

Covers the cheap-now/expensive-later fields added to every intent:
``actor`` (who submitted), ``kind`` (INTERNAL_STATE vs EXTERNAL_EFFECT),
and ``idempotency_key`` (commit-time dedup of retries). The fields are
recorded into the ledger payload, hence covered by the hash chain, but
do not change the constraint verdict.

Covers both the server engine and the SDK client ledger, which must stay
in parity.
"""

import json

import pytest

from world_engine.core import engine
from world_engine.core.engine import (
    INTENT_KIND_EXTERNAL,
    INTENT_KIND_INTERNAL,
    SEED_ENTITY_ID,
    IntentTransaction,
)
from world_sdk import LocalLedger, WorldClient


def _intent(**overrides):
    base = {
        "entity_id": SEED_ENTITY_ID,
        "action": "ALLOCATE",
        "requested_delta_capacity": -50.0,
        "requested_delta_cash": 0.0,
    }
    base.update(overrides)
    return IntentTransaction(**base)


def _payload_of_latest_row():
    rows = engine.get_ledger(limit=1)
    assert rows, "expected at least one ledger row"
    return json.loads(rows[0]["payload"])


# ---------------------------------------------------------------------------
# Server engine: schema defaults and validation
# ---------------------------------------------------------------------------


def test_actor_kind_key_default_to_unset_internal(isolated_db):
    engine.execute_deterministic_transition(_intent())
    payload = _payload_of_latest_row()
    assert payload["intent"]["actor"] is None
    assert payload["intent"]["kind"] == INTENT_KIND_INTERNAL
    assert payload["intent"]["idempotency_key"] is None


def test_actor_and_external_kind_recorded_in_payload(isolated_db):
    engine.execute_deterministic_transition(
        _intent(actor="mind-planner-7", kind=INTENT_KIND_EXTERNAL)
    )
    payload = _payload_of_latest_row()
    assert payload["intent"]["actor"] == "mind-planner-7"
    assert payload["intent"]["kind"] == INTENT_KIND_EXTERNAL


def test_kind_does_not_change_the_verdict(isolated_db):
    # An overspend is REJECTED whether it is internal or external.
    for kind in (INTENT_KIND_INTERNAL, INTENT_KIND_EXTERNAL):
        result = engine.execute_deterministic_transition(
            _intent(kind=kind, requested_delta_cash=-99999999.0)
        )
        assert result["status"] == "REJECTED"


def test_invalid_kind_is_malformed(isolated_db):
    with pytest.raises(ValueError, match="kind"):
        engine.execute_deterministic_transition(_intent(kind="SIDE_EFFECT"))


def test_non_string_kind_is_malformed(isolated_db):
    with pytest.raises(ValueError, match="kind"):
        engine.execute_deterministic_transition(_intent(kind=None))


def test_invalid_actor_is_malformed(isolated_db):
    with pytest.raises(ValueError, match="actor"):
        engine.execute_deterministic_transition(_intent(actor=""))
    with pytest.raises(ValueError, match="actor"):
        engine.execute_deterministic_transition(_intent(actor=42))


def test_invalid_idempotency_key_type_is_malformed(isolated_db):
    with pytest.raises(ValueError, match="idempotency_key"):
        engine.execute_deterministic_transition(_intent(idempotency_key=123))


def test_new_fields_are_hash_covered(isolated_db):
    # actor/kind/key live inside the payload JSON, which the record hash
    # covers, so tampering with them breaks verify_chain.
    engine.execute_deterministic_transition(_intent(actor="agent-a"))
    ok, bad = engine.verify_chain()
    assert (ok, bad) == (True, None)


# ---------------------------------------------------------------------------
# Server engine: idempotency
# ---------------------------------------------------------------------------


def test_same_key_returns_original_verdict_without_new_row(isolated_db):
    first = engine.execute_deterministic_transition(_intent(idempotency_key="req-1"))
    second = engine.execute_deterministic_transition(
        _intent(
            idempotency_key="req-1",
            requested_delta_capacity=-999.0,  # different payload, same key
            note="retry after timeout",
        )
    )
    assert first["status"] == "COMMITTED"
    assert second["status"] == first["status"]
    assert second["details"] == first["details"]
    rows = engine.get_ledger(limit=10)
    assert len(rows) == 1, "retry must not append a duplicate row"


def test_idempotent_retry_does_not_double_apply(isolated_db):
    before = engine.get_entity(SEED_ENTITY_ID)["capacity"]
    engine.execute_deterministic_transition(
        _intent(idempotency_key="req-2", requested_delta_capacity=-50.0)
    )
    engine.execute_deterministic_transition(
        _intent(idempotency_key="req-2", requested_delta_capacity=-50.0)
    )
    after = engine.get_entity(SEED_ENTITY_ID)["capacity"]
    assert after == before - 50.0


def test_rejected_intent_dedups_too(isolated_db):
    first = engine.execute_deterministic_transition(
        _intent(idempotency_key="req-3", requested_delta_cash=-99999999.0)
    )
    second = engine.execute_deterministic_transition(
        _intent(idempotency_key="req-3", requested_delta_cash=-99999999.0)
    )
    assert first["status"] == "REJECTED"
    assert second["status"] == "REJECTED"
    assert second["details"] == first["details"]
    assert len(engine.get_ledger(limit=10)) == 1


def test_distinct_keys_are_distinct_intents(isolated_db):
    engine.execute_deterministic_transition(_intent(idempotency_key="req-a"))
    engine.execute_deterministic_transition(_intent(idempotency_key="req-b"))
    assert len(engine.get_ledger(limit=10)) == 2


def test_no_key_means_no_dedup(isolated_db):
    engine.execute_deterministic_transition(_intent())
    engine.execute_deterministic_transition(_intent())
    assert len(engine.get_ledger(limit=10)) == 2


# ---------------------------------------------------------------------------
# SDK parity
# ---------------------------------------------------------------------------


@pytest.fixture()
def sdk_ledger(tmp_path):
    return LocalLedger(tmp_path / "client.db")


def test_sdk_records_actor_kind_key(sdk_ledger):
    result = sdk_ledger.intent(
        SEED_ENTITY_ID,
        "ALLOCATE",
        deltas=(-50.0, 0.0),
        actor="mind-planner-7",
        kind=INTENT_KIND_EXTERNAL,
        idempotency_key="sdk-req-1",
    )
    assert result["status"] == "COMMITTED"
    intent = result["details"]["intent"]
    assert intent["actor"] == "mind-planner-7"
    assert intent["kind"] == INTENT_KIND_EXTERNAL
    assert intent["idempotency_key"] == "sdk-req-1"


def test_sdk_idempotent_retry_returns_original(sdk_ledger):
    first = sdk_ledger.intent(
        SEED_ENTITY_ID, "ALLOCATE", deltas=(-50.0, 0.0), idempotency_key="sdk-req-2"
    )
    second = sdk_ledger.intent(
        SEED_ENTITY_ID, "ALLOCATE", deltas=(-999.0, 0.0), idempotency_key="sdk-req-2"
    )
    assert second["status"] == first["status"]
    assert second["details"] == first["details"]
    assert second["transaction_id"] == first["transaction_id"]
    assert len(sdk_ledger.get_ledger(limit=10)) == 1


def test_sdk_rejects_bad_kind(sdk_ledger):
    with pytest.raises(ValueError, match="kind"):
        sdk_ledger.intent(SEED_ENTITY_ID, "ALLOCATE", kind="WHATEVER")


def test_world_client_threads_metadata(tmp_path):
    client = WorldClient(
        ledger_path=tmp_path / "client.db", index_path=tmp_path / "index.db"
    )
    result = client.intent(
        SEED_ENTITY_ID,
        "ALLOCATE",
        deltas=(-10.0, 0.0),
        actor="agent-x",
        kind=INTENT_KIND_EXTERNAL,
        idempotency_key="wc-1",
    )
    assert result["status"] == "COMMITTED"
    assert result["details"]["intent"]["actor"] == "agent-x"
    assert result["details"]["intent"]["kind"] == INTENT_KIND_EXTERNAL
    # A retry through the client also dedups (timestamp sidecar upserts).
    again = client.intent(
        SEED_ENTITY_ID, "ALLOCATE", deltas=(-10.0, 0.0), idempotency_key="wc-1"
    )
    assert again["status"] == "COMMITTED"
    assert len(client.ledger.get_ledger(limit=10)) == 1


# ---------------------------------------------------------------------------
# Fixes: empty keys, import rebuild, malformed payloads
# ---------------------------------------------------------------------------


def test_empty_idempotency_key_is_malformed(isolated_db):
    with pytest.raises(ValueError, match="idempotency_key"):
        engine.execute_deterministic_transition(_intent(idempotency_key=""))


def test_sdk_empty_idempotency_key_is_malformed(sdk_ledger):
    with pytest.raises(ValueError, match="idempotency_key"):
        sdk_ledger.intent(SEED_ENTITY_ID, "ALLOCATE", idempotency_key="")


def test_import_rebuilds_idempotency_mappings(tmp_path):
    source = LocalLedger(tmp_path / "source.db")
    first = source.intent(
        SEED_ENTITY_ID, "ALLOCATE", deltas=(-50.0, 0.0), idempotency_key="imp-1"
    )
    rows = source.get_ledger(limit=10)

    dest = LocalLedger(tmp_path / "dest.db")
    assert dest.import_ledger_rows(rows) == 1

    # Same key on the imported ledger dedups to the original verdict;
    # no new row is appended.
    retry = dest.intent(
        SEED_ENTITY_ID, "ALLOCATE", deltas=(-999.0, 0.0), idempotency_key="imp-1"
    )
    assert retry["status"] == first["status"]
    assert retry["transaction_id"] == first["transaction_id"]
    assert len(dest.get_ledger(limit=10)) == 1


def test_import_skips_rows_without_keys(tmp_path):
    source = LocalLedger(tmp_path / "source.db")
    source.intent(SEED_ENTITY_ID, "ALLOCATE", deltas=(-50.0, 0.0))
    rows = source.get_ledger(limit=10)

    dest = LocalLedger(tmp_path / "dest.db")
    assert dest.import_ledger_rows(rows) == 1

    # No mapping was created, so an unkeyed intent appends a new row.
    dest.intent(SEED_ENTITY_ID, "ALLOCATE", deltas=(-10.0, 0.0))
    assert len(dest.get_ledger(limit=10)) == 2


def test_rebuild_tolerates_malformed_payload(sdk_ledger):
    import sqlite3

    conn = sqlite3.connect(sdk_ledger.db_path)
    try:
        conn.execute(
            "INSERT INTO state_ledger "
            "(timestamp, entity_id, action, payload, previous_hash, "
            " record_hash, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                "2026-01-01T00:00:00",
                SEED_ENTITY_ID,
                "ALLOCATE",
                "not-json{{{",
                None,
                "tampered",
                "COMMITTED",
            ),
        )
        conn.commit()
    finally:
        conn.close()
    # Must not raise; the bad row is simply skipped.
    sdk_ledger._rebuild_idempotency_keys()
