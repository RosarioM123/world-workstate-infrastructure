"""Producer: fold a chat transcript into a World's document.

Parses the transcript with the deterministic ``world_engine`` parser and
merges the extracted items (decisions, assumptions, questions, constraints,
notes) into ``state["transcript"]``. The import is idempotent on the
transcript text: re-importing the same text returns the original version
without appending a duplicate row.
"""

from __future__ import annotations

import hashlib
from typing import Any

from ..core import World

__all__ = ["import_transcript"]

_KIND_KEYS = {
    "DECISION": "decisions",
    "ASSUMPTION": "assumptions",
    "QUESTION": "questions",
    "CONSTRAINT": "constraints",
    "NOTE": "notes",
}


def import_transcript(work: World, text: str, *, actor: str | None = None) -> int:
    """Parse *text* and merge its items into the world's document."""
    from world_engine.ingestion.transcript import parse_transcript

    items = parse_transcript(text)
    if not items:
        return work.version
    key = "transcript:" + hashlib.sha256(text.encode("utf-8")).hexdigest()

    state: dict[str, Any] = work.state()
    bucket = state.get("transcript")
    if not isinstance(bucket, dict):
        bucket = {}
    for item in items:
        kind_key = _KIND_KEYS.get(item.get("kind", ""), "notes")
        bucket.setdefault(kind_key, []).append(
            {"speaker": item.get("speaker", ""), "text": item.get("text", "")}
        )
    state["transcript"] = bucket
    return work.update(
        state,
        actor=actor,
        note=f"transcript import: {len(items)} items",
        idempotency_key=key,
    )
