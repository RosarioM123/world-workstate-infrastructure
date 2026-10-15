"""Crash-consistency driver: SIGKILL a writer mid-transaction, then verify.

Each round spawns experiments/crash-consistency/worker.py, kills it with
SIGKILL after a random delay, then asserts the database is intact:

- the world opens cleanly (WAL recovery),
- verify() is True (no torn writes, chain intact),
- every row's state parses as JSON,
- version() equals the max COMMITTED seq.

The worker's start/done markers reveal whether the kill landed inside a
transaction (a "start i" with no matching "done i"), which measures how
hard the test actually stresses the commit window.

    python experiments/crash-consistency/crash_test.py [--rounds K]
"""

from __future__ import annotations

import argparse
import json
import os
import random
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from world.core import World  # noqa: E402

WORKER = os.path.join(os.path.dirname(__file__), "worker.py")


def run_round(seed: int, payload_kb: int = 256, delay: tuple = (0.15, 0.5)) -> dict:
    rng = random.Random(seed)
    d = tempfile.mkdtemp(prefix="crash-")
    proc = subprocess.Popen(
        [sys.executable, WORKER, d, "victim", "100000", str(payload_kb)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    assert proc.stdout is not None
    time.sleep(rng.uniform(*delay))
    proc.kill()  # SIGKILL: no cleanup, no flush, no mercy
    out, _ = proc.communicate()
    assert proc.returncode == -signal.SIGKILL, proc.returncode

    started, done = set(), set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[0] in ("start", "done"):
            (started if parts[0] == "start" else done).add(int(parts[1]))
    mid_transaction = len(started - done) > 0

    # The actual assertions: open, verify, parse every row, version sane.
    w = World("victim", dir=d)
    assert w.verify(), "hash chain broken after SIGKILL"
    cx = sqlite3.connect(w.path)
    try:
        rows = cx.execute("SELECT seq, state, status FROM versions").fetchall()
    finally:
        cx.close()
    for seq, state_text, _status in rows:
        json.loads(state_text)  # torn write would not parse / mismatch hash
    committed = [r[0] for r in rows if r[2] == "COMMITTED"]
    assert w.version == (max(committed) if committed else 0)
    return {
        "seed": seed, "rows": len(rows), "version": w.version,
        "mid_transaction_kill": mid_transaction,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=15)
    ap.add_argument("--seed", type=int, default=20261015)
    args = ap.parse_args()
    results = []
    for r in range(args.rounds):
        res = run_round(args.seed + r)
        results.append(res)
        print(f"round {r}: rows={res['rows']} version={res['version']} "
              f"mid_transaction_kill={res['mid_transaction_kill']}", flush=True)
    mid = sum(r["mid_transaction_kill"] for r in results)
    print(f"\n{args.rounds} SIGKILL rounds: 0 failures; "
          f"{mid}/{args.rounds} kills landed mid-transaction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
