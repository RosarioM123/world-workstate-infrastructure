"""Benchmarks for the current ``src/world`` primitive.

Exercises the real ``World`` API (update with invariant judgment,
optimistic-concurrency updates, state reads, time travel, chain
verification, history scans) against a database in a temp dir; nothing
touches ``$WORLD_DIR`` or ``world_state.db``.

    python tools/bench_world.py [--rows N]   # default N = 5000 updates

Timings are machine-dependent; the results table in
``docs/benchmarks/world-primitive.md`` records where and when the
published numbers were measured.
"""

import argparse
import logging
import os
import platform
import random
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from world.core import World  # noqa: E402

logger = logging.getLogger(__name__)


def _must_be_non_negative(_old: dict, new: dict) -> None:
    # A representative invariant: cheap to judge, exercises the judgment path.
    if new.get("n", 0) < 0:
        from world.core import InvariantViolation

        raise InvariantViolation("n must be non-negative")


def bench_updates(world: World, n: int) -> float:
    """Seconds for n sequential ``update`` calls (invariant judged)."""
    start = time.perf_counter()
    for i in range(n):
        world.update({"n": i}, actor="bench")
    return time.perf_counter() - start


def bench_updates_expected_version(world: World, n: int) -> float:
    """Seconds for n updates with ``expected_version`` (re-validated path)."""
    start = time.perf_counter()
    for i in range(n):
        v = world.version
        world.update({"n": i}, actor="bench", expected_version=v)
    return time.perf_counter() - start


def bench_update_many(world: World, n: int, batch: int = 500) -> float:
    """Seconds for n updates via ``update_many`` in batches of ``batch``."""
    start = time.perf_counter()
    for base in range(0, n, batch):
        world.update_many(
            [{"n": i} for i in range(base, min(base + batch, n))],
            actor="bench",
        )
    return time.perf_counter() - start


def bench_state_latest(world: World, n: int) -> float:
    """Seconds for n ``state()`` reads of the latest version."""
    start = time.perf_counter()
    for _ in range(n):
        world.state()
    return time.perf_counter() - start


def bench_state_historical(world: World, n: int, max_version: int) -> float:
    """Seconds for n ``state(version=k)`` time-travel reads."""
    versions = [random.randint(1, max_version) for _ in range(n)]
    start = time.perf_counter()
    for v in versions:
        world.state(version=v)
    return time.perf_counter() - start


def bench_verify(world: World) -> float:
    """Seconds for ``verify()`` over the full hash chain."""
    start = time.perf_counter()
    ok = world.verify()
    elapsed = time.perf_counter() - start
    assert ok, "chain did not verify"
    return elapsed


def bench_history(world: World, limit: int) -> float:
    """Seconds for ``history(limit=...)`` scan."""
    start = time.perf_counter()
    rows = world.history(limit=limit)
    elapsed = time.perf_counter() - start
    assert len(rows) == limit
    return elapsed


def bench_rmw_old(world: World, n: int) -> float:
    """Read-modify-write the old way: state() + version + update.

    Three connection lifecycles per loop: the version read exists only
    because state() does not return its version.
    """
    start = time.perf_counter()
    for i in range(n):
        doc = world.state()
        ver = world.version
        doc["n"] = i
        world.update(doc, actor="bench", expected_version=ver)
    return time.perf_counter() - start


def bench_rmw_new(world: World, n: int) -> float:
    """Read-modify-write with read(): one atomic (state, version) read."""
    start = time.perf_counter()
    for i in range(n):
        doc, ver = world.read()
        doc["n"] = i
        world.update(doc, actor="bench", expected_version=ver)
    return time.perf_counter() - start


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description="Benchmark the src/world primitive.")
    parser.add_argument("--rows", type=int, default=5000)
    args = parser.parse_args()
    n = args.rows

    d = tempfile.mkdtemp(prefix="world-bench-")
    world = World("bench", dir=d, invariants=[_must_be_non_negative])
    assert world.version == 0

    logger.info("machine: %s / %s / python %s", platform.system(), platform.machine(), platform.python_version())
    logger.info("appending %d versions ...", n)
    append_s = bench_updates(world, n)
    logger.info("appending %d versions with expected_version ...", n)
    append_ev_s = bench_updates_expected_version(world, n)
    total_versions = world.version
    logger.info("total versions: %d", total_versions)

    logger.info("reading latest state %d times ...", n)
    read_s = bench_state_latest(world, n)
    logger.info("reading %d random historical versions ...", n)
    hist_read_s = bench_state_historical(world, n, total_versions)
    logger.info("verifying chain ...")
    verify_s = bench_verify(world)
    logger.info("scanning history(limit=%d) ...", total_versions)
    history_s = bench_history(world, total_versions)

    logger.info("read-modify-write old style (state+version+update) ...")
    rmw_old_s = bench_rmw_old(world, n)
    logger.info("read-modify-write with read() ...")
    rmw_new_s = bench_rmw_new(world, n)

    logger.info("update_many (batches of 500, separate world) ...")
    batch_world = World("bench-batch", dir=d, invariants=[_must_be_non_negative])
    batch_s = bench_update_many(batch_world, n)
    assert batch_world.version == n
    assert batch_world.verify()

    rows = [
        ("update (invariant judged)", n, append_s),
        ("update (expected_version)", n, append_ev_s),
        ("update_many (batch 500)", n, batch_s),
        ("state() latest", n, read_s),
        ("state(version=k) historical", n, hist_read_s),
        ("verify() full chain", total_versions, verify_s),
        ("history(limit=all)", total_versions, history_s),
        ("rmw old (state+version+update)", n, rmw_old_s),
        ("rmw new (read+update)", n, rmw_new_s),
    ]
    logger.info("")
    logger.info("| operation | ops | total | per-op | throughput |")
    logger.info("| --- | ---: | ---: | ---: | ---: |")
    for name, ops, total in rows:
        logger.info(
            "| %s | %d | %.2fs | %.3f ms | %.0f ops/s |",
            name,
            ops,
            total,
            total / ops * 1000,
            ops / total,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
