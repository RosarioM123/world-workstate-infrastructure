# WORLD Technical Debt Register

**Date:** 2026-11-25 (Mission Day 14, Prompt 1). **Version:** 0.1.0.
Every item below is open on the current tree, re-verified 2026-11-25 unless
marked DOCUMENTED (docs and code agree it is a limit) or NEEDS VALIDATION.
Closed Day 1 findings are in `REPOSITORY_AUDIT.md`, not here. No em dashes.

Severity meanings: High blocks a deploy or a trust claim; Medium is a real
defect or a missing guarantee; Low is a nit, a doc inconsistency, or a
hygiene item. "Decision needed" means the fix cannot start until Rosario
chooses; "fix" means the work is unblocked.

## High (3)

### H-1. Local main and remote main histories diverged

- **Location:** git history. Local main `2c5c3b2`, remote main `b2d63c4`;
  55 commits each side of merge base `b23249c`, identical trees, different
  SHAs (the 2026-11-11 bodies were pushed via the Git Data API, which
  recreated the commits).
- **Cost of delay:** any push from local main is non-fast-forward; the longer
  it stands, the more likely someone force-pushes or rebases by mistake.
- **Fix:** Rosario decides: keep remote main as canonical and rebase local
  work onto it, or the reverse. Do not push, force-push, rebase, or merge
  without her explicit decision.

### L-1. `render.yaml` as written cannot start

- **Location:** `render.yaml:6` (`pip install -e .`); `pyproject.toml:28`
  (`dependencies = []`, fastapi/uvicorn only in the `[server]` extra).
- **Cost of delay:** the repo's only deploy config crash-loops on first
  deploy; anyone following the README deploy path hits it.
- **Fix:** change the build command to `pip install -e ".[server]"` and verify
  with a clean-venv smoke test in CI. Deployment change: needs Rosario's
  approval.

### L-2. Legacy writes are unauthenticated unless the operator remembers to set the key

- **Location:** `src/world_engine/api/auth.py:40-41`
  (`require_api_key` silently returns when unset);
  `src/world_engine/api/main.py:48-56` (startup log warning only);
  `render.yaml:27-28` (`WORLD_API_KEY` with `sync: false`, no value).
- **Cost of delay:** a deploy with the secret left unset serves open writes,
  plus `/rogue-attack`, which appends 3 ledger rows per call.
- **Fix:** fail startup (or refuse `0.0.0.0` binding) when the key is unset,
  or set the key as a required Render secret with a deploy-time check.
  Decision needed: fail-closed startup vs required secret.

## Medium (9)

### L-3. "Frozen prototype" contradicts the live deployment wiring

- **Location:** `docs/architecture.md:7` calls `world_engine` "a separate
  frozen prototype"; `render.yaml:7` deploys it; `pyproject.toml:65-66`
  still ships `world-server` / `world-import` pointing at it; nothing
  deploys `world serve`.
- **Cost of delay:** every new contributor reads the architecture doc, then
  finds the opposite in the deploy config; work lands on the wrong system.
- **Fix:** pick one direction and record it in an ADR. Decision needed.

### L-7. Unauthenticated GETs are unrated; two are unbounded/O(n)

- **Location:** `src/world_engine/api/middleware.py:71-91` (`_WRITE_LIMITS`
  covers only POST `/intent`, `/entities`, `/rogue-attack`);
  `src/world_engine/api/v1.py:147` (`GET /api/v1/replay` runs full-chain
  `verify_chain()` plus replay per request);
  `src/world_engine/api/v1.py:48-53` (`GET /api/v1/state` returns every
  entity, no pagination).
- **Cost of delay:** a trivially repeatable expensive read on a large ledger.
- **Fix:** rate-limit the GETs (or at least `/replay`) and cap/paginate
  `/state`.

### L-5. SDK time-travel replay silently drops node locks

- **Location:** `src/world_sdk/ledger.py:559-607` (`replay_to` handles only
  `REGISTER_ENTITY` and COMMITTED intent rows; no `LOCK` handling);
  `src/world_engine/core/engine.py:779-784` (engine replay honors
  `LOCK_ENTITY`/`UNLOCK_ENTITY`). `replay_to` also skips intents for
  entities absent from its state map, while the engine materializes
  ledger-external entities from the row pre-image.
- **Cost of delay:** `WorldClient.state_at_block()` reports a locked node as
  `ACTIVE`, diverging from the server's replay of the same chain.
- **Fix:** port the lock-flip and pre-image branches into `replay_to`, with a
  test replaying a lock/unlock sequence through both implementations and
  comparing.

### L-8. SDK duplicates the engine intent path (~120 lines), already drifted

- **Location:** `src/world_sdk/ledger.py:216-360` (`LocalLedger.intent`)
  re-implements `execute_deterministic_transition`. Drift exists: the engine
  repairs an orphan idempotency-key mapping (`engine.py:354-355`); the SDK
  has no equivalent branch.
- **Cost of delay:** the two implementations will keep diverging silently;
  the next drift may be a correctness difference, not a missing branch.
- **Fix:** extract the shared transition into one function both call, or add
  a parity test covering the orphan-key path in both.

### L-4. Shipped dashboard uses the deprecated `/api/*` routes

- **Location:** `static/dashboard.html:96,130,149` fetches `/api/state`,
  `/api/intent`, `/api/rogue-attack`; `src/world_engine/api/main.py:16,21-24`
  promises the `/api` aliases "will be removed in v0.3.0".
- **Cost of delay:** removing the aliases breaks the dashboard that ships in
  the repo; keeping them blocks the v0.3.0 cleanup.
- **Fix:** migrate the dashboard to `/api/v1/*` (the React landing page
  already uses v1). Same fix closes L-14.

### L-6. Idempotency keys are global, not scoped to entity or payload (DOCUMENTED)

- **Location:** `src/world_engine/core/engine.py:337-338`; duplicated in
  `src/world_sdk/ledger.py:216+`. "The key, not the payload, defines
  identity, so a retried submission gets the first submission's outcome
  even if the agent changed the fields."
- **Cost of delay:** two different agents (or entities) reusing a key such as
  `retry-1` get the first verdict back, silently.
- **Fix:** scope keys per entity or bind the key into the row hash. This is
  the open F3b decision; do not change silently. Decision needed. Note:
  binding keys into the row hash would break verification of existing
  databases.

### D-7. FastAPI app reports version "0.2.0" against package 0.1.0

- **Location:** `src/world/server.py:83`
  (`FastAPI(title="world", version="0.2.0")`);
  `src/world/__init__.py:12` (`__version__ = "0.1.0"`).
- **Cost of delay:** clients and docs read two versions for one service;
  small, but it is a version lie in the shipped API surface.
- **Fix:** derive the app version from `world.__version__`. Code change:
  needs approval.

### D-8. Top-level exports lag the handoff API

- **Location:** `src/world/__init__.py` does not export `Assumption`,
  `project_state`, `revision_chain`, `validate_state`;
  `src/world/handoff.py:31` defines them and they are importable only from
  `world.handoff`.
- **Cost of delay:** the shipped public surface is smaller than the shipped
  API; new developers find the F1 names only by reading the handoff module.
- **Fix:** export the four names from `world`, or keep the documented split
  as a deliberate decision. Code change or decision: needs approval.

### T-10. Mypy excludes the Experiment #003 runner and analysis script

- **Location:** `pyproject.toml:99-109` (exclusion with a comment explaining
  the same-named-module collision: `prompts.py` and `analyze.py` exist under
  both Experiment #002 and #003).
- **Cost of delay:** the #003 runner and analysis script are unchecked;
  type errors there are invisible to CI.
- **Fix:** rename the colliding modules or scope the mypy run per experiment
  directory so both can be checked.

### F-1. README test-count claims are stale

- **Location:** `README.md:52,125,566,610` ("409 tests"). The suite is 500
  tests since Day 13.
- **Cost of delay:** a new reader trusts the README count and then sees 500
  pass; small, but it is a living doc contradicting the suite.
- **Fix:** update the four lines to 500 with the current date. Docs-only.

## Low (9)

### C-10. `POST /v1/resume` drops `expected_version` / `idempotency_key`

- **Location:** `src/world/server.py:276-306` reads only `name`, `actor`,
  `note`; `src/world/core.py:696-704` (`World.resume`) accepts both
  parameters.
- **Cost of delay:** HTTP clients cannot do a guarded or idempotent resume.
- **Fix:** accept and forward both fields, with the same validation the
  other POST routes use.

### C-11. `world update-many` has no way to pass idempotency keys

- **Location:** `src/world/cli.py:457-466` (no `--idempotency-key` flag on
  `update-many`); `cmd_update_many` (`cli.py:57-76`) does not pass keys.
  The core already supports them (`src/world/core.py:436-444`,
  `update_many(..., idempotency_keys=...)`).
- **Cost of delay:** batch CLI users cannot do idempotent retries.
- **Fix:** add the flag (single key applied to the batch, or per-line keys
  in the JSONL); the core side is done.

### L-14. The two shipped UIs call different API versions

- **Location:** `static/dashboard.html` uses deprecated `/api/*`;
  `frontend/src/components/StatePanel.jsx:13` uses `/api/v1/*`.
- **Cost of delay:** consistency nit; the frontend build in `static/site/`
  is current, so this is not staleness.
- **Fix:** same as L-4.

### L-9. `world_engine/__init__.py` documents a root shim that does not exist

- **Location:** `src/world_engine/__init__.py:8-9` names `ingest.py` as a
  working entry point (`python ingest.py`); repo root has no `ingest.py`.
- **Cost of delay:** a reader tries the documented command and it fails.
- **Fix:** correct the docstring to `import_transcript.py` / `world-import`.
  Docs-only.

### L-10. `pyproject.toml` still describes `world_engine` as "the kernel"

- **Location:** `pyproject.toml:46-48` comment: "the kernel lives in
  `src/world_engine/`". The primitive in `src/world/` is the kernel now.
- **Cost of delay:** misdirects anyone reading the packaging config.
- **Fix:** rewrite the comment to name `src/world/` as the kernel and
  `src/world_engine/` as the legacy demo. Docs-only.

### L-11. Rate limiting trusts the first `X-Forwarded-For` entry (DOCUMENTED)

- **Location:** `src/world_engine/api/middleware.py:94-101` (`_client_ip`).
  A hostile client can rotate IPs and dodge the per-IP bucket. The code
  comment states the tradeoff explicitly.
- **Cost of delay:** low on the current deploy; real only if the service is
  exposed behind a proxy an attacker can reach directly.
- **Fix:** only trust XFF when the direct peer is a known proxy, or accept
  as documented demo behavior. Decision needed, or leave as is.

### L-13. Demo signing key lives in source (DOCUMENTED)

- **Location:** `demo/common.py:22`
  (`DEMO_TIP_KEY = "demo-tip-key-not-a-secret"`, commented demo-only).
- **Cost of delay:** harmless as documented, but any copy-paste of the demo
  into real code carries a known key.
- **Fix:** read it from `WORLD_DEMO_TIP_KEY` with the constant only as a
  fallback, or note it in `demo/README.md`.

### T-11. `spec/world.tla` never executed through TLC

- **Location:** `spec/world.tla` exists; no TLC step in
  `.github/workflows/ci.yml`.
- **Cost of delay:** the TLA+ spec is documentation, not a checked artifact;
  a drift between the spec and the model checker would go unnoticed.
- **Fix:** add a CI step running TLC over `world.tla`, or record a decision
  that the Python model checker is the checked artifact and the TLA+ file
  is reference only.

### T-13. Suite is slow and has no timing budget

- **Location:** no timing budget in `pyproject.toml` or
  `.github/workflows/ci.yml`. Suite runs 102.69 s locally (500 tests).
- **Cost of delay:** the suite grows without a guardrail; a future slowdown
  is found by a human noticing, not by CI.
- **Fix:** add a `--durations` report and a CI wall-clock budget with an
  alert threshold.

### T-14. `REPRODUCE.md` section 7 cleanroom install not re-verified (NEEDS VALIDATION)

- **Location:** `REPRODUCE.md` section 7 still cites the 2026-11-05
  verification.
- **Cost of delay:** the clean-install claim ages; a packaging regression
  since Nov 5 would not be caught by the doc.
- **Fix:** re-run the cleanroom install in a fresh venv and re-date the
  section.

### D-10. F5 streaming-verify RSS figure differs across docs (DOCUMENTED)

- **Location:** `experiments/prompt3/BENCHMARKS.md` (0.8 MB, repeat 1.2 MB);
  `experiments/prompt6/REPORT.md` (1.1 MB re-measurement, 2026-11-05);
  `research/RESEARCH_OVERVIEW.md` ("about 1 MB after"); README and PAPER
  quote 0.8 MB.
- **Cost of delay:** a reader comparing docs sees three numbers for one
  result; the numbers are separate runs, not contradictions, but nothing
  says so in one place.
- **Fix:** pick one canonical figure with its run date, or annotate each
  with its run. Docs-only.

### F-2. `build/` is tracked in git and holds a stale server copy

- **Location:** `git ls-files build` returns `build/lib/world/server.py`,
  a stale copy (pre-Day-2 code, old line numbers, pre-C-1/C-4 fix).
- **Cost of delay:** the stale copy can be imported or read by mistake;
  it also silently re-introduces the fixed checkpoint-pin bypass to anyone
  who reads it as current code.
- **Fix:** add `build/` to `.gitignore` and remove it from tracking.

### F-3. STATUS.md header date is stale

- **Location:** `STATUS.md:7` reads "Updated 2026-11-12 (Mission Day 1
  audit)" while its Tests line was re-dated 2026-11-24.
- **Cost of delay:** none beyond a misleading header.
- **Fix:** re-date the header when the file is next touched. Docs-only.

## Debt that is NOT in this register (deliberately)

- **Revision history (unresolved):** #002 failed revision history (2/5,
  both runs) against #003 ceiling (1.000, all conditions). A discriminating
  experiment is still not run. This is research debt, tracked in STATUS.md,
  not a code defect.
- **Invariants are code, not data:** the persisted invariant registry is
  designed, not built. Tracked in STATUS.md open items.
- **No per-actor identity; no RBAC:** `actor` is self-asserted. Tracked in
  STATUS.md open items.
- **External validation pending:** zero external reviewers have completed the
  validation protocol. Tracked in STATUS.md open items.
- **No release approval:** Prompt 3 and #003 unreviewed; see
  `experiments/prompt6/RELEASE_READINESS.md`.
- **Legacy `world_engine` retire-or-merge:** a roadmap item, not a defect.

**Totals:** 26 open debt items (3 High, 10 Medium, 13 Low). Of these, 5 need a Rosario decision before work starts: H-1, L-1, L-2, L-3, L-6 (plus D-7/D-8 and L-11/T-11, which need approval or a recorded decision).
