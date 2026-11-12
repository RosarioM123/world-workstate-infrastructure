# Release-readiness assessment

Written in Prompt 6 (2026-11-05). This is an assessment, not a
release. No package has been published, no release has been
created, and neither may happen without the maintainer's explicit
approval.

## Package identity and metadata

- Distribution name: `world-engine` (pyproject `[project] name`).
  The project and repository are named WORLD; if this is ever
  published to PyPI, the distribution name will be `world-engine`,
  and that naming difference should be a deliberate decision, not
  a surprise. Availability of the name on PyPI was not checked in
  this session and is not claimed.
- Version: 0.1.0, single-sourced from `src/world/__init__.py`
  (`world.__version__`) via setuptools dynamic versioning.
- License: MIT (`LICENSE`, unchanged).
- Classifier state: `Development Status :: 3 - Alpha`, Python
  3.11, 3.12, 3.13 classifiers. Accurate for a research prototype.
- Metadata present: description, keywords, `[project.urls]`
  Homepage and Repository, `readme = "README.md"` (so the README
  is the published long description; its accuracy is
  release-relevant, and Prompt 6 Phase F rewrote it for exactly
  this reason).
- Metadata gaps (cosmetic, non-blocking, observed in the
  clean-install check): pyproject declares no `authors`, so
  `pip show` reports an empty Author field; with pip 24.0 the
  `pip show` Home-page line rendered empty despite
  `[project.urls]`. Neither blocks installation or use.

## Dependencies and pinning

- Core runtime dependencies: none. `src/world` is standard library
  only, which is the strongest reproducibility property the package
  has.
- Optional extras are exactly pinned: `server` (fastapi==0.141.1,
  uvicorn==0.53.0) and `test` (pytest==9.1.1, pytest-cov==7.1.0,
  hypothesis==6.168.0, httpx==0.28.1, fastapi==0.141.1).
- Build requirement is a floor, not a pin: `setuptools>=68` with
  build isolation. Low risk, recorded for completeness.

## Python compatibility

- `requires-python = ">=3.11"`.
- CI test matrix: Python 3.11, 3.12, 3.13 (`.github/workflows/ci.yml`).
- Verified in this session on Python 3.12.3 only; the matrix claim
  rests on the CI configuration and its recorded runs, not on a
  local 3.11 or 3.13 run in this session.

## CI assessment

- Jobs: test (3.11 to 3.13, pytest with coverage, plus an examples
  test job), lint (ruff check, ruff format check, mypy on Python
  3.12), frontend (builds the legacy landing page and checks the
  committed build output).
- Observed weakness, recorded in the Prompt 3 audit trail and not
  fixed here (Prompt 6 does not change CI): the lint job installs
  **unpinned** ruff and mypy (`pip install ruff mypy`). Tool
  behavior therefore drifts without any code change; this already
  caused one real incident in the project's history, where a newer
  CI ruff flagged directives the older local ruff accepted.
  Recommendation: pin both tools in the workflow (for example to
  the versions in the test environment) in a separate, reviewed
  change.
- Coverage gate: pyproject sets `fail_under = 85` for the coverage
  report. Measured in this session with the CI command
  (`.venv/bin/python -m pytest tests/ -q --cov`): **total coverage
  92.71%** across `world`, `world_engine`, and `world_sdk` (branch
  coverage), gate reached, 409 tests passed. Measured 2026-11-05;
  it is a property of this tree, not a standing guarantee.

## Clean-install verification

Verified 2026-11-05 from a fresh virtualenv outside the
repository: installed from the local tree, `pip show` reports
world-engine 0.1.0, the `world` CLI responds, and a smoke script
exercising update, checkpoint, the Prompt 3 handoff schema
(save_state, load_state, revision_chain), and `verify()` passed
from an unrelated working directory. Full record:
`REPRODUCE.md` section 7. No packaging defects blocked
installation; the two cosmetic metadata gaps above are the only
findings.

## Security disclosure posture

- `docs/SECURITY.md` carries the threat model, the detected and
  undetected attack classes (each pinned by a test), and a
  Reporting section. It is current through Prompt 3 (fail-closed
  writes, checkpoint pins and their residual, actor
  self-assertion).
- Known integrity limitation to disclose in any release notes:
  the idempotency table is outside the hash chain (F3b, undecided;
  the binding fix would change the hash format and break existing
  databases), and the hash chain is tamper-evident, not immutable.

## Blockers for a public release

1. **The work is uncommitted and unreviewed.** Prompt 3 (F1 to
   F6), Experiment #003, and this Prompt 6 package all exist only
   in the working tree on top of `cbcbc66`. A release cannot be
   cut from an unreviewed tree; review and commit come first, and
   any push needs its own approval under the project's standing
   rule.
2. **No release approval.** The maintainer has not approved a
   release, a version bump, or a PyPI publication. This assessment
   does not substitute for that decision.
3. **External validation is pending.** The independent
   reproduction protocol (`experiments/prompt6/VALIDATION_PROTOCOL.md`)
   has zero completed records. A release presented as validated by
   outsiders would be false; a release presented as an
   unvalidated research prototype would be accurate.
4. **Repository presentation outside the tree** (GitHub
   description, topics) cannot be changed from inside the
   repository and has not been reviewed for the release framing.
5. **CI lint pinning** (above) should land before a release so the
   released tree's checks are reproducible; it is a small change
   but it is a CI change and belongs in its own review.

## Assessment

Technically, the package installs cleanly, its checks reproduce,
and its documentation after Prompt 6 states its limits as plainly
as its results. Procedurally, it is not ready: blockers 1 to 3 are
decisions and reviews, not engineering. Recommended posture for
any first public release, once approved: version stays in the
0.1.x line, labeled a research prototype, with the limitations and
the pending external validation stated in the release notes
themselves.
