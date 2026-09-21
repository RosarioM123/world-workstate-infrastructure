"""Backward-compatible shim: ``uvicorn app:app`` still works.

The FastAPI application now lives in ``src/world_engine/api/main.py``;
the canonical target is ``uvicorn world_engine.api.main:app``.
render.yaml, .devcontainer/devcontainer.json and the README all use this
shim target, so no deploy config had to change.
"""

from world_engine.api.main import app  # noqa: F401
