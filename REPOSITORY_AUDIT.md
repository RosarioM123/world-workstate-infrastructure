# WORLD Repository Audit (Prompt 1)

**Date:** 2026-11-25 (Mission Day 14, Prompt 1, Phase 1)
**Branch:** `mission/day-14` (from Day 13 tip `f88dd0c`)
**Auditor:** daily mission run. No code was modified by this audit; the only
changes in this run are the four audit deliverables themselves.
**Supersedes nothing; reconciles:** `experiments/mission-90/AUDIT.md`
(Day 1 audit, 2026-11-12) and `experiments/mission-90/LOG.md` (Days 1 to 13).

**Evidence classes:** VERIFIED (traced code path or live run), DOCUMENTED
(docs and code agree it is a limit), PRELIMINARY (small-n experiment),
NEEDS VALIDATION (needs a test or external check to confirm).
**Status words:** CLOSED (fixed on a mission day, fix SHA cited) or OPEN
(re-verified against the current tree on 2026-11-25, current file path cited).

## 1. Reproducible baseline (measured 2026-11-25)

| Check | Result |
|---|---|
| Full suite, CI command (`pytest tests/ -q --cov --cov-report=term-missing`) | 500 passed, 0 failed, 1 warning, 102.69 s, Python 3.12.3 |
| Coverage over the expanded scope | 95.16% total (CI gate 85%) |
| Test files / test functions | 51 files, 453 `def test` functions |
| Python files under `src/`, `tests/`, `tools/`, `demo/`, `examples/`, `spec/`, `docs/` | 94 |
| Model checker (`spec/model_check.py`) | 1,220,255 states, P1 to P6 hold (Day 1 measurement, not re-run today) |
| GitHub open issues/PRs (read-only) | NOT CHECKED today: `gh` CLI is unauthenticated in this VM. Day 13 reported 1 open issue (#4) and 12 open Dependabot PRs plus #29 and #30. No GitHub state is claimed for today. |
| Working tree at audit start | Clean, on `mission/day-13`, tip `f88dd0c` |

Day 1 baseline was 409 passed; Days 2 to 13 added 91 tests and closed 33 of
the 56 Day 1 findings. The suite is green and the tree is clean.

## 2. Reconciliation: core primitive (`src/world/`)

| ID | Severity | Day 1 finding | Status |
|---|---|---|---|
| C-1 | High | Server `GET /v1/state` bypassed checkpoint pin verification | CLOSED Day 2, `8a4683f` |
| C-2 | High | `redact_field` missed encrypted fields in REJECTED rows | CLOSED Day 2, `0f88e0b` |
| C-3 | Medium | Unvalidated POST bodies returned 500 instead of 400 | CLOSED Day 3, `3cd1e92` |
| C-4 | Medium | `GET /v1/state` on an empty world returned 404 | CLOSED Day 2, `8a4683f` |
| C-5 | Medium | Invariant judgment ran outside the write lock; README overstated atomicity | CLOSED Day 11, `7233204` (README wording corrected) |
| C-6 | Medium | `world import` silently orphaned encrypted fields | CLOSED Day 7, `f8cacae` |
| C-7 | Medium | Transcript import had a lost-update race | CLOSED Day 6, `8c72180` |
| C-8 | Medium | `encrypt_fields` silently skipped fields nested in lists | CLOSED Day 5, `21aa480` |
| C-9 | Medium | CLI `diff`/`blame`/`import` leaked tracebacks on ordinary errors | CLOSED Day 9, `3261d29` |
| C-10 | Low | `POST /v1/resume` drops `expected_version` / `idempotency_key` | OPEN, re-verified: `src/world/server.py:276-306` reads only `name`, `actor`, `note` from the body, while `src/world/core.py:696-704` (`World.resume`) accepts both parameters. The HTTP route cannot express them. |
| C-11 | Low | `world update-many` has no way to pass idempotency keys | OPEN, re-verified: `src/world/cli.py:457-466` defines no `--idempotency-key` flag for `update-many`, and `cmd_update_many` (`cli.py:57-76`) does not pass keys. Note: the core supports them (`src/world/core.py:436-444`, `update_many(..., idempotency_keys=...)`); only the CLI lacks the flag. |
| C-12 | Low | No busy-timeout / retry on SQLite lock contention | CLOSED Day 10, `eeb703e` |
| C-13 | Low | `update_encrypted` spanned three transactions | CLOSED Day 10, `eeb703e` (documented crash window) |
| C-14 | Low | Transcript producer crashed with a traceback if `world_engine` was not installed | CLOSED Day 9, `3261d29` |
| C-15 | Low | `decrypt_fields` error could lose the field path on nested envelopes | CLOSED Day 5, `21aa480` |

Core primitive: 13 of 15 closed. The two open items are both Low, both at
surface layers (HTTP route, CLI), not in the core protocol.

## 3. Reconciliation: legacy engine, SDK, surfaces, deploy

| ID | Severity | Day 1 finding | Status |
|---|---|---|---|
| L-1 | High | `render.yaml` as written cannot start (`pip install -e .` without the `[server]` extra; fastapi/uvicorn live only in the extra) | OPEN, re-verified: `render.yaml:6` still reads `pip install -e .` while `pyproject.toml:28` has `dependencies = []` and fastapi/uvicorn are in the `[server]` extra. Needs Rosario's approval (deployment change). |
| L-2 | High | Legacy writes unauthenticated unless the operator remembers to set the key | OPEN, re-verified: `src/world_engine/api/main.py:48-56` only logs a warning when `WORLD_API_KEY` is unset; writes then serve unauthenticated. Needs Rosario's decision (fail-closed startup vs required secret). |
| L-3 | Medium | "Frozen prototype" contradicts the live deployment wiring | OPEN, re-verified: `docs/architecture.md:7` still calls `world_engine` "a separate frozen prototype", while `render.yaml:7` still deploys `uvicorn app:app` (legacy) and nothing deploys `world serve`. Needs an ADR picking one direction. |
| L-4 | Medium | Shipped dashboard uses deprecated `/api/*` routes slated for removal in v0.3.0 | OPEN, re-verified: `static/dashboard.html:96,130,149` still fetches `/api/state`, `/api/intent`, `/api/rogue-attack`. |
| L-5 | Medium | SDK time-travel replay silently drops node locks; server replay honors them | OPEN, not re-probed line by line today; no fix commit exists on the mission branch chain. Carried as open. |
| L-6 | Medium | Idempotency keys are global, not scoped to entity or payload | OPEN (DOCUMENTED). The F3b decision (bind keys into the row hash or scope keys) is still undecided. No silent behavior change. |
| L-7 | Medium | Unauthenticated GETs unrated; two are unbounded/O(n) | OPEN, re-verified: `src/world_engine/api/middleware.py:71-91` (`_WRITE_LIMITS`) still covers only POST routes; `GET /api/v1/state` (`src/world_engine/api/v1.py:48-53`) still returns every entity with no pagination. |
| L-8 | Medium | SDK duplicates the engine intent path (~120 lines), already drifted by one branch | OPEN, not re-probed line by line today; no fix commit exists on the mission branch chain. Carried as open. |
| L-9 | Low | `world_engine/__init__.py` documents a root shim that does not exist | OPEN, re-verified: `src/world_engine/__init__.py:8-9` still names `ingest.py` as a working entry point; repo root has no `ingest.py` (only `app.py`, `engine.py`, `import_transcript.py`). |
| L-10 | Low | `pyproject.toml` still describes `world_engine` as "the kernel" | OPEN, re-verified: `pyproject.toml:46-48` comment still reads "the kernel lives in `src/world_engine/`". |
| L-11 | Low | Rate limiting trusts the first `X-Forwarded-For` entry | OPEN (DOCUMENTED). Tradeoff is stated in the code comment; fix is to trust XFF only from a known proxy, or accept as demo behavior. |
| L-12 | Low | `tools/export_ledger.py` mutated state | CLOSED Day 13, `c94ab55` |
| L-13 | Low | Demo signing key lives in source | OPEN, re-verified: `demo/common.py:22` still defines `DEMO_TIP_KEY = "demo-tip-key-not-a-secret"`. Documented as demo-only. |
| L-14 | Low | The two shipped UIs call different API versions | OPEN, re-verified: `static/dashboard.html` uses deprecated `/api/*` while `frontend/src/components/StatePanel.jsx:13` uses `/api/v1/*`. Same fix as L-4. |

Legacy/SDK: 1 of 14 closed. This is the largest open cluster, and three of its
items (L-1, L-2, L-3) need Rosario's decisions before any fix.

## 4. Reconciliation: tests, spec, CI

| ID | Severity | Day 1 finding | Status |
|---|---|---|---|
| T-1 | High | `test_soak_no_latency_drift` flaky under load | CLOSED Day 3, `23c6e80` |
| T-2 | High | CI installs unpinned `ruff` and `mypy` | CLOSED Day 4, `0248e76` |
| T-3 | High | Lint and typecheck scope excluded `spec/`, `tools/`, `demo/`, root shims | CLOSED Day 4, `0248e76` and `bc40111` |
| T-4 | Medium | CLI coverage 80%, weakest area; `world serve` entirely untested | CLOSED Day 11, `4e1767d` |
| T-5 | Medium | Uncovered lines in `core.py` clustered in security-sensitive negative paths | CLOSED Day 11, `4c39136` |
| T-6 | Medium | Independent C# verifier never ran in this environment | CLOSED Day 13, `49c241e` (CI job fails unless the 4 verifier tests run; dotnet SDK 8.0.426 verified present in this VM) |
| T-7 | Medium | `importorskip` silently dropped large test areas when extras were missing | CLOSED Day 12, `68aa58b` |
| T-8 | Medium | Hypothesis slowness detection disabled in three property-test files | CLOSED Day 12, `f00a871` |
| T-9 | Medium | `tools/`, `demo/`, root shims outside coverage measurement | CLOSED Day 13, `7422f0b` |
| T-10 | Medium | Mypy excludes the Experiment #003 runner and analysis script | OPEN, re-verified: `pyproject.toml:99-109` still carries the exclusion with its comment explaining the same-named-module collision. |
| T-11 | Low | `spec/world.tla` never executed through TLC | OPEN, re-verified: `spec/world.tla` exists; no TLC step in `.github/workflows/ci.yml`. |
| T-12 | Low | `serve` paths hidden from the coverage gate by exclusions | CLOSED Day 11, `0b4b6cf` |
| T-13 | Low | Suite is slow and has no timing budget | OPEN, re-verified: no timing budget in `pyproject.toml` or `.github/workflows/ci.yml`. Suite runs 102.69 s locally. |
| T-14 | Low | `REPRODUCE.md` section 7 cleanroom install not re-verified this session | OPEN (NEEDS VALIDATION). Section 7 still cites the 2026-11-05 verification; no re-run has been recorded since. |

Tests/CI: 10 of 14 closed. The remaining four are infrastructure tail items,
not correctness gaps.

## 5. Reconciliation: docs and research consistency

| ID | Severity | Day 1 finding | Status |
|---|---|---|---|
| D-1 | High | STATUS.md "Uncommitted work" section was false | CLOSED Day 1 |
| D-2 | High | REPRODUCE.md tree state was stale | CLOSED Day 1 |
| D-3 | Medium | Dated reports' "uncommitted" statements now read as current state | CLOSED Day 8, `0194108` (dated addenda) |
| D-4 | Medium | `docs/architecture.md` carried the stale "uncommitted" framing | CLOSED Day 1 |
| D-5 | Medium | `research/RESEARCH_OVERVIEW.md:51` truncated sentence | CLOSED Day 1 |
| D-6 | Medium | `research/RESEARCH_OVERVIEW.md:63` CI row | CLOSED Day 1 |
| D-7 | Medium | FastAPI app reports version "0.2.0" against package 0.1.0 | OPEN, re-verified: `src/world/server.py:83` still reads `FastAPI(title="world", version="0.2.0")` while `src/world/__init__.py:12` sets `__version__ = "0.1.0"`. Fix is a code change (derive from `world.__version__`); needs approval. |
| D-8 | Medium | Top-level exports lag the handoff API | OPEN, re-verified: `from world import Assumption` still raises `ImportError`; `Assumption`, `project_state`, `revision_chain`, `validate_state` are importable only from `world.handoff`. `src/world/__init__.py` exports the other handoff names already. Fix is a code change or a deliberate documented split; needs approval. |
| D-9 | Low | STATUS.md test claim predated the 2026-11-11 commits | CLOSED Day 1 |
| D-10 | Low | F5 streaming-verify RSS figure differs across docs (0.8 vs 1.1 vs 1.2 MB) | OPEN, re-verified: `experiments/prompt3/BENCHMARKS.md` still reports 0.8 MB (repeat 1.2 MB); `experiments/prompt6/REPORT.md` still reports 1.1 MB. Separate runs of one script; a reader comparing docs still sees three numbers. |
| D-11 | Low | `research/EVIDENCE_REGISTER.md` compilation framing now stale | CLOSED Day 8, `0194108` |
| D-12 | Low | `docs/SECURITY.md:191` wrong path | CLOSED Day 1 |

Docs: 9 of 12 closed. The three open items need either a code change (D-7,
D-8) or a one-line canonical figure (D-10).

## 6. History and process

| ID | Severity | Day 1 finding | Status |
|---|---|---|---|
| H-1 | High | Local main and remote main histories diverged (parallel SHAs, identical trees) | OPEN. No push, force-push, rebase, or merge without Rosario's explicit decision. Recorded Day 1; unchanged through Day 13. |

## 7. Fresh findings (verified 2026-11-25, not in the Day 1 audit)

### F-1. Medium, VERIFIED: README test-count claims are stale

`README.md:52` ("409 tests in the suite"), `:125` ("The suite is 409 tests
passing (2026-11-05)"), `:566` ("full suite (409 tests on the current tree)"),
`:610` ("/tests 409 tests"). The suite is 500 tests since Day 13. These are
living-doc claims, not dated reports, so they should read 500. `STATUS.md`
already reads 500 (re-dated 2026-11-24); the README was not updated with it.

### F-2. Low, VERIFIED: `build/` is tracked in git and holds a stale server copy

`git ls-files build` returns `build/lib/world/server.py`, which is a stale
copy (its line 53 still has the pre-Day-2 `FastAPI(..., version="0.2.0")`
with the old line number, and it predates the C-1/C-4 fix). A build artifact
in the repo can be imported or read by mistake. Fix: add `build/` to
`.gitignore` and remove it from tracking, or delete it.

### F-3. Low, VERIFIED: STATUS.md header date is stale

`STATUS.md:7` still reads "Updated 2026-11-12 (Mission Day 1 audit)" while
its Tests line was re-dated 2026-11-24. One-line fix when the file is next
touched.

## 8. Areas checked and clean (fresh, 2026-11-25)

- Full suite green on the current tree: 500 passed, 0 failed, 1 warning.
- Coverage 95.16%, above the 85% CI gate, over the expanded scope that now
  includes `tools/`, `demo/`, and the root shims.
- No uncommitted changes at audit start; the mission branch chain is intact
  (`mission/day-13`, tip `f88dd0c`, 341 commits).
- The `world_engine/__init__.py` docstring shim claim (L-9) is the only
  false entry-point claim found; `app.py`, `engine.py`, and
  `import_transcript.py` all exist at the root as documented.
- `src/world/__init__.py` exports the main handoff names (`AgentState`,
  `Decision`, `Evidence`, `load_state`, `save_state`); the D-8 gap is exactly
  the four F1 names, no more.
- `World.update_many` already accepts per-state `idempotency_keys` at the
  core layer; the C-11 gap is CLI-only.
- Dated experiment reports (`experiments/prompt3/`, `experiments/prompt6/`)
  still cite 409 tests, which is correct as dated history, not staleness.
- No em dashes in the four new audit deliverables.

## 9. What this audit did not do

- Did not re-run the model checker, the soak, or the crash-consistency
  suite; Day 1 measurements stand and are labeled as such.
- Did not re-probe L-5 and L-8 line by line; they are carried open because no
  fix commit exists for them, not because they were re-verified today.
- Did not check GitHub issues or PRs; `gh` is unauthenticated in this VM.
- Did not change any code. Prompt 2 implementation waits on Rosario's review
  of this audit (see the gate in `PROMPT_SEQUENCE_LOG.md`).

## 10. Highest-priority improvements (in order)

1. **H-1: Rosario decides the local/remote history question.** Blocks any
   future push from local main; the divergence has stood since Nov 12.
2. **L-1/L-2/L-3: decide the legacy service's fate.** One decision covers the
   deploy config that cannot start, the unauthenticated-by-default writes,
   and the frozen-vs-live contradiction. Needs her approval; an ADR should
   record it.
3. **L-7: rate-limit the expensive unauthenticated GETs and paginate
   `/state`.** The only open Medium that is a live abuse surface on the
   deployed service.
4. **L-5/L-8: SDK replay parity and the shared intent path.** The SDK and the
   engine can disagree about locked nodes on the same chain; a parity test
   first, then the shared transition or the ported branches.
5. **L-4/L-14: migrate the shipped dashboard to `/api/v1/*`.** Unblocks
   removing the deprecated `/api/*` aliases promised for v0.3.0.
6. **D-7/D-8: derive the server version from the package and export the four
   handoff names.** Two small code changes; both need approval.
7. **L-6/F3b: decide idempotency-key scoping.** Bind keys into the row hash
   or scope them per entity; either way it is a compatibility decision, not a
   silent fix.
8. **C-10/C-11: carry `expected_version` and idempotency keys through the
   resume route and the `update-many` CLI.** Both are surface gaps; the core
   already supports both parameters.
9. **T-10/T-11/T-13/T-14: close the test-infrastructure tail.** Mypy
   exclusion note, TLC for `world.tla`, a suite timing budget, and a
   cleanroom re-verification of `REPRODUCE.md` section 7.
10. **F-1/F-2/F-3: fix the stale README counts, untrack `build/`, and re-date
    the STATUS.md header.** Small docs and hygiene items; F-1 and F-2 are the
    only fresh findings that could mislead a new reader.

**Counts:** Day 1 findings closed 33 of 56 (C 13/15, L 1/14, T 10/14,
D 9/12, H 0/1). Open: 23 Day 1 findings plus 3 fresh findings (F-1, F-2, F-3).

## 11. Addendum (Mission Day 15, 2026-11-26, Prompt 2)

- **C-10 and C-11 CLOSED.** `POST /v1/resume` and `world resume` now
  accept and forward `expected_version` and `idempotency_key`, and
  `world update-many` accepts a repeatable `--idempotency-key`. Four
  new tests. Suite 504 passed, 0 failed.
- **F-1 and F-3 CLOSED.** README test counts updated 409 to 504;
  STATUS.md header date corrected to 2026-11-26.
- **F-2 corrected, not reproduced.** No file under `build/` is tracked
  on this branch (`build/` is already in `.gitignore`); the audit's
  claim that `git ls-files build` returned `build/lib/world/server.py`
  does not hold here. The stale on-disk build copy was removed.
  Day 1 findings closed: 35 of 56 (C 15/15).
