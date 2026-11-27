"""Smoke tests for the paths outside the shipped primitive (T-9).

tools/, demo/, and the root shims (app.py, engine.py,
import_transcript.py) were outside coverage measurement entirely, so
the 97% figure said nothing about them. These tests exercise the
tool and demo entry points in-process (loaded by path, so the script
modules are measured by coverage) plus the two shim __main__ paths
as subprocesses, which is how they actually run.
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
DEMO = ROOT / "demo"


def _load(name, path):
    """Import a script module by file path (scripts are not packages)."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def ledger_db(tmp_path, monkeypatch):
    """A small legacy ledger with two TICK rows, isolated by env."""
    db_path = tmp_path / "world_state.db"
    monkeypatch.setenv("WORLD_DB_PATH", str(db_path))
    from world_engine.core import engine as legacy

    legacy.init_db()
    for _ in range(2):
        legacy.execute_deterministic_transition(
            legacy.IntentTransaction(
                entity_id=legacy.SEED_ENTITY_ID,
                action="TICK",
                requested_delta_capacity=0.0,
                requested_delta_cash=1.0,
            )
        )
    return db_path


def test_export_ledger_round_trip_to_file(ledger_db, tmp_path, monkeypatch, capsys):
    export_ledger = _load("tools_export_ledger", TOOLS / "export_ledger.py")
    out = tmp_path / "ledger.json"
    monkeypatch.setattr(sys, "argv", ["export_ledger.py", str(out)])
    export_ledger.main()
    rows = json.loads(out.read_text(encoding="utf-8"))
    assert [r["transaction_id"] for r in rows] == [1, 2]
    assert all(r["action"] == "TICK" for r in rows)
    assert "exported 2 ledger rows" in capsys.readouterr().out


def test_export_ledger_stdout(ledger_db, monkeypatch, capsys):
    export_ledger = _load("tools_export_ledger", TOOLS / "export_ledger.py")
    monkeypatch.setattr(sys, "argv", ["export_ledger.py"])
    export_ledger.main()
    rows = json.loads(capsys.readouterr().out)
    assert [r["transaction_id"] for r in rows] == [1, 2]


def test_export_ledger_missing_db_fails_without_creating(tmp_path, monkeypatch, capsys):
    """L-12: the export must not create a ledger on a fresh checkout."""
    missing = tmp_path / "no-such.db"
    monkeypatch.setenv("WORLD_DB_PATH", str(missing))
    export_ledger = _load("tools_export_ledger", TOOLS / "export_ledger.py")
    monkeypatch.setattr(sys, "argv", ["export_ledger.py"])
    with pytest.raises(SystemExit) as exc:
        export_ledger.main()
    assert exc.value.code == 1
    assert str(missing) in capsys.readouterr().err
    assert not missing.exists()


def test_bench_small(tmp_path, monkeypatch):
    bench = _load("tools_bench", TOOLS / "bench.py")
    # bench.main() sets WORLD_DB_PATH itself; monkeypatch restores it.
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "orig.db"))
    monkeypatch.setattr(sys, "argv", ["bench.py", "--rows", "3"])
    assert bench.main() == 0


def test_bench_world_small(monkeypatch):
    bench_world = _load("tools_bench_world", TOOLS / "bench_world.py")
    monkeypatch.setattr(sys, "argv", ["bench_world.py", "--rows", "2"])
    assert bench_world.main() == 0


def test_bench_contention_small(monkeypatch):
    bench_contention = _load("tools_bench_contention", TOOLS / "bench_contention.py")
    monkeypatch.setattr(sys, "argv", ["bench_contention.py", "--ops-per-thread", "2"])
    assert bench_contention.main() == 0


def test_guardrail_audit_pass_and_flag(tmp_path, monkeypatch, capsys):
    audit = _load("tools_guardrail_audit", TOOLS / "guardrail_audit.py")
    bundle = tmp_path / "bundle.json"
    bundle.write_text(
        json.dumps({"guardrails": [{"id": g} for g in ("G1", "G2", "G3", "G4")]}),
        encoding="utf-8",
    )
    clean = tmp_path / "clean.md"
    clean.write_text("plain text, no issues.\n", encoding="utf-8")
    actions = tmp_path / "actions.json"
    actions.write_text(
        json.dumps([{"type": "write", "target": "notes.md", "path": str(clean)}]),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "guardrail_audit.py",
            "--bundle",
            str(bundle),
            "--actions",
            str(actions),
            "--json",
        ],
    )
    with pytest.raises(SystemExit) as exc:
        audit.main()
    assert exc.value.code == 0
    results = json.loads(capsys.readouterr().out)
    assert [r["id"] for r in results] == ["G1", "G2", "G3", "G4"]
    assert all(r["verdict"] in ("PASS", "MANUAL") for r in results)

    dashy = tmp_path / "dashy.md"
    dashy.write_text("an em dash \u2014 here\n", encoding="utf-8")
    flagged = tmp_path / "flagged.json"
    flagged.write_text(
        json.dumps(
            [
                {"type": "write", "target": "notes.md", "path": str(dashy)},
                {"type": "write", "target": "LICENSE", "path": str(clean)},
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["guardrail_audit.py", "--bundle", str(bundle), "--actions", str(flagged)],
    )
    with pytest.raises(SystemExit) as exc:
        audit.main()
    assert exc.value.code == 1
    assert "FLAG" in capsys.readouterr().out


def _git(repo, *args, date=None):
    env = dict(os.environ)
    if date is not None:
        env["GIT_AUTHOR_DATE"] = date
        env["GIT_COMMITTER_DATE"] = date
    subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )


def _dated_repo(tmp_path):
    """A throwaway git repo with controlled commit dates.

    docs/architecture.md is committed on 2026-11-20 and never touched
    again; docs/evolving.md is committed the same day and changed on
    2026-11-25. An entity recorded on 2026-11-24 therefore sees the
    first file as unchanged and the second as changed, no matter what
    checkout this test itself runs in. (The previous version ran
    against the real repo and broke in CI, where the default shallow
    checkout makes the boundary commit appear to touch every file.)
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "docs" / "architecture.md").write_text("v1\n", encoding="utf-8")
    (repo / "docs" / "evolving.md").write_text("v1\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "initial", date="2026-11-20T12:00:00+00:00")
    (repo / "docs" / "evolving.md").write_text("v2\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "update", date="2026-11-25T12:00:00+00:00")
    return repo


def test_staleness_ok_and_stale(tmp_path, monkeypatch, capsys):
    staleness = _load("tools_staleness", TOOLS / "staleness.py")
    repo = _dated_repo(tmp_path)
    head = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    bundle = tmp_path / "world-state.json"
    bundle.write_text(
        json.dumps(
            {
                "decisions": [
                    {
                        "id": "D1",
                        "source": "docs/architecture.md",
                        "created_at": "2026-11-24",
                    },
                    {"id": "D2", "source": head, "created_at": ""},
                    {"id": "D3", "source": "prose, no reference", "created_at": ""},
                    {
                        "id": "D4",
                        "source": "docs/evolving.md",
                        "created_at": "2026-11-24",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["staleness.py", "--bundle", str(bundle), "--repo", str(repo), "--json"],
    )
    with pytest.raises(SystemExit) as exc:
        staleness.main()
    assert exc.value.code == 0
    results = json.loads(capsys.readouterr().out)
    assert {r["id"]: r["verdict"] for r in results} == {
        "D1": "ok",
        "D2": "ok",
        "D3": "uncheckable",
        "D4": "changed",
    }

    stale_bundle = tmp_path / "stale.json"
    stale_bundle.write_text(
        json.dumps(
            {
                "decisions": [
                    {
                        "id": "D9",
                        "source": "docs/no-such-file.md",
                        "created_at": "",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["staleness.py", "--bundle", str(stale_bundle), "--repo", str(repo)],
    )
    with pytest.raises(SystemExit) as exc:
        staleness.main()
    assert exc.value.code == 1
    assert "STALE" in capsys.readouterr().out


def test_staleness_shallow_clone_history_unavailable(tmp_path, monkeypatch, capsys):
    """In a shallow clone the change history is truncated, so a file
    that did change after it was recorded must come back as history
    unavailable (verdict ok), never as a false "changed"."""
    staleness = _load("tools_staleness_shallow", TOOLS / "staleness.py")
    repo = _dated_repo(tmp_path)
    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{repo}", str(shallow)],
        capture_output=True,
        text=True,
        check=True,
    )
    bundle = tmp_path / "world-state.json"
    bundle.write_text(
        json.dumps(
            {
                "decisions": [
                    {
                        "id": "D4",
                        "source": "docs/evolving.md",
                        "created_at": "2026-11-24",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["staleness.py", "--bundle", str(bundle), "--repo", str(shallow), "--json"],
    )
    with pytest.raises(SystemExit) as exc:
        staleness.main()
    assert exc.value.code == 0
    results = json.loads(capsys.readouterr().out)
    assert {r["id"]: r["verdict"] for r in results} == {"D4": "ok"}
    assert results[0]["detail"] == "path exists; change history unavailable"


def test_write_cost_record_and_report(tmp_path, monkeypatch, capsys):
    write_cost = _load("tools_write_cost", TOOLS / "write_cost.py")
    log = tmp_path / "write-cost.jsonl"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "write_cost.py",
            "--log",
            str(log),
            "record",
            "--session",
            "2026-11-24-test",
            "--seconds",
            "30",
            "--entities",
            "2",
        ],
    )
    write_cost.main()
    rows = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert rows == [
        {
            "session": "2026-11-24-test",
            "seconds": 30,
            "entities_changed": 2,
            "note": "",
        }
    ]
    monkeypatch.setattr(sys, "argv", ["write_cost.py", "--log", str(log), "report"])
    write_cost.main()
    assert "2026-11-24-test" in capsys.readouterr().out
    monkeypatch.setattr(
        sys,
        "argv",
        ["write_cost.py", "--log", str(tmp_path / "missing.jsonl"), "report"],
    )
    write_cost.main()
    assert "no data yet" in capsys.readouterr().out


def test_demo_common_spend_cap(tmp_path, monkeypatch):
    common = _load("demo_common", DEMO / "common.py")
    from world.core import InvariantViolation

    with pytest.raises(InvariantViolation):
        common.spend_cap_invariant({}, {"spend": {"committed_usd": 5001}})
    common.spend_cap_invariant({}, {"spend": {"committed_usd": 5000}})
    common.spend_cap_invariant({}, {"spend": "not a dict"})
    common.spend_cap_invariant({}, {})
    monkeypatch.setenv("WORLD_DEMO_DIR", str(tmp_path))
    assert common.demo_dir() == tmp_path


def test_demo_agent_a_then_b(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("WORLD_DEMO_DIR", str(tmp_path))
    agent_a = _load("demo_agent_a", DEMO / "agent_a.py")
    assert agent_a.main() == 0
    assert (tmp_path / "battery-supplier-memo.db").exists()
    agent_b = _load("demo_agent_b", DEMO / "agent_b.py")
    assert agent_b.main() == 0
    assert "final verify(): True" in capsys.readouterr().out


def test_root_shims_import(monkeypatch):
    pytest.importorskip("fastapi")
    monkeypatch.syspath_prepend(str(ROOT))
    import app
    import engine
    import import_transcript

    assert app.app is not None
    assert hasattr(engine, "get_ledger")
    assert hasattr(import_transcript, "main")


def test_engine_shim_main_runs_day1_demo(tmp_path):
    env = dict(os.environ, WORLD_DB_PATH=str(tmp_path / "world_state.db"))
    proc = subprocess.run(
        [sys.executable, "engine.py"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,  # returncode is inspected by the caller
    )
    assert proc.returncode == 0, proc.stderr
    assert "Attempt 1" in proc.stdout


def test_import_transcript_shim_dry_run(tmp_path):
    notes = tmp_path / "notes.md"
    notes.write_text(
        "Alice: We decided to use SQLite for the ledger.\n"
        "Bob: We assume the chain stays under 1M rows.\n",
        encoding="utf-8",
    )
    env = dict(os.environ, WORLD_DB_PATH=str(tmp_path / "world_state.db"))
    proc = subprocess.run(
        [sys.executable, "import_transcript.py", "--dry-run", str(notes)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,  # returncode is inspected by the caller
    )
    assert proc.returncode == 0, proc.stderr
    assert "items=" in proc.stdout
    assert not (tmp_path / "world_state.db").exists()
