"""Concurrency test for the check-then-act claim.

engine.execute_deterministic_transition() documents that the
read-check-write sequence runs inside a single BEGIN IMMEDIATE
transaction, so concurrent writers cannot both pass the constraint
checks against the same stale state. This test proves it: N threads
race to drain the same node with intents that only one of them can
afford. Exactly one must commit, the rest must be rejected for the
physical limit, the ledger must stay valid, and the materialized state
must match the single winner.
"""

import threading

from world_engine.core import engine


def test_concurrent_conflicting_writes_serialize(tmp_path, monkeypatch):
    db = str(tmp_path / "world_race.db")
    monkeypatch.setenv("WORLD_DB_PATH", db)
    engine.init_db()

    n = 16
    # Seed capacity is 1000.0; each racer tries to drain 600.0, so at most
    # one can ever pass the physical-limit check.
    barrier = threading.Barrier(n)
    results: list = [None] * n

    def worker(i: int) -> None:
        barrier.wait()  # release all threads at once for a real race
        results[i] = engine.execute_deterministic_transition(
            engine.IntentTransaction(
                entity_id=engine.SEED_ENTITY_ID,
                action=f"RACE_DRAIN_{i}",
                requested_delta_capacity=-600.0,
                requested_delta_cash=0.0,
            )
        )

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    committed = [r for r in results if r["status"] == "COMMITTED"]
    rejected = [r for r in results if r["status"] == "REJECTED"]

    assert len(committed) == 1, f"expected exactly one winner, got {len(committed)}"
    assert len(rejected) == n - 1
    assert all(
        "Capacity cannot drop below zero" in r["details"]["reason"] for r in rejected
    )

    # Materialized state matches the single winner: 1000 - 600 = 400.
    entity = engine.get_entity(engine.SEED_ENTITY_ID)
    assert entity is not None
    assert entity["capacity"] == 400.0

    # All N attempts are on the ledger and the chain still verifies.
    assert len(engine.get_ledger(limit=n + 1)) == n
    assert engine.verify_chain() == (True, None)
