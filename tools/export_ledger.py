"""Export the WORLD ledger to JSON for independent verification.

Writes an array of ledger rows (transaction_id order) to stdout or a
file. The companion C# verifier (tools/ChainVerify) reads this format
and re-checks the hash chain without touching the Python code.

Usage:
    python tools/export_ledger.py ledger.json
    python tools/export_ledger.py > ledger.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import get_ledger, init_db  # noqa: E402


def main() -> None:
    init_db()
    # get_ledger returns newest-first; the export is oldest-first so a
    # verifier can walk the chain forward from genesis.
    rows = list(reversed(get_ledger(limit=10_000_000)))
    doc = [
        {
            "transaction_id": r["transaction_id"],
            "timestamp": r["timestamp"],
            "entity_id": r["entity_id"],
            "action": r["action"],
            "payload": r["payload"],
            "previous_hash": r["previous_hash"],
            "record_hash": r["record_hash"],
            "status": r["status"],
        }
        for r in rows
    ]
    out = json.dumps(doc, indent=2)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(out, encoding="utf-8")
        print(f"exported {len(doc)} ledger rows to {sys.argv[1]}")
    else:
        print(out)


if __name__ == "__main__":
    main()
