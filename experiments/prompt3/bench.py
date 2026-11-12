"""Prompt 3 before/after benchmarks for the WORLD primitive.

Stdlib only. Builds fresh worlds in a temp dir and measures:

- single ``update`` throughput
- ``update_many`` throughput
- ``checkpoint`` creation time
- ``resume`` time
- ``verify()`` time and peak-RSS delta on a 20,000-version chain
- revision-relevant reads: ``state(version=N)``, ``history()``,
  ``blame(path)`` timing on the same large chain

Run unchanged before and after the Prompt 3 changes; the numbers are
only comparable because the script, sizes, and methodology are fixed.

Usage: python experiments/prompt3/bench.py
"""

from __future__ import annotations

import json
import os
import platform
import resource
import sys
import tempfile
import time

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "src",
    ),
)

from world.core import World

SINGLE_UPDATES = 1000
BATCH_SIZE = 2000
LARGE_VERSIONS = 20_000


def _rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def _doc(i: int) -> dict:
    return {
        "counter": i,
        "meta": {"owner": "agent-a", "phase": "build"},
        "items": [f"item-{j}" for j in range(10)],
        "handoff": {
            "objective": "benchmark world",
            "decisions": [{"text": f"decision {i}", "rationale": "bench"}],
        },
    }


def main() -> int:
    print(f"python: {platform.python_version()}")
    print(f"platform: {platform.platform()}")
    print(f"machine: {platform.machine()}, cpus: {os.cpu_count()}")

    tmp = tempfile.mkdtemp(prefix="world-bench-")

    # --- single update throughput -------------------------------------
    w = World("bench-single", dir=tmp)
    t0 = time.perf_counter()
    for i in range(SINGLE_UPDATES):
        w.update(_doc(i), actor="bench", note=f"update {i}")
    dt = time.perf_counter() - t0
    print(
        f"single update: {SINGLE_UPDATES} updates in {dt:.3f}s "
        f"= {SINGLE_UPDATES / dt:.1f} updates/s"
    )

    # --- update_many throughput ---------------------------------------
    w2 = World("bench-batch", dir=tmp)
    states = [_doc(i) for i in range(BATCH_SIZE)]
    t0 = time.perf_counter()
    w2.update_many(states, actor="bench", note="batch")
    dt = time.perf_counter() - t0
    print(
        f"update_many: {BATCH_SIZE} updates in {dt:.3f}s "
        f"= {BATCH_SIZE / dt:.1f} updates/s"
    )

    # --- checkpoint + resume on the single-update world ----------------
    t0 = time.perf_counter()
    w.checkpoint("bench-cp")
    dt = time.perf_counter() - t0
    print(f"checkpoint create: {dt * 1000:.2f} ms")

    t0 = time.perf_counter()
    w.resume("bench-cp", actor="bench")
    dt = time.perf_counter() - t0
    print(f"resume: {dt * 1000:.2f} ms")

    # --- large chain: verify time + memory, revision reads -------------
    w3 = World("bench-large", dir=tmp)
    chunk = [_doc(i) for i in range(500)]
    built = 0
    while built < LARGE_VERSIONS:
        # meta.owner flips once, halfway, so blame() has to walk.
        for d in chunk:
            if built + chunk.index(d) >= LARGE_VERSIONS // 2:
                d["meta"]["owner"] = "agent-b"
        w3.update_many(chunk, actor="bench", note="bulk")
        built += len(chunk)
    assert w3.version == LARGE_VERSIONS

    rss_before = _rss_mb()
    t0 = time.perf_counter()
    ok = w3.verify()
    dt = time.perf_counter() - t0
    rss_after = _rss_mb()
    print(
        f"verify: {LARGE_VERSIONS} versions, ok={ok}, {dt:.3f}s "
        f"({LARGE_VERSIONS / dt:.0f} rows/s), peak RSS {rss_before:.1f} -> "
        f"{rss_after:.1f} MB (delta {rss_after - rss_before:.1f} MB)"
    )

    t0 = time.perf_counter()
    doc = w3.state(version=LARGE_VERSIONS // 2)
    dt = time.perf_counter() - t0
    print(f"state(version=N): {dt * 1000:.2f} ms (counter={doc['counter']})")

    t0 = time.perf_counter()
    hist = w3.history()
    dt = time.perf_counter() - t0
    print(f"history(): {len(hist)} rows in {dt * 1000:.1f} ms")

    t0 = time.perf_counter()
    blame = w3.blame("meta.owner")
    dt = time.perf_counter() - t0
    print(
        f"blame('meta.owner'): {dt * 1000:.1f} ms "
        f"(seq={blame['seq'] if blame else None}, "
        f"change={blame['change'] if blame else None})"
    )

    db_size = os.path.getsize(w3.path) / (1024 * 1024)
    print(f"large-chain db size: {db_size:.1f} MB for {LARGE_VERSIONS} versions")
    print(json.dumps({"tmpdir": tmp}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
