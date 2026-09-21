"""Tests for the CLI entry points and the remaining engine/API branches.

These cover the user-facing surfaces that the kernel tests do not:
the ``world-import`` main() function, engine validation edge cases,
the transaction rollback path, API page fallbacks, and the unhandled
exception envelope.

(The synthetic weather/port demo moved to
``examples/synthetic-logistics-demo/`` with its own tests.)
"""

import io
import logging
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from world_engine.api import main as api_main
from world_engine.api.middleware import install as install_middleware
from world_engine.core import engine
from world_engine.ingestion import transcript as transcript_mod


@pytest.fixture()
def clients_db(tmp_path, monkeypatch):
    db = str(tmp_path / "world_cli.db")
    monkeypatch.setenv("WORLD_DB_PATH", db)
    engine.init_db()
    return db


# --- engine edge branches -------------------------------------------------


def test_empty_entity_id_rejected(clients_db):
    with pytest.raises(ValueError, match="entity_id"):
        engine.execute_deterministic_transition(
            engine.IntentTransaction("", "X", 0.0, 0.0)
        )


def test_empty_action_rejected(clients_db):
    with pytest.raises(ValueError, match="action"):
        engine.execute_deterministic_transition(
            engine.IntentTransaction(engine.SEED_ENTITY_ID, "", 0.0, 0.0)
        )


def test_mid_transaction_exception_rolls_back_cleanly(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "world_rb.db"))
    engine.init_db()
    before = len(engine.get_ledger(limit=100))

    def _boom(*args, **kwargs):
        raise RuntimeError("hash backend exploded")

    monkeypatch.setattr(engine, "_hash_record", _boom)
    with pytest.raises(RuntimeError, match="hash backend exploded"):
        engine.execute_deterministic_transition(
            engine.IntentTransaction(engine.SEED_ENTITY_ID, "X", -1.0, 0.0)
        )

    # Nothing was partially written: no new ledger row, state untouched.
    assert len(engine.get_ledger(limit=100)) == before
    assert engine.get_entity(engine.SEED_ENTITY_ID)["capacity"] == 1000.0
    assert engine.verify_chain() == (True, None)


# --- transcript importer CLI -----------------------------------------------


def _write(tmp_path, name: str, text: str) -> str:
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return str(p)


def test_transcript_main_dry_run_from_file(tmp_path, caplog):
    path = _write(
        tmp_path, "t.md", "Alice: Decision: we will ship the new gateway in Q3.\n"
    )
    with caplog.at_level(logging.INFO):
        rc = transcript_mod.main([path, "--dry-run"])
    assert rc == 0
    assert "DECISION" in caplog.text


def test_transcript_main_dry_run_from_stdin(monkeypatch, caplog):
    monkeypatch.setattr(
        sys, "stdin", io.StringIO("Bob: Question: who owns the deploy pipeline?\n")
    )
    with caplog.at_level(logging.INFO):
        rc = transcript_mod.main(["--dry-run"])
    assert rc == 0
    assert "QUESTION" in caplog.text


def test_transcript_main_imports_and_reports(clients_db, tmp_path, caplog):
    path = _write(
        tmp_path, "t.md", "Alice: Decision: we will ship the new gateway in Q3.\n"
    )
    with caplog.at_level(logging.INFO):
        rc = transcript_mod.main([path, "--source", "cli-test"])
    assert rc == 0
    assert '"committed": 1' in caplog.text
    rows = engine.get_ledger(limit=5)
    assert any("DECISION" in r["payload"] for r in rows)


def test_block_without_trailing_blank_line_is_kept():
    # Covers the trailing-block branch of _split_blocks.
    items = transcript_mod.parse_transcript(
        "Alice: Decision: we will ship the new gateway in Q3."
    )
    assert len(items) == 1
    assert items[0]["kind"] == "DECISION"


def test_short_cleaned_content_is_skipped():
    # Block is long enough to parse, but the content after cleaning is
    # below MIN_BLOCK_CHARS, so it is dropped.
    items = transcript_mod.parse_transcript("Christopher: yes")
    assert items == []


def test_long_note_is_truncated(clients_db):
    long_text = "Alice: Decision: " + "x" * 2100 + "\n"
    result = transcript_mod.import_transcript(long_text, source="trunc-test")
    assert result["committed"] == 1
    rows = engine.get_ledger(limit=1)
    assert "[truncated]" in rows[0]["payload"]


# --- API page routes, fallbacks, unhandled errors ---------------------------


def test_landing_health_demo_routes(api_client):
    assert api_client.get("/").status_code == 200
    r = api_client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
    assert api_client.get("/demo").status_code == 200


def test_page_loader_fallbacks_on_missing_files(tmp_path, monkeypatch):
    monkeypatch.setattr(api_main, "SITE_DIR", tmp_path / "nope")
    monkeypatch.setattr(api_main, "REPO_ROOT", tmp_path / "nope")
    landing = api_main._load_landing_page()
    dashboard = api_main._load_dashboard_page()
    assert "not built yet" in landing
    assert "unavailable" in dashboard


def test_unhandled_exception_returns_error_envelope():
    boom = FastAPI()
    install_middleware(boom)

    @boom.get("/boom")
    def _boom():
        raise RuntimeError("kaput")

    with TestClient(boom, raise_server_exceptions=False) as c:
        r = c.get("/boom")
    assert r.status_code == 500
    error = r.json()["error"]
    assert error["code"] == "internal_error"
    assert error["message"] == "Internal server error"
    assert error["request_id"]


@pytest.fixture()
def api_client(tmp_path, monkeypatch):
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "world_api2.db"))
    with TestClient(api_main.app) as c:
        yield c
