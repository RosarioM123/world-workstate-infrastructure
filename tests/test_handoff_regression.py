"""Regression lock for experiment 001's state-extraction path.

tests/test_state_continuity.py already proves a committed state snapshot
survives a session teardown and reload (see
test_state_snapshot_roundtrip_across_fresh_session); this file does not
repeat that. What it locks in is the exact path experiments/handoff_001.py
uses on real transcripts:

    transcript text -> parse_transcript -> import_transcript (commits)
    -> chain verifies -> fresh session reload
    -> reconstructed bundle has the same kinds, speakers, and texts

If a future change alters the parser's classification, the note format,
or the commit path, this test fails instead of silently handing Model B
a different state than Model A produced.
"""

import json
import shutil

from tests.conftest import checkpoint
from world_engine.core import engine
from world_engine.ingestion import transcript as ti

TRANSCRIPT = """\
Muse: Decision: we will frame WORLD as deterministic state infrastructure, not as another memory layer.

Muse: Assumption: reviewers compare us against Mem0 and Zep first, so the comparison table leads with determinism.

Muse: Open question: how do we frame compliance-readiness without overclaiming what the ledger proves?

User: Constraint: never present a 2/5 trial result as anything other than 2/5.

Muse: Note: the stranger test decides scoring; slightly-off continuations are failures.
"""


def _reconstruct_bundle(rows: list[dict]) -> dict:
    """Rebuild the handoff bundle from ledger rows alone, the way a fresh
    session would. Notes are stored as "KIND | speaker=NAME | text"."""
    bundle: dict[str, list[str]] = {
        "decisions": [],
        "assumptions": [],
        "open_questions": [],
        "constraints": [],
        "notes": [],
    }
    field_for = {
        "DECISION": "decisions",
        "ASSUMPTION": "assumptions",
        "QUESTION": "open_questions",
        "CONSTRAINT": "constraints",
        "NOTE": "notes",
    }
    for row in rows:
        payload = json.loads(row["payload"])
        note = payload["intent"]["note"]
        kind, rest = note.split(" | ", 1)
        speaker_part, text = rest.split(" | ", 1)
        speaker = speaker_part.split("=", 1)[1]
        bundle[field_for[kind]].append({"speaker": speaker, "text": text})
    return bundle


def test_transcript_to_ledger_to_bundle_is_stable(isolated_db, tmp_path, monkeypatch):
    items = ti.parse_transcript(TRANSCRIPT)
    assert [i["kind"] for i in items] == [
        "DECISION",
        "ASSUMPTION",
        "QUESTION",
        "CONSTRAINT",
        "NOTE",
    ]

    report = ti.import_transcript(TRANSCRIPT, source="handoff-regression")
    assert report["items_found"] == 5
    assert report["committed"] == 5
    assert report["rejected"] == 0

    verified, bad_id = engine.verify_chain()
    assert verified and bad_id is None

    # Session teardown: checkpoint, copy, reopen under a fresh path.
    checkpoint(isolated_db)
    session_b_db = str(tmp_path / "session_b.db")
    shutil.copy(isolated_db, session_b_db)
    monkeypatch.setenv("WORLD_DB_PATH", session_b_db)

    rows = engine.get_ledger(ti.ENTITY_ID, limit=50)
    assert len(rows) == 5
    bundle = _reconstruct_bundle(rows)

    expected = {
        "decisions": [items[0]],
        "assumptions": [items[1]],
        "open_questions": [items[2]],
        "constraints": [items[3]],
        "notes": [items[4]],
    }
    for field, originals in expected.items():
        assert len(bundle[field]) == len(originals) == 1
        assert bundle[field][0]["speaker"] == originals[0]["speaker"]
        assert bundle[field][0]["text"] == originals[0]["text"]

    verified, _ = engine.verify_chain()
    assert verified


def test_reimport_is_idempotent_for_handoff(isolated_db):
    """Running the same Model A transcript twice must not double the
    state Model B receives."""
    first = ti.import_transcript(TRANSCRIPT, source="handoff-regression")
    second = ti.import_transcript(TRANSCRIPT, source="handoff-regression")
    assert first["committed"] == 5
    assert second["committed"] == 0
    assert second["skipped_duplicate"] == 5
    rows = engine.get_ledger(ti.ENTITY_ID, limit=50)
    assert len(rows) == 5
