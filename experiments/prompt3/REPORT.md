# Prompt 3 Report: Architecture Strengthening, Implemented

Date: 2026-11-04. Status: implemented in the working tree,
uncommitted, awaiting review. Nothing in this report describes a
commit or a push; neither was made. Changes F1, F2, F3a, F4, F5, F6
were implemented as approved. F3b was not approved and was not
touched.

## A. Architecture audit summary

The Phase 1 audit is preserved at `experiments/prompt3/AUDIT.md`
and is the design spec for everything below. Its central findings:
Experiment #003 never exercised the shipped `World` code path
(condition A was hand-authored Markdown); the shipped handoff schema
could not express the fields behind the experiment's one consistent
WORLD advantage (assumption metadata); the HTTP server failed open
when no API key was configured; checkpoints and the idempotency
table sit outside `verify()`; actor attribution is self-asserted;
`verify()` materialized the whole chain in memory. The audit also
rejected, as unjustified by evidence, a core revision-history
table, replacing vendored Ed25519, delta storage, general RBAC,
ZK proofs, a storage-layer fix for unverifiable additions, and
executing TLA+. None of those were built.

## B. Experiment-driven justification, per change

- **F1 (handoff schema).** #003 metric 3 (assumption retention,
  A 0.721 vs B 0.500 vs C 0.488) turned on confidence level and
  fact-vs-assumption status, and metric 5 grading turns on status,
  supersession, and evidence linkage. The shipped `AgentState`
  could express none of these (audit D1). The schema was brought up
  to the research state model in `docs/state-model.md`, with
  referential-integrity validation and a computed `revision_chain`
  view (audit section G).
- **F2 (fail-closed writes).** Audit D3: `server.py` returned no
  rejection when no API key was configured, so a deployment that
  forgot the key served open writes with only a log warning. A
  security default that fails open on a missing configuration is a
  defect independent of any experiment.
- **F3a (checkpoint pins).** Audit D4: repointing a checkpoint was
  undetected (a test pinned the limit). Checkpoints are the
  mechanism `resume()` trusts; a silent repoint silently changes
  what a name restores.
- **F4 (actor override).** Audit finding: actor is self-asserted
  everywhere. Full per-actor identity was rejected as unjustified;
  the narrow mitigation is a server-side fixed actor for
  single-purpose deployments.
- **F5 (streaming verify).** The 2026-10-15 soak measured
  `verify()` at 659 MB RSS on a 1.06M-row chain because it loads
  every row (audit D8). Memory growth with chain length is a
  scaling defect in the primitive's core audit operation.
- **F6 (projection).** #003 metric 10: WORLD bundles were the least
  context-efficient on all 8 tasks (20,382 words vs 6,142 for
  summaries). A projection that keeps live items in full and
  compacts dead items is the scoped response; the audit made its
  adoption conditional on a revalidation M5 check (section G of
  this report).

## C. Design

All changes are additive. F1 adds fields with defaults and a
tolerant `from_dict`, so every previously stored handoff loads
unchanged; there is no migration. `save_state` validates the
revision graph before proposing (supersedes targets exist,
evidence ids resolve, a superseded decision has exactly one
successor) and raises `ValueError` on violation. `revision_chain`
is a read-only derivation over committed snapshots, so revision
history needs no new storage and cannot disagree with the ledger.
F2 defaults `allow_unauthenticated_writes` to False; the opt-in is
explicit in code and on the CLI. F3a adds a nullable `pinned_hash`
column (guarded ALTER for existing databases); rows without a pin
are pre-F3a rows and are served unverified, which the docstrings
state. F5 changes iteration strategy only; semantics are pinned by
the unchanged test suite. F6 is a pure function producing a reading
view; its docstring states it is not a state to save back.

## D. Implementation

Source:

- `src/world/handoff.py` (F1, F6): `Assumption` dataclass;
  `Decision` gains id, status, supersedes, evidence_ids; `Evidence`
  gains id, kind; `validate_state`; `revision_chain`;
  `project_state`.
- `src/world/server.py` (F2, F4): `allow_unauthenticated_writes`
  and `actor` parameters on `create_app`; module docstring
  documents self-asserted actor in all other modes.
- `src/world/cli.py` (F2): `world serve --allow-unauthenticated`.
- `src/world/core.py` (F3a, F5): `pinned_hash` column and
  migration guard; pin stored at `checkpoint()` and verified in
  `state()` and `resume()`; streaming `verify()` and `blame()`.

Tests (32 new or net-new; suite 377 to 409):

- `tests/test_handoff.py` (F1): 11 tests, new-field round-trips,
  validation rejections, the #003-mirroring supersession loss test.
- `tests/test_revision_chain.py` (F1, new): 6 tests, 3-revision
  history with an interleaved REJECTED row; the six M5 questions
  asserted mechanically.
- `tests/test_world_server_security.py` (F2, F4, new): 401 on all
  three write routes with no key and no flag; flag preserves old
  behavior; key behavior unchanged; actor override wins; unset
  actor preserves body actor.
- `tests/test_world_cli_server.py` (F2): eight pre-existing tests
  updated to pass the explicit flag, the audit-sanctioned change
  for tests that pinned open-by-default behavior.
- `tests/test_redteam.py` (F3a): the checkpoint limit test renamed
  to `test_checkpoint_repoint_detected` with a comment recording
  the approved behavior change and date; two added tests (NULL pin
  served unverified; pinned-row rewrite detected). Net +2.
- `tests/test_projection.py` (F6, new): 6 tests, completeness of
  live items, no superseded item presented as current, word-count
  reduction on a representative state.

Documents: `docs/SECURITY.md` (fail-closed default, checkpoint pin
with residual, actor note), `research/LIMITATIONS.md` (verify
memory amended, checkpoint line amended, idempotency unchanged),
`research/RESEARCH_OVERVIEW.md` (VERIFIED rows for F1, F2, F3a, F5,
suite count, and the revalidation row),
`docs/state-model.md` (implementation status note),
`CHANGELOG.md` (Unreleased entries per change).

Experiment artifacts: `experiments/prompt3/bench.py`,
`BENCHMARKS.md`, and `revalidation/` (mapping, bundles, prompts,
raw outputs, blinded judged copies, scores, RESULTS.md,
PROVENANCE_NOTE.md).

## E. Testing

- Full suite before any change: **377 passed**. After all changes,
  final tree: **409 passed** (re-run on the finished tree,
  409 passed in 65.53s). No test was weakened. The only
  pre-existing tests changed are the two classes the audit names:
  open-by-default server tests (F2, flag added) and the checkpoint
  limit test (F3a, renamed with the behavior change recorded).
  VERIFIED.
- Model checker before and after: **1,220,255 explored states**
  (165,579 + 935,111 + 119,565 across the three configurations),
  properties P1 to P6 hold, mutation test detects the injected P4
  bug. Identical, as predicted: no change alters the checked
  transition semantics. VERIFIED.
- Lint and types: changed files are clean under the local ruff
  (check and format) and mypy is clean on `src/` (24 files). The
  local ruff (0.16.9) is older than CI's; tree-wide pre-existing
  findings remain in files this work did not touch (3 in
  `experiments/experiment-003/`, 2 in `tests/test_sdk.py`), and CI
  was green at the base commit. A CI-identical lint run was not
  reproduced locally. DOCUMENTED, with the skew stated.

## F. Performance

Same script (`experiments/prompt3/bench.py`), same machine,
before and after; full table in `BENCHMARKS.md`.

- `verify()` on a 20,000-version chain: 0.109s to 0.096s; peak RSS
  delta **19.7 MB to 0.8 MB** (repeat 1.2 MB). F5's target, met.
  VERIFIED at this scale; the 1.06M-row soak was not re-run.
- `blame()`: 130.7 ms to 60.7 ms (repeat 63.3 ms), about 2x, from
  the streaming walk stopping at the change.
- No material change: update_many (55,925.6/s before; 56,961.3/s
  and 50,936.0/s on two after runs), checkpoint create (0.57 to
  0.55 ms), resume (0.97 to 0.89 ms), state(version=N), history(),
  database size.
- Single update read 1,853.6/s on the first after run and
  2,352.6/s on repeat, against 2,407.4/s before: recorded as host
  variance, not a regression. No change touches the update hot
  path; F3a's schema check runs once per World construction.

## G. Comparison with Experiment #003 (revalidation)

Full detail: `experiments/prompt3/revalidation/RESULTS.md`.
PRELIMINARY, single model family, n=3 per cell, blind grading.

- R1: A-prime full and projected both at M1 1.000, M3 1.000,
  M5 1.000, M7 fabricated 0, M8 3.00; #003 A was identical on
  retention with M8 2.00. Bundle words 913 / 881 vs 2,314 (not
  like-for-like; see RESULTS.md).
- R2: full M1 0.958, M3 0.500, M5 0.963; projected M1 0.875,
  M3 0.500, M5 0.981; #003 A was M1 1.000, M3 0.500, M5 1.000,
  M8 3.00 in both A-prime types. The M3 0.500 replicates the #003
  weakness and traces to confidence values recorded in the
  original production, not to either bundle type.
- C1: A-prime M1 1.000 (both types) vs #003 A 0.750; M3 1.000;
  unverifiable additions 0 vs 12; M8 2.67 vs 2.00.
- **F6 decision input:** projected M5 does not regress on any
  task (R1 equal, R2 higher, C1 not applicable). Under the audit's
  rule the projection is retained. Recorded counter-note: R2 M1
  is lower under projection (0.875 vs 0.958), one partial verdict
  in two additional trials at n=3.

## H. Security assessment

- HTTP writes now fail closed (F2): VERIFIED by
  `tests/test_world_server_security.py`. A missing API key no
  longer silently disables write authentication; the local-dev
  opt-in is explicit and visible in the command line.
- Checkpoint repointing is detected at serve time (F3a):
  VERIFIED by `tests/test_redteam.py`. Residual, stated plainly:
  the pin lives in the same database, so an attacker who rewrites
  both the seq and the pinned hash defeats it; `verify()` still
  does not cover the checkpoints table; signed tips remain the
  out-of-band defense.
- The idempotency table remains outside the chain. Binding its
  keys into the row hash (F3b) would change the hash format and
  break verification of every existing database. It was framed as
  a stop-and-ask decision, was not approved, and is untouched.
  NEEDS DECISION, unchanged from the audit.
- Actor attribution remains self-asserted except where a server
  pins one actor (F4). There is still no per-actor identity and
  no RBAC. DOCUMENTED in `docs/SECURITY.md` and the server module
  docstring.

## I. Limitations and deviations

- One deviation from the first implementation pass, corrected
  during revalidation: `validate_state` initially also required a
  supersession target to be marked superseded. That rule is not
  in the approved design and it rejected R2's legitimate
  reversed-with-successor graph. The rule was removed, the
  docstring aligned, and the R2 shape pinned by a positive test.
  The shipped validation is exactly the audit's rule set.
- Decision and assumption ids are not auto-assigned on save;
  callers supply them. Auto-assignment would have broken a
  pre-existing round-trip equality test that this work was not
  permitted to change, and the approved spec did not require it.
- `tests/test_api_security.py` was not modified: it exercises the
  legacy `world_engine` API, not `world.server.create_app`, so
  the audit's F2 note about it does not apply. Flagged here
  because the implementation task named it.
- Multi-successor partial supersession is not representable under
  the approved validation (exactly one successor per superseded
  decision). Found on real data in R1 (D1 superseded in part by
  D2 and D3); the second link survives only in rationale text.
  Assumption supersession and invalidation provenance likewise
  have no fields. These are schema findings for a future decision,
  recorded in `revalidation/MAPPING.md`, not silently worked
  around.
- The revalidation outputs were re-filed once after a delivery
  inconsistency was caught against the on-disk prompts and ground
  truths; grading was restarted on a fresh blind mapping.
  `revalidation/PROVENANCE_NOTE.md` documents it. All revalidation
  numbers derive from the corrected set.
- Everything in section G is one model family at n=3 per cell.
  It supports the narrow adoption decision for F6 and nothing
  broader. NEEDS VALIDATION beyond that, as in #003.

## J. Recommendation

- Adopt F1 to F5 as implemented: each closes an audit defect with
  tests, no measured regression, and no change to the checked
  protocol semantics. VERIFIED at the levels section E states.
- Retain F6 (`project_state`): the audit's withdrawal condition
  (an M5 regression) did not occur. Its measured benefit is
  modest (3.5 to 13.8 percent fewer words on these states), so it
  should be presented as a convenience view with a correctness
  property (dead items never presented as current), not as an
  efficiency breakthrough.
- Leave F3b undecided and untouched until it gets its own review;
  it is the only remaining item that would break existing
  databases.
- Next evidence step, when a model API key exists: cross-model
  revalidation and a human-graded subset, per the standing
  research plan. The in-environment results here are PRELIMINARY.
- Per the standing rule, this work is uncommitted in the working
  tree for review. No commit and no push has been made.
