"""Victim process for crash-consistency testing.

Hammers a WORLD with updates, printing markers around each one so the
driver can tell whether SIGKILL landed mid-transaction:

    python worker.py <dir> <name> <iters> <payload_kb>

The payload widens the BEGIN IMMEDIATE..COMMIT window, so a random kill
reliably lands inside some transaction.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from world.core import World  # noqa: E402


def main() -> int:
    d, name, iters, payload_kb = (
        sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    w = World(name, dir=d)
    pad = "x" * (payload_kb * 1024)
    for i in range(iters):
        print(f"start {i}", flush=True)
        w.update({"i": i, "pad": pad})
        print(f"done {i}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
