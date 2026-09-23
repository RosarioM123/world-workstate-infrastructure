"""
WORLD transcript importer (world_engine.ingestion.transcript).

Turns a raw chat transcript into WORLD state. Paste or pipe a transcript
in, and the importer extracts the durable items (decisions, assumptions,
open questions, constraints, notes) and submits each one as an intent to
the deterministic ledger.

The extraction is a pure deterministic function: no network, no LLM, no
API keys, stdlib only. The same transcript always yields the same items
in the same order.

Pipeline:
    PARSE (split turns, classify) -> INTENT (one per item, zero deltas)
        -> engine.execute_deterministic_transition

Each item becomes an intent against the dedicated ``transcript-knowledge``
entity with zero capacity/cash deltas, so the constraint verdict is
trivially COMMITTED while the item text rides in the intent's ``note``
field and is hash-chained into the ledger like every other record.

Idempotency: each imported item's content hash is recorded in the
``transcript_imports`` table (UNIQUE on the hash). Re-importing the same
transcript imports zero new items. The whole import runs inside a single
transaction, so a crash mid-import rolls back to zero items and two
concurrent importers serialize instead of duplicating rows.

Usage:
    python import_transcript.py notes.md
    python import_transcript.py --dry-run notes.md   # preview, writes nothing
    cat notes.md | python import_transcript.py        # read from stdin
    python import_transcript.py --source chatgpt notes.md
"""

import argparse
import hashlib
import json
import logging
import re
import sqlite3
import sys
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

from world_engine.core.engine import (
    IntentTransaction,
    connect_db,
    execute_deterministic_transition,
    init_db,
)

__all__ = [
    "ENTITY_ID",
    "import_transcript",
    "main",
    "parse_transcript",
]

# Dedicated knowledge entity. Kept separate from the seeded hub node so
# imported notes can never move real capacity or liquidity.
ENTITY_ID = "transcript-knowledge"
SOURCE_DEFAULT = "paste"
MAX_NOTE_CHARS = 2000
MIN_BLOCK_CHARS = 12

KIND_ACTION = {
    "DECISION": "NOTE_DECISION",
    "ASSUMPTION": "NOTE_ASSUMPTION",
    "QUESTION": "NOTE_QUESTION",
    "CONSTRAINT": "NOTE_CONSTRAINT",
    "NOTE": "NOTE",
}

# Explicit "Label: ..." prefixes win over keyword matching. The author's
# own label is stronger evidence than any keyword guess.
_LABEL_RE = re.compile(
    r"^(decision|assumption|open question|question|constraint|note)\s*:\s*(.+)$",
    re.IGNORECASE | re.DOTALL,
)
_LABEL_KIND = {
    "decision": "DECISION",
    "assumption": "ASSUMPTION",
    "open question": "QUESTION",
    "question": "QUESTION",
    "constraint": "CONSTRAINT",
    "note": "NOTE",
}

# Keyword rules, checked in this fixed priority order. Deterministic: the
# first matching kind wins, so the same line always classifies the same way.
_KEYWORD_RULES = [
    (
        "DECISION",
        [
            "decision",
            "decided",
            "we will",
            "will do",
            "agreed",
            "going with",
            "chose",
            "chosen",
            "selected",
            "finalized",
            "settled on",
        ],
    ),
    (
        "CONSTRAINT",
        [
            "must",
            "never",
            "always",
            "constraint",
            "required",
            "do not",
            "don't",
            "cannot",
            "can't",
            "guardrail",
            "not allowed",
            "forbidden",
        ],
    ),
    (
        "ASSUMPTION",
        ["assum", "presum", "given that", "taking it as", "suppos", "hypothesis"],
    ),
    (
        "QUESTION",
        [
            "?",
            "open question",
            "todo",
            "tbd",
            "follow up",
            "follow-up",
            "need to find",
            "need to check",
            "need to confirm",
            "need to decide",
            "unclear",
            "unknown",
            "unresolved",
        ],
    ),
]

# "Name: ..." or "**Name:** ..." at the start of a turn.
_SPEAKER_RE = re.compile(
    r"^(?:\*\*)?([A-Za-z][\w .'\-]{0,40})(?:\*\*)?\s*:\s*(.+)$",
    re.DOTALL,
)
_TURN_SPLIT_RE = re.compile(r"^(?:\*\*)?[A-Za-z][\w .'\-]{0,40}(?:\*\*)?\s*:")


def _utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _split_blocks(text: str) -> list[str]:
    """Split a transcript into blocks. A blank line always ends a block;
    a new ``Speaker:`` turn also ends one, since chat exports rarely use
    blank lines between turns."""
    blocks: list[str] = []
    current: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                blocks.append(" ".join(current))
                current = []
            continue
        if current and _TURN_SPLIT_RE.match(line):
            blocks.append(" ".join(current))
            current = []
        current.append(line)
    if current:
        blocks.append(" ".join(current))
    return blocks


def _extract_speaker(block: str) -> tuple[str, str]:
    """Return (speaker, remainder). A label word is not a speaker."""
    m = _SPEAKER_RE.match(block)
    if m:
        name = m.group(1).strip()
        if name.lower() in _LABEL_KIND:
            return "unknown", block
        return name, m.group(2).strip()
    return "unknown", block


def _classify(text: str) -> tuple[str, str]:
    """Return (kind, content) for one block of text."""
    m = _LABEL_RE.match(text)
    if m:
        return _LABEL_KIND[m.group(1).lower()], m.group(2).strip()
    lowered = text.lower()
    for kind, keywords in _KEYWORD_RULES:
        if any(k in lowered for k in keywords):
            return kind, text
    return "NOTE", text


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_transcript(text: str) -> list[dict[str, str]]:
    """Extract durable items from a transcript.

    Returns a list of {"kind", "speaker", "text"} dicts in transcript
    order. Pure function: no I/O, no clock, no randomness.
    """
    items = []
    for block in _split_blocks(text):
        if len(block) < MIN_BLOCK_CHARS:
            continue
        speaker, rest = _extract_speaker(block)
        kind, content = _classify(rest)
        content = _clean(content)
        if len(content) < MIN_BLOCK_CHARS:
            continue
        items.append({"kind": kind, "speaker": speaker, "text": content})
    return items


def _item_hash(item: dict[str, str]) -> str:
    """Content hash for idempotency. Case-insensitive so trivial
    re-capitalization does not double-import an item."""
    basis = "\n".join([item["kind"], item["speaker"].lower(), item["text"].lower()])
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def _format_note(item: dict[str, str]) -> str:
    text = item["text"]
    if len(text) > MAX_NOTE_CHARS:
        text = text[:MAX_NOTE_CHARS] + " [truncated]"
    return f"{item['kind']} | speaker={item['speaker']} | {text}"


def init_transcript_store() -> None:
    """Idempotency store. Raw transcripts are never mutated; the hash of
    each imported item is recorded once."""
    with closing(connect_db()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transcript_imports (
                item_hash TEXT PRIMARY KEY,
                imported_at TEXT NOT NULL,
                source TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                action TEXT NOT NULL,
                kind TEXT NOT NULL,
                speaker TEXT NOT NULL,
                note TEXT NOT NULL
            )
        """)
        conn.commit()


def ensure_knowledge_entity() -> None:
    """Register the dedicated knowledge entity if absent. Zero capacity
    and zero liquidity: imported notes are pure record, never value."""
    with closing(connect_db()) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO entities
                (entity_id, capacity, available_liquidity, status, last_updated)
            VALUES (?, 0.0, 0.0, 'ACTIVE', ?)
        """,
            (ENTITY_ID, _utcnow()),
        )
        conn.commit()


def _already_imported(item_hash: str, conn: sqlite3.Connection | None = None) -> bool:
    """Check the idempotency store. Pass the import's shared connection
    inside import_transcript so the check sees the current transaction."""
    if conn is None:
        with closing(connect_db()) as owned:
            return _already_imported(item_hash, owned)
    row = conn.execute(
        "SELECT 1 FROM transcript_imports WHERE item_hash = ?",
        (item_hash,),
    ).fetchone()
    return row is not None


def _record_import(
    item_hash: str,
    source: str,
    item: dict[str, str],
    note: str,
    conn: sqlite3.Connection | None = None,
) -> None:
    """Record an imported item's hash. With the shared connection the row
    joins the import's transaction (no commit here); standalone callers
    get their own connection and commit."""
    if conn is None:
        with closing(connect_db()) as owned:
            _record_import(item_hash, source, item, note, owned)
            owned.commit()
        return
    conn.execute(
        """
        INSERT INTO transcript_imports
            (item_hash, imported_at, source, entity_id, action,
             kind, speaker, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            item_hash,
            _utcnow(),
            source,
            ENTITY_ID,
            KIND_ACTION[item["kind"]],
            item["kind"],
            item["speaker"],
            note,
        ),
    )


def import_transcript(
    text: str, source: str = SOURCE_DEFAULT, dry_run: bool = False
) -> dict:
    """Parse a transcript and commit one intent per item.

    With dry_run=True this is a pure function: it parses and reports
    without touching the database at all.

    The import is atomic and concurrency-safe: every new item's ledger
    row and idempotency record are written inside a single BEGIN
    IMMEDIATE transaction on one shared connection. A crash or error
    anywhere rolls back to zero imported items (no partial imports, no
    ledger rows without their dedup record), and two concurrent
    importers serialize on the write lock — the loser sees the winner's
    item hashes and imports nothing new.
    """
    items = parse_transcript(text)
    result: dict[str, Any] = {
        "source": source,
        "items_found": len(items),
        "committed": 0,
        "rejected": 0,
        "skipped_duplicate": 0,
        "dry_run": dry_run,
        "statuses": [],
    }
    if dry_run:
        return result
    init_db()
    init_transcript_store()
    ensure_knowledge_entity()

    conn = connect_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        for item in items:
            digest = _item_hash(item)
            if _already_imported(digest, conn):
                result["skipped_duplicate"] += 1
                continue
            note = _format_note(item)
            intent = IntentTransaction(
                entity_id=ENTITY_ID,
                action=KIND_ACTION[item["kind"]],
                requested_delta_capacity=0.0,
                requested_delta_cash=0.0,
                note=note,
            )
            # Shares this connection: the transition joins the import's
            # transaction instead of committing on its own.
            outcome = execute_deterministic_transition(intent, conn=conn)
            _record_import(digest, source, item, note, conn=conn)
            result["statuses"].append(outcome["status"])
            if outcome["status"] == "COMMITTED":
                result["committed"] += 1
            else:
                result["rejected"] += 1
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return result


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(message)s")
    parser = argparse.ArgumentParser(
        description="Import a chat transcript into the WORLD state ledger."
    )
    parser.add_argument(
        "path", nargs="?", help="Transcript file (.md/.txt). Reads stdin if omitted."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and list items without writing anything.",
    )
    parser.add_argument(
        "--source",
        default=SOURCE_DEFAULT,
        help="Label recorded with the import (default: paste).",
    )
    args = parser.parse_args(argv)

    if args.path:
        text = Path(args.path).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    if args.dry_run:
        items = parse_transcript(text)
        for i, item in enumerate(items, 1):
            preview = item["text"][:120]
            logger.info(
                "%d. [%s] (speaker=%s) %s", i, item["kind"], item["speaker"], preview
            )
        logger.info("items=%d (dry run, nothing written)", len(items))
        return 0

    logger.info(
        "%s",
        json.dumps(
            import_transcript(text, source=args.source), indent=2, sort_keys=True
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
