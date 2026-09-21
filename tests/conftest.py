"""Shared test setup for the WORLD kernel test suite.

- Puts the repo root on sys.path so ``world_engine`` imports without an
  installed package (CI also does ``pip install -e .``; both paths work).
- ``isolated_db``: a fresh ledger DB per test via the WORLD_DB_PATH env var,
  so the real world_state.db is never touched.
- ``checkpoint``: force WAL contents into the main DB file before copying it.
"""

import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from world_engine.core import engine


@pytest.fixture()
def isolated_db(tmp_path, monkeypatch):
    """Fresh, initialized ledger in a temp DB; engine is pointed at it."""
    db = str(tmp_path / "world_test.db")
    monkeypatch.setenv("WORLD_DB_PATH", db)
    engine.init_db()
    return db


def checkpoint(db_path: str) -> None:
    """Force WAL contents into the main DB file so a file copy is complete."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        conn.commit()
    finally:
        conn.close()
