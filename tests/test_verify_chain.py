"""Tests for engine.verify_chain: full hash-chain verification.

Covers: clean ledger verifies, tampered payload / previous_hash /
record_hash are each pinpointed to the exact transaction_id, appending
after a successful verify still passes, and an empty ledger verifies
trivially.

Isolation: every test points the engine at a throwaway SQLite file via
WORLD_DB_PATH, so the real world_state.db is never touched.
"""

import sqlite3

import pytest

import engine
from engine import IntentTransaction, execute_deterministic_transition


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "test.db"))
    engine.init_db()
    yield


def _commit(n=3):
    for i in range(n):
        execute_deterministic_transition(
            IntentTransaction("node_rotterdam_hub", f"ACTION_{i}",
                              -10.0 * (i + 1), 100.0 * i)
        )


def _tamper(tx_id: int, column: str, value):
    conn = sqlite3.connect(engine._db_path())
    try:
        conn.execute(
            f"UPDATE state_ledger SET {column} = ? WHERE transaction_id = ?",
            (value, tx_id),
        )
        conn.commit()
    finally:
        conn.close()


def test_empty_ledger_verifies():
    assert engine.verify_chain() == (True, None)


def test_clean_ledger_verifies():
    _commit(5)
    assert engine.verify_chain() == (True, None)


def test_rejected_rows_are_part_of_the_chain():
    execute_deterministic_transition(
        IntentTransaction("node_rotterdam_hub", "DRAIN", -999999.0, 0.0))
    assert engine.verify_chain() == (True, None)


def test_tampered_payload_pinpointed():
    _commit(4)
    _tamper(3, "payload", '{"forged": true}')
    ok, bad_id = engine.verify_chain()
    assert ok is False
    assert bad_id == 3


def test_tampered_record_hash_pinpointed():
    _commit(4)
    _tamper(2, "record_hash", "0" * 64)
    ok, bad_id = engine.verify_chain()
    assert ok is False
    assert bad_id == 2


def test_spliced_previous_hash_pinpointed():
    # Rewriting a row's previous_hash to point at a non-adjacent record
    # breaks the link even though the row's own hash still matches.
    _commit(4)
    conn = sqlite3.connect(engine._db_path())
    try:
        first_hash = conn.execute(
            "SELECT record_hash FROM state_ledger WHERE transaction_id = 1"
        ).fetchone()[0]
        conn.execute(
            "UPDATE state_ledger SET previous_hash = ?"
            " WHERE transaction_id = 3",
            (first_hash,),
        )
        conn.commit()
    finally:
        conn.close()
    ok, bad_id = engine.verify_chain()
    assert ok is False
    assert bad_id == 3


def test_first_bad_row_wins():
    _commit(4)
    _tamper(4, "payload", '{"forged": true}')
    _tamper(2, "payload", '{"forged": true}')
    ok, bad_id = engine.verify_chain()
    assert (ok, bad_id) == (False, 2)


def test_append_after_verify_still_passes():
    _commit(2)
    assert engine.verify_chain() == (True, None)
    _commit(3)
    assert engine.verify_chain() == (True, None)


def test_genesis_link_is_none_not_empty_string():
    _commit(1)
    conn = sqlite3.connect(engine._db_path())
    try:
        prev = conn.execute(
            "SELECT previous_hash FROM state_ledger WHERE transaction_id = 1"
        ).fetchone()[0]
    finally:
        conn.close()
    assert prev is None
    assert engine.verify_chain() == (True, None)
