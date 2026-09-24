"""Fleet mission persistence: WORLD as the mission layer for robots in the field.

Scenario: a mission planner defines a multi-step robot mission (survey field,
tow trailer, return to depot). The mission state lives in WORLD — versioned,
invariant-checked, hash-chained. If the planner process dies, the executor
process loads the same mission and continues. Nothing is lost.

This is the WORLD half of the WORLD -> REALITY story: WORLD persists *what
must be done* (the mission), REALITY executes *what is happening* (the
physical world). See the reality-spatial-intelligence repo for the fleet
operations layer that consumes missions like this one.

Run:
    python examples/fleet_mission/mission.py
"""

import os
import tempfile

os.environ.setdefault("WORLD_DIR", tempfile.mkdtemp(prefix="world-fleet-"))

from world import InvariantViolation, World
from world.invariants import no_negative


def _mission_world() -> World:
    """Every handle on the mission carries the invariants (they're code)."""
    return World(
        "mission-alpha",
        invariants=[no_negative("battery_pct"), no_negative("steps_remaining")],
    )


def plan_mission() -> World:
    """The planner: define the mission, checkpoint it, exit."""
    mission = _mission_world()

    mission.update(
        {
            "objective": "Survey field-north, tow trailer to depot",
            "steps": ["survey field-north", "tow trailer", "return to depot"],
            "steps_remaining": 3,
            "assigned_robot": "r-hauler-1",
            "battery_pct": 92,
            "status": "planned",
        },
        actor="mission-planner",
        note="mission defined",
    )
    mission.checkpoint("mission-planned")
    print(f"planner: mission defined, {mission.state()['steps_remaining']} steps")
    return mission


def execute_mission(mission_name: str) -> None:
    """The executor: a separate process. Loads the mission, does one step."""
    # New handle, same world — this is the handoff.
    mission = _mission_world()
    state = mission.state()
    print(f"executor: loaded mission, status={state['status']!r}")

    step = state["steps"][0]
    print(f"executor: executing {step!r}...")

    # Battery drains as work happens; invariants guard against bad data.
    try:
        mission.update({"battery_pct": -5}, actor="executor", note="bad telemetry")
    except InvariantViolation as e:
        print(f"executor: rejected bad telemetry ({e.reason})")

    remaining = state["steps"][0:1]
    mission.update(
        {
            "steps": state["steps"][1:],
            "steps_remaining": state["steps_remaining"] - 1,
            "battery_pct": state["battery_pct"] - 8,
            "status": "in_progress" if state["steps_remaining"] > 1 else "complete",
            "last_completed": remaining[0],
        },
        actor="executor",
        note=f"completed {remaining[0]}",
    )
    mission.checkpoint(f"step-done-{remaining[0].replace(' ', '-')}")
    print(f"executor: step done, {mission.state()['steps_remaining']} remaining")


def main() -> None:
    plan_mission()
    # The planner process "dies" here. The executor is a fresh start.
    execute_mission("mission-alpha")
    execute_mission("mission-alpha")

    final = _mission_world()
    print(
        f"\nfinal: {final.state()['status']}, battery {final.state()['battery_pct']}%"
    )
    print(f"chain valid: {final.verify()}")


if __name__ == "__main__":
    main()
