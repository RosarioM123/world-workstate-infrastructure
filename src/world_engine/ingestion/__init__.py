"""Live data ingestion: feeds -> normalized observations -> intents."""
from world_engine.ingestion.client import (  # noqa: F401
    ingest_live,
    init_observations,
    rogue_agent_attack,
    weather_to_intent,
)
