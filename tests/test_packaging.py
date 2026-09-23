"""Packaging guarantees for the WORLD kernel.

The SDK and the examples/experiments type-check against the installed
packages, which only works if the distributions ship PEP 561 ``py.typed``
markers. These tests pin that down so a packaging regression cannot
silently break downstream mypy runs.
"""

import importlib.util
from pathlib import Path


def _package_dir(package: str) -> Path:
    spec = importlib.util.find_spec(package)
    assert spec is not None, f"package {package!r} is not importable"
    locations = spec.submodule_search_locations
    assert locations, f"package {package!r} has no search locations"
    return Path(locations[0])


def test_world_engine_ships_py_typed():
    assert (_package_dir("world_engine") / "py.typed").is_file()


def test_world_sdk_ships_py_typed():
    assert (_package_dir("world_sdk") / "py.typed").is_file()


def test_ingestion_reexports_transcript():
    from world_engine import ingestion

    assert ingestion.transcript is not None
    assert "transcript" in ingestion.__all__
