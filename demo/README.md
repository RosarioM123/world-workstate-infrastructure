# WORLD two-process handoff demo

Two separate Python processes, no shared memory, no shared session.
`agent_a.py` works a research task, records its state in WORLD,
revises a decision with a reason and an evidence link, checkpoints,
signs the chain tip, and exits. `agent_b.py` starts cold, opens the
same world file, reconstructs the task (including what was
superseded, why, and on what evidence), continues the work, and
verifies the resulting history.

Nothing in either script prints a hardcoded result: every value
Agent B reports is derived from the world file at runtime.

## Setup

From the repository root, with the test environment installed (see
`REPRODUCE.md` section 1), or any environment where the `world`
package is importable:

```bash
.venv/bin/python demo/agent_a.py
.venv/bin/python demo/agent_b.py
```

`agent_a.py` resets the demo world on each run, so the pair is
re-runnable in order. `agent_b.py` is not idempotent by design: it
continues the work, which appends a new committed version each run,
as a real successor would. The demo world and the signed tip live
in `demo/demo-data/` (gitignored, regenerated per run); set
`WORLD_DEMO_DIR` to relocate them.

## What the demo shows, mapped to the scenario

1. Agent A begins a nontrivial task (a sourcing memo on
   solid-state battery suppliers).
2. It records decisions, assumptions with confidence levels, and a
   constraint (a 5,000 USD spend cap, declared as an invariant).
3. The constraint bites: an over-cap proposal is judged, recorded
   as REJECTED at seq 2, and the committed state does not move.
4. The state is saved through the typed handoff API (`save_state`).
5. New evidence arrives; decision D3 supersedes D1 with a reason
   and an evidence link, and D1 is marked superseded.
6. Agent A checkpoints, signs the chain tip (HMAC, demo key), and
   its process exits. The session boundary is the process exit.
7. Agent B, a new process, verifies the chain and the signed tip,
   loads the state, and reconstructs: the authoritative decisions,
   the revision chain for D1 (original, what changed, who, why,
   evidence, current successor), the active assumptions with
   confidence, and the recorded constraint enforcement.
8. Agent B prints the projection view's size effect on this state
   and a plain-summary rendering of the same state, with the two
   losses Experiment #003 actually measured in summaries (assumption
   confidence, and fact-versus-assumption and supersession status).
   The demo does not claim other contrasts.
9. Agent B continues the task (decision D4), and the final
   `verify()` and the full verdict log close the run.

## Expected output

Captured from an actual run on 2026-11-05 (Python 3.12.3, Linux
x86_64). Paths reflect the checkout location; sequence numbers,
verdicts, and values are stable across runs, timestamps inside the
world file are not printed.

### `python demo/agent_a.py`

```
Agent A: opened world 'battery-supplier-memo' at <repo>/demo/demo-data/battery-supplier-memo.db
committed seq 1: spend 1200 USD of 5000 USD cap
rejected seq 2: spend_cap: committed_usd 9000 exceeds cap 5000
committed spend is still 1200 USD
committed seq 3: handoff state saved (decisions D1, D2; assumptions A1, A2)
committed seq 4: D3 supersedes D1 (reason and evidence E2 recorded)
checkpoint 'handoff-ready' pinned at seq 4
signed tip for seq 4 written out of band to <repo>/demo/demo-data/tip.json
verify() inside Agent A: True
Agent A process exiting now. Only the world file and the tip survive.
```

### `python demo/agent_b.py`

```
Agent B: new process, opened world 'battery-supplier-memo' at <repo>/demo/demo-data/battery-supplier-memo.db
Agent B: re-declared the spend-cap invariant on its own handle
         (invariants are per-handle code; the server is the
          uniform-enforcement point for remote writers)
verify(): True
verify_tip(signed tip from seq 4): True

Objective: Write a sourcing memo on solid-state battery cell suppliers

Authoritative decisions now (accepted or proposed):
  D2 [accepted] Scope the memo to cell makers, not pack assemblers
      why: Pack economics follow cell prices with a lag
  D3 [accepted] Use the January teardown refresh as the primary cost source
      why: The refresh corrects the March cathode pricing error and puts the leading cell at 104 USD per kWh

No longer authoritative (kept in the record, not current guidance):
  D1 [superseded] Use the March teardown dataset as the primary cost source

Revision chain for D1 (derived from committed snapshots):
  seq 3 by agent-a: status accepted
      text: Use the March teardown dataset as the primary cost source
  seq 4 by agent-a: status superseded
      text: Use the March teardown dataset as the primary cost source
  authoritative successor: D3 [accepted] Use the January teardown refresh as the primary cost source
      why it changed: The refresh corrects the March cathode pricing error and puts the leading cell at 104 USD per kWh
      evidence E2: January refresh: leading cell at 104 USD per kWh, cathode error corrected (source: Supplier data room, January teardown refresh)

Active assumptions (confidence and status are fields, not prose):
  A1 [confidence medium] Pilot-line yields reach 80 percent by Q2 2027
  A2 [confidence low] Licensing terms for the leading patent holder stay non-exclusive

Constraint on record: committed spend 1200 USD, cap 5000 USD
  enforcement on record: seq 2 REJECTED by agent-a: book the full teardown series | REJECTED: spend_cap: committed_usd 9000 exceeds cap 5000

Projection view: full state 1583 chars, projected 1529 chars
  projected D1 is a compact status-marked entry: [superseded] Use the March teardown dataset as the primary cost source

For contrast, a plain summary of this state would read:
  Write a sourcing memo on solid-state battery cell suppliers. Scope the memo to cell makers, not pack assemblers. Use the January teardown refresh as the primary cost source. Assumed: Pilot-line yields reach 80 percent by Q2 2027. Assumed: Licensing terms for the leading patent holder stay non-exclusive.
  What that summary cannot carry, computed from the state above:
    A1: confidence level 'medium' (Experiment #003 metric 3:
         summaries recovered assumption substance but lost exactly this)
    A2: confidence level 'low' (Experiment #003 metric 3:
         summaries recovered assumption substance but lost exactly this)
    D1 vs D3: which decision is authoritative, and that one
         superseded the other, with the reason and the evidence link

Agent B continued the work: committed seq 5 (decision D4 added)
final verify(): True

Verdict log (every attempt, committed and rejected):
  seq 1 COMMITTED agent-a: booked supplier data-room access
  seq 2 REJECTED agent-a: book the full teardown series | REJECTED: spend_cap: committed_usd 9000 exceeds cap 5000
  seq 3 COMMITTED agent-a: initial handoff state
  seq 4 COMMITTED agent-a: D3 supersedes D1 on E2
  seq 5 COMMITTED agent-b: continuing: base case set from D3
```

## Honesty notes

- The signed tip uses a demo key printed in `demo/common.py`. The
  mechanism is real (HMAC over name, seq, and tip hash, verified
  against the live chain); the key management is deliberately not.
- The invariant is re-declared by Agent B on its own handle.
  WORLD invariants are per-handle code, not stored rules; the demo
  says so in its own output rather than hiding it.
- The summary contrast is limited to the losses Experiment #003
  measured. On most other #003 metrics the summary condition tied
  or beat the structured state; see
  `experiments/experiment-003/REPORT.md` before generalizing from
  this demo.
