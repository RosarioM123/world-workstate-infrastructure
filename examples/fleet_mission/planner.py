"""Fleet mission planner: defines the mission, checkpoints, exits.

Run as a subprocess by run_demo.py:
    python planner.py <mission-name>

Takes the mission name on the command line. Nothing else is passed —
the mission definition is written to WORLD, and the process terminates.
"""

import os
import sys

from world import World
from world.invariants import no_negative

MISSION_STEPS = ["survey field-north", "tow trailer", "return to depot"]


def plan_mission(mission_name: str) -> None:
    mission = World(
        mission_name,
        invariants=[no_negative("battery_pct"), no_negative("steps_remaining")],
    )
    mission.update(
        {
            "objective": "Survey field-north, tow trailer to depot",
            "steps": list(MISSION_STEPS),
            "steps_remaining": len(MISSION_STEPS),
            "assigned_robot": "r-hauler-1",
            "battery_pct": 92,
            "status": "planned",
        },
        actor="mission-planner",
        note="mission defined",
    )
    mission.checkpoint("mission-planned")
    print(
        f"planner (PID {os.getpid()}): mission defined, "
        f"{mission.state()['steps_remaining']} steps"
    )


if __name__ == "__main__":
    plan_mission(sys.argv[1])
