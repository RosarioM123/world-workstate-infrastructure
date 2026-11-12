"""Shared pieces for the two-process WORLD demo.

Both demo processes import this module. It holds only the world
name, the demo data directory, the demo signing key, and the one
invariant the scenario runs under. All state lives in the world
file; nothing is shared in memory between the two processes.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from world.core import InvariantViolation

WORLD_NAME = "battery-supplier-memo"

#: Demo-only key for the HMAC signed tip. A real deployment holds
#: tip keys out of band and never in source control; here the key is
#: printed in the open because the demo's point is the mechanism.
DEMO_TIP_KEY = "demo-tip-key-not-a-secret"

SPEND_CAP_USD = 5000


def demo_dir() -> Path:
    """Directory holding the demo world file and the signed tip."""
    override = os.environ.get("WORLD_DEMO_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "demo-data"


def spend_cap_invariant(old_state: dict[str, Any], new_state: dict[str, Any]) -> None:
    """The scenario's one declared constraint, enforced as a rule.

    Total committed spend recorded in the document may not exceed
    SPEND_CAP_USD. A proposal that crosses the cap is judged and
    recorded as REJECTED; the committed state does not move.
    """
    spend = new_state.get("spend")
    if not isinstance(spend, dict):
        return
    committed = spend.get("committed_usd")
    if isinstance(committed, (int, float)) and committed > SPEND_CAP_USD:
        raise InvariantViolation(
            f"spend_cap: committed_usd {committed} exceeds cap {SPEND_CAP_USD}"
        )
