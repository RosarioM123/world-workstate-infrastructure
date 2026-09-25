"""Fleet mission executor: loads the mission, does one step, exits.

Run as a subprocess by run_demo.py:
    python executor.py <mission-name>

A brand-new process with only the mission name. It recovers the full
mission from WORLD — steps, battery, status, provenance — executes the
next step, and checkpoints. Run it once per step.
"""

import os
import sys

from world import InvariantViolation, World
from world.invariants import no_negative


def execute_mission(mission_name: str) -> None:
    mission = World(
        mission_name,
        invariants=[no_negative("battery_pct"), no_negative("steps_remaining")],
    )
    state = mission.state()
    print(f"executor (PID {os.getpid()}): loaded mission, status={state['status']!r}")

    step = state["steps"][0]
    print(f"executor: executing {step!r}...")

    # Battery drains as work happens; invariants guard against bad data.
    try:
        mission.update({"battery_pct": -5}, actor="executor", note="bad telemetry")
    except InvariantViolation as e:
        print(f"executor: rejected bad telemetry ({e.reason})")

    mission.update(
        {
            "steps": state["steps"][1:],
            "steps_remaining": state["steps_remaining"] - 1,
            "battery_pct": state["battery_pct"] - 8,
            "status": "in_progress" if state["steps_remaining"] > 1 else "complete",
            "last_completed": step,
        },
        actor="executor",
        note=f"completed {step}",
    )
    mission.checkpoint(f"step-done-{step.replace(' ', '-')}")
    print(f"executor: step done, {mission.state()['steps_remaining']} remaining")


if __name__ == "__main__":
    execute_mission(sys.argv[1])
