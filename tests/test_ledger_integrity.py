"""Ledger integrity tests for the WORLD deterministic state ledger.

These tests isolate state via the WORLD_DB_PATH env var (see engine._db_path)
so the real world_state.db is never touched.

Covers:
  (a) a clean, appended ledger verifies: verify_chain() -> (True, None);
  (b) tamper-evidence: altering one committed record's payload in a *copy*
      of the DB makes verify_chain() on the copy return (False, tampered_id),
      pinpointing the tampered record;
  (c) appending more records after a successful verification still verifies.
"""

import json
import os
import shutil
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import engine  # noqa: E402


@pytest.fixture()
def ledger_db(tmp_path, monkeypatch):
    """Fresh, populated ledger in a temp DB; engine is pointed at it."""
    db = str(tmp_path / "world_test.db")
    monkeypatch.setenv("WORLD_DB_PATH", db)
    engine.init_db()
    # A couple of committed transitions plus a rejected one (rejections are
    # also on the ledger, so the chain must cover them too).
    engine.execute_deterministic_transition(
        engine.IntentTransaction(
            entity_id=engine.SEED_ENTITY_ID,
            action="ALLOCATE_RESOURCES",
            requested_delta_capacity=-100.0,
            requested_delta_cash=1000.0,
        )
    )
    engine.execute_deterministic_transition(
        engine.IntentTransaction(
            entity_id=engine.SEED_ENTITY_ID,
            action="DRAIN_RESOURCES",
            requested_delta_capacity=-99999.0,
            requested_delta_cash=0.0,
        )
    )
    return db


def _checkpoint(db_path: str) -> None:
    """Force WAL contents into the main DB file so a file copy is complete."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        conn.commit()
    finally:
        conn.close()


def test_clean_ledger_verifies(ledger_db):
    assert engine.verify_chain() == (True, None)


def test_tampered_record_detected_and_named(tmp_path, monkeypatch, ledger_db):
    _checkpoint(ledger_db)

    tampered = str(tmp_path / "world_tampered.db")
    shutil.copyfile(ledger_db, tampered)

    conn = sqlite3.connect(tampered)
    try:
        row = conn.execute(
            "SELECT transaction_id, payload FROM state_ledger"
            " ORDER BY transaction_id LIMIT 1 OFFSET 1"
        ).fetchone()
        tampered_id, payload = row
        doc = json.loads(payload)
        doc["tampered"] = True
        conn.execute(
            "UPDATE state_ledger SET payload = ? WHERE transaction_id = ?",
            (json.dumps(doc, sort_keys=True), tampered_id),
        )
        conn.commit()
    finally:
        conn.close()

    monkeypatch.setenv("WORLD_DB_PATH", tampered)
    ok, bad_id = engine.verify_chain()
    assert ok is False
    assert bad_id == tampered_id

    # The original ledger is untouched and still verifies.
    monkeypatch.setenv("WORLD_DB_PATH", ledger_db)
    assert engine.verify_chain() == (True, None)


def test_append_after_verification_still_verifies(ledger_db):
    ok, bad_id = engine.verify_chain()
    assert (ok, bad_id) == (True, None)

    engine.execute_deterministic_transition(
        engine.IntentTransaction(
            entity_id=engine.SEED_ENTITY_ID,
            action="TOP_UP",
            requested_delta_capacity=50.0,
            requested_delta_cash=500.0,
        )
    )
    assert engine.verify_chain() == (True, None)


def test_empty_ledger_verifies(tmp_path, monkeypatch):
    db = str(tmp_path / "world_empty.db")
    monkeypatch.setenv("WORLD_DB_PATH", db)
    engine.init_db()
    assert engine.verify_chain() == (True, None)
