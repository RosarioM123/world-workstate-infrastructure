"""Packaging guarantees for the WORLD kernel.

The SDK and the examples/experiments type-check against the installed
packages, which only works if the distributions ship PEP 561 ``py.typed``
markers. These tests pin that down so a packaging regression cannot
silently break downstream mypy runs.
"""

import importlib
import importlib.util
from pathlib import Path


def _package_dir(package: str) -> Path:
    spec = importlib.util.find_spec(package)
    assert spec is not None, f"package {package!r} is not importable"
    locations = spec.submodule_search_locations
    assert locations, f"package {package!r} has no search locations"
    return Path(locations[0])


# Test extras (fastapi, httpx, hypothesis) are declared in
# pyproject.toml under `[project.optional-dependencies] test`. A bare
# `pip install -e .` leaves them out, and the API, security, and
# property tests then skip wholesale via `pytest.importorskip` while
# the suite still reports green. This guard runs with no extras at
# all, so a bare install fails loudly here instead of passing with
# large test areas silently untested (audit finding T-7).
TEST_EXTRAS = ("fastapi", "httpx", "hypothesis")


def test_test_extras_are_installed():
    missing = []
    for name in TEST_EXTRAS:
        try:
            importlib.import_module(name)
        except ImportError:
            missing.append(name)
    assert not missing, (
        "test extras missing: " + ", ".join(missing) + "; "
        'run `pip install -e ".[test]"` before running the suite'
    )


def test_world_engine_ships_py_typed():
    assert (_package_dir("world_engine") / "py.typed").is_file()


def test_world_sdk_ships_py_typed():
    assert (_package_dir("world_sdk") / "py.typed").is_file()


def test_ingestion_reexports_transcript():
    from world_engine import ingestion

    assert ingestion.transcript is not None
    assert "transcript" in ingestion.__all__
