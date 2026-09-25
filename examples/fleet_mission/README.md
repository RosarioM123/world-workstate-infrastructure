# Fleet mission persistence

WORLD as the mission layer for robots in the field.

A mission planner defines a multi-step robot mission. The mission state
lives in WORLD — versioned, invariant-checked (`battery_pct` and
`steps_remaining` can never go negative), hash-chained. If the planner
process dies, the executor process loads the same mission and continues.
Bad telemetry (negative battery) is rejected by invariants; the chain
stays verifiable end to end.

This is the WORLD half of the WORLD → REALITY story:

- **WORLD** persists *what must be done* (the mission, its steps, its constraints)
- **REALITY** (`reality-spatial-intelligence`) executes *what is happening*
  (the physical world: robots, zones, verified action outcomes)

Run:

```bash
python examples/fleet_mission/run_demo.py
```

`run_demo.py` launches `planner.py` as a real OS subprocess (it defines
the mission, checkpoints, and terminates), then launches `executor.py`
once per step as a brand-new process with only the mission name — no
shared memory, no transcript. The mission survives process death because
it lives in WORLD, not in any process.
