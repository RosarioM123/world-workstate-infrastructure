"""Run the fleet mission demo end-to-end with a single command.

    python examples/fleet_mission/run_demo.py

What it does:
  1. Creates an isolated WORLD_DIR (temp dir) — the demo touches nothing
     of yours.
  2. Launches planner.py as a real OS subprocess. The planner defines the
     mission, checkpoints it, and its process TERMINATES.
  3. Launches executor.py as a brand-new OS process with only the mission
     name on its command line. It recovers the mission from WORLD,
     executes one step, checkpoints, terminates. Run once per step.
  4. Verifies the hash chain as the closing proof.

The point: the mission survives process death. The planner is gone; the
executor never saw its code or its memory — only the WORLD it left
behind.
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(REPO, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)  # bare checkout: parent needs world too

from world import World
from world.invariants import no_negative

MISSION_NAME = "mission-alpha"
STEPS = 3


def run_script(script: str, mission_name: str, env: dict) -> None:
    proc = subprocess.Popen(
        [sys.executable, os.path.join(HERE, script), mission_name],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    print(f"--- {script} started as PID {proc.pid} ---")
    out, _ = proc.communicate()
    print(out, end="")
    print(f"--- PID {proc.pid} terminated (returncode {proc.returncode}) ---")
    if proc.returncode != 0:
        raise SystemExit(f"{script} failed with returncode {proc.returncode}")


def main() -> None:
    world_dir = tempfile.mkdtemp(prefix="world-fleet-")
    env = dict(
        os.environ,
        WORLD_DIR=world_dir,
        PYTHONPATH=SRC + os.pathsep + os.environ.get("PYTHONPATH", ""),
    )
    os.environ["WORLD_DIR"] = world_dir  # this process reads the same dir
    print(f"WORLD_DIR={world_dir}\n")

    run_script("planner.py", MISSION_NAME, env)

    for i in range(STEPS):
        print("\n================ PROCESS BOUNDARY ================")
        print(
            f"Previous process is gone. Executor starts with only "
            f"the mission name (step {i + 1}/{STEPS}).\n"
        )
        run_script("executor.py", MISSION_NAME, env)

    # Closing proof: fresh handle, chain verification.
    final = World(
        MISSION_NAME,
        invariants=[no_negative("battery_pct"), no_negative("steps_remaining")],
    )
    state = final.state()
    print(
        f"\nfinal: {state['status']}, battery {state['battery_pct']}%, "
        f"{state['steps_remaining']} steps remaining"
    )
    print(f"chain valid: {final.verify()}")


if __name__ == "__main__":
    main()
