# WORLD

**Deterministic append-only state ledger with hash-chain verification for AI agent work-state.**

[![CI](https://github.com/RosarioM123/world-workstate-infrastructure/actions/workflows/ci.yml/badge.svg)](https://github.com/RosarioM123/world-workstate-infrastructure/actions/workflows/ci.yml)
![Python 3.11 | 3.12 | 3.13](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)

AI can generate work. What it cannot do reliably is maintain a shared,
verifiable record of that work as it moves between models, agents, humans,
tools, and time. WORLD is that record: a deterministic state kernel where
agents submit *intents*, a constraint engine returns `COMMITTED` or
`REJECTED`, and every attempt — legal or rogue — is appended to a SHA-256
hash-chained ledger.

**Status: working prototype, not deployed.** Deterministic engine,
FastAPI backend, React landing page, full suite green in CI. Write
endpoints require `X-API-Key` when `WORLD_API_KEY` is set and are
per-IP rate-limited; the ledger is tamper-evident
(via `verify_chain()`) rather than immutable. Sample data in the demo is
labeled as sample. Hosting is deferred — `render.yaml` (with a persistent
disk for the ledger) and `/health` keep it deploy-ready.

## The `world` primitive (v0.2)

The general-purpose successor to the demo engine: a named, durable,
versioned JSON document where every state change is judged by invariants
and every verdict — COMMITTED *or* REJECTED — is hash-chained evidence.

### 60-second quickstart

Five operations. Zero dependencies (stdlib only). No agent framework, no
UI, no vector DB, no LLM calls — state lives in SQLite, so a fresh
process loads it with `World(name)`.

| Operation  | Python                          | CLI                                     |
|------------|---------------------------------|-----------------------------------------|
| create     | `World("my-project")`           | `world init my-project`                 |
| update     | `work.update({...})`            | `world update my-project --file s.json` |
| checkpoint | `work.checkpoint("v1")`         | `world checkpoint my-project v1`        |
| load       | `World("my-project").state()`   | `world state my-project`                |
| resume     | `work.resume("v1")`             | `world resume my-project v1`            |

```bash
pip install -e .   # core: no dependencies. Add [server] for `world serve`, [test] for the suite
world init my-project
echo '{"balance": 100}' > s.json
world update my-project --file s.json --actor alice --note "seed"
world checkpoint my-project v1
world verify my-project   # ok
```

```python
from world import World, InvariantViolation
from world.invariants import no_negative

work = World("my-project", invariants=[no_negative("balance")])  # create (or load)
work.update({"balance": 100}, actor="alice")          # -> 1 (COMMITTED)
try:
    work.update({"balance": -5}, actor="bob")         # judged: REJECTED, recorded, raised
except InvariantViolation as e:
    print(e.seq, e.reason)                            # 2  no_negative: balance = -5
work.state()                                          # {"balance": 100} — untouched
work.checkpoint("v1")                                 # pin version 1
work.resume("v1")                                     # restore appends a new version
work.history()                                        # verdict log, rejections included
print(work.verify())                                  # True — hash chain intact
```

`world serve my-project` (needs `pip install -e ".[server]"`) exposes the same
model over HTTP (`POST /v1/update`,
`GET /v1/state`, checkpoints, resume, history, verify) with the API-key gate
and per-IP rate limiting; declare invariants once via
`--invariants mymod:rules` so every remote writer is judged equally.
`world import-transcript` folds a chat transcript into the document
(idempotent on the transcript text). See `docs/adr/0008-world-primitive.md`
for the design rationale.

## Demo

<!-- TODO: drop a ~30s screen recording here (docs/demo.gif): the /demo
     dashboard, one ALLOCATE intent committing, then the rogue-attack
     simulation getting REJECTED. Record with any screen capture tool,
     keep it under 5 MB, and replace this comment with:
     ![WORLD demo](docs/demo.gif) -->

## Quickstart

Five lines, zero setup beyond Python:

```bash
pip install -e ".[test]"
python - <<'EOF'
from world_engine.core import engine
engine.init_db()
r = engine.execute_deterministic_transition(
    engine.IntentTransaction("node_rotterdam_hub", "ALLOCATE", -50.0, 0.0))
print(r["status"], engine.verify_chain())  # COMMITTED (True, None)
EOF
```

The full tour (test suite, API, dashboard) is right below.

```bash
pip install -e ".[test]"

# verify the ledger's hash chain (no server needed)
python - <<'EOF'
from world_engine.core import engine
engine.init_db()
print(engine.verify_chain())  # (True, None) — or (False, bad_id)
EOF

# run the API + dashboard
uvicorn app:app
# http://127.0.0.1:8000/demo    interactive dashboard
# http://127.0.0.1:8000/api/v1/state  materialized state + recent ledger
```

**GitHub Codespaces** (zero local setup): Code → Codespaces → Create
codespace on `main`, wait ~2 minutes, then open forwarded port **8000**
(globe icon) in the Ports panel.

## Transcript importer

Feed a chat transcript in, get WORLD state out. The importer extracts
decisions, assumptions, open questions, constraints, and notes with a
deterministic parser (no network, no LLM, stdlib only) and commits one
intent per item to the ledger. Re-imports are idempotent, and each import
is atomic: a crash mid-import rolls back to zero items (no partial
imports, no ledger row without its dedup record), and concurrent
importers serialize on the write lock instead of duplicating rows.

```bash
python import_transcript.py notes.md --dry-run   # preview, writes nothing
python import_transcript.py notes.md             # commit to the ledger
cat notes.md | python import_transcript.py        # read from stdin
```

## How it works

```mermaid
flowchart LR
    A[Agent / human / CLI] -->|intent| B[FastAPI\napp.py]
    B --> C[Constraint engine\nengine.py]
    C -->|COMMITTED / REJECTED| D[(SQLite ledger\nSHA-256 hash-chained)]
    D --> F[Materialized state]
    F --> G[/demo dashboard]
    F --> H[/api/v1/state]
```

(The Rotterdam weather/port flow that used to sit beside the kernel now
lives in `examples/synthetic-logistics-demo/` as a synthetic stress-test
domain, not the product demo.)

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
curl -X POST 127.0.0.1:8000/api/v1/rogue-attack
# every verdict: REJECTED
```

(The unversioned `/api/*` routes still work as deprecated aliases.)

**API quickstart:**

```bash
curl 127.0.0.1:8000/api/v1/state

curl -X POST 127.0.0.1:8000/api/v1/intent \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"node_rotterdam_hub","action":"ALLOCATE","delta_capacity":-50.0,"delta_cash":0.0}'

# Register a second node, then page through the ledger:
curl -X POST 127.0.0.1:8000/api/v1/entities \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"node_singapore_hub","capacity":2000.0,"liquidity":100000.0}'

curl "127.0.0.1:8000/api/v1/ledger?limit=10"
# pass next_cursor back as ?cursor= to keep walking toward older rows

# Lock a node — intents against it are REJECTED until unlocked
# (the flip is a ledger-logged LOCK_ENTITY row, so it replays too):
curl -X POST 127.0.0.1:8000/api/v1/entities/node_singapore_hub/lock
curl -X POST 127.0.0.1:8000/api/v1/entities/node_singapore_hub/unlock

# Engine-side deterministic replay: rebuild state from the ledger and
# confirm it matches the live tables (read-only):
curl 127.0.0.1:8000/api/v1/replay
```

**Exposing a public demo:** set `WORLD_API_KEY` to a long random value —
the write endpoints then require it as the `X-API-Key` header, and
per-IP rate limits apply (tune with `WORLD_RATE_LIMIT_*_PER_MIN`, disable
with `WORLD_RATE_LIMIT_ENABLED=0`). Point `WORLD_DB_PATH` at persistent
storage so redeploys don't wipe the ledger (`render.yaml` wires this to
a Render disk).

Every response carries an `X-Request-ID` header, and every failure
returns the same JSON error envelope:
`{"error": {"code": "...", "message": "...", "request_id": "..."}}`.

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

**Replay the ledger** — rebuild materialized state from history, from the
genesis seed forward, and compare it against the live tables:

```bash
python - <<'EOF'
import engine
report = engine.replay_ledger()
print(report["chain_ok"], report["divergences"])  # True, [] on a healthy node
# engine.replay_ledger(apply=True)  # repair a corrupted state from the ledger
EOF
```

`GET /api/v1/replay` exposes the verify-only report on a running server.
Repair (`apply=True`) stays an operator-level engine call: it rewrites the
`entities` table and is never an HTTP endpoint.

## Client SDK (local index)

Work Item 1 of the buildout: an offline-first, stdlib-only Python client
(`src/world_sdk/`, 41 tests in `tests/test_sdk.py`). `WorldClient.intent()`
validates intents locally against the same constraint policy as the server
(imported, not copied) and appends to a client-owned ledger in the same
entry format, so client and server rows stay interoperable. A sqlite3
sidecar holds the disposable indexes: block height to embedding vector
(bring-your-own vectors, pure-Python cosine search) and block height to
block time, which powers client-side time-travel reads
(`state_at_time(T)` resolves locally, then replays the ledger). The ledger
remains the sole system of record; verification stays deterministic and
LLM-free. Full doc: `docs/SDK.md`.

```python
from world_sdk import WorldClient
client = WorldClient()
client.intent("node_rotterdam_hub", "ALLOCATE", deltas={"capacity": -50.0})
print(client.verify())  # (True, None)
```

## Tests

The test suite covers the hardening guarantees: invalid deltas rejected, unknown
entities logged as rejected, concurrent writes serialized (16 threads race
to over-drain one node; exactly one commits), full hash-chain verification with
tamper pinpointing (including hypothesis property tests over random
ledgers and random single-field tampers), seed-constant consistency,
and FastAPI integration tests for the v1 routes. CI runs the suite with a
pytest-cov gate (85% minimum) on Python 3.11, 3.12, and 3.13, plus ruff,
mypy, and the frontend production build for every push and pull request
to `main`.

```bash
python -m pytest tests/ -q --cov
# synthetic demo domain tests (kept with the demo, not the product suite)
python -m pytest examples/synthetic-logistics-demo/tests -q
```

## Benchmarks

Measured 2026-09-21 on a shared Linux dev VM (`python tools/bench.py`
with 100,000 intents). Your numbers will differ; the shape will not.

| operation | rows | total | per-op | throughput |
| --- | ---: | ---: | ---: | ---: |
| append (`execute_deterministic_transition`) | 100,000 | 57.8s | 0.58 ms/intent | 1,730 intents/s |
| `verify_chain` | 100,000 | 0.57s | 0.006 ms/row | 176,195 rows/s |

Appends serialize on the single SQLite write lock (by design, see
`docs/adr/0003-single-transaction-check-then-act.md`); verification is
a pure sequential hash walk, so it scales linearly with ledger size.

Scope of these numbers, stated plainly: single-writer appends on one
shared VM, no network, no concurrent readers, no production hardware.
They measure the kernel's raw throughput, not a deployed system's
latency. The continuity claim (can a fresh session pick up work from
the ledger alone) is tested separately by the handoff experiment in
`experiments/`; its results will ship in this README verbatim, pass or
fail.

## Repository layout

```
/src/world_engine      — the packaged kernel (pip install -e .)
  /core/engine.py      — deterministic state kernel (hash-chained SQLite
                         ledger, verify_chain(), constraint policy)
  /ingestion/transcript.py — deterministic transcript importer
                         (CLI: world-import)
/src/world_sdk          — offline-first client SDK (Work Item 1): WorldClient
                         with local intent validation, client-owned ledger
                         in the server entry format, sqlite3 sidecar for
                         the embedding index and the timestamp index
                         (docs/SDK.md)
/api/main.py           — FastAPI backend (serves the React build + /demo
                         dashboard); uvicorn world_engine.api.main:app
  /api/v1.py             — versioned routes (/api/v1/*; /api/* are
                         deprecated aliases)
/api/middleware.py      — request IDs, structured access logging, the
                         uniform JSON error envelope
/engine.py, /app.py,
/import_transcript.py  — thin shims: `uvicorn app:app`, `python -m engine`,
                         `python import_transcript.py` all still work unchanged
/examples/synthetic-logistics-demo — the Rotterdam weather/port flow, moved
                         out of the product: a synthetic domain that
                         stress-tests the constraint engine. Not the
                         product demo.
/frontend    — landing page source: React 18 + Sass (Vite)
               → builds into /static/site (committed, served by app.py)
/static      — built landing page (static/site/) + /demo dashboard
/tests       — regression tests for the kernel
/tools       — export_ledger.py + ChainVerify (independent C# chain verifier)
                         + bench.py (ledger append/verify benchmarks)
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
- **Interim auth, not full RBAC.** When `WORLD_API_KEY` is set, the
  write endpoints (`POST /intent`, `/entities`, `/rogue-attack`) require
  it as the `X-API-Key` header and are per-IP rate-limited; reads stay
  open. There is still no per-actor identity — `actor` remains
  self-asserted (see `docs/adr/0006-auth-rbac-shape.md`).
- **The Rotterdam weather/port flow is a synthetic stress-test domain,**
  not the product demo (`examples/synthetic-logistics-demo/`). Wind speed
  derating port capacity is a fixed, auditable rule invented to exercise
  the constraint engine, not a validated operations model.
- **Two API decisions are open by design, not oversight.** The OBSERVE
  intent schema (freeform note-only vs structured fields) and the
  time-travel canonical key (block height vs timestamp) are unresolved;
  timestamp resolution currently lives client-side in the SDK so the
  server stays stdlib-pure.

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

- `docs/VISION.md` — the one-page thesis: the one secret, the three
  layers, the build order
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
