"""Demo process 1: Agent A works a research task and hands off.

Scenario: a memo on solid-state battery suppliers. Agent A records
a spend position under a declared cap, saves a structured handoff
state (decisions, assumptions with confidence, evidence), then
revises its primary decision when new evidence arrives, superseding
the old decision with a reason and an evidence link. It checkpoints
the result, signs the chain tip, and exits. Everything Agent B
later reconstructs comes from the world file alone.

Run:  python demo/agent_a.py     (then run demo/agent_b.py)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import DEMO_TIP_KEY, WORLD_NAME, demo_dir, spend_cap_invariant

from world import InvariantViolation, World
from world.handoff import AgentState, Assumption, Decision, Evidence, save_state


def main() -> int:
    data_dir = demo_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / f"{WORLD_NAME}.db"
    if db_path.exists():
        db_path.unlink()
        print(f"reset: removed previous demo world at {db_path}")

    work = World(WORLD_NAME, dir=data_dir, invariants=[spend_cap_invariant])
    print(f"Agent A: opened world {WORLD_NAME!r} at {work.path}")

    # 1. Record spend under the declared cap (constraint as data).
    seq = work.update(
        {"spend": {"committed_usd": 1200, "cap_usd": 5000, "note": "data-room access"}},
        actor="agent-a",
        note="booked supplier data-room access",
    )
    print(f"committed seq {seq}: spend 1200 USD of 5000 USD cap")

    # 2. Try to blow through the cap. The invariant judges it, the
    #    attempt is recorded as REJECTED, and the state does not move.
    doc = dict(work.state())
    doc["spend"] = {"committed_usd": 9000, "cap_usd": 5000, "note": "full teardown"}
    try:
        work.update(doc, actor="agent-a", note="book the full teardown series")
        print("UNEXPECTED: over-cap update committed")
    except InvariantViolation as e:
        print(f"rejected seq {e.seq}: {e.reason}")
    print(f"committed spend is still {work.state()['spend']['committed_usd']} USD")

    # 3. Save the handoff state: decisions, assumptions, evidence.
    state_v1 = AgentState(
        objective="Write a sourcing memo on solid-state battery cell suppliers",
        decisions=[
            Decision(
                text="Use the March teardown dataset as the primary cost source",
                rationale="It is the only dataset with cell-level cost splits",
                id="D1",
                status="accepted",
                evidence_ids=["E1"],
            ),
            Decision(
                text="Scope the memo to cell makers, not pack assemblers",
                rationale="Pack economics follow cell prices with a lag",
                id="D2",
                status="accepted",
                evidence_ids=["E1"],
            ),
        ],
        assumptions=[
            Assumption(
                text="Pilot-line yields reach 80 percent by Q2 2027",
                id="A1",
                confidence="medium",
                status="active",
            ),
            Assumption(
                text="Licensing terms for the leading patent holder stay non-exclusive",
                id="A2",
                confidence="low",
                status="active",
            ),
        ],
        evidence=[
            Evidence(
                claim="March teardown: leading cell at 118 USD per kWh",
                source="Supplier data room, March teardown dataset",
                id="E1",
                kind="measurement",
            ),
        ],
        open_questions=["Will the leading supplier license its anode process?"],
        next_actions=["Draft the cost-curve section", "Interview two cell makers"],
    )
    v1 = save_state(work, state_v1, actor="agent-a", note="initial handoff state")
    print(f"committed seq {v1}: handoff state saved (decisions D1, D2; assumptions A1, A2)")

    # 4. New evidence arrives and the primary decision is revised.
    #    D1 is marked superseded; D3 replaces it, names what it
    #    supersedes, says why, and links the new evidence.
    state_v2 = AgentState(
        objective=state_v1.objective,
        decisions=[
            Decision(
                text="Use the March teardown dataset as the primary cost source",
                rationale="It is the only dataset with cell-level cost splits",
                id="D1",
                status="superseded",
                evidence_ids=["E1"],
            ),
            Decision(
                text="Scope the memo to cell makers, not pack assemblers",
                rationale="Pack economics follow cell prices with a lag",
                id="D2",
                status="accepted",
                evidence_ids=["E1"],
            ),
            Decision(
                text="Use the January teardown refresh as the primary cost source",
                rationale=(
                    "The refresh corrects the March cathode pricing error and "
                    "puts the leading cell at 104 USD per kWh"
                ),
                id="D3",
                status="accepted",
                supersedes="D1",
                evidence_ids=["E2"],
            ),
        ],
        assumptions=state_v1.assumptions,
        evidence=[
            state_v1.evidence[0],
            Evidence(
                claim="January refresh: leading cell at 104 USD per kWh, cathode error corrected",
                source="Supplier data room, January teardown refresh",
                id="E2",
                kind="measurement",
            ),
        ],
        open_questions=state_v1.open_questions,
        next_actions=["Draft the cost-curve section on the refreshed numbers"],
    )
    v2 = save_state(work, state_v2, actor="agent-a", note="D3 supersedes D1 on E2")
    print(f"committed seq {v2}: D3 supersedes D1 (reason and evidence E2 recorded)")

    # 5. Checkpoint the handoff point and sign the chain tip. The
    #    tip is stored outside the database, as a holder would.
    cp = work.checkpoint("handoff-ready")
    tip = work.sign_tip(DEMO_TIP_KEY)
    tip_path = data_dir / "tip.json"
    tip_path.write_text(json.dumps(tip, indent=2))
    print(f"checkpoint 'handoff-ready' pinned at seq {cp}")
    print(f"signed tip for seq {tip['seq']} written out of band to {tip_path}")
    print(f"verify() inside Agent A: {work.verify()}")
    print("Agent A process exiting now. Only the world file and the tip survive.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
