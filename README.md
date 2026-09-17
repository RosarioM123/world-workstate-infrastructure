# WORLD

**WORLD — persistent work-state infrastructure for AI and human work.**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/RosarioM123/world-ai-infrastructure)

> **Live demo:** `https://world.onrender.com` — the full
> site. The interactive dashboard (live ledger, intent submission,
> rogue-attack simulation) lives at `/demo`. Free tier: the service sleeps
> after 15 minutes idle, so the first load takes ~30s to wake up.

Core hypothesis: AI can generate work, but current AI systems do not reliably
maintain a shared, verifiable state of work as that work moves between
different models, agents, humans, tools, and time.

WORLD is **not** an AI memory system. It is the canonical record of a
project's state — context, tasks, decisions, assumptions, evidence,
artifacts, provenance, actions, state changes, outstanding questions, and
handoff state — readable and writable by any authorized participant,
regardless of model or tool.

> **Status: docs-first, prototype running.** The thesis is still being
> challenged in `docs/thesis-challenge.md` and tested by the handoff
> experiments, and a runnable Day 1 prototype of the deterministic state
> kernel exists alongside that work (see below). No application architecture
> beyond the prototype until the experiments justify it.

## Start here

- `docs/hypothesis.md` — the thesis, precisely stated, with falsifiability criteria
- `docs/thesis-challenge.md` — the adversarial case: "why isn't WORLD just X?"
- `docs/state-model.md` — the canonical state ontology (draft v0.1)
- `docs/experiment-handoff.md` — the investment-research experiment that decides if we build
- `research/comparisons.md` — WORLD vs. databases, event sourcing, Git, RAG, agent memory, MCP, orchestration
- `docs/development-log.md` — running log of decisions

## Repository layout

```
/engine.py   — deterministic state kernel (hash-chained SQLite ledger)
/ingest.py   — live data ingestion piped through the kernel
/app.py      — FastAPI backend + dark-mode dashboard
/research  — competitive/technical research
/docs      — product hypothesis, architecture, experiments, development log
/tests     — regression tests for the demo kernel
```

## Rules

- No secrets in this repo: no API keys, passwords, tokens, or `.env` files.
- This repo is the single home of the WORLD project. No new repos for it.

## Day 1 demo: deterministic state kernel

A standalone, runnable prototype alongside the docs above — it does not
replace the thesis or the experiment program.

- `engine.py` — append-only, hash-chained SQLite state ledger. Agents submit
  *intents*; a hard-coded constraint engine returns COMMITTED or REJECTED.
- `ingest.py` — pulls live Rotterdam weather (Open-Meteo, no API key) and
  pipes it through the ledger. `python ingest.py --demo` also unleashes a
  rogue agent whose illegal intents are all blocked.
- `app.py` — FastAPI backend + dark-mode dashboard.

Run it with zero local setup via GitHub Codespaces: **Code → Codespaces →
Create codespace on main**, wait ~2 minutes, then open forwarded port
**8000** (globe icon) in the Ports panel.

Or locally:

```bash
pip install -r requirements.txt
uvicorn app:app --reload
# open http://127.0.0.1:8000
```
