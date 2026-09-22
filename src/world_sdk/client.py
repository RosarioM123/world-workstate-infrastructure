"""WorldClient: the offline-first WORLD SDK entry point.

A ``WorldClient`` owns two local files and needs no server:

- a ``LocalLedger`` (hash-chained, same entry format as the server ledger)
  where ``intent()`` validates and appends locally;
- an ``EmbeddingSidecar`` (sqlite3) holding the disposable embedding index
  and the client-side timestamp index.

Guarantee boundary, stated plainly: the ledger is the sole system of
record. The sidecar is derived and disposable. Verification
(``verify()``) walks the hash chain only: deterministic, LLM-free, no
second store in the integrity path.
"""

from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

from world_engine.core.engine import INTENT_KIND_INTERNAL
from world_sdk.index import EmbeddingSidecar, default_index_path
from world_sdk.ledger import LocalLedger, default_db_path, normalize_deltas


class WorldClient:
    """Offline-first client for the WORLD deterministic ledger."""

    def __init__(
        self,
        ledger_path: str | Path | None = None,
        index_path: str | Path | None = None,
    ) -> None:
        self.ledger = LocalLedger(ledger_path or default_db_path())
        self.index = EmbeddingSidecar(index_path or default_index_path())

    def intent(
        self,
        entity: str,
        action: str,
        deltas: Mapping[str, Any] | Sequence[Any] | None = None,
        note: str | None = None,
        actor: str | None = None,
        kind: str = INTENT_KIND_INTERNAL,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Propose an intent: validated and committed locally, no server.

        ``deltas`` may be None, a mapping with ``"capacity"``/``"cash"``
        keys, or a ``(delta_capacity, delta_cash)`` pair. Returns the
        server-shaped verdict ``{"status": ..., "details": ...}``. The
        block's timestamp is recorded in the client timestamp index
        automatically, so ``state_at_time`` works without extra bookkeeping.

        ``actor`` names the submitter, ``kind`` marks INTERNAL_STATE vs
        EXTERNAL_EFFECT, and ``idempotency_key`` deduplicates retries: a
        second submission with the same key returns the first verdict.
        """
        result = self.ledger.intent(
            entity,
            action,
            deltas=deltas,
            note="" if note is None else note,
            actor=actor,
            kind=kind,
            idempotency_key=idempotency_key,
        )
        self.index.record_timestamp(
            int(result["transaction_id"]), str(result["timestamp"])
        )
        return {"status": result["status"], "details": result["details"]}

    def state_at_block(self, height: int) -> dict[str, dict[str, Any]]:
        """Materialized state after replaying the ledger to a block height."""
        return self.ledger.replay_to(height)

    def state_at_time(self, at_time: str | datetime) -> dict[str, dict[str, Any]]:
        """Materialized state as of a timestamp, resolved client-side.

        The timestamp is resolved to the latest block at or before it via
        the client timestamp index, then the local ledger is replayed to
        that height. Raises ValueError when no block exists at or before
        the given time.
        """
        height = self.index.resolve(at_time)
        if height is None:
            raise ValueError(f"No block recorded at or before {at_time}.")
        return self.state_at_block(height)

    def verify(self) -> tuple[bool, int | None]:
        """Verify the local hash chain. Deterministic and LLM-free."""
        return self.ledger.verify_chain()

    def add_embedding(self, block_height: int, vector: Sequence[Any]) -> None:
        """Index a caller-supplied embedding vector for a block height."""
        self.index.add(block_height, vector)

    def search(
        self, query_vector: Sequence[Any], k: int = 5
    ) -> list[tuple[int, float]]:
        """Top-k block heights by cosine similarity over indexed vectors."""
        return self.index.search(query_vector, k)

    def record_timestamp(self, block_height: int, block_time: str | datetime) -> None:
        """Manually record a block timestamp (e.g. when syncing)."""
        self.index.record_timestamp(block_height, block_time)

    def import_ledger_rows(self, rows: Sequence[Mapping[str, Any]]) -> int:
        """Copy server ledger rows into the local ledger.

        Hashes are preserved verbatim and the merged chain is verified.
        Imported rows' timestamps are recorded in the client timestamp
        index so ``state_at_time`` covers synced history too. Returns the
        number of rows inserted.
        """
        inserted = self.ledger.import_ledger_rows(rows)
        # Record timestamps for the imported rows (upsert, so re-importing
        # is idempotent) so state_at_time covers synced history too.
        for row in rows:
            self.index.record_timestamp(
                int(row["transaction_id"]), str(row["timestamp"])
            )
        return inserted

    def latest_height(self) -> int:
        """Highest block height in the local ledger."""
        return self.ledger.latest_height

    @staticmethod
    def normalize_deltas(
        deltas: Mapping[str, Any] | Sequence[Any] | None,
    ) -> tuple[float, float]:
        """Public alias for the deltas normalization used by ``intent``."""
        return normalize_deltas(deltas)
