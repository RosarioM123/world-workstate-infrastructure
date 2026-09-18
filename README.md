# WORLD

**Deterministic append-only state ledger with hash-chain verification for AI agent work-state.**

[![CI](https://github.com/RosarioM123/world-workstate-infrastructure/actions/workflows/ci.yml/badge.svg)](https://github.com/RosarioM123/world-workstate-infrastructure/actions/workflows/ci.yml)
![Python 3.12 | 3.13](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue.svg)

AI can generate work. What it cannot do reliably is maintain a shared,
verifiable record of that work as it moves between models, agents, humans,
tools, and time. WORLD is that record: a deterministic state kernel where
agents submit *intents*, a constraint engine returns `COMMITTED` or
`REJECTED`, and every attempt — legal or rogue — is appended to a SHA-256
hash-chained ledger.

**Status: working prototype, not deployed.** Deterministic engine,
live data ingestion, FastAPI backend, React landing page, 33 passing
tests. No auth or rate limiting yet, and the ledger is tamper-evident
(via `verify_chain()`) rather than immutable. Sample data in the demo is
labeled as sample. Hosting is deferred — `render.yaml` and `/health`
keep it deploy-ready.

## Demo

<!-- TODO: drop a ~30s screen recording here (docs/demo.gif): the /demo
     dashboard, one ALLOCATE intent committing, then the rogue-attack
     simulation getting REJECTED. Record with any screen capture tool,
     keep it under 5 MB, and replace this comment with:
     ![WORLD demo](docs/demo.gif) -->

## Quickstart

30 seconds, zero setup beyond Python:

```bash
pip install -r requirements.txt

# verify the ledger's hash chain (no server needed)
python - <<'EOF'
import engine
engine.init_db()
print(engine.verify_chain())  # (True, None) — or (False, bad_id)
EOF

# run the API + dashboard
uvicorn app:app
# http://127.0.0.1:8000/demo    interactive dashboard
# http://127.0.0.1:8000/api/state  materialized state + recent ledger
```

**GitHub Codespaces** (zero local setup): Code → Codespaces → Create
codespace on `main`, wait ~2 minutes, then open forwarded port **8000**
(globe icon) in the Ports panel.

## How it works

```mermaid
flowchart LR
    A[Agent / human / CLI] -->|intent| B[FastAPI\napp.py]
    E[ingest.py\nlive Open-Meteo data] -->|intent| C
    B --> C[Constraint engine\nengine.py]
    C -->|COMMITTED / REJECTED| D[(SQLite ledger\nSHA-256 hash-chained)]
    D --> F[Materialized state]
    F --> G[/demo dashboard]
    F --> H[/api/state]
```

1. An **intent** proposes a state change: an entity, an action, and deltas.
2. The **constraint engine** validates it — capacity and liquidity cannot go
   negative, node locks are respected, deltas must be finite numbers
   (NaN, Infinity, and booleans are rejected).
3. The verdict is **appended to the ledger**: committed and rejected
   attempts alike, each row hash-chained to the previous one.
4. **Materialized state** is rebuilt deterministically from the ledger, so
   any participant can replay history and arrive at the same state.

Try the rogue-attack simulation — illegal drain, withdrawal, and spoof
intents are all blocked and logged:

```bash
curl -X POST 127.0.0.1:8000/api/rogue-attack
# every verdict: REJECTED
```

**API quickstart:**

```bash
curl 127.0.0.1:8000/api/state

curl -X POST 127.0.0.1:8000/api/intent \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"node_rotterdam_hub","action":"ALLOCATE","requested_delta_capacity":-50.0,"requested_delta_cash":0.0}'
```

## Verify the chain

```bash
python - <<'EOF'
import engine
engine.init_db()
print(engine.verify_chain())  # (True, None) — or (False, bad_id)
EOF

# Independent check (no shared code with engine.py — needs .NET 8 SDK):
python tools/export_ledger.py ledger.json
dotnet run --project tools/ChainVerify -- ledger.json
```

## Tests

```bash
python -m pytest tests/ -q
```

33 tests cover the hardening guarantees: invalid deltas rejected, unknown
entities logged as rejected, concurrent writes serialized, weather derates
computed from a fixed baseline, full hash-chain verification with
tamper pinpointing, and seed-constant consistency between engine and
ingest. CI runs the suite on Python 3.12 and 3.13 plus the frontend
production build for every push and pull request to `main`.

## Repository layout

```
/engine.py   — deterministic state kernel (hash-chained SQLite ledger,
               verify_chain(), constraint policy)
/ingest.py   — live data ingestion piped through the kernel
/app.py      — FastAPI backend (serves the React build + /demo dashboard)
/frontend    — landing page source: React 18 + Sass (Vite)
               → builds into /static/site (committed, served by app.py)
/static      — built landing page (static/site/) + /demo dashboard
/tests       — regression tests for the kernel
/tools       — export_ledger.py + ChainVerify (independent C# chain verifier)
/research    — competitive/technical research
/docs        — product hypothesis, architecture, experiments, development log
```

Rebuilding the landing page after editing `frontend/`:

```bash
cd frontend && npm install && npm run build
# output lands in static/site/ — commit it with the source change
```

## Honest limits

- **Tamper-evident, not immutable.** The ledger is hash-chained, so edits
  are detectable — but anyone holding the database file can rewrite it.
- **No auth or rate limiting yet.** The API trusts its callers.
- **The weather mapping is a demo hypothesis.** Wind speed derating port
  capacity is a fixed, auditable rule for demonstration, not a validated
  operations model.

## The thesis behind it

WORLD is **not** an AI memory system. It is the canonical record of a
project's state — context, tasks, decisions, assumptions, evidence,
artifacts, provenance, actions, state changes, outstanding questions, and
handoff state — readable and writable by any authorized participant,
regardless of model or tool.

Core hypothesis: AI can generate work, but current AI systems do not
reliably maintain a shared, verifiable state of work as that work moves
between different models, agents, humans, tools, and time.

Start here:

- `docs/hypothesis.md` — the thesis, precisely stated, with falsifiability criteria
- `docs/thesis-challenge.md` — the adversarial case: "why isn't WORLD just X?"
- `docs/state-model.md` — the canonical state ontology (draft v0.1)
- `docs/experiment-handoff.md` — the investment-research experiment that decides if we build
- `research/comparisons.md` — WORLD vs. databases, event sourcing, Git, RAG, agent memory, MCP, orchestration
- `docs/development-log.md` — running log of decisions

> The thesis is still being challenged in `docs/thesis-challenge.md` and
> tested by the handoff experiments. No application architecture beyond the
> prototype until the experiments justify it.

## Rules

- No secrets in this repo: no API keys, passwords, tokens, or `.env` files.
- This repo is the single home of the WORLD project. No new repos for it.
