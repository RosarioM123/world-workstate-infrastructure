"""Backward-compatible shim for the flat-layout entry point.

The transcript importer now lives in
``src/world_engine/ingestion/transcript.py``; this module re-exports its
public names so ``python import_transcript.py`` keeps working.
New code should ``from world_engine.ingestion.transcript import ...``.
"""

from world_engine.ingestion.transcript import *  # noqa: F401,F403

if __name__ == "__main__":
    main()  # noqa: F405
