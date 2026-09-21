# tools/ - small helpers for the WORLD file-convention MVP

The MVP is `WORLD.md` + `world-state.json`. These scripts keep that convention honest. They are stdlib-only, work on any bundle, and make no product claims beyond what they check.

## staleness.py (idea 4)

Flags reference rot: bundle entities whose `source` points at repo paths or commits that no longer exist, and files that changed after the entity was recorded.

```bash
python3 tools/staleness.py --bundle docs/startup/write-side-trial/world-state.json --repo /path/to/checkout
```

Exit 1 when anything is stale. What it cannot catch: semantic staleness (a statement that was true and stopped being true). That still needs the human rot check in the trial's `rot-log.md`.

## write_cost.py (idea 5)

Times the record transition (the end-of-session bundle update). Two bars: 60 seconds is the product aspiration, 5 minutes is the write-side trial's pass/fail.

```bash
python3 tools/write_cost.py record --session 2026-09-21-02 --seconds 94 --entities 4
python3 tools/write_cost.py report
```

## guardrail_audit.py (idea 6)

Re-runs a session's action log against the bundle's guardrails and flags violations: em dashes in written text, writes to protected paths, license/secret/history issues. Guardrails that need judgment are marked MANUAL.

```bash
python3 tools/guardrail_audit.py --bundle docs/startup/write-side-trial/world-state.json --actions session-02-actions.json
```

The action log is one JSON object per action: `{"type": "write", "target": "tools/x.py", "path": "/local/x.py"}`. For text checks, `path` must hold the exact bytes that were committed.
