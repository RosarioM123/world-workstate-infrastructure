"""Backward-compatible shim for the flat-layout entry point.

The kernel now lives in ``src/world_engine/core/engine.py``; this module
re-exports its public names so ``python engine.py``, ``import engine``,
``tools/export_ledger.py`` and the README snippets keep working unchanged.
New code should ``from world_engine.core.engine import ...``.
"""

from world_engine.core.engine import *  # noqa: F401,F403

if __name__ == "__main__":
    # `python engine.py` still runs the original Day 1 demo. The module is
    # already imported above (for the re-export), so drop it first to let
    # runpy execute the demo block cleanly without a RuntimeWarning.
    import runpy
    import sys

    sys.modules.pop("world_engine.core.engine", None)
    runpy.run_module("world_engine.core.engine", run_name="__main__")
