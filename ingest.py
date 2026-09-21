"""Backward-compatible shim for the flat-layout entry point.

The ingestor now lives in ``src/world_engine/ingestion/client.py``; this
module re-exports its public names so ``python ingest.py`` and
``import ingest`` keep working unchanged.
New code should ``from world_engine.ingestion.client import ...``.
"""

from world_engine.ingestion.client import *  # noqa: F401,F403

if __name__ == "__main__":
    main()  # noqa: F405
