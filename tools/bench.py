"""Ledger benchmarks: append throughput and chain-verification latency.

Builds a ledger of N intents through the real engine path
(execute_deterministic_transition) and reports honest numbers:

    python tools/bench.py [--rows N]   # default N = 100000

The database lives in a temp dir; nothing touches world_state.db.
Timings are machine-dependent; the README table records where and when
the published numbers were measured.
"""

import argparse
import logging
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from world_engine.core import engine  # noqa: E402

logger = logging.getLogger(__name__)


def bench_appends(n: int) -> float:
    """Seconds to append n intents through the full engine path."""
    start = time.perf_counter()
    for _ in range(n):
        engine.execute_deterministic_transition(
            engine.IntentTransaction(
                entity_id=engine.SEED_ENTITY_ID,
                action="TICK",
                requested_delta_capacity=0.0,
                requested_delta_cash=1.0,
            )
        )
    return time.perf_counter() - start


def bench_verify() -> float:
    """Seconds for verify_chain() over the current ledger."""
    start = time.perf_counter()
    ok, bad = engine.verify_chain()
    elapsed = time.perf_counter() - start
    assert (ok, bad) == (True, None), f"ledger did not verify: {(ok, bad)}"
    return elapsed


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description="Benchmark the WORLD ledger.")
    parser.add_argument("--rows", type=int, default=100_000)
    args = parser.parse_args()

    db = os.path.join(tempfile.mkdtemp(prefix="world-bench-"), "bench.db")
    os.environ["WORLD_DB_PATH"] = db
    engine.init_db()

    logger.info("appending %d intents ...", args.rows)
    append_s = bench_appends(args.rows)
    logger.info("verifying chain ...")
    verify_s = bench_verify()

    per_append_ms = append_s / args.rows * 1000
    logger.info("")
    logger.info("| operation | rows | total | per-op | throughput |")
    logger.info("| --- | ---: | ---: | ---: | ---: |")
    logger.info(
        "| append (execute_deterministic_transition) | %d | %.1fs | %.2f ms/intent | %.0f intents/s |",
        args.rows,
        append_s,
        per_append_ms,
        args.rows / append_s,
    )
    logger.info(
        "| verify_chain | %d | %.2fs | %.3f ms/row | %.0f rows/s |",
        args.rows,
        verify_s,
        verify_s / args.rows * 1000,
        args.rows / verify_s,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
