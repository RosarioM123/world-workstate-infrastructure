"""Crash-consistency: SIGKILL the writer mid-transaction, then verify.

Each round spawns a subprocess hammering a WORLD with 256KB updates
(widening the BEGIN IMMEDIATE..COMMIT window), kills it with SIGKILL at
a random moment, and asserts the database opens cleanly, verify() is
True, every row parses, and version() is sane. The worker's start/done
markers confirm the kill actually landed inside a transaction.
"""

import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "experiments",
                    "crash-consistency"))

from crash_test import run_round  # noqa: E402


def test_sigkill_mid_transaction_leaves_clean_db():
    mids = 0
    for r in range(6):
        res = run_round(seed=20261015 + r, payload_kb=256)
        assert res["rows"] > 0
        mids += res["mid_transaction_kill"]
    # The test is only meaningful if kills actually hit the window.
    assert mids >= 1, "no kill landed mid-transaction; widen the payload"
