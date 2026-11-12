"""Demo process 2: Agent B reconstructs the work and continues it.

A separate process with no shared memory opens the same world file
Agent A left behind. Everything printed below is derived from the
world file (and the out-of-band signed tip) at runtime: the current
authoritative decisions, the revision chain of the superseded
decision, the active assumptions with their confidence levels, the
recorded constraint rejection, and a verification of the chain.
Agent B then continues the task with one new decision and verifies
the resulting history.

Run after demo/agent_a.py:  python demo/agent_b.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import DEMO_TIP_KEY, WORLD_NAME, demo_dir, spend_cap_invariant

from world import World
from world.handoff import Decision, load_state, project_state, revision_chain, save_state


def main() -> int:
    data_dir = demo_dir()
    work = World(WORLD_NAME, dir=data_dir, invariants=[spend_cap_invariant])
    print(f"Agent B: new process, opened world {WORLD_NAME!r} at {work.path}")
    print("Agent B: re-declared the spend-cap invariant on its own handle")
    print("         (invariants are per-handle code; the server is the")
    print("          uniform-enforcement point for remote writers)")

    # 1. Verify the chain, and the signed tip if one was left.
    print(f"verify(): {work.verify()}")
    tip_path = data_dir / "tip.json"
    if tip_path.exists():
        tip = json.loads(tip_path.read_text())
        print(f"verify_tip(signed tip from seq {tip['seq']}): {work.verify_tip(DEMO_TIP_KEY, tip)}")

    # 2. Reconstruct the task context.
    state = load_state(work)
    print(f"\nObjective: {state.objective}")
    print("\nAuthoritative decisions now (accepted or proposed):")
    for d in state.decisions:
        if d.status in ("accepted", "proposed"):
            print(f"  {d.id} [{d.status}] {d.text}")
            print(f"      why: {d.rationale}")
    superseded = [d for d in state.decisions if d.status in ("superseded", "reversed")]
    print("\nNo longer authoritative (kept in the record, not current guidance):")
    for d in superseded:
        print(f"  {d.id} [{d.status}] {d.text}")

    # 3. The revision chain of the superseded decision: original,
    #    what changed, who, why, on what evidence, what rules now.
    print("\nRevision chain for D1 (derived from committed snapshots):")
    for e in revision_chain(work, "D1"):
        print(f"  seq {e['seq']} by {e['actor']}: status {e['status']}")
        print(f"      text: {e['text']}")
    successor = next(d for d in state.decisions if d.supersedes == "D1")
    ev = {e.id: e for e in state.evidence}
    print(f"  authoritative successor: {successor.id} [{successor.status}] {successor.text}")
    print(f"      why it changed: {successor.rationale}")
    for eid in successor.evidence_ids:
        print(f"      evidence {eid}: {ev[eid].claim} (source: {ev[eid].source})")

    # 4. Assumptions, with the metadata free-text handoffs lose.
    print("\nActive assumptions (confidence and status are fields, not prose):")
    for a in state.assumptions:
        if a.status == "active":
            print(f"  {a.id} [confidence {a.confidence}] {a.text}")

    # 5. The constraint, and its recorded enforcement.
    spend = work.state()["spend"]
    print(f"\nConstraint on record: committed spend {spend['committed_usd']} USD, cap {spend['cap_usd']} USD")
    for row in work.history():
        if row["status"] == "REJECTED":
            print(f"  enforcement on record: seq {row['seq']} REJECTED by {row['actor']}: {row['note']}")

    # 6. The projection view, measured on this state.
    full = json.dumps(state.to_dict())
    projected = project_state(state)
    proj = json.dumps(projected.to_dict())
    print(f"\nProjection view: full state {len(full)} chars, projected {len(proj)} chars")
    for d in projected.decisions:
        if d.status in ("superseded", "reversed"):
            print(f"  projected {d.id} is a compact status-marked entry: [{d.status}] {d.text}")

    # 7. What a conventional summary of this same state would carry.
    print("\nFor contrast, a plain summary of this state would read:")
    summary_bits = [state.objective + "."]
    for d in state.decisions:
        if d.status == "accepted":
            summary_bits.append(d.text + ".")
    for a in state.assumptions:
        summary_bits.append("Assumed: " + a.text + ".")
    print("  " + " ".join(summary_bits))
    print("  What that summary cannot carry, computed from the state above:")
    for a in state.assumptions:
        print(f"    {a.id}: confidence level {a.confidence!r} (Experiment #003 metric 3:")
        print("         summaries recovered assumption substance but lost exactly this)")
    print(f"    D1 vs {successor.id}: which decision is authoritative, and that one")
    print("         superseded the other, with the reason and the evidence link")

    # 8. Continue the task: one new decision on the refreshed basis.
    continued = load_state(work)
    continued.decisions.append(
        Decision(
            text="Draft the memo with the refreshed cost curve as the base case",
            rationale="D3 established the refreshed dataset as authoritative",
            id="D4",
            status="accepted",
            evidence_ids=["E2"],
        )
    )
    continued.next_actions = ["Write the memo draft on the D3 basis"]
    seq = save_state(work, continued, actor="agent-b", note="continuing: base case set from D3")
    print(f"\nAgent B continued the work: committed seq {seq} (decision D4 added)")

    # 9. Final verification and the full verdict log.
    print(f"final verify(): {work.verify()}")
    print("\nVerdict log (every attempt, committed and rejected):")
    for row in work.history():
        print(f"  seq {row['seq']} {row['status']} {row['actor']}: {row['note']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
