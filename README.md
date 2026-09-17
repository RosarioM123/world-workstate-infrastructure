# world

**WORLD — persistent work-state infrastructure for AI and human work.**

Core hypothesis: AI can generate work, but current AI systems do not reliably
maintain a shared, verifiable state of work as that work moves between
different models, agents, humans, tools, and time.

WORLD is **not** an AI memory system. It is the canonical record of a
project's state — context, tasks, decisions, assumptions, evidence,
artifacts, provenance, actions, state changes, outstanding questions, and
handoff state — readable and writable by any authorized participant,
regardless of model or tool.

> **Status: docs-first.** We are deliberately not building the application
> yet. The thesis must survive `docs/thesis-challenge.md` and the handoff
> experiment before any architecture is designed.

## Start here

- `docs/hypothesis.md` — the thesis, precisely stated, with falsifiability criteria
- `docs/thesis-challenge.md` — the adversarial case: "why isn't WORLD just X?"
- `docs/state-model.md` — the canonical state ontology (draft v0.1)
- `docs/experiment-handoff.md` — the investment-research experiment that decides if we build
- `research/comparisons.md` — WORLD vs. databases, event sourcing, Git, RAG, agent memory, MCP, orchestration
- `docs/development-log.md` — running log of decisions

## Repository layout

```
/app      — prototype application (scaffolded only after the thesis survives)
/research  — competitive/technical research
/docs      — product hypothesis, architecture, experiments, development log
/tests     — evaluation and automated tests (built alongside /app)
```

## Rules

- No secrets in this repo: no API keys, passwords, tokens, or `.env` files.
- `world` is the single repository for the WORLD project. No new repos for it.

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
