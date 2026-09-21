"""Transcript importer tests for the WORLD deterministic state ledger.

These tests isolate state via the WORLD_DB_PATH env var (see engine._db_path)
so the real world_state.db is never touched.

Covers:
  (a) explicit "Label:" prefixes classify correctly;
  (b) keyword classification with deterministic priority;
  (c) speaker extraction, including **bold** names;
  (d) dry run parses without writing anything;
  (e) import commits one intent per item with zero deltas and the item
      text in the ledger payload note;
  (f) re-importing the same transcript imports zero new items (idempotent);
  (g) the hash chain still verifies after an import.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from world_engine.core import engine
from world_engine.ingestion import transcript as ti


@pytest.fixture()
def tdb(tmp_path, monkeypatch):
    """Fresh ledger in a temp DB; engine is pointed at it."""
    db = str(tmp_path / "world_test.db")
    monkeypatch.setenv("WORLD_DB_PATH", db)
    engine.init_db()
    return db


SAMPLE = """Rosario: Decision: we will ship the transcript importer this week.

**Muse:** Assumption: users paste transcripts more often than they upload files.

Open question: who owns the billing entity?

Constraint: never store raw credentials in the ledger.

We should probably write docs too.
"""


def test_label_prefixes_classify():
    items = ti.parse_transcript(
        "Decision: we will ship Friday.\n\n"
        "Assumption: users prefer dark mode.\n\n"
        "Open question: who owns billing?\n\n"
        "Constraint: never store raw passwords."
    )
    kinds = [i["kind"] for i in items]
    assert kinds == ["DECISION", "ASSUMPTION", "QUESTION", "CONSTRAINT"]


def test_keyword_priority_is_deterministic():
    # Matches both DECISION and CONSTRAINT keywords; DECISION wins by
    # fixed priority order, every time.
    items = ti.parse_transcript("We decided that we must never do this.")
    assert items[0]["kind"] == "DECISION"
    items = ti.parse_transcript("We decided that we must never do this.")
    assert items[0]["kind"] == "DECISION"


def test_question_mark_classifies():
    items = ti.parse_transcript("Who owns the billing entity?")
    assert items[0]["kind"] == "QUESTION"


def test_speaker_extraction():
    items = ti.parse_transcript("Rosario: We will ship Friday.")
    assert items[0]["speaker"] == "Rosario"
    assert items[0]["kind"] == "DECISION"


def test_bold_speaker_extraction():
    items = ti.parse_transcript("**Muse:** We will ship Friday.")
    assert items[0]["speaker"] == "Muse"


def test_label_word_is_not_a_speaker():
    items = ti.parse_transcript("Decision: we will ship Friday.")
    assert items[0]["speaker"] == "unknown"


def test_short_noise_blocks_are_skipped():
    assert ti.parse_transcript("ok\n\nsure") == []


def test_dry_run_writes_nothing(tdb):
    result = ti.import_transcript(SAMPLE, dry_run=True)
    assert result["items_found"] == 5
    assert result["dry_run"] is True
    assert engine.get_ledger() == []


def test_import_commits_one_intent_per_item(tdb):
    result = ti.import_transcript(SAMPLE, source="test")
    assert result["items_found"] == 5
    assert result["committed"] == 5
    assert result["rejected"] == 0

    rows = engine.get_ledger(ti.ENTITY_ID, limit=50)
    assert len(rows) == 5
    for row in rows:
        payload = json.loads(row["payload"])
        assert payload["intent"]["requested_delta_capacity"] == 0.0
        assert payload["intent"]["requested_delta_cash"] == 0.0
        assert payload["intent"]["note"]
    notes = [json.loads(r["payload"])["intent"]["note"] for r in rows]
    assert any("ship the transcript importer" in n for n in notes)
    assert any("DECISION | speaker=Rosario" in n for n in notes)

    # The knowledge entity holds no value; notes are pure record.
    entity = engine.get_entity(ti.ENTITY_ID)
    assert entity["capacity"] == 0.0
    assert entity["available_liquidity"] == 0.0


def test_reimport_is_idempotent(tdb):
    first = ti.import_transcript(SAMPLE, source="test")
    assert first["committed"] == 5
    second = ti.import_transcript(SAMPLE, source="test")
    assert second["committed"] == 0
    assert second["skipped_duplicate"] == 5
    assert len(engine.get_ledger(ti.ENTITY_ID, limit=50)) == 5


def test_chain_verifies_after_import(tdb):
    ti.import_transcript(SAMPLE, source="test")
    ok, bad_id = engine.verify_chain()
    assert ok is True
    assert bad_id is None


def test_note_validation_rejects_non_string(tdb):
    with pytest.raises(ValueError):
        engine.execute_deterministic_transition(
            engine.IntentTransaction(
                entity_id=ti.ENTITY_ID,
                action="NOTE",
                requested_delta_capacity=0.0,
                requested_delta_cash=0.0,
                note=123,  # type: ignore[arg-type]
            )
        )
