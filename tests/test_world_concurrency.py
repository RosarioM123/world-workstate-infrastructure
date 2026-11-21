"""Concurrency test for the WORLD primitive's optimistic concurrency.

N threads race to update the same world with the same ``expected_version``.
The version check is re-validated inside the write transaction, so exactly
one writer commits and the rest raise :class:`ConflictError`: no lost
updates, no phantom rows, and the hash chain stays valid.
"""

import sqlite3
import threading
import time

from world.core import ConflictError, World


def test_concurrent_same_expected_version_serializes(tmp_path):
    n = 16
    d = str(tmp_path / "race")
    seed = World("race", dir=d)
    seed.update({"n": 0}, actor="seed")
    assert seed.version == 1

    barrier = threading.Barrier(n)
    results: list = [None] * n

    def worker(i: int) -> None:
        try:
            barrier.wait()  # release all threads at once for a real race
            w = World("race", dir=d)
            try:
                seq = w.update({"n": i + 1}, actor=f"racer-{i}", expected_version=1)
            except ConflictError as e:
                results[i] = ("conflict", str(e))
            else:
                results[i] = ("committed", seq)
        except Exception as e:  # noqa: BLE001 - any worker failure must be
            # recorded; an uncaught exception here would hang the barrier
            # and the whole suite.
            results[i] = ("error", repr(e))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(r is not None for r in results), f"threads failed: {results}"
    committed = [r for r in results if r[0] == "committed"]
    conflicts = [r for r in results if r[0] == "conflict"]
    assert not [r for r in results if r[0] == "error"], f"errors: {results}"
    assert len(committed) == 1, f"expected exactly one winner, got {len(committed)}"
    assert len(conflicts) == n - 1, f"expected {n - 1} conflicts, got {len(conflicts)}"

    winner = World("race", dir=d)
    assert winner.version == 2
    # Materialized state matches the single winner.
    assert winner.state()["n"] in range(1, n + 1)
    # No phantom rows from the losers: seed + winner only, chain verifies.
    assert len(winner.history()) == 2
    assert winner.verify()


def test_update_waits_out_held_write_lock(tmp_path):
    """C-12: a writer waits for a held write lock instead of failing.

    One raw connection holds BEGIN IMMEDIATE for 6 s, longer than the
    old 5 s default busy timeout. An update racing it must wait the
    lock out and commit, not raise OperationalError ("database is
    locked"). The writer handle is built before the lock is taken so
    the constructor (which runs DDL) is not the thing that blocks.
    """
    d = str(tmp_path / "lock")
    w = World("lock", dir=d)
    w.update({"n": 0}, actor="seed")
    writer = World("lock", dir=d)

    holder = sqlite3.connect(w.path)
    holder.execute("PRAGMA journal_mode=WAL")
    holder.execute("BEGIN IMMEDIATE")
    result: dict[str, object] = {}

    def run_update() -> None:
        try:
            result["seq"] = writer.update({"n": 1}, actor="writer")
        except Exception as e:  # noqa: BLE001 - record any worker failure
            result["error"] = repr(e)

    t = threading.Thread(target=run_update)
    t.start()
    try:
        time.sleep(6)
    finally:
        holder.execute("COMMIT")
        holder.close()
    t.join(timeout=40)
    assert not t.is_alive(), "writer thread did not finish after the lock released"
    assert "error" not in result, f"update failed under contention: {result}"
    assert result["seq"] == 2
    assert World("lock", dir=d).verify()


def test_many_writers_no_lock_errors(tmp_path):
    """C-12: many concurrent writers never see a leaked lock error.

    16 threads x 10 last-writer-wins updates each. Every update must
    commit (no OperationalError escapes), the chain must hold all 160
    rows, and verify() must stay green.
    """
    n_threads = 16
    n_each = 10
    d = str(tmp_path / "many")
    seed = World("many", dir=d)
    seed.update({"n": 0}, actor="seed")

    barrier = threading.Barrier(n_threads)
    results: list = [None] * n_threads

    def worker(i: int) -> None:
        try:
            barrier.wait()
            w = World("many", dir=d)
            seqs = []
            for j in range(n_each):
                seqs.append(w.update({"n": i * n_each + j + 1}, actor=f"w-{i}"))
            results[i] = ("ok", seqs)
        except Exception as e:  # noqa: BLE001 - record any worker failure
            results[i] = ("error", repr(e))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(r is not None for r in results), f"threads failed: {results}"
    errors = [r for r in results if r[0] == "error"]
    assert not errors, f"writer errors under contention: {errors}"
    seqs = sorted(s for r in results for s in r[1])
    assert seqs == list(range(2, 2 + n_threads * n_each))
    final = World("many", dir=d)
    assert final.version == 1 + n_threads * n_each
    assert final.verify()
