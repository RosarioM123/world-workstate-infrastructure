"""Concurrency test for the WORLD primitive's optimistic concurrency.

N threads race to update the same world with the same ``expected_version``.
The version check is re-validated inside the write transaction, so exactly
one writer commits and the rest raise :class:`ConflictError`: no lost
updates, no phantom rows, and the hash chain stays valid.
"""

import threading

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
