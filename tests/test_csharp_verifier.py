"""The independent C# verifier agrees with Python's verify().

Builds a world, checks the C# reimplementation accepts it, tampers via
raw SQL, and checks the C# verifier rejects it. Skipped when dotnet is
unavailable.
"""

import os
import shutil
import sqlite3
import subprocess

import pytest

from world import World
from world.invariants import monotonic

PROJ = os.path.join(
    os.path.dirname(__file__), "..", "tools", "ChainVerifyWorld",
    "ChainVerifyWorld.csproj",
)
DOTNET = os.path.expanduser("~/.dotnet/dotnet")

pytestmark = pytest.mark.skipif(
    not (shutil.which("dotnet") or os.path.exists(DOTNET)),
    reason="dotnet not available",
)


def _run_csharp(db_path, name):
    dotnet = shutil.which("dotnet") or DOTNET
    env = dict(os.environ, DOTNET_CLI_TELEMETRY_OPTOUT="1",
               DOTNET_NOLOGO="1")
    return subprocess.run(
        [dotnet, "run", "--project", PROJ, "--", db_path, name],
        capture_output=True, text=True, timeout=600, env=env,
    )


def _world(tmp_path):
    w = World("csharp", dir=str(tmp_path), invariants=[monotonic("n")])
    n = 0
    for i in range(25):
        n += 1 if i % 4 else -1
        try:
            w.update({"n": n, "i": i}, actor="a" if i % 2 else None,
                     note=f"n{i}" if i % 3 else "")
        except Exception:
            pass
    assert w.verify()
    return w


def test_csharp_accepts_valid_chain(tmp_path):
    w = _world(tmp_path)
    p = _run_csharp(str(w.path), "csharp")
    assert p.returncode == 0, p.stderr
    assert "25 rows verified" in p.stdout or "rows verified" in p.stdout


def test_csharp_rejects_tampered_chain(tmp_path):
    w = _world(tmp_path)
    cx = sqlite3.connect(w.path)
    try:
        cx.execute("UPDATE versions SET state = ? WHERE seq = 10",
                   ('{"n": 9999}',))
        cx.commit()
    finally:
        cx.close()
    assert not w.verify()  # Python agrees
    p = _run_csharp(str(w.path), "csharp")
    assert p.returncode == 1, p.stderr
    assert "seq 10" in p.stderr


def test_csharp_rejects_broken_link(tmp_path):
    w = _world(tmp_path)
    cx = sqlite3.connect(w.path)
    try:
        cx.execute("UPDATE versions SET prev_hash = '00' WHERE seq = 20")
        cx.commit()
    finally:
        cx.close()
    p = _run_csharp(str(w.path), "csharp")
    assert p.returncode == 1
    assert "seq 20" in p.stderr


def test_csharp_rejects_wrong_world_name(tmp_path):
    w = _world(tmp_path)
    p = _run_csharp(str(w.path), "not-csharp")
    assert p.returncode == 1  # genesis prev_hash binds the name
