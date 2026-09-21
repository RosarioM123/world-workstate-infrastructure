"""Property tests for the hash-chained ledger.

Two invariants, stated as properties over generated inputs:

1. No false positives: any ledger built purely through
   execute_deterministic_transition() verifies cleanly.
2. No false negatives: any single-field tamper of any record (payload,
   timestamp, action, or status) is detected, and verify_chain() names
   the exact tampered record.

A row deleted from the middle of the chain is also detected, since the
following record's previous_hash no longer links.
"""

import json
import os
import shutil
import sqlite3
import tempfile

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from tests.conftest import checkpoint
from world_engine.core import engine

ACTIONS = ["ALLOCATE", "RELEASE", "TOP_UP", "FEE", "REBATE", "ADJUST"]


def _fresh_db() -> str:
    """A brand-new initialized ledger; points the engine at it."""
    db = os.path.join(tempfile.mkdtemp(), "prop.db")
    os.environ["WORLD_DB_PATH"] = db
    engine.init_db()
    return db


def _restore_env(old: str | None) -> None:
    if old is None:
        os.environ.pop("WORLD_DB_PATH", None)
    else:
        os.environ["WORLD_DB_PATH"] = old


def _seed_ledger(n: int) -> list[int]:
    """Commit n small valid intents; return their transaction ids in order."""
    ids = []
    for i in range(n):
        result = engine.execute_deterministic_transition(
            engine.IntentTransaction(
                entity_id=engine.SEED_ENTITY_ID,
                action=ACTIONS[i % len(ACTIONS)],
                requested_delta_capacity=-10.0,
                requested_delta_cash=100.0,
            )
        )
        assert result["status"] == "COMMITTED"
        rows = engine.get_ledger(limit=1)
        ids.append(rows[0]["transaction_id"])
    return ids


@given(
    st.lists(
        st.tuples(
            st.sampled_from(ACTIONS),
            st.floats(
                min_value=-900.0,
                max_value=900.0,
                allow_nan=False,
                allow_infinity=False,
            ),
            st.floats(
                min_value=-40000.0,
                max_value=40000.0,
                allow_nan=False,
                allow_infinity=False,
            ),
        ),
        min_size=1,
        max_size=25,
    )
)
@settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_random_ledgers_always_verify(draws):
    old = os.environ.get("WORLD_DB_PATH")
    try:
        _fresh_db()
        for action, delta_capacity, delta_cash in draws:
            engine.execute_deterministic_transition(
                engine.IntentTransaction(
                    entity_id=engine.SEED_ENTITY_ID,
                    action=action,
                    requested_delta_capacity=delta_capacity,
                    requested_delta_cash=delta_cash,
                )
            )
        assert engine.verify_chain() == (True, None)
    finally:
        _restore_env(old)


@given(
    st.integers(min_value=0, max_value=7),
    st.sampled_from(["payload", "timestamp", "action", "status"]),
)
@settings(max_examples=40, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_single_field_tamper_always_detected_and_named(record_index, field):
    old = os.environ.get("WORLD_DB_PATH")
    try:
        db = _fresh_db()
        ids = _seed_ledger(8)
        target_id = ids[record_index]

        checkpoint(db)
        tampered = db + ".tampered"
        shutil.copyfile(db, tampered)

        conn = sqlite3.connect(tampered)
        try:
            if field == "payload":
                (payload,) = conn.execute(
                    "SELECT payload FROM state_ledger WHERE transaction_id = ?",
                    (target_id,),
                ).fetchone()
                doc = json.loads(payload)
                doc["_tampered"] = True
                new_value = json.dumps(doc, sort_keys=True)
            else:
                (current,) = conn.execute(
                    f"SELECT {field} FROM state_ledger WHERE transaction_id = ?",
                    (target_id,),
                ).fetchone()
                new_value = current + "X"
            conn.execute(
                f"UPDATE state_ledger SET {field} = ? WHERE transaction_id = ?",
                (new_value, target_id),
            )
            conn.commit()
        finally:
            conn.close()

        os.environ["WORLD_DB_PATH"] = tampered
        ok, bad_id = engine.verify_chain()
        assert ok is False
        assert bad_id == target_id

        # The pristine ledger is untouched and still verifies.
        os.environ["WORLD_DB_PATH"] = db
        assert engine.verify_chain() == (True, None)
    finally:
        _restore_env(old)


def test_deleted_middle_row_breaks_chain(isolated_db):
    ids = _seed_ledger(5)
    victim = ids[2]

    conn = sqlite3.connect(isolated_db)
    try:
        conn.execute("DELETE FROM state_ledger WHERE transaction_id = ?", (victim,))
        conn.commit()
    finally:
        conn.close()

    ok, bad_id = engine.verify_chain()
    assert ok is False
    # The record after the deleted one no longer links to its predecessor.
    assert bad_id == ids[3]
