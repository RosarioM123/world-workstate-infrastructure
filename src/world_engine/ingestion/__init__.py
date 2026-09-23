"""Data ingestion: feeds -> normalized observations -> intents.

The transcript importer lives here (``transcript``); the synthetic
Rotterdam weather/port demo moved to ``examples/synthetic-logistics-demo/``.
"""

from world_engine.ingestion import transcript as transcript

__all__ = ["transcript"]
