# WORLD

**Deterministic work-state infrastructure for AI agents and humans.**

[![CI](https://github.com/RosarioM123/world-ai-infrastructure/actions/workflows/ci.yml/badge.svg)](https://github.com/RosarioM123/world-ai-infrastructure/actions/workflows/ci.yml)
![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/RosarioM123/world-ai-infrastructure)

> **Live demo:** `https://world.onrender.com` — the landing page. The
> interactive dashboard (live ledger, intent submission, rogue-attack
> simulation) is at `/demo`. The free tier sleeps after 15 minutes idle,
> so the first load takes ~30s to wake up.

AI can generate work. What it cannot do reliably is maintain a shared,
verifiable record of that work as it moves between models, agents, humans,
tools, and time. WORLD is that record: a deterministic state kernel where
agents submit *intents*, a constraint engine returns `COMMITTED` or
`REJECTED`, and every attempt — legal or rogue — is appended to a SHA-256
hash-chained ledger.

**Status: working prototype.** Deterministic engine, live data ingestion,
FastAPI dashboard, 11 passing tests. No auth or rate limiting yet, and the
ledger is tamper-evident rather than immutable. Sample data in the demo is
labeled as sample.

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
curl -X POST https://world.onrender.com/api/rogue-attack
# every verdict: REJECTED
```

## Run it

**GitHub Codespaces** (zero local setup): Code → Codespaces → Create
codespace on `main`, wait ~2 minutes, then open forwarded port **8000**
(globe icon) in the Ports panel.

**Locally:**

```bash
pip install -r requirements.txt
uvicorn app:app --reload
# http://127.0.0.1:8000         landing page
# http://127.0.0.1:8000/demo    interactive dashboard
```

**API quickstart:**

```bash
curl https://world.onrender.com/api/state

curl -X POST https://world.onrender.com/api/intent \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"node_rotterdam_hub","action":"ALLOCATE","requested_delta_capacity":-50.0,"requested_delta_cash":0.0}'
```

## Tests

```bash
python -m pytest tests/ -q
```

11 regression tests cover the hardening guarantees: invalid deltas
rejected, unknown entities logged as rejected, concurrent writes
serialized, weather derates computed from a fixed baseline. CI runs the
suite on Python 3.12 and 3.13 for every push and pull request to `main`.

## Repository layout

```
/engine.py   — deterministic state kernel (hash-chained SQLite ledger)
/ingest.py   — live data ingestion piped through the kernel
/app.py      — FastAPI backend + dashboard
/static      — redesigned landing page (served at /)
/tests       — regression tests for the kernel
/research    — competitive/technical research
/docs        — product hypothesis, architecture, experiments, development log
```

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
