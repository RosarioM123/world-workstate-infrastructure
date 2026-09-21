"""State-continuity tests for the WORLD handoff thesis.

The ledger-mechanics tests (concurrency, tamper detection, constraint
rejection) prove the engine is correct. These tests prove the thesis:
session state committed by one agent can be reloaded by a fresh session
and continue from exactly where the first left off.

Covers:
  (a) a structured state snapshot (objective, decisions, next_action,
      open_questions) survives a full session teardown: the DB file is
      checkpointed, copied, and reopened under a fresh WORLD_DB_PATH,
      and the reconstructed fields match exactly;
  (b) the hash chain still verifies on the reopened copy;
  (c) corrupted or partial transcripts fail gracefully: empty input
      imports nothing, truncated input never crashes and commits only
      valid items, pure gibberish never classifies as a decision, and a
      missing file fails loudly instead of producing wrong state.

Run:  pytest
Isolation: every test points the engine at a throwaway SQLite file via
WORLD_DB_PATH, so the real world_state.db is never touched.
"""

import json
import shutil
import sqlite3
from contextlib import closing
from datetime import UTC, datetime

import pytest

from world_engine.core import engine
from world_engine.core.engine import (
    IntentTransaction,
    execute_deterministic_transition,
)
from world_engine.ingestion import transcript as ti

STATE_ENTITY_ID = "handoff-session"


def _checkpoint(db_path: str) -> None:
    """Force WAL contents into the main DB file so a file copy is whole."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        conn.commit()
    finally:
        conn.close()


def _ensure_state_entity() -> None:
    """Register the dedicated handoff-state entity. Zero capacity and
    zero liquidity: state snapshots are pure record, never value."""
    with closing(engine.connect_db()) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO entities
                (entity_id, capacity, available_liquidity, status, last_updated)
            VALUES (?, 0.0, 0.0, 'ACTIVE', ?)
            """,
            (STATE_ENTITY_ID, datetime.now(UTC).isoformat()),
        )
        conn.commit()


def _commit_state_snapshot(state: dict) -> None:
    """Commit one state snapshot as a zero-delta intent, the way an agent
    would hand its session state to the ledger."""
    _ensure_state_entity()
    outcome = execute_deterministic_transition(
        IntentTransaction(
            entity_id=STATE_ENTITY_ID,
            action="STATE_SNAPSHOT",
            requested_delta_capacity=0.0,
            requested_delta_cash=0.0,
            note=json.dumps(state, sort_keys=True),
        )
    )
    assert outcome["status"] == "COMMITTED"


def test_state_snapshot_roundtrip_across_fresh_session(
    isolated_db, tmp_path, monkeypatch
):
    state = {
        "objective": "Ship the WORLD handoff experiment this week.",
        "decisions": [
            "Use the existing ledger as the state store.",
            "Log every attempt, including failures.",
        ],
        "next_action": "Run handoff_001.py five times on real tasks.",
        "open_questions": [
            "Which two models should serve as Model A and Model B?",
        ],
    }
    _commit_state_snapshot(state)

    # Tear down the session: checkpoint the WAL, copy the DB file, and
    # reopen it under a fresh path the way a second agent process would.
    _checkpoint(isolated_db)
    session_b_db = str(tmp_path / "session_b.db")
    shutil.copy(isolated_db, session_b_db)
    monkeypatch.setenv("WORLD_DB_PATH", session_b_db)

    rows = engine.get_ledger(STATE_ENTITY_ID, limit=5)
    assert len(rows) == 1
    payload = json.loads(rows[0]["payload"])
    restored = json.loads(payload["intent"]["note"])

    assert restored["objective"] == state["objective"]
    assert restored["decisions"] == state["decisions"]
    assert restored["next_action"] == state["next_action"]
    assert restored["open_questions"] == state["open_questions"]
    assert restored == state

    # The copy is still a verifiable ledger, not just a bag of rows.
    ok, bad_id = engine.verify_chain()
    assert ok is True
    assert bad_id is None


def test_empty_transcript_imports_nothing_gracefully(isolated_db):
    result = ti.import_transcript("")
    assert result["items_found"] == 0
    assert result["committed"] == 0
    assert result["rejected"] == 0
    assert result["statuses"] == []
    # Nothing written, nothing half-written.
    assert engine.get_ledger() == []


def test_truncated_transcript_commits_only_valid_items(isolated_db):
    partial = (
        "Rosario: Decision: we will ship the handoff experiment this week.\n\n"
        "Muse: I agree, and the next step is to run it five times on real tas"
    )
    result = ti.import_transcript(partial, source="test")
    assert result["items_found"] >= 1
    assert result["committed"] == result["items_found"]
    assert result["rejected"] == 0

    rows = engine.get_ledger(ti.ENTITY_ID, limit=10)
    assert len(rows) == result["committed"]
    for row in rows:
        intent = json.loads(row["payload"])["intent"]
        assert intent["requested_delta_capacity"] == 0.0
        assert intent["requested_delta_cash"] == 0.0
        assert isinstance(intent["note"], str) and intent["note"]


def test_gibberish_never_classifies_as_decision(isolated_db):
    gibberish = (
        "xkq wvz blorp zzt nnn qqq rrr sss ttt uuu\n\n"
        "plip plop zzz yyy xxx www vvv 123 456 789\n\n"
        "**@@@**: zzzk qqqw eerr ttyy uuui ooop asdf\n"
    )
    result = ti.import_transcript(gibberish, source="test")
    assert result["items_found"] > 0

    rows = engine.get_ledger(ti.ENTITY_ID, limit=10)
    assert len(rows) == result["committed"]
    for row in rows:
        note = json.loads(row["payload"])["intent"]["note"]
        # Unclassifiable text falls back to NOTE; it is never promoted
        # to a decision, assumption, question, or constraint.
        assert note.startswith("NOTE |"), note


def test_missing_transcript_file_fails_loudly():
    with pytest.raises(FileNotFoundError):
        ti.main(["/does/not/exist.md"])
