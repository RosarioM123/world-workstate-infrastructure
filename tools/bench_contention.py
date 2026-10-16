"""Contention profile: OCC latency and conflict rate vs writer threads.

Each thread runs K read-modify-write loops against one shared WORLD using
the optimistic-concurrency pattern (``read()`` then
``update(expected_version=v)`` with re-read-and-retry on ``ConflictError``).
Per-op latency covers the whole loop including retries.

    python tools/bench_contention.py [--ops-per-thread K]

Reports, per thread count: aggregate throughput, p50/p90/p99 per-op
latency, conflict rate (conflicts / attempts), and a correctness check
(final version equals total committed ops, verify() clean).
"""

from __future__ import annotations

import argparse
import os
import platform
import statistics
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from world import World  # noqa: E402
from world.core import ConflictError  # noqa: E402

LEVELS = [1, 2, 4, 8, 16]


def percentile(sorted_xs: list[float], q: float) -> float:
    if not sorted_xs:
        return 0.0
    i = min(len(sorted_xs) - 1, int(q * len(sorted_xs)))
    return sorted_xs[i]


def run_level(nthreads: int, ops_per_thread: int) -> dict:
    d = tempfile.mkdtemp(prefix="world-contention-")
    World("c", dir=d).update({"n": 0})
    latencies: list[float] = []
    conflicts = attempts = 0
    lock = threading.Lock()

    def worker() -> None:
        nonlocal conflicts, attempts
        w = World("c", dir=d)
        local_lat, local_conf, local_att = [], 0, 0
        for _ in range(ops_per_thread):
            t0 = time.perf_counter()
            while True:
                local_att += 1
                try:
                    state, ver = w.read()
                    w.update({"n": state["n"] + 1}, expected_version=ver)
                    break
                except ConflictError:
                    local_conf += 1
            local_lat.append(time.perf_counter() - t0)
        with lock:
            latencies.extend(local_lat)
            conflicts += local_conf
            attempts += local_att

    threads = [threading.Thread(target=worker) for _ in range(nthreads)]
    t0 = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    wall = time.perf_counter() - t0

    latencies.sort()
    w = World("c", dir=d)
    expected_version = 1 + nthreads * ops_per_thread
    ok = w.version == expected_version and w.verify()
    return {
        "threads": nthreads,
        "ops": len(latencies),
        "wall_s": wall,
        "throughput": len(latencies) / wall,
        "p50_ms": percentile(latencies, 0.50) * 1000,
        "p90_ms": percentile(latencies, 0.90) * 1000,
        "p99_ms": percentile(latencies, 0.99) * 1000,
        "conflicts": conflicts,
        "attempts": attempts,
        "conflict_rate": conflicts / attempts if attempts else 0.0,
        "correct": ok,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ops-per-thread", type=int, default=200)
    args = ap.parse_args()

    print(f"machine: {platform.system()} / {platform.machine()} / "
          f"python {platform.python_version()}")
    print(f"workload: OCC read-modify-write with retry, "
          f"{args.ops_per_thread} ops/thread\n")
    print("| threads | throughput | p50 | p90 | p99 | conflict rate | correct |")
    print("| ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    results = []
    for nthreads in LEVELS:
        r = run_level(nthreads, args.ops_per_thread)
        results.append(r)
        print(f"| {r['threads']} | {r['throughput']:.0f} ops/s "
              f"| {r['p50_ms']:.2f} ms | {r['p90_ms']:.2f} ms "
              f"| {r['p99_ms']:.2f} ms | {r['conflict_rate']:.3f} "
              f"| {'yes' if r['correct'] else 'NO'} |")
        assert r["correct"], f"correctness check failed at {nthreads} threads"
    means = statistics.mean(r["throughput"] for r in results)
    print(f"\nmean aggregate throughput: {means:.0f} ops/s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
