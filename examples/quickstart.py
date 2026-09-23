"""Minimal WORLD example. Works right after ``pip install .``.

Run:
    python examples/quickstart.py

Uses a throwaway directory (not ~/.world) so the example is
self-contained and leaves nothing behind in your home directory.
"""

import os
import tempfile

os.environ.setdefault("WORLD_DIR", tempfile.mkdtemp(prefix="world-example-"))

from world import InvariantViolation, World
from world.invariants import no_negative


def main() -> None:
    work = World("example-project", invariants=[no_negative("balance")])

    seq = work.update(
        {"task": "draft memo", "balance": 100},
        actor="alice",
        note="seed",
    )
    print(f"committed version {seq}: {work.state()}")

    try:
        work.update({"balance": -5}, actor="bob", note="overspend")
    except InvariantViolation as e:
        print(f"rejected version {e.seq}: {e.reason}")
    print(f"state untouched: {work.state()}")

    work.checkpoint("v1")
    print(f"checkpoints: {work.checkpoints()}")
    print(f"chain valid: {work.verify()}")


if __name__ == "__main__":
    main()
