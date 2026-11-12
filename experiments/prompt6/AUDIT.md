# WORLD Repository Audit (Prompt 6, Phase A: Independent Audit)

Date: 2026-11-05. Auditor role: external researcher, read-only except
for this file. Repo: `~/workspace/world-workstate-infrastructure`,
local HEAD `cbcbc66` plus uncommitted Prompt 3 changes in the working
tree. Nothing was committed or pushed. Raw artifacts under
`experiments/` were read as evidence and not altered.

Classification labels used below, as defined in the task and in
`research/RESEARCH_OVERVIEW.md`: VERIFIED, EXPERIMENTALLY OBSERVED,
DOCUMENTED, PRELIMINARY, NEEDS VALIDATION.

Severity labels used in section 3:

- CONTRADICTED: a present-tense claim that code, a test, or a
  recorded artifact in the current tree directly contradicts.
- STALE: a claim that was true, or defensible, at its dated source,
  but is now incomplete, unamended, or misleading by omission. No
  single current source flatly contradicts the words as dated.

Counts: 28 register entries. 16 CONTRADICTED (A-1 to A-6, A-10,
A-11, A-12, A-15, A-16, A-17, A-22, A-26, A-27, A-28; A-6, A-16,
and A-22 are mixed entries counted once as CONTRADICTED because
they contain a directly contradicted present-tense claim).
12 STALE (A-7, A-8, A-9, A-13, A-14, A-18, A-19, A-20, A-21,
A-23, A-24, A-25).

## 1. Scope and method

Scope: `README.md`, `STATUS.md`, `CHANGELOG.md`, `research/*.md`,
`docs/**` (with depth on `docs/SECURITY.md`, `docs/state-model.md`,
and `docs/spec/protocol-verification.md`), checked against
`src/world/`, `tests/`, `pyproject.toml`,
`.github/workflows/ci.yml`, and the recorded artifacts in
`experiments/prompt3/`, `experiments/experiment-003/`, and
`docs/experiment-002/`.

Evidence base read first, as instructed:

- `experiments/prompt3/AUDIT.md` and `experiments/prompt3/REPORT.md`:
  Prompt 3 changes F1 (handoff schema: ids, status, supersedes,
  confidence, `revision_chain`), F2 (server fails closed by default,
  `--allow-unauthenticated` opt-in), F3a (checkpoint `pinned_hash`),
  F4 (server actor override), F5 (streaming `verify()`), F6
  (`project_state`). Source: `experiments/prompt3/REPORT.md`
  sections B to D.
- `experiments/prompt3/BENCHMARKS.md`: same script before and after;
  `verify()` on a 20,000-version chain, peak RSS delta 19.7 MB
  before and 0.8 MB after (repeat 1.2 MB); `blame()` 130.7 ms to
  60.7 ms; suite 377 to 409 passed; model checker unchanged at
  1,220,255 states. Source: `experiments/prompt3/BENCHMARKS.md`.
- `experiments/experiment-003/REPORT.md`: complete, all results
  PRELIMINARY, single model family. Condition A was hand-authored
  Markdown built to `docs/state-model.md` and never exercised the
  `World` class (also `experiments/prompt3/AUDIT.md` scope note).
  M3 assumptions A 0.721 vs B 0.500 vs C 0.488; M5 revision history
  1.000 in all conditions; M1 decisions A 0.948 vs B 0.979 vs
  C 0.979; M7 unverifiable additions 12 under A only, fabrications
  0 in all conditions; M10 bundles 20,382 words (A) vs 6,142 (B) vs
  7,488 (C). Source: `experiments/experiment-003/REPORT.md` results
  table and negative findings 1 to 5.
- `research/RESEARCH_OVERVIEW.md` evidence classification table,
  `research/LIMITATIONS.md`, `research/HYPOTHESIS.md`,
  `research/RELATED_WORK.md`, `docs/SECURITY.md`,
  `docs/state-model.md`, `docs/spec/protocol-verification.md`
  (model checker table: 165,579 plus 935,111 plus 119,565 equals
  1,220,255 states, properties P1 to P6 hold).

Method: line-by-line cross-check of present-tense claims in the
documents above against code and tests, plus spot checks run
with the repo `.venv` python on 2026-11-05: (1) the full suite,
result 409 passed (two runs in this audit, 80.68s and 85.87s;
consistent with `experiments/prompt3/REPORT.md` section E,
409 passed, and the parent-supplied baseline); (2)
`python3 spec/model_check.py`, result 165,579 plus 935,111 plus
119,565 equals 1,220,255 states, all properties P1 to P6 hold,
and the mutation test found the injected P4 violation;
(3) `.venv/bin/world --help`, whose subcommand list matches
`src/world/cli.py`; (4) import probes in section 5 (A-26).
`experiments/experiment-003/analysis/analyze.py`
was not run, per instructions. Earlier documentation was not assumed
correct; where a Prompt 3 amended document and an unamended document
disagree, the amended document plus code is treated as the source of
truth and the disagreement is registered.

One structural fact frames many findings: the current state is not
what a clone of remote main contains. `git status` in this audit
shows Prompt 3 modifications uncommitted across `CHANGELOG.md`,
`docs/SECURITY.md`, `docs/state-model.md`, `research/LIMITATIONS.md`,
`research/RESEARCH_OVERVIEW.md`, `src/world/cli.py`,
`src/world/core.py`, `src/world/handoff.py`, `src/world/server.py`,
and four test files, with `experiments/experiment-003/`,
`experiments/prompt3/`, `tests/test_projection.py`,
`tests/test_revision_chain.py`, and
`tests/test_world_server_security.py` untracked. Every correction
below is therefore a working-tree correction first; none of it
reaches an external reader until a commit decision is made. That
decision is out of scope for Phase A.

## 2. Research question and positioning clarity

The research question itself is stated clearly and consistently in
three places: `README.md` opening and research hypothesis paragraph,
`research/RESEARCH_OVERVIEW.md` first paragraph, and
`research/HYPOTHESIS.md` central hypothesis. All three ask whether
explicit structured work-state preserves more decision-relevant
information across an agent handoff than a summary or a transcript,
and whether the record can be made auditable. That part needs no
repair. Classification of the question: DOCUMENTED.

The positioning around the question has drifted in three ways.

First, the headline evidence framing still centers Experiments #001
and #002 and decision governance. The strongest current handoff
evidence is narrower and different: in Experiment #003 the only
consistent WORLD advantage was assumption metadata (M3, paired
+0.221 vs B and +0.233 vs C, PRELIMINARY, source:
`experiments/experiment-003/REPORT.md`), while decisions slightly
favored the baselines (M1 paired -0.031), provenance tied, and
revision history tied at ceiling. A reader of `README.md`,
`research/HYPOTHESIS.md`, or `research/RELATED_WORK.md` alone would
not learn this. The only top-level documents that carry the #003
result are the Prompt 3 rows added to
`research/RESEARCH_OVERVIEW.md` (revalidation row) and
`experiments/experiment-003/REPORT.md` itself.

Second, two different claims are routinely blended: (a) the
primitive's mechanism guarantees (hash chain, judging, optimistic
concurrency), which are VERIFIED by tests and the model checker, and
(b) the handoff benefit claim, which is PRELIMINARY at best and
NEEDS VALIDATION for any general form, as
`research/RESEARCH_OVERVIEW.md` itself states in its final table
rows. `README.md` keeps these apart better than `STATUS.md` and
`research/RELATED_WORK.md` do; the audit found no place where a doc
states the general reliability claim as proven, which is to the
repo's credit, but several places where the #002-era narrow result
is presented without its #003 narrowing (A-6, A-19, A-21, A-22).

Third, there are three positionings in the tree for three different
audiences, and the docs do not label them as such: the primitive
(`src/world/`, `README.md` main text), the research program
(`research/`), and the startup vision (`docs/VISION.md`, WORLD /
MIND / REALITY layers, intent and constraint-engine vocabulary that
describes the legacy `world_engine`, not the primitive). An external
researcher can reconstruct which is current only by reading the
Legacy section near the end of `README.md`. See section 7.

## 3. Inconsistency register

### README.md

- A-1. CONTRADICTED. Test count 377 in three places: Status
  paragraph ("377 tests in the suite"), Correctness contract
  ("The 377-test suite exercises each guarantee"), and Repository
  layout ("`/tests` 377 tests"). Conflicting source: the suite is
  409 passed, `experiments/prompt3/REPORT.md` section E and
  `experiments/prompt3/BENCHMARKS.md` (AFTER table), and this
  audit's own run (409 passed). Correction: replace all three with
  409 and date the count, as `research/RESEARCH_OVERVIEW.md` does.
  Assigned to Prompt 6 (README phase).

- A-2. CONTRADICTED. CLI and HTTP section: the API-key gate is
  described as "fail-open with a warning when unset" for
  `WORLD_API_KEY` / `X-API-Key`. Conflicting source:
  `src/world/server.py` module docstring and `_guard` (no key and
  no `allow_unauthenticated_writes` returns 401 on write routes),
  `src/world/cli.py` (`world serve --allow-unauthenticated`),
  `tests/test_world_server_security.py`, and the amended
  `docs/SECURITY.md` section "HTTP write authentication (Prompt 3
  F2, 2026-11-04)". Correction: state the fail-closed default and
  the explicit opt-in. This also fixes a live DX trap: a reader
  following the current text expects open writes and gets 401.
  Assigned to Prompt 6 (README phase).

- A-3. CONTRADICTED. Current limitations: "`verify()` is O(n) in
  time and memory. A 1.06M-row chain verified in 14.0s at 659 MB
  RSS in the soak test. A streaming verifier is future work."
  Roadmap repeats it: "Streaming `verify()` (constant memory)" as
  future work. Conflicting source: `src/world/core.py` `verify()`
  docstring ("Rows are streamed from the cursor, never
  materialized as a list (Prompt 3 F5)") and the same streaming
  walk in `blame()`; `experiments/prompt3/BENCHMARKS.md` (20,000
  row chain peak RSS delta 19.7 MB to 0.8 MB). The 14.0s and 659 MB
  figures remain true as the dated 2026-10-15 soak record
  (`experiments/soak/RESULTS.md`); what is false is the present
  tense and the roadmap placement. `research/LIMITATIONS.md` shows
  the correct amended form ("`verify()` is O(n) in time", memory
  half fixed, soak not re-run at scale). Correction: copy that
  amended form into `README.md` and remove streaming verify from
  the roadmap. Assigned to Prompt 6 (README phase).

- A-4. CONTRADICTED. Correctness contract: "`verify()` pinpoints
  the first bad row". Conflicting source: `src/world/core.py`
  `verify()` returns `bool` only (True or False, no row, no seq).
  Naming the first broken record is the legacy
  `world_engine` `verify_chain()` behavior described in
  `docs/SECURITY.md` Part B. Correction: say `verify()` returns
  False on the first mismatch it reaches, or drop "pinpoints".
  Assigned to Prompt 6 (README phase).

- A-5. CONTRADICTED (overstated). Two places claim deterministic
  replay for the primitive: the opening ("immutable checkpoints,
  deterministic replay") and the Correctness contract
  ("Deterministic replay. State rebuilds from the version log
  alone; checkpoints restore as new versions"). Conflicting
  source: `experiments/prompt3/AUDIT.md` section B5, confirmed by
  code inspection in this audit: `src/world/` has no replay
  function; every version row stores the complete document, so
  `state(version=N)` is snapshot retrieval, not replay;
  `replay_ledger()` exists only in legacy `src/world_engine/`;
  CLI `import` builds a fresh chain with new timestamps and hashes
  and skips REJECTED rows (`src/world/cli.py` `cmd_import`, also
  visible in `world --help`: "replay an export JSONL into a world
  (fresh hash chain; rejected rows are skipped)"). Correction:
  replace the replay claim with snapshot retrieval and committed
  only time travel, which is what the code provides. Assigned to
  Prompt 6 (README phase).

- A-6. CONTRADICTED in the roadmap, STALE in the framing. (i)
  Roadmap: "Experiment #003: adversarial handoff, conflicting
  successor goals" plus "a targeted revision-history experiment,
  the open failure from #002", both as future work. Conflicting
  source: `experiments/experiment-003/REPORT.md` is complete
  (status line: complete; 8 tasks, 72 of 72 continuations graded),
  and the executed #003 was not the adversarial design the roadmap
  describes: its tasks were F1, F2, S1, S2, R1, R2, C1, C2 under a
  parity gate, per its Design as executed section. (ii) Framing:
  "What has actually been demonstrated" and "What remains
  unproven" call revision-history preservation "a current failure,
  not just an untested area", with no #003 context. Conflicting
  source: #003 M5 was 1.000 in all three conditions (ceiling, no
  discrimination; source: `experiments/experiment-003/REPORT.md`
  negative finding 1), and the Prompt 3 revalidation found no M5
  regression from the F6 projection (source:
  `experiments/prompt3/revalidation/RESULTS.md`). The accurate
  current statement is the one in `experiments/prompt3/AUDIT.md`
  section C: revision behavior is protocol-sensitive and
  unresolved, #002 failure against #003 ceiling. Correction:
  remove #003 from the roadmap, describe the executed #003, and
  reframe revision history as unresolved with both results cited.
  Assigned to Prompt 6 (README phase).

- A-7. STALE (incomplete by omission). Architecture diagram,
  State model, API table, and Agent handoff section all predate
  Prompt 3. Specifically: the diagram and text describe
  checkpoints only as "immutable name to seq", with no
  `pinned_hash` (conflicting source: `src/world/core.py`
  checkpoint schema comment, `checkpoint()`, `_verify_checkpoint_pin`,
  and `tests/test_redteam.py::test_checkpoint_repoint_detected`);
  the API table and Reads list omit the checkpoint pin behavior of
  `state(checkpoint=)` and `resume()`; the Agent handoff example
  uses only pre-F1 fields and never mentions `Assumption`,
  `Decision` `id` / `status` / `supersedes` / `evidence_ids`,
  `revision_chain`, or `project_state` (conflicting source:
  `src/world/handoff.py` `__all__` and classes, `tests/test_handoff.py`,
  `tests/test_revision_chain.py`, `tests/test_projection.py`).
  Correction: add one short Prompt 3 paragraph and one handoff
  example extension; do not rebuild the diagram. Assigned to
  Prompt 6 (README phase).

- A-8. STALE (dated record, pre-F5 context missing). Performance
  table is headed "Measured 2026-10-15" and lists `verify()` full
  chain at 200,081 rows/s and `update` (invariant judged) at
  1,339 ops/s, from `docs/benchmarks/world-primitive.md`. The
  dating and the "re-run before quoting" note are honest, and the
  numbers are not contradicted as records. The gap is that the
  table predates F5 and sits two sections away from the F5 result
  an external reader needs for context (207,427 rows/s on a
  20,000-version chain in `experiments/prompt3/BENCHMARKS.md`,
  different chain size, not directly comparable). Correction:
  add a one-line pointer to `experiments/prompt3/BENCHMARKS.md`
  under the table. Recommend-only if space is contested; the
  dating already limits the harm.

- A-9. STALE. Research section: "Both handoff experiments hand
  the same Agent A research output to a successor", method detail
  given for #002 only, results listed for #001 and #002 only, and
  the preamble says every quantitative claim carries a status of
  "(VERIFIED, DOCUMENTED, or NEEDS VALIDATION)". Conflicting
  sources: there are now three handoff experiments plus a
  revalidation (`experiments/experiment-003/REPORT.md`;
  `experiments/prompt3/revalidation/RESULTS.md`), and the
  classification table in `research/RESEARCH_OVERVIEW.md` now
  also uses EXPERIMENTALLY OBSERVED and PRELIMINARY (see A-17).
  Correction: add a #003 bullet (M3 result, M5 ceiling, M10 cost,
  PRELIMINARY) and update the status list. Assigned to Prompt 6
  (README phase).

- A-10. CONTRADICTED (minor). Status paragraph: "CI also runs
  ruff and mypy on Python 3.11 to 3.13". Conflicting source:
  `.github/workflows/ci.yml`: the test matrix is Python 3.11,
  3.12, 3.13, but the lint job is a single job on Python 3.12
  only, and it installs unpinned tools (`pip install ruff mypy`).
  Same phrasing problem in `STATUS.md` (A-13 note). Correction:
  "CI runs pytest on Python 3.11 to 3.13, and ruff and mypy on
  Python 3.12". Assigned to Prompt 6 (README phase).

### STATUS.md

- A-11. CONTRADICTED. Header "Updated 2026-11-02" and Tests line
  "377 passing, 0 failing (full suite run locally 2026-11-02,
  Python 3.12.3)". As a dated 2026-11-02 record this was accurate;
  as the file's stated purpose ("Single-pointer dashboard") it is
  now false. Conflicting source: 409 passed,
  `experiments/prompt3/REPORT.md` section E, and this audit's run.
  Correction: regenerate the dashboard or stamp it as a
  2026-11-02 snapshot and point to `research/RESEARCH_OVERVIEW.md`
  for current numbers. Assigned to Prompt 6 (STATUS phase).

- A-12. CONTRADICTED. Open items: "streaming verify" listed among
  "designed gaps, not built"; Soak line calls `verify()` O(n)
  memory "the known scaling limit" with no F5 amendment.
  Conflicting source: A-3 sources (`src/world/core.py` streaming
  `verify()`, `experiments/prompt3/BENCHMARKS.md`).
  `research/LIMITATIONS.md` carries the amended form; `STATUS.md`
  was not amended. Correction: same amended wording as A-3.
  Assigned to Prompt 6 (STATUS phase).

- A-13. STALE. The whole Experiments and Shipped sections omit
  Experiment #003 and all of Prompt 3 (F1 to F6), and Open items
  still calls revision history "the next experiment the record
  calls for". Conflicting sources: `experiments/experiment-003/REPORT.md`
  (complete) and `experiments/prompt3/REPORT.md` (implemented,
  uncommitted). A dashboard that omits the two largest work items
  since its date misleads even if every line in it is dated.
  Correction: add #003 and Prompt 3 entries, or retire the file
  in favor of the overview (see section 7). Assigned to Prompt 6
  (STATUS phase).

### research/RESEARCH_OVERVIEW.md

- A-14. STALE (self-confusing, not false as history). The
  classification table now contains both "Test suite: 377 tests
  pass, VERIFIED, run 2026-11-02" and "Test suite: 409 tests
  pass, VERIFIED, run 2026-11-04", and the paragraph after the
  table still says "the 377 passing tests (VERIFIED) demonstrate
  software behavior". A careful reader can reconstruct that 377
  is the superseded baseline, but the table presents both rows at
  the same status with no superseded marker. Correction: mark
  the 377 row superseded by the 409 row and update the paragraph
  to 409. Assigned to Prompt 6 (research docs phase).

- A-15. CONTRADICTED as a current claim. Table row: "CI on the
  current remote main: test jobs pass on Python 3.11, 3.12, and
  3.13; the lint job fails at the Ruff lint step, VERIFIED via
  API query, 2026-11-02, run 41517883400 on commit `ec1a4b27`".
  Conflicting sources: the two commits now at the top of local
  history are `a860cf8` "resolve pre-existing ruff lint errors"
  and `cbcbc66` "remove stale noqa directives flagged by ruff
  0.17.3" (git log, this audit), which postdate that run and
  target exactly that failure, and `experiments/prompt3/REPORT.md`
  section E states "CI was green at the base commit". The row's
  own evidence is dated 2026-11-02, but its label says "current
  remote main" with no as-of qualifier in the claim column.
  Caveat: this audit did not query the GitHub API, so the current
  remote CI state is NEEDS VALIDATION; what is established is
  that the row cannot still be presented as current without a
  recheck. Correction: recheck CI, then either update the row
  with the new run or relabel it as a 2026-11-02 record.
  Assigned to Prompt 6 (research docs phase, with the recheck
  itself recommend-only until run).

- A-16. CONTRADICTED in one line, STALE in the rest. Evidence
  base item 2 still lists as a soak finding "one honest scaling
  limit (`verify()` is O(n) memory)", present tense, with no F5
  amendment, although the classification table in the same file
  carries the F5 VERIFIED row. Evidence base item 4 (Handoff
  experiments) covers only #001 and #002, and "What is
  demonstrated, and what is not" still says revision-history
  preservation is "currently a failure, not a gap in testing"
  with no #003 ceiling context. Conflicting sources: A-3 and A-6
  sources. Note the asymmetry: `research/LIMITATIONS.md` received
  Prompt 3 amendments and this file's table received Prompt 3
  rows, but this file's prose sections did not. Correction:
  amend item 2 (memory half fixed, soak not re-run), add #003 to
  item 4 with PRELIMINARY status, and reframe the revision line
  as unresolved (#002 failure, #003 ceiling). Assigned to
  Prompt 6 (research docs phase).

- A-17. CONTRADICTED (internal, minor). The Evidence
  classification preamble says every claim carries "one of three
  statuses" (VERIFIED, DOCUMENTED, NEEDS VALIDATION). The table
  itself uses at least two more: "EXPERIMENTALLY OBSERVED,
  preliminary" (Prompt 3 revalidation row) and compound labels
  such as "DOCUMENTED, preliminary" and "DOCUMENTED as recorded;
  the underlying property is VERIFIED by re-exercise".
  `README.md` Research preamble repeats the three-status version
  (A-9). Correction: define five labels (adding EXPERIMENTALLY
  OBSERVED and PRELIMINARY) in the preamble of this file and in
  `README.md`. Assigned to Prompt 6 (research docs phase).

- A-18. STALE. The System in one paragraph and Performance
  records sections are pre-Prompt 3 in emphasis: the handoff
  layer is described as "`AgentState`: objective, decisions,
  assumptions, evidence, open questions, next actions", which is
  now accurate for the field list (this seed-adjacent suspicion
  is REFUTED for the field list), but the paragraph does not
  mention `revision_chain`, `project_state`, the checkpoint pin,
  or the fail-closed server, and the Performance table has no
  pointer to `experiments/prompt3/BENCHMARKS.md`. Same fix shape
  as A-7 and A-8. Recommend-only (the paragraph is a summary, and
  the table rows in the same file do carry the Prompt 3 facts).

### research/LIMITATIONS.md

- A-19. STALE (unamended lead). The file leads, under Negative
  findings, with "Revision history does not survive", supported
  only by Experiment #002 (2 out of 5 in both runs, journal 4 of
  5 in the replication). Prompt 3 amended three later sections
  of this same file (checkpoint pin in System limits, F2 and F4
  in No per-actor identity, F5 in the `verify()` item, each
  dated 2026-11-04 in the text), but this lead section received
  no #003 or revalidation amendment. Conflicting context:
  #003 M5 1.000 in all conditions and the revalidation M5
  results (A-6 sources). As written, a reader who stops at the
  lead section gets the pre-#003 verdict. Correction: keep the
  #002 finding verbatim, add a dated amendment paragraph
  recording the #003 ceiling, the protocol-sensitivity
  explanation, and the unresolved status. Assigned to Prompt 6
  (research docs phase).

- A-20. STALE. Experiment methodology limits are written for
  #001 and #002 only: "n=1 per run", "One model family
  throughout", experimenter-built answer keys, no context
  isolation. Those statements remain true of #001 and #002, but
  the file presents them as the program's methodology limits
  and never mentions #003, whose design differs in ways that
  matter (8 tasks, 3 trials per cell, n=24 per condition for
  most metrics, parity gate, blind grading by 8 grader sessions,
  no human grading; source: `experiments/experiment-003/REPORT.md`
  Design as executed and Limitations). Correction: scope the
  existing bullets to #001 and #002 and add a #003 methodology
  bullet set, mostly liftable from the #003 report's own
  Limitations section. Assigned to Prompt 6 (research docs
  phase).

### research/HYPOTHESIS.md

- A-21. STALE. The whole evidence section is pre-#003: sub-claim
  1 "failed" on revision history with no ceiling result; "This
  is the next experiment the record calls for" for the
  revision question; falsifiability status for summary parity
  resting only on the #002 replication (0.36); ontology
  generality "untested beyond two investment-research tasks and
  one earlier task". Conflicting sources: #003 tested 8 tasks
  across financial, software engineering, revision, and control
  categories and returned split verdicts (H1 supported for
  assumptions only; H2, H3 not supported; H4, H5 supported;
  source: `experiments/experiment-003/REPORT.md` Hypothesis
  verdicts). Correction: add a dated #003 verdict paragraph per
  sub-claim; do not rewrite the hypothesis statement itself,
  which is correctly labeled a hypothesis. Assigned to Prompt 6
  (research docs phase).

### research/RELATED_WORK.md

- A-22. CONTRADICTED in one line, STALE in the rest. (i) Agent
  handoff approaches: "`AgentState` helpers in
  `src/world/handoff.py` are a thin typed layer over that
  document (decisions, evidence, open questions, next actions)".
  Conflicting source: `src/world/handoff.py` `AgentState` has
  six sections (objective, decisions, evidence, open questions,
  next actions, assumptions), and assumptions are the section
  behind the #003 M3 result. The list omits objective and
  assumptions. (ii) Open research gaps item 1: "Structured
  state demonstrably fails to transmit revision history
  (Experiment #002, both runs). Whether an explicit
  revision-chain schema fixes this is untested anywhere in this
  repo." Conflicting sources: F1 shipped an explicit schema
  plus `revision_chain` (`src/world/handoff.py`), and the
  Prompt 3 revalidation exercised it on R1, R2, and C1 with no
  M5 regression (PRELIMINARY, source:
  `experiments/prompt3/revalidation/RESULTS.md`); #003 also
  complicates "demonstrably fails" (A-6). Correction: update
  the helper list, and reframe gap 1 as unresolved with the
  schema now built and preliminarily exercised. Assigned to
  Prompt 6 (research docs phase).

### CHANGELOG.md

- A-23. Seed suspicion REFUTED in its main form; remaining issues
  STALE. Checked: the Unreleased section DOES contain Prompt 3
  entries for every change, F1 handoff schema and
  `revision_chain` and `project_state` (Added), F3a checkpoint
  pinned hash (Added), F4 server actor override (Added), F2
  fail-closed server (Changed), F5 streaming `verify()` and
  `blame()` (Changed), each dated 2026-11-04 and accurately
  worded against the code. No correction is needed for
  existence or accuracy of those entries. Two residual problems:
  (i) ordering: the Unreleased Added and Changed lists lead
  with pre-primitive and legacy `world_engine` work (versioned
  `/api/v1`, multi-entity ledger, transcript era items) and the
  Prompt 3 entries sit at the end of each list, so a reader
  scanning from the top gets the oldest work as the headline;
  (ii) omission: there is no entry anywhere in the file for
  Experiment #003 or for the Prompt 3 revalidation, although
  both are research results the repo elsewhere treats as
  headline events. Correction: reorder Unreleased newest-first
  within each subsection, and add a #003 entry. Assigned to
  Prompt 6 (docs phase); the reordering half is recommend-only
  if the maintainer prefers append order as a convention.

### docs/state-model.md

- A-24. Seed suspicion PARTLY REFUTED, partly CONFIRMED; STALE.
  The file does carry an accurate implementation note dated
  2026-11-04 (Prompt 3 F1) stating which Decision, Assumption,
  and Evidence fields are now implemented, that `save_state`
  validates referential integrity, that `revision_chain` exists,
  and that the remaining entities are still draft only with core
  storage still one opaque JSON document per version. That note
  is correct against `src/world/handoff.py`. What is now
  inaccurate is the status framing above it: the title still
  says "(Draft v0.1)" for the whole model, and the Status line
  still says the model "becomes real only after the handoff
  experiment validates that these entities are what actually
  prevent information loss", although a handoff experiment
  (#003) has now run, did bear on exactly these fields (M3), and
  part of the model is implemented. Two naming drifts add
  friction: the note itself flags `supersedes` (code) vs
  `supersedes_id` (this doc) for Decision, and the same kind of
  drift is unflagged for Decision `statement` (doc) vs `text`
  (code) and Evidence `summary` / `reference` (doc) vs `claim` /
  `source` (code). Correction: split the Status line by entity
  (implemented: Decision, Assumption, Evidence as handoff types;
  draft only: Project, Task, Artifact, Action, StateChange,
  Question, Handoff as stored types) and add a field-name mapping
  note. Assigned to Prompt 6 (docs phase).

### docs/SECURITY.md

- A-25. STALE (recommend-only). Part A is current and accurate
  post-Prompt 3 (see section 6). Part B, explicitly labeled as
  the legacy `world_engine` record, ends with a "Planned
  hardening (not yet built)" list whose item 1 is signed
  checkpoints, which Part A records as BUILT 2026-10-15 for the
  primitive, and whose item 4 is encrypted notes, while the
  primitive has per-field encryption built (`src/world/fieldcrypto.py`).
  Because Part B is scoped to the legacy engine, this is not a
  strict contradiction; the legacy engine may indeed lack those
  features. The risk is purely presentational: a diligence
  reader who lands on Part B via search gets a not-built list
  for features the repo has built in the other system.
  Correction: add one line at the top of Part B's Planned
  hardening list pointing to Part A mitigation ranking for the
  primitive status of each item. Recommend-only.

### Code and packaging surfaces found by cross-checking (not in the seed list)

- A-26. CONTRADICTED. Top-level package exports lag the handoff
  API. `src/world/handoff.py` `__all__` exports `Assumption`,
  `project_state`, `revision_chain`, and `validate_state`, and
  the tests import them from `world.handoff`
  (`tests/test_handoff.py`, `tests/test_projection.py`,
  `tests/test_revision_chain.py`). But `src/world/__init__.py`
  exports only `AgentState`, `Decision`, `Evidence`,
  `load_state`, `save_state` from handoff. Verified in this
  audit: `.venv/bin/python -c "from world import Assumption"`
  fails with ImportError, while the same import from
  `world.handoff` succeeds. A user following the README pattern
  (`from world import AgentState, Decision, Evidence, ...`)
  cannot reach the Prompt 3 API at top level. Correction:
  either export the four names from `world` or document
  `world.handoff` as the import path in `README.md`. Assigned
  to Prompt 6 (docs phase if documentation only; a code export
  change is a separate approval).

- A-27. CONTRADICTED (minor). Version disagreement:
  `src/world/__init__.py` sets `__version__ = "0.1.0"` and
  `pyproject.toml` takes the version dynamically from it, but
  `src/world/server.py` `create_app` builds
  `FastAPI(title="world", version="0.2.0")`. The HTTP surface
  therefore reports a version that exists nowhere else in the
  repo. Correction: derive the FastAPI version from
  `world.__version__` or set it to 0.1.0. Recommend-only (code
  change, outside a docs phase unless approved).

- A-28. CONTRADICTED (packaging, minor). `pyproject.toml`
  distribution name is `world-engine`, while the import package
  every document teaches is `world` (`from world import World`).
  The console scripts deepen the split: `world` points to
  `world.cli:main` (the primitive), but `world-import` points
  to `world_engine.ingestion.transcript:main` and
  `world-server` points to `world_engine.api.main:serve` (the
  legacy engine), so two of the three installed commands named
  `world-*` run the legacy system. Stale comments in the same
  file say "the kernel lives in `src/world_engine/`" as the src
  layout note and describe the package-data comment in terms of
  `world_engine` / `world_sdk`. Conflicting sources: `src/world/`
  layout on disk, `README.md` Install and Repository layout
  sections. Correction: at minimum document the name split in
  `README.md` Install; renaming the distribution or the legacy
  scripts is a maintainer decision. Assigned to Prompt 6 as a
  documentation note; any rename is recommend-only.

## 4. Reproducibility assessment

What an external researcher can re-run from the preserved tree,
assuming they have the full working tree (see the clone caveat
below):

- Full test suite: `.venv/bin/python -m pytest tests/ -q` from
  the repo root. Result in this audit: 409 passed. VERIFIED.
- Protocol model checker: `python3 spec/model_check.py` reports
  1,220,255 explored states (165,579 plus 935,111 plus 119,565
  across three configurations), properties P1 to P6 hold, with a
  mutation test that produces the P4 counterexample. Re-run in
  full in this audit on 2026-11-05 with exactly those results
  (mutation test: P4 violated, second winner for
  expected_version=0). Sources: this audit's run, plus
  `docs/spec/protocol-verification.md` results table and
  `experiments/prompt3/REPORT.md` section E. VERIFIED.
- Prompt 3 benchmarks: `experiments/prompt3/bench.py` regenerates
  the before and after style measurements on a fresh 20,000
  version chain, including the F5 memory result. DOCUMENTED as a
  runnable script; numbers are single-machine records.
- Primitive and contention benchmarks: `python tools/bench_world.py`
  and `python tools/bench_contention.py` (`README.md`
  Reproduction). The published 2026-10-15 figures (A-8) are
  records, not targets.
- Experiment #003 analysis of preserved outputs:
  `python3 analysis/analyze.py` regenerates
  `experiments/experiment-003/analysis/results.json` and
  `tables.md` from `results/scores/`; `runner/build_prompts.py`,
  `runner/parity_gate.py`, `runner/blind.py`, and
  `runner/blind_artifacts.py` regenerate prompts, parity checks,
  and blinded copies with recorded seeds (trial order seed
  20261102, blinding seed 20261103). Source:
  `experiments/experiment-003/REPORT.md` Reproducibility items
  1 to 6. This audit did not run `analyze.py` in place, per
  instructions; the claim here is that the path exists and is
  documented, not that it was exercised.
- Independent C# verifier: exercised through
  `tests/test_csharp_verifier.py` inside the suite
  (`tools/ChainVerifyWorld/`, no shared code with the Python
  verifier). VERIFIED via the suite run.

What an external researcher cannot re-run:

- The agent runs behind Experiments #001, #002, and #003 and the
  Prompt 3 revalidation. These needed in-environment agent
  sessions: Agent A productions, continuations, summaries, and
  blind grading were all performed by agents inside this
  environment, on a single model family, with the exact model
  version not reported by the platform and no seed or
  temperature control. Source: `experiments/experiment-003/REPORT.md`
  Reproducibility ("The only non-reproducible element is the
  agent sessions themselves") and Limitations. What is
  reproducible is analysis of the preserved raw outputs, scores,
  and mappings, not the runs.
- Human grading: none exists to reproduce. #003 preserved raw
  outputs so a human can grade a 25 percent subset (18
  continuations) later; that grading has not happened. Source:
  `experiments/experiment-003/REPORT.md` Limitations and
  Recommended next steps item 1.
- The 1.06M-row soak at scale after F5: not re-run. The at-scale
  memory figure on record remains the 2026-10-15 one (659 MB RSS,
  `experiments/soak/RESULTS.md`), as `research/LIMITATIONS.md`
  correctly states.
- CI as configured: the lint job installs unpinned `ruff` and
  `mypy` (`pip install ruff mypy` in `.github/workflows/ci.yml`),
  so lint results are not pinned to a tool version and can drift
  between runs. `experiments/prompt3/REPORT.md` section E records
  the local consequence: local ruff 0.16.9 vs the CI-era tool, a
  CI-identical lint run not reproduced locally, and pre-existing
  tree-wide findings in files Prompt 3 did not touch.

Clone caveat, the largest reproducibility gap found: none of the
above Prompt 3 or #003 material is on remote main. HEAD is
`cbcbc66`; the Prompt 3 code and test changes are uncommitted
modifications and the #003 and Prompt 3 experiment trees are
untracked (section 1). A researcher who clones the public repo
today gets the 377-test baseline without F1 to F6, without
Experiment #003, and without this audit's evidence base. Every
reproducibility statement above is conditional on access to this
working tree. Classification: VERIFIED from `git status` in this
audit.

## 5. Developer experience friction (documentation inspection only)

The parent is running the actual install separately; everything
in this section is a doc-inspection finding, not an install
result, except the import probes in A-26, which were run.

- Install path naming (A-28): the distribution is
  `world-engine`, the import is `world`, the repo is
  `world-workstate-infrastructure`, and two of three `world-*`
  console scripts run the legacy engine. Nothing in `README.md`
  Install warns about any of this. Highest DX friction found.
- Quickstart accuracy: the `README.md` Quickstart and the
  Agent A / Agent B handoff walkthrough were checked line by
  line against `src/world/core.py` and match the API
  (`World("my-project")`, `update`, `checkpoint`, `state()`,
  `verify()` returning True, `InvariantViolation` carrying `seq`
  and `reason`, history rows in the order shown).
  `examples/quickstart.py` exists, is self-contained (it sets a
  throwaway `WORLD_DIR`), and matches its docstring. No
  correction needed. One nit: the README Quickstart does not
  mention that `World("my-project")` persists under `~/.world/`
  (or `$WORLD_DIR`), which the Architecture section does state;
  a first-time user meets the persistence location late.
- Server first run (A-2): the Install section presents
  `pip install -e ".[server]"` and the CLI and HTTP section
  presents `world serve` with the stale fail-open text. Post-F2,
  a new user who follows the docs, starts the server without a
  key, and posts an update gets 401 with no doc telling them
  about `WORLD_API_KEY` setup or `--allow-unauthenticated` for
  local development. The code's 401 hint and the server log
  message do explain it at runtime, which limits the damage.
- Handoff API reachability (A-26): the README handoff pattern
  teaches top-level imports from `world`, but the Prompt 3
  additions live only under `world.handoff`. Either fix is
  cheap; leaving both unfixed guarantees the new API is missed.
- Extras and skips: the Install section correctly distinguishes
  core (zero dependencies), `[server]`, and `[test]`, and notes
  that without the extras, server tests skip cleanly. The CI
  matrix (Python 3.11, 3.12, 3.13) matches `pyproject.toml`
  `requires-python = ">=3.11"` and classifiers. No correction
  needed beyond A-10.
- Legacy surface area: a new user browsing the tree meets
  `app.py`, `engine.py`, and `import_transcript.py` at the root,
  `src/world_engine/`, `src/world_sdk/`, `docs/SDK.md`, and a
  `frontend/` app, all legacy, before they find any marker
  except the README Legacy section near the end. See section 7.

## 6. Security posture summary

Full source: `docs/SECURITY.md` Part A (current, Prompt 3
amended) and `experiments/prompt3/AUDIT.md` sections A, D, E;
`experiments/prompt3/REPORT.md` section H.

WORLD is tamper-evident, not immutable. `verify()` in
`src/world/core.py` recomputes the SHA-256 chain and detects
in-place edits to any row field, middle-row deletion, and row
reordering, each pinned by a `*_detected` test in
`tests/test_redteam.py`. `verify()` does not detect tail
truncation (rollback), a full chain rewrite with recomputed
hashes (the row hash is unkeyed, ADR 0002), or forks (two copies
extended differently both verify). The defense against those
three is out-of-band: HMAC or Ed25519 signed tips
(`sign_tip` / `verify_tip`, `sign_tip_ed25519` /
`verify_tip_ed25519`, with Ed25519 key rotation), which detect
truncation and rewrite only for a holder who stored a tip
out-of-band and checks it. Classification: VERIFIED by the
red-team suite, including `*_undetected_documents_limit` tests
that assert the undetected attacks succeed.

Two tables sit outside the chain. The checkpoints table was
partly closed by F3a: a checkpoint now records the pinned row's
hash and `state(checkpoint=)` and `resume()` verify it before
serving (`test_checkpoint_repoint_detected`). Residual: the pin
lives in the same database, so an attacker who rewrites both the
seq and the `pinned_hash` defeats it, `verify()` itself still
does not cover the checkpoints table, and pre-F3a checkpoints
carry no pin and are served unverified. The idempotency table
remains fully outside the chain: deleting a key row lets a retry
commit twice while the chain verifies
(`test_idempotency_deletion_enables_double_apply_documents_limit`).
Binding idempotency keys into the row hash (F3b) would change
the hash format and break verification of existing databases; it
was framed as a stop-and-ask item in Prompt 3, was not approved,
and remains undecided. Classification: VERIFIED limits; F3b
NEEDS DECISION.

Identity and HTTP posture. `actor` is self-asserted everywhere
(free-text caller-supplied, hash-covered after the fact, never
authenticated); there is no per-actor identity and no RBAC
(ADR 0006 open). F4 narrows this only for a server configured
with a fixed `actor`, which overrides body-supplied labels.
Since F2 the `world` HTTP server fails closed: with no API key
configured, write routes return 401 unless unauthenticated
writes were explicitly allowed (`--allow-unauthenticated`);
read routes stay open in every mode, including rejected
proposals with their full documents. The legacy `world_engine`
API retains its own gate described in `docs/SECURITY.md` Part B
and was not changed by F2. Classification: VERIFIED by
`tests/test_world_server_security.py` for the primitive server.

Net assessment: the security documentation is the most current
documentation in the repo. Part A of `docs/SECURITY.md`,
`research/LIMITATIONS.md` system limits, and the server module
docstring all agree with the code post-Prompt 3. The stale
security text is in `README.md` (A-2) and in Part B's planned
hardening list (A-25, recommend-only).

## 7. Documentation architecture assessment

Current and trustworthy (agree with code and artifacts as of
2026-11-04 or 2026-11-05):

- `docs/SECURITY.md` Part A: current threat model, Prompt 3
  amended (F2, F3a residual, F4).
- `experiments/prompt3/AUDIT.md`, `REPORT.md`, `BENCHMARKS.md`,
  and `revalidation/RESULTS.md`: the design and evidence record
  for the current code. Uncommitted and untracked, see section 4.
- `experiments/experiment-003/REPORT.md` plus its `protocol.md`,
  `analysis/`, and preserved `results/`: the current handoff
  evidence. Untracked.
- `research/RESEARCH_OVERVIEW.md` classification table (Prompt 3
  rows): current, subject to A-14 and A-15. Its prose sections
  are not current (A-16, A-18).
- `research/LIMITATIONS.md` system-limits sections: Prompt 3
  amended and accurate. Its experiment sections are not (A-19,
  A-20).
- `CHANGELOG.md` Prompt 3 entries: accurate (A-23).
- `docs/state-model.md` implementation note: accurate (A-24).
- `docs/spec/protocol-verification.md`: accurate and still
  matches the checker (1,220,255 states, P1 to P6); dated
  2026-10-15 and unaffected by Prompt 3, correctly so, since no
  change altered the checked transition semantics
  (`experiments/prompt3/REPORT.md` section E).

Stale as wholes (every claim may be dated-true; the file as a
present-tense document misleads):

- `README.md`: the front door. Findings A-1 to A-10 concentrate
  here. It was not touched by Prompt 3 at all (it does not appear
  in the Prompt 3 diff), which is the single root cause of most
  of this register.
- `STATUS.md`: a 2026-11-02 dashboard still presenting itself as
  the single pointer (A-11 to A-13).
- `research/HYPOTHESIS.md` and `research/RELATED_WORK.md`
  evidence and gaps sections: pre-#003 (A-21, A-22).

Legacy (kept for the record, describing `world_engine` or
`world_sdk`, not the primitive; risk is discovery order, not
falsehood, except where noted):

- `docs/SECURITY.md` Part B (with the A-25 presentational risk).
- `docs/SDK.md` (`src/world_sdk` offline client), `docs/VISION.md`
  (WORLD / MIND / REALITY, intent ledger vocabulary),
  `docs/demo-script.md`, `docs/development-log.md`,
  `docs/experiment-handoff.md`, `docs/thesis-challenge.md`,
  `docs/startup/`, `docs/benchmarks/` except where cited as
  dated records, `research/comparisons.md` (the survey
  `research/RELATED_WORK.md` extends; it predates #003 and F1).
- Duplication risk: `docs/hypothesis.md` (fuller internal
  version) vs `research/HYPOTHESIS.md` (research-facing
  statement that says it is "kept in sync" with it). Both are
  pre-#003; when A-21 is fixed, both need the same amendment or
  the sync claim becomes the next inconsistency. The same
  pattern exists for `docs/experiment-001-results.md` and
  `docs/experiment-002/` (primary records, correctly frozen as
  artifacts; they should be treated as evidence, not updated).

Architecture verdict: the repo does not lack documentation; it
lacks a propagation path. Prompt 3 updated the documents closest
to the code (SECURITY, LIMITATIONS system sections, the overview
table, state-model note, CHANGELOG) and none of the documents a
new reader meets first (README, STATUS, HYPOTHESIS, RELATED_WORK
prose). Prompt 6 exists, on this evidence, to close exactly that
propagation gap.

## 8. Summary: corrections for Prompt 6 phases B to G vs recommendations

Recount used here, by per-entry severity tag in section 3:
CONTRADICTED 16 (A-1, A-2, A-3, A-4, A-5, A-6, A-10, A-11, A-12,
A-15, A-16, A-17, A-22, A-26, A-27, A-28; A-6, A-16, and A-22
are mixed entries counted once as CONTRADICTED).
STALE 12 (A-7, A-8, A-9, A-13, A-14, A-18, A-19, A-20, A-21,
A-23, A-24, A-25).
Total register entries: 28. Two seed suspicions were refuted in
whole or part and are recorded as such, not as defects: the
CHANGELOG Prompt 3 entries exist and are accurate (A-23), and
the RESEARCH_OVERVIEW system paragraph AgentState field list is
accurate (A-18); the state-model suspicion was partly refuted
because the 2026-11-04 implementation note is accurate (A-24).

Corrections that belong in Prompt 6 phases B to G (documentation
corrections only; no code change, no commit, no push implied by
this audit):

1. README phase: A-1 (409, three places), A-2 (fail-closed
   server), A-3 (streaming verify, roadmap removal), A-4
   (verify wording), A-5 (replay wording), A-6 (roadmap and
   revision framing, add #003), A-7 (Prompt 3 paragraph and
   handoff API), A-9 (research section and status labels),
   A-10 (CI wording), A-28 documentation note (name split).
2. STATUS phase: A-11, A-12, A-13 (regenerate, amend, or retire
   the dashboard in favor of the overview).
3. Research docs phase: A-14 (supersede the 377 row), A-15
   (relabel the CI row as a 2026-11-02 record; the recheck
   itself is a separate run), A-16 (overview prose), A-17
   (five status labels), A-19 and A-20 (LIMITATIONS experiment
   sections), A-21 (HYPOTHESIS #003 verdicts, mirrored in
   `docs/hypothesis.md`), A-22 (RELATED_WORK helper list and
   gap 1).
4. Docs phase: A-23 (CHANGELOG ordering and a #003 entry),
   A-24 (state-model status split and field-name mapping),
   A-26 documentation half (document `world.handoff` as the
   import path for the Prompt 3 API).

Recommendations for later (recommend-only; each needs its own
decision and is not assigned above):

- A-8: pointer from the README performance table to
  `experiments/prompt3/BENCHMARKS.md`.
- A-18: refresh the overview System paragraph and Performance
  pointer.
- A-23 ordering half, if append order is a deliberate
  convention.
- A-25: Part B Planned hardening cross-pointer in
  `docs/SECURITY.md`.
- A-26 code half: export `Assumption`, `project_state`,
  `revision_chain`, and `validate_state` from `world`.
- A-27: unify the FastAPI version with `world.__version__`.
- A-28 code half: rename the distribution or the legacy
  `world-import` and `world-server` scripts.
- Pin `ruff` and `mypy` versions in `.github/workflows/ci.yml`
  (section 4), so lint is reproducible.
- Re-run the 1.06M-row soak post-F5 before quoting any at-scale
  memory figure other than the dated 2026-10-15 record.
- Human-grade the preserved 25 percent subset of #003 (18
  continuations) and design harder revision tasks that break
  the M5 ceiling, per `experiments/experiment-003/REPORT.md`
  Recommended next steps. Without that, the revision question
  stays unresolved no matter how the docs are worded.
- Decide F3b (idempotency keys in the row hash) on its own
  review; it is the only open item in this audit that would
  break verification of existing databases.

End of audit.
