"""Producer: fold a chat transcript into a World's document.

Parses the transcript with the deterministic ``world_engine`` parser and
merges the extracted items (decisions, assumptions, questions, constraints,
notes) into ``state["transcript"]``. The import is idempotent on the
transcript text: re-importing the same text returns the original version
without appending a duplicate row.

Concurrency: the import is a read-modify-write, so it runs the optimistic
concurrency loop: ``read()`` for ``(state, version)``, then ``update()``
with ``expected_version=version``. A concurrent writer makes the update
raise :class:`ConflictError` before anything is appended; the import
re-reads and retries instead of silently overwriting the other writer's
merged items. Retries are bounded; exhaustion raises ``ConflictError``.
"""

from __future__ import annotations

import copy
import hashlib
from typing import Any

from ..core import ConflictError, World

__all__ = ["import_transcript"]

_KIND_KEYS = {
    "DECISION": "decisions",
    "ASSUMPTION": "assumptions",
    "QUESTION": "questions",
    "CONSTRAINT": "constraints",
    "NOTE": "notes",
}

# Upper bound on optimistic-concurrency retries. Each attempt re-reads the
# current document, so a retry under sustained contention converges as
# soon as one attempt lands between other writers' commits.
_MAX_ATTEMPTS = 10


def _merge_items(state: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    """Return a copy of *state* with the parsed *items* appended."""
    merged = copy.deepcopy(state)
    bucket = merged.get("transcript")
    if not isinstance(bucket, dict):
        bucket = {}
        merged["transcript"] = bucket
    for item in items:
        kind_key = _KIND_KEYS.get(item.get("kind", ""), "notes")
        bucket.setdefault(kind_key, []).append(
            {"speaker": item.get("speaker", ""), "text": item.get("text", "")}
        )
    return merged


def import_transcript(work: World, text: str, *, actor: str | None = None) -> int:
    """Parse *text* and merge its items into the world's document."""
    from world_engine.ingestion.transcript import parse_transcript

    items = parse_transcript(text)
    if not items:
        return work.version
    key = "transcript:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
    note = f"transcript import: {len(items)} items"
    for _attempt in range(_MAX_ATTEMPTS):
        state, version = work.read()
        try:
            return work.update(
                _merge_items(state, items),
                actor=actor,
                note=note,
                idempotency_key=key,
                expected_version=version,
            )
        except ConflictError:
            continue
    raise ConflictError(
        f"transcript import aborted after {_MAX_ATTEMPTS} conflicting attempts"
    )
