# WORLD: persistent work-state infrastructure for AI agents

**The problem.** AI agents do work that outlives any single session:
a research task, an investigation, a build. When that work passes
to a successor (a new session, a different model, a different tool),
what crosses the boundary is usually a natural-language summary or
a raw transcript. Summaries are lossy in exactly the places that
matter: rationales, confidence levels, supersession history, and
binding constraints are the first things compressed away.
Transcripts preserve everything and index nothing: the governance
content sits inside chronological narrative and the successor must
re-derive it. Neither format can be checked. Nothing verifies that
a constraint still holds, that a decision was superseded, or that
the record was not edited after the fact.

**What WORLD does.** WORLD is a named, durable document that is
the canonical state of a piece of work, stored as one SQLite file.
Every proposed change is judged by declared invariants before it
is committed, and every verdict, COMMITTED or REJECTED, is
appended to a SHA-256 hash-chained log, so rejected work is
evidence rather than silence. The primitive provides optimistic
concurrency (`expected_version`), idempotent retries, checkpoints
with tamper-evident pins, and committed-only time travel (full
snapshots are stored per version, so reading an old version is
retrieval, not replay). Agent A finishes; Agent B loads the state
by name and continues, with the decisions, assumptions, evidence,
constraints, and revision history intact and auditable.

**How it differs from a summary or transcript handoff.** A summary
is prose written for a reader; a WORLD state is a record written
for a verifier. Decisions carry stable ids, lifecycle status, and
supersession links; assumptions carry confidence levels and a
fact-versus-assumption status; both are fields, not sentences, and
`save_state` rejects a state whose revision links do not resolve.
The record of how the state got here (including every rejected
attempt) is hash-chained and checkable with `verify()`. What the
experiments actually support about this difference is narrower
than the design intuition, and is stated with its limits in the
evidence section below.

**The research hypothesis** (stated as a hypothesis, not a
result): for work that moves between participants across sessions,
explicit structured work-state with stable labels preserves more
decision-relevant information across handoffs, and makes it more
auditable, than summaries or transcripts. Full statement,
sub-claims, and falsifiability conditions: `research/HYPOTHESIS.md`.

[![CI](https://github.com/RosarioM123/world-workstate-infrastructure/actions/workflows/ci.yml/badge.svg)](https://github.com/RosarioM123/world-workstate-infrastructure/actions/workflows/ci.yml)
![Python 3.11 | 3.12 | 3.13](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)

**Status:** v0.1.0 primitive. Working prototype, not deployed,
not production-ready, no external users. 409 tests in the suite
(count as of 2026-11-05; pytest on Python 3.11 to 3.13, ruff and
mypy in a separate lint job on Python 3.12). Research
documentation: `research/RESEARCH_OVERVIEW.md`. Reproduction:
`REPRODUCE.md`. Two-process demonstration: `demo/`.

## How it works

One named world is one SQLite file (`~/.world/<name>.db`, or
`$WORLD_DIR`). Handles are stateless views: every read hits the
database, so two processes sharing a name always agree.

- **The document is opaque JSON.** `update()` replaces it
  wholesale: no merging, no schema, no migration. What you put in
  is what comes out.
- **Every proposal gets a verdict.** Invariants (plain callables
  `(old_state, new_state)`) judge the transition; the verdict is
  appended to the hash chain either way. COMMITTED rows advance
  the state; REJECTED rows preserve the attempted document and
  the reason as evidence.
- **Concurrency.** Writers serialize on SQLite's write lock;
  `expected_version` gives optimistic concurrency, revalidated
  inside the write transaction so judgment and append are atomic
  (`ConflictError` on a stale read); `idempotency_key` makes
  committed retries return the original version instead of
  appending twice.
- **Checkpoints are pins, not copies.** A checkpoint names a
  version and stores the hash of that version's row (Prompt 3
  F3a); reading or resuming a checkpoint verifies the pin first.
  `resume()` restores a checkpoint's document as a *new* version:
  history is append-only and never rewritten.
- **Time travel is committed-only.** `state(version=N)` returns
  the committed snapshot at N; rejected proposals are auditable
  separately through `proposal(seq)`.
- **Integrity layers are optional and explicit.** `verify()`
  recomputes the whole chain (streaming, constant memory in chain
  length) and returns True only if every link matches. Signed
  tips (HMAC or Ed25519, keys held out of band) anchor the tip
  against rollback and full rewrite, which the unkeyed chain
  alone cannot detect. Per-field encryption with
  crypto-shredding redaction and Merkle inclusion proofs are
  available on the same log.
- **The handoff layer** (`src/world/handoff.py`) is the
  agent-facing API: a typed `AgentState` (objective, decisions,
  assumptions, evidence, open questions, next actions) stored
  under a reserved document key, with referential-integrity
  validation at save time, a computed `revision_chain` view of
  one decision's history, and a `project_state` reading view
  that compacts superseded items without ever presenting them
  as current.

Full diagram, component inventory, data flow, and trust
boundaries: `docs/architecture.md` (editable source:
`docs/architecture.mmd`).

## What has been demonstrated

Every claim below carries a status. The full evidence register,
mapping each claim to its source artifact, is
`research/EVIDENCE_REGISTER.md`; the classification table in
`research/RESEARCH_OVERVIEW.md` is the detailed version.

**The mechanism (software behavior under tested conditions).**

- The commit protocol is model-checked exhaustively over bounded
  configurations: 1,220,255 explored states, properties P1 to P6
  holding throughout, with a mutation test proving the checker
  can fail. **VERIFIED** (`spec/model_check.py`,
  `docs/spec/protocol-verification.md`).
- The suite is 409 tests passing (2026-11-05), covering the
  protocol, invariant judging, tamper fuzzing (500 of 500 seeded
  mutations detected, DOCUMENTED), Hypothesis stateful testing
  against a reference model (DOCUMENTED), crash injection, and an
  independent C# chain verifier sharing no code with the Python
  one. **VERIFIED** as behavior under tested conditions. Test
  counts demonstrate software behavior; they are not evidence
  about AI agent reliability.
- A preregistered scripted-agent experiment lost updates in 33
  of 50 unprotected trials and 0 of 50 with `expected_version`
  plus retry. **DOCUMENTED** (`experiments/lost-update/`). The
  agents were scripted, not LLMs.

**The handoff question (the actual research claim).**

- Experiments #001 and #002 (blind-graded, predeclared answer
  keys, independent evaluator): the structured-state continuation
  preserved decision governance best in all three runs, narrowly;
  it also **failed revision history in both #002 runs** (2 of 5),
  and a strong summary came within 0.36 of it in the replication.
  n=1 per run, one model family: exploratory, not statistically
  significant. **DOCUMENTED, preliminary.**
- Experiment #003 (preregistered, 8 tasks, 72 continuations,
  blind grading, information parity gate): the one consistent
  structured-state advantage was assumption retention (A 0.721
  vs summary 0.500 vs transcript 0.488), and the mechanism was
  specific: baselines recovered assumption substance but lost
  confidence level or fact-versus-assumption status. Decisions
  slightly favored the baselines (0.948 vs 0.979), provenance
  tied, revision history tied at ceiling (1.000 in all
  conditions, so #003 cannot distinguish the representations on
  the metric #002 failed), unverifiable additions appeared only
  under the structured condition (12 vs 0 and 0), and the
  structured bundles cost 2.7x to 3.3x the words.
  **PRELIMINARY**, single model family. Scope caveat: #003's
  structured condition was hand-authored Markdown built to
  `docs/state-model.md`; it never exercised the `World` class.
- The Prompt 3 revalidation (2026-11-04) was the first run
  through the shipped code path (new handoff schema,
  `save_state`/`load_state`, tasks R1, R2, C1, n=3 per cell,
  blind graded): preservation at or near the #003 structured
  level, with no revision-history regression from the projection
  view. **PRELIMINARY** (`experiments/prompt3/revalidation/`).

**What remains unproven.** Any general claim that WORLD improves
AI agent reliability (**NEEDS VALIDATION**); cross-model
handoffs; human auditability in practice; whether revision
history is preserved well or badly (the #002 failure and the
#003 ceiling conflict; the honest status is unresolved, and the
discriminating experiment, harder chains with no parity gate on
revision elements plus human grading, has not been run); and any
real-world adoption: WORLD has no external users and no
deployments, and the independent reproduction protocol
(`experiments/prompt6/VALIDATION_PROTOCOL.md`) is written but
**PENDING**, with zero completed external records. Full list:
`research/LIMITATIONS.md`.

## Install

Not on PyPI yet. Install from source. The core has zero
dependencies (stdlib only).

Naming note: the distribution is named `world-engine` (that is
what `pip show` will report), the import package is `world`, and
two legacy console scripts (`world-import`, `world-server`) run
the legacy `world_engine` demo described at the end of this file.
The `world` command is the primitive's CLI.

```bash
git clone https://github.com/RosarioM123/world-workstate-infrastructure.git
cd world-workstate-infrastructure
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .            # the `world` primitive + `world` CLI
pip install -e ".[server]"  # optional: `world serve` HTTP API
pip install -e ".[test]"    # optional: full test suite (server + property tests)

python examples/quickstart.py   # minimal example, self-contained
python -m pytest tests/ -q      # without the extras, server tests skip cleanly
world --help
```

## Quickstart

Ten lines, under five minutes. Zero dependencies, stdlib only.

```python
from world import World

work = World("my-project")                    # create (or load, same call)
work.update({"task": "draft memo", "done": False})
work.checkpoint("end-of-day")                 # pin this version
print(work.state())                           # {'task': 'draft memo', 'done': False}
print(work.verify())                          # True, hash chain intact
```

The world persists as `~/.world/my-project.db` (or under
`$WORLD_DIR` if set); nothing else is needed to reopen it later,
from any process.

## The handoff

The scenario WORLD exists for. Two processes, as separate as two
agents can be: no shared memory, no shared session. A runnable
version of exactly this flow is in `demo/` (`demo/agent_a.py`,
then `demo/agent_b.py`).

**Agent A** works, records, checkpoints. Its process then exits:

```python
from world import World, InvariantViolation
from world.invariants import no_negative

work = World("research-acme", invariants=[no_negative("budget")])
work.update({
    "decision": "source 18A yield data from SEC filings only",
    "assumptions": ["yields stabilize by Q3"],
    "open_questions": ["foundry breakeven date?"],
    "budget": 4000,
}, actor="agent-a", note="phase 1 findings")

try:
    work.update({"budget": -500}, actor="agent-a")   # judged
except InvariantViolation as e:
    print(e.seq, e.reason)                           # 2  no_negative: budget = -500
work.state()["budget"]                               # 4000, untouched

work.checkpoint("phase-1-done")
# Agent A's process exits here. Nothing else persists.
```

**Agent B** starts later, new interpreter, new session, and
continues:

```python
from world import World

work = World("research-acme")          # loads A's state from disk
print(work.version)                    # 1, the work so far, numbered
print(work.state()["decision"])        # source 18A yield data from SEC filings only

state = work.state()
state["status"] = "phase 2 started"
work.update(state, actor="agent-b", note="picking up phase 2")

for h in work.history():               # the verdict log, how we got here
    print(h["seq"], h["status"], h["actor"], "-", h["note"])
# 1 COMMITTED agent-a - phase 1 findings
# 2 REJECTED agent-a - REJECTED: no_negative: budget = -500
# 3 COMMITTED agent-b - picking up phase 2
```

One honest detail: invariants are code, declared per handle.
Agent B judges with its own rules (or none). If every remote
writer must face the same rules, run `world serve`: the server
declares invariants once and judges all writers equally.

### The typed handoff API

The agent-facing layer on the primitive, stdlib only. An agent
writes its work state; a fresh agent recovers it from the world
name alone. The basic types (`AgentState`, `Decision`,
`Evidence`, `load_state`, `save_state`) import from `world`; the
full Prompt 3 surface (`Assumption`, `project_state`,
`revision_chain`, `validate_state`) imports from `world.handoff`.

```python
from world import AgentState, Decision, Evidence, load_state, save_state
from world.handoff import Assumption, revision_chain

state = AgentState(
    objective="Draft the Q3 foundry memo",
    decisions=[Decision("Source yields from SEC filings only",
                        rationale="Filings give quarterly granularity",
                        id="D1", evidence_ids=["E1"])],
    assumptions=[Assumption("Yields stabilize by Q3",
                            id="A1", confidence="medium")],
    evidence=[Evidence("Defect density improved 2x QoQ",
                       source="10-Q Q2 2026", id="E1")],
    open_questions=["Foundry breakeven date?"],
    next_actions=["Build the DCF", "Run the credit stress case"],
)
save_state("research-acme", state, actor="agent-a")  # returns version seq

# later, a fresh session / process / model:
recovered = load_state("research-acme")   # the identical AgentState
chain = revision_chain("research-acme", "D1")  # D1's revision history
```

Decisions carry `id`, `status` (proposed, accepted, superseded,
reversed), `supersedes`, and `evidence_ids`; assumptions carry
`id`, `confidence` (low, medium, high), `status`, and
`validated_by`. `save_state` validates that the links resolve
before anything is proposed, and stores under the reserved
`"handoff"` key (other document keys are preserved); every save
is a judged, hash-chained version. `load_state` accepts a world
name or a `World`, plus `version=` / `checkpoint=` for historical
handoffs, and raises `KeyError` if nothing was ever saved.
Round-trip fidelity is pinned by `tests/test_handoff.py`,
including a two-interpreter test proving no in-memory state
leaks.

## API

Core operations. Full reference: `src/world/core.py` (typed,
`py.typed` shipped). Design rationale:
`docs/adr/0008-world-primitive.md`.

| Operation  | Python                                                        | CLI                                       |
|------------|---------------------------------------------------------------|-------------------------------------------|
| create     | `World("my-project")`                                         | `world init my-project`                   |
| update     | `work.update(doc, actor=, note=, expected_version=, idempotency_key=)` returns seq | `world update my-project --file s.json` |
| batch update | `work.update_many(docs)` returns seqs, one transaction | `world update-many my-project --file s.json` |
| checkpoint | `work.checkpoint("v1")` returns seq; the pin stores the row hash and is verified on read and resume | `world checkpoint my-project v1` |
| load       | `work.state()` / `state(version=)` / `state(checkpoint=)` (committed versions only) | `world state my-project` |
| read       | `work.read()` returns `(state, version)` atomically | `world read my-project` |
| resume     | `work.resume("v1")` returns seq (checkpoint restored as a new version) | `world resume my-project v1` |
| blame      | `work.blame("budget.total", version=)` returns row that last changed the field (committed only) | `world blame my-project budget.total` |
| selective disclosure | `work.merkle_root()`, `work.inclusion_proof(seq)`, `World.verify_inclusion(proof)` (DB-free) | (no CLI) |

Reads: `history(limit=)` (verdict log, oldest first),
`proposal(seq)` (audit one proposal by seq, any status),
`verify()` (hash-chain check, returns a bool), `version`,
`checkpoints()`, `name`, `path`.
Optional integrity and confidentiality layers: `sign_tip` /
`verify_tip` (HMAC), `sign_tip_ed25519` / `verify_tip_ed25519`
and `rotate_ed25519` (Ed25519, vendored pure Python),
`encrypt_fields` / `decrypt_fields` / `redact` (per-field
encryption and crypto-shredding redaction;
`src/world/fieldcrypto.py`).
Errors: `InvariantViolation` (carries `seq` and `reason` of the
recorded rejection), `ConflictError`, `KeyError` (unknown
version/checkpoint), `ValueError` (bad name, bad JSON, duplicate
checkpoint).

### Invariants

An invariant is `(old_state, new_state) -> None`; raise
`InvariantViolation` to reject. Shipped helpers in
`world.invariants`: `no_negative(*paths)`,
`finite_numbers(*paths)`, `require_keys(*paths)`,
`respect_locks()`, `monotonic(*paths, strict=False)`,
`immutable_fields(*paths)`, `type_stable(*paths)`, plus the
`all_of(*invs)` conjunction combinator. Path patterns are
dot-separated with `*` wildcards (`"totals.*"`,
`"tasks.0.status"`). Anything else is a plain function you write.
Non-violation exceptions propagate uncaught and are *not*
recorded: a crashing judge is a bug, not a verdict.

### Performance

Measured 2026-10-15 with `python tools/bench_world.py` (10,000
versions, Linux x86_64, Python 3.12.3); full tables in
`docs/benchmarks/world-primitive.md`:

| operation | throughput |
|---|---:|
| `update` (invariant judged) | 1,339 ops/s |
| `update` (`expected_version`) | 692 ops/s |
| `state()` reads | 3,794 ops/s |
| `verify()` full chain | 200,081 rows/s |
| `update_many` (batches of 500) | 54,975 ops/s |

These are dated records from one machine, not guarantees; re-run
before quoting. For post-Prompt-3 measurements (including the
streaming `verify()` memory result: peak-RSS delta 19.7 MB to
0.8 MB on a 20,000-version chain), see
`experiments/prompt3/BENCHMARKS.md` and the re-runnable
`experiments/prompt3/bench.py`. Under concurrent writers,
throughput plateaus near 810 ops/s past 8 threads and the p99
tail degrades sharply, while correctness holds
(`docs/benchmarks/contention.md`).

### CLI and HTTP

The `world` command covers every operation: `init`, `update`,
`update-many`, `state`, `read`, `checkpoint`, `checkpoints`,
`resume`, `history`, `proposal`, `verify`, `diff`, `blame`,
`export`, `import`, `import-transcript`, `serve`. `world serve
my-project` (needs `pip install -e ".[server]"`) exposes the same
model over HTTP (`GET /v1/state`, `POST /v1/update`,
`/v1/checkpoint`, `/v1/resume`, `GET /v1/history`,
`/v1/checkpoints`, `/v1/verify`). Write routes are gated by an
API key (`WORLD_API_KEY` maps to the `X-API-Key` header) and
**fail closed**: with no key configured, writes return 401
unless `--allow-unauthenticated` is passed explicitly for local
development. Read routes are open in every mode; per-IP write
rate limiting applies. Declare invariants once via
`--invariants mymod:rules`. `world import-transcript` folds a
chat transcript into `state["transcript"]`, idempotent on the
transcript text.

## Correctness contract

The state model above is a contract the test suite enforces, not
just documentation:

- **Exactly-once proposal semantics.** Each proposal is judged,
  then appended exactly once. `expected_version` gives
  optimistic concurrency and `idempotency_key` dedupes committed
  retries while rejections are always recorded. The protocol is
  model-checked (P1 to P6, above).
- **The invariant engine is the correctness boundary.** Nothing
  is persisted until the declared invariants pass. NaN,
  infinities, and non-JSON values are rejected before anything
  is written.
- **Tamper-evident audit trail.** Every version is SHA-256
  hash-chained over prev-hash, seq, timestamp, actor, note,
  status, and the canonical state. `verify()` recomputes every
  link and returns False if any row was altered; rejected
  proposals are chained too, so the trail records what was
  blocked and why.
- **Append-only history.** Checkpoints restore as new versions,
  never rewrites; any participant reading the log arrives at the
  same committed snapshots.

Boundary, stated plainly: tamper-evident, not immutable, and the
database cannot name the rule set that judged a historical
version (see Current limitations). The 409-test suite exercises
each guarantee above, and the commit protocol behind them is
model-checked separately (`docs/spec/protocol-verification.md`).

## Current limitations

- **Tamper-evident, not immutable.** The hash chain detects
  partial edits; anyone holding the DB file can rewrite the
  whole chain consistently. Optional signed tips anchor the tip
  only if a verifier holds key material out of band. No
  consensus, no third-party witnessing. `docs/SECURITY.md`
  lists which attacks are and are not detected, including
  tested undetected cases (tail truncation, full rewrite,
  forks).
- **Two tables sit outside the chain.** Checkpoint pins (F3a)
  detect a repoint unless the attacker rewrites the pin as
  well; `verify()` does not cover the checkpoints table. The
  idempotency table is uncovered entirely: deleting a key row
  lets a retry commit twice while the chain verifies. Binding
  the keys into the row hash (F3b) would break verification of
  existing databases and is an open, undecided item.
- **Invariants are code, not data.** The database cannot name
  the rule set that judged a historical version. Two handles on
  one world can judge by different rules; `world serve` is the
  uniform-enforcement point for remote writers.
- **No per-actor identity.** `actor` is self-asserted. The
  API-key gate authenticates the deployment, not the writer.
  No RBAC. (A server may pin one fixed actor label, F4; that is
  a narrowing, not identity.)
- **Single-writer serialization.** Appends serialize on
  SQLite's write lock by design; `expected_version` is
  optimistic concurrency, not a transaction across documents.
  Tail latency degrades sharply under many concurrent writers
  (see Performance).
- **`verify()` is O(n) in time.** It streams, so memory is
  constant in chain length (F5); the 1.06M-row soak predates
  the streaming change (75,921 rows/s and 659 MB RSS at the
  time) and has not been re-run at that scale.
- **Local-first.** One SQLite file per world. No replication,
  no sync protocol: multi-machine sharing is out of scope for
  the primitive.
- **No external validation yet.** No deployments, no external
  users, the handoff evidence is small-n on one model family,
  and revision history is unresolved between #002 and #003.
  See `research/LIMITATIONS.md` for the complete list.

## Roadmap

- A discriminating revision-history experiment: harder chains,
  no parity gate on revision elements, human grading of the
  preserved #003 subset (the open question from #002 and #003)
- The F3b decision: bind idempotency keys into the row hash, or
  document the limit permanently
- Persisted invariant registry: the DB names the rules that
  judged each version (closes the code-not-data gap)
- Cross-model handoff runs, when a model API credential exists
- External validation: run the protocol in
  `experiments/prompt6/VALIDATION_PROTOCOL.md` with independent
  reviewers
- Retire or merge the legacy `world_engine` package (below)
- Sync protocol design: only if the evidence and real adoption
  demand it; explicitly not started

## Research

Research home: `research/` (overview, hypothesis, limitations,
related work, paper draft at `research/PAPER.md`, evidence
register at `research/EVIDENCE_REGISTER.md`). All three handoff
experiments hand the same Agent A research output to a successor
Agent B in three conditions (structured WORLD state, conventional
summary, raw transcript or journal) and grade the continuations
blind. Every quantitative claim in the research documents
carries one of five evidence statuses (VERIFIED,
EXPERIMENTALLY OBSERVED, DOCUMENTED, PRELIMINARY, NEEDS
VALIDATION), defined in `research/RESEARCH_OVERVIEW.md` and
mapped claim by claim in the evidence register.

- **#001** (2026-09-17, Block Inc.): WORLD state won on
  governance: 5/5 decisions with rationales intact, 7/7
  assumptions with confidence levels, zero errors. Narrative
  formats preserved facts but lost decisions-as-decisions. n=1.
  (`docs/experiment-001-results.md`)
- **#002** (2026-09-17 to 23, Intel plus Disney replication):
  WORLD-state continuation preserved decision governance best
  in both runs (Intel 3.92 vs 3.58 vs 3.33; Disney 4.45 vs 4.09
  vs 2.82, reference means); the advantage is narrow, the
  summary came within 0.36 in the replication, and the WORLD
  continuation failed on revision history in both runs.
  (`docs/experiment-002/results.md`)
- **#003** (2026-11-03, preregistered): assumption retention
  was the one consistent advantage (0.721 vs 0.500 vs 0.488);
  revision history tied at ceiling; decisions slightly favored
  the baselines; structured bundles cost 2.7x to 3.3x the
  words. PRELIMINARY, single model family; condition A was
  hand-authored Markdown and never exercised the shipped code.
  (`experiments/experiment-003/REPORT.md`)
- **Prompt 3 revalidation** (2026-11-04): the first handoff
  runs through the shipped code path, on tasks R1, R2, C1:
  preservation at or near the #003 structured level, no
  revision-history regression from the projection view.
  PRELIMINARY. (`experiments/prompt3/revalidation/RESULTS.md`)

Verification work behind the primitive (all with artifacts in
the repo): protocol model checking (1,220,255 states, P1 to
P6); Hypothesis stateful testing against a reference model;
linearizability checking; deterministic simulation; verifier
fuzzing and a red-team suite with tested limits
(`docs/SECURITY.md`); crash-consistency fault injection (15 of
15 recorded mid-transaction kills recovered, plus 39 further
rounds with zero durability violations in 2026-11-02 checks);
a 1.06M-row soak (`experiments/soak/`); and an independent C#
chain verifier sharing no code with the Python implementation
(`tools/ChainVerifyWorld/`).

Standing rule: report the ugly number. A stated weakness with a
results file behind it beats a suspiciously perfect run with
none.

### Reproduction

```bash
pip install -e ".[test]"
python -m pytest tests/ -q                       # full suite (409 tests on the current tree)
python3 spec/model_check.py                      # model checker + mutation test
python tools/bench_world.py                      # primitive benchmarks
python tools/bench_contention.py                 # contention profile
python demo/agent_a.py && python demo/agent_b.py # two-process handoff demo
```

The complete reproduction workflow, with expected outputs, the
clean-install verification, and an explicit list of what cannot
be reproduced from this repository (the agent experiment runs
themselves), is `REPRODUCE.md`. Experiment protocols were
predeclared (`docs/experiment-002/protocol.md`,
`experiments/lost-update/PREREGISTRATION.md`,
`experiments/experiment-003/protocol.md`); raw outputs, answer
keys, and grading records are kept in `docs/experiment-002/` and
`experiments/`.

## Legacy: the `world_engine` demo

The repo also contains the original prototype this primitive
was distilled from: a deterministic constraint-checked ledger
for a synthetic logistics domain, with a FastAPI backend, a
React landing page, an offline client SDK (`src/world_sdk`,
`docs/SDK.md`), and a deterministic transcript importer. It is
**not** the product direction; the `world` primitive above is.
Its hardening work (hash-chained verdicts, atomic writes,
idempotency, replay, locks, API-key gate, rate limiting) is what
the primitive was built from; note that deterministic replay is
a legacy-engine feature, not a primitive feature (the primitive
stores full snapshots instead).

Pointers: `src/world_engine/` (kernel), `src/world_sdk/`,
`examples/synthetic-logistics-demo/`, `tools/bench.py`,
`docs/adr/`. The primitive's own design rationale is
`docs/adr/0008-world-primitive.md`.

## Repository layout

```
/src/world            the primitive (this README): core, invariants,
                      CLI, HTTP server (opt-in), handoff layer,
                      signing, field crypto, transcript producer
/src/world_engine     legacy demo kernel (see above)
/src/world_sdk        legacy offline client SDK (docs/SDK.md)
/tests                409 tests: primitive, kernel, SDK, API, security
/spec                 protocol model checker, TLA+ transcription,
                      linearizability and deterministic-simulation checkers
/research             research overview, hypothesis, limitations, related
                      work, paper draft, evidence register
/docs/adr             architecture decision records
/docs                 architecture, thesis, state model, experiments, specs
/experiments          handoff and systems experiment harnesses + results
/demo                 two-process handoff demonstration (Prompt 6)
/REPRODUCE.md         reproduction workflow with verified commands
```

## Rules

- No secrets in this repo: no API keys, passwords, tokens, or
  `.env` files.
- This repo is the single home of the WORLD project. No new
  repos for it.
