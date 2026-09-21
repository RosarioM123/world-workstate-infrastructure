"""WORLD deterministic state kernel, packaged.

Layout:
    world_engine.core       - deterministic constraint engine + hash-chained ledger
    world_engine.ingestion  - live data feeds piped through the kernel as intents
    world_engine.api        - FastAPI backend serving the dashboard and ledger API

Thin compatibility shims remain at the repo root (engine.py, ingest.py,
app.py) so existing entry points (`uvicorn app:app`, `python ingest.py`)
keep working; new code should import from this package.
"""

__version__ = "0.1.0"
