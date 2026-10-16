"""Soak test: 1M-row chain, then sustained singles measuring latency drift.

Phase 1 builds a 1,000,000-row chain with ``update_many`` (bulk ingest at
scale). Phase 2 appends 60,000 single updates in 12 chunks of 5,000,
recording per-chunk p50/p99 per-op latency to detect drift as the chain
grows. Phase 3 runs ``verify()`` over the full ~1.06M-row chain.

    python experiments/soak/soak.py [--rows N] [--singles M]

Writes experiments/soak/results.json and prints a summary. Too slow for
CI (see tests/test_soak.py for the scaled-down gate); run on demand.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import sqlite3
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from world import World  # noqa: E402

RESULTS = os.path.join(os.path.dirname(__file__), "results.json")


def percentile(sorted_xs: list[float], q: float) -> float:
    return sorted_xs[min(len(sorted_xs) - 1, int(q * len(sorted_xs)))]


def db_size_bytes(path: str) -> int:
    total = 0
    for suffix in ("", "-wal", "-shm"):
        try:
            total += os.path.getsize(path + suffix)
        except OSError:
            pass
    return total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=1_000_000)
    ap.add_argument("--singles", type=int, default=60_000)
    ap.add_argument("--chunk", type=int, default=5_000)
    ap.add_argument("--batch", type=int, default=2_000)
    args = ap.parse_args()

    d = tempfile.mkdtemp(prefix="world-soak-")
    w = World("soak", dir=d)
    out: dict = {
        "machine": f"{platform.system()} / {platform.machine()} / "
                   f"python {platform.python_version()}",
        "rows": args.rows,
        "singles": args.singles,
    }

    # Phase 1: bulk build.
    t0 = time.perf_counter()
    for base in range(0, args.rows, args.batch):
        w.update_many([{"n": i} for i in range(base, min(base + args.batch, args.rows))])
    out["phase1_bulk_s"] = time.perf_counter() - t0
    out["phase1_ops_per_s"] = args.rows / out["phase1_bulk_s"]
    assert w.version == args.rows

    # Phase 2: sustained singles, per-chunk latency.
    chunks = []
    n0 = args.rows
    t0 = time.perf_counter()
    for c in range(args.singles // args.chunk):
        lat: list[float] = []
        for i in range(args.chunk):
            t1 = time.perf_counter()
            w.update({"n": n0 + c * args.chunk + i})
            lat.append(time.perf_counter() - t1)
        lat.sort()
        chunks.append({
            "chunk": c,
            "p50_ms": percentile(lat, 0.50) * 1000,
            "p99_ms": percentile(lat, 0.99) * 1000,
        })
    out["phase2_singles_s"] = time.perf_counter() - t0
    out["phase2_ops_per_s"] = args.singles / out["phase2_singles_s"]
    out["chunks"] = chunks
    out["p99_first_chunk_ms"] = chunks[0]["p99_ms"]
    out["p99_last_chunk_ms"] = chunks[-1]["p99_ms"]
    out["p99_drift_ratio"] = chunks[-1]["p99_ms"] / chunks[0]["p99_ms"]
    assert w.version == args.rows + args.singles

    # Phase 3: full-chain verification at scale.
    t0 = time.perf_counter()
    ok = w.verify()
    out["phase3_verify_s"] = time.perf_counter() - t0
    out["phase3_rows_per_s"] = w.version / out["phase3_verify_s"]
    out["verify"] = ok
    assert ok

    # Size and memory footprint.
    cx = sqlite3.connect(w.path)
    try:
        cx.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        cx.commit()
    finally:
        cx.close()
    out["db_bytes"] = db_size_bytes(str(w.path))
    out["db_mb"] = out["db_bytes"] / 1e6
    out["max_rss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    out["final_version"] = w.version

    with open(RESULTS, "w") as fh:
        json.dump(out, fh, indent=2)

    print(f"rows={out['final_version']:,} verify={ok}")
    print(f"phase1 bulk: {out['phase1_ops_per_s']:.0f} ops/s "
          f"({out['phase1_bulk_s']:.1f}s for {args.rows:,})")
    print(f"phase2 singles: {out['phase2_ops_per_s']:.0f} ops/s "
          f"({out['phase2_singles_s']:.1f}s for {args.singles:,})")
    print(f"p99 first chunk: {out['p99_first_chunk_ms']:.2f} ms, "
          f"last chunk: {out['p99_last_chunk_ms']:.2f} ms, "
          f"drift ratio: {out['p99_drift_ratio']:.2f}x")
    print(f"phase3 verify: {out['phase3_rows_per_s']:.0f} rows/s "
          f"({out['phase3_verify_s']:.1f}s)")
    print(f"db size: {out['db_mb']:.1f} MB, max RSS: {out['max_rss_mb']:.0f} MB")
    print(f"raw: {RESULTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
