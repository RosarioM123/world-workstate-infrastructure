# Prompt 6 Report: Independent Research Validation and Public Release Preparation

**Date:** 2026-11-05. **Scope rule honored throughout:** no commits,
no pushes, no published release, no package upload. Everything
below is uncommitted in the working tree for the user's review.
No raw experimental artifacts were modified; the Experiment #003
analysis was exercised only on scratch copies outside the repo.

## 1. Independent audit summary

`experiments/prompt6/AUDIT.md` (922 lines): an external-researcher
review of README.md, STATUS.md, research/*.md, docs/**, and
CHANGELOG.md against the code, tests, and benchmark artifacts.
Register: **28 inconsistencies, 16 CONTRADICTED and 12 STALE.**
Two seed suspicions were refuted in whole or part and recorded as
such (the CHANGELOG does carry accurate Prompt 3 entries; the
overview's AgentState field list is accurate), and the
state-model suspicion was partly refuted (its 2026-11-04
implementation note is accurate).

Top findings: the README, untouched by Prompt 3, was the root
cause of most of the register (stale 377 test count in three
places; the server described as fail-open a full change after F2
made it fail closed; `verify()` described as O(n) memory with
streaming listed as future work after F5 shipped it; a
"deterministic replay" claim for a primitive that stores
snapshots; revision history framed as a settled current failure
with no #003 context; Experiment #003 listed as future roadmap
work after it completed). Three code-level findings were
registered but, per scope, only documented, not fixed: top-level
exports lag the handoff API (A-26), the FastAPI app reports
version "0.2.0" against package 0.1.0 (A-27), and the
distribution name `world-engine` plus two legacy `world-*`
console scripts create a naming split (A-28). The audit also
verified by re-run: suite 409 passed (twice), model checker
1,220,255 states with P1 to P6 holding and the mutation test
catching the injected P4 violation. Its largest reproducibility
finding: none of the Prompt 3 or #003 material is on remote main,
so every reproducibility statement is conditional on this working
tree.

## 2. Reproduction package

`REPRODUCE.md` at the repo root. Every command in it was executed
in the Prompt 6 session on 2026-11-05 (Python 3.12.3, Linux
7.0.0-39-generic x86_64, 4 virtualized CPUs), and re-executed at
final verification:

- Full suite: **409 passed, 1 warning** (78.14s first run; 61.88s
  at final verification; the audit's two runs also 409).
- Model checker: **1,220,255 states** (165,579 + 935,111 +
  119,565), P1 to P6 hold, mutation test catches the injected P4
  violation.
- Benchmark script (`experiments/prompt3/bench.py`): verify on a
  20,000-version chain ok in 0.154s (129,763 rows/s) with peak RSS
  delta 1.1 MB, the F5 streaming result; update_many 29,750/s;
  blame 92.4 ms.
- Experiment #003 analysis: run on a scratch copy, the
  regenerated `results.json` and `tables.md` were **byte
  identical** to the preserved files (72 continuations scored).
- Fully reproducible vs not, stated explicitly in the document:
  the #001, #002, #003, and revalidation agent runs themselves
  are NOT reproducible (in-environment agent sessions, single
  model family, no seed control); analysis of their preserved
  outputs IS. Human grading of #003 does not exist. The 1.06M-row
  soak was not re-run post-F5. No step needs external services or
  credentials except the initial clone.

## 3. Paper

`research/PAPER.md` (18,590 words): full 12-section structure
(Abstract, Introduction, Problem Formulation, Related Work,
Architecture, Formal Properties, Experimental Methodology,
Results, Security and Threat Model, Performance, Limitations,
Future Work, Conclusion) plus References split into external
sources and project artifacts. Results use only #002, #003, and
revalidation numbers, each labeled PRELIMINARY where applicable
with n and protocol caveats; the paper states plainly in the
abstract and methodology that #003 never exercised the World
class and that the revalidation is the first code-path run at
small n. Negative findings appear at equal prominence (revision
history, summary parity, unverifiable additions, context cost).
Nine external citations, each verified for existence and
bibliographic details by web search in the Phase C session
before inclusion (MemGPT arXiv:2310.08560; Generative Agents
arXiv:2304.03442, DOI 10.1145/3586183.3606763; Fowler event
sourcing, 2005; RFC 8032; Reflexion arXiv:2303.11366; ReAct
arXiv:2210.03629; SQLite WAL documentation; W3C PROV-DM, 2013;
Lamport, Specifying Systems, 2002). The paper ends with the
explicit statement that it is an unpublished manuscript, not
peer-reviewed. Spot-checked in this session against the evidence
base: all #002, #003, revalidation, systems, and performance
figures match their source artifacts.

## 4. Diagram

`docs/architecture.md` with the standalone editable source at
`docs/architecture.mmd`. Components: agent layer, handoff API
(AgentState, save_state, load_state, project_state,
revision_chain), World core (update protocol, invariant judging,
OCC), SQLite persistence (versions, checkpoints with pinned
hashes, idempotency, field_keys), integrity (hash chain verify,
HMAC and Ed25519 signed tips, Merkle proofs), server and CLI
surfaces, model checker. Every named component was verified
against the code (the four tables are exactly the `_SCHEMA` in
`src/world/core.py`; routes match `src/world/server.py`). Data
flow and trust boundaries are drawn; deliberate omissions (no
replication, no consensus, no RBAC) are listed as omissions, not
drawn as components. Syntax was validated by actually parsing
with mermaid@10 under jsdom: parse OK.

## 5. Demo

`demo/` at the repo root: `common.py` (shared world definition,
a battery-supplier memo scenario with a 5,000 USD spend-cap
invariant and a demo tip key labeled as not a secret),
`agent_a.py`, `agent_b.py`, `README.md` with expected output
captured from the real run, and `recorded-demo-script.md`. Run
end to end in this session and re-run at final verification.
Agent A: seq 1 committed (spend 1,200), seq 2 REJECTED (9,000
over the cap, state unmoved), seq 3 save_state (decisions D1 and
D2, assumptions A1 medium and A2 low), seq 4 D3 supersedes D1
with rationale and evidence, checkpoint "handoff-ready", HMAC
tip signed, verify() True. Agent B, a separate process, derived
everything from the world file at runtime: verify() True,
verify_tip True, authoritative decisions D2 and D3 only, D1
shown as superseded with its full revision chain, assumptions
with confidence levels, the rejection on record, then one new
committed update (seq 5) and a final verify() True. The
conventional-summary comparison panel is limited to the contrast
#003 supports: confidence level and fact-versus-assumption /
supersession status are what summaries measurably lost. No
hardcoded outputs; agent_b reads the world file. One design
note recorded in the demo README: agent_b is not idempotent (it
appends one version per run by design); agent_a resets the demo
world each run.

## 6. Clean-install instructions and result

Documented in `REPRODUCE.md` and executed twice (before and after
the Phase F documentation changes). Fresh venv outside the repo
(`~/cleanroom/venv`), non-editable `pip install` of the local
repo path installed world-engine 0.1.0; the `world` CLI responds;
a smoke script run from a different working directory exercised
create, update, checkpoint, save_state/load_state with the new
handoff schema (D1 accepted at v2, superseded at v3; D2 accepted
with supersedes D1; assumption A1 high/active), revision_chain,
and verify(): **SMOKE OK**. No installation-blocking packaging
defects, so pyproject.toml was not changed. Two cosmetic metadata
gaps recorded: no `authors` declared (pip shows an empty Author),
and pip 24.0 rendered the Home-page line empty despite
`[project.urls]` being present.

## 7. README changes

`README.md` rewritten in the mandated order: problem, what WORLD
does, how it differs (only as supported), technical summary,
what has been demonstrated (PRELIMINARY labels and the #003
scope caveat inline), how to run it (pointing to REPRODUCE.md
and demo/), what remains unproven. Every README inconsistency in
the audit register was corrected (A-1 to A-10, plus the A-26
documentation half and the A-28 naming note). STATUS.md was
regenerated as a current 2026-11-05 dashboard (A-11 to A-13).
CHANGELOG.md gained Experiment #003 and Prompt 6 entries in
Unreleased (A-23). The research docs were amended: overview
five-status preamble, superseded 377 row, CI row relabeled as a
dated record, #003 added to the evidence base, revision framing
(A-14 to A-18); LIMITATIONS revision amendment and #003
methodology bullet set (A-19, A-20); HYPOTHESIS #003 verdict
paragraph, mirrored by a note in docs/hypothesis.md (A-21);
RELATED_WORK helper list and gap 1 (A-22); state-model status
split and field-name mapping (A-24); SECURITY Part B
cross-pointer (A-25, recommend-only item, applied as a note).
CONTRIBUTING.md gained the model checker step and the
no-claims-inflation rule. License unchanged (MIT).

## 8. Release-readiness assessment

`experiments/prompt6/RELEASE_READINESS.md`. Version 0.1.0,
consistent between pyproject (dynamic) and `world.__version__`
(one inconsistency registered: the FastAPI app string "0.2.0").
Core has zero runtime dependencies; optional extras are unpinned
ranges (reproducibility weakness, recorded). CI: pytest on
Python 3.11, 3.12, 3.13; the lint job installs unpinned ruff and
mypy (recommendation: pin; CI not changed in this prompt).
Coverage measured with the CI command on 2026-11-05: **92.71%**
branch coverage, 85% gate reached, 409 passed. Clean-install:
passed (section 6). Blockers, in order: (1) Prompt 3,
Experiment #003, and Prompt 6 are uncommitted and unreviewed,
and remote main still shows the pre-Prompt-3 state; (2) no
release approval from the user; (3) external validation has not
happened (protocol PENDING); (4) GitHub description and topics
live outside the tree; (5) CI lint pinning should land first,
as its own reviewed change.

## 9. External validation protocol status

`experiments/prompt6/VALIDATION_PROTOCOL.md`: a seven-task
independent reproduction challenge (environment setup, suite,
model checker, benchmarks, #003 analysis reproduction, demo,
claim spot-check), what to record (setup time, errors, doc gaps,
per-task success, feedback), and success criteria (all seven
tasks completable from the documents alone; analysis outputs
byte-identical; no step needing the author). **Status: PENDING.
Zero external reviewers have completed it, and no document in
this tree claims otherwise.**

## 10. Evidence and limitations register summary

`research/EVIDENCE_REGISTER.md` maps every quantitative or
guarantee claim in README.md and research/PAPER.md to its source
artifact, classification, and caveat; verifies the paper's nine
external citations; and lists removals. Headline classifications:
the mechanism claims (model checker, protocol tests, tamper
boundary) are VERIFIED under tested conditions; the dated
performance and systems records are DOCUMENTED; all handoff
results are PRELIMINARY (#003 also EXPERIMENTALLY OBSERVED
within its design); the general reliability claim, revision
quality, human auditability, and external validation are NEEDS
VALIDATION. Limitations were not softened anywhere; the
LIMITATIONS.md amendments add #003's own limits (hand-authored
condition A, blind agent grading only, parity-gate ceiling,
unverifiable additions under A) at the same prominence as the
older ones.

## 11. Files created and modified

Created by Prompt 6:

- `REPRODUCE.md`
- `demo/agent_a.py`, `demo/agent_b.py`, `demo/common.py`,
  `demo/README.md`, `demo/recorded-demo-script.md`
- `docs/architecture.md`, `docs/architecture.mmd`
- `research/PAPER.md`, `research/EVIDENCE_REGISTER.md`
- `experiments/prompt6/AUDIT.md`,
  `experiments/prompt6/VALIDATION_PROTOCOL.md`,
  `experiments/prompt6/RELEASE_READINESS.md`,
  `experiments/prompt6/REPORT.md` (this file)

Modified by Prompt 6:

- `README.md` (rewritten), `STATUS.md` (rewritten)
- `CHANGELOG.md`, `CONTRIBUTING.md`
- `research/RESEARCH_OVERVIEW.md`, `research/LIMITATIONS.md`,
  `research/HYPOTHESIS.md`, `research/RELATED_WORK.md`
- `docs/hypothesis.md`, `docs/state-model.md`, `docs/SECURITY.md`
- `.gitignore` (one line: `demo/demo-data/`)

Not touched by Prompt 6: all `src/` and `tests/` modifications in
the tree are Prompt 3's; all raw experimental artifacts
(`experiments/**` results, outputs, scores, `docs/experiment-002/`)
are byte-identical to their pre-Prompt-6 state.

Final verification on the finished tree (2026-11-05): full suite
409 passed; model checker 1,220,255 states, P1 to P6 hold,
mutation test catches the injected violation; bench.py verify
0.096s on 20,000 versions, RSS delta 1.2 MB; quickstart runs;
demo pair runs end to end; #003 analysis byte-identical;
clean-install smoke OK after reinstalling the final tree.

## 12. Recommended publication and research directions

Publication, in dependency order:

1. Review and commit in reviewable units: Prompt 3 code and
   tests first (its own decision, still the user's), then
   Experiment #003, then the Prompt 6 documentation set. Until
   step 1 happens, the public repo contradicts this tree.
2. Pin ruff and mypy in CI as a separate small change, so the
   lint gate is reproducible before any release tag.
3. Fix the two one-line code nits in the same review pass if
   approved: export the F1 names from `world` (A-26) and derive
   the FastAPI version from `world.__version__` (A-27).
4. Only then consider a 0.1.0 tag and a PyPI upload, each with
   explicit approval; neither happened in this prompt.
5. Recruit two or three independent reviewers to run the
   validation protocol and record the first completed rows.

Research directions, in the order the evidence calls for them:

1. The discriminating revision experiment: harder chains, no
   parity gate on revision elements, human grading of the
   preserved #003 25 percent subset (18 continuations) first.
2. Explain the unverifiable-additions finding (12 under A, 0
   under B and C): is plausibility contagious from rich bundles?
3. Cross-model handoffs, when a model API credential exists.
4. Context-efficiency work on the structured bundle: F6
   projection saved only 3.5 to 13.8 percent on revalidation
   states; the 2.7x to 3.3x word cost is the standing price of
   the one demonstrated advantage.
5. Decide F3b (idempotency keys in the row hash) on its own
   review; it is the only open item that would break
   verification of existing databases.

## Claims found unsupported, removed or downgraded

Full detail in `research/EVIDENCE_REGISTER.md`; summary:

1. "Deterministic replay" for the primitive: removed (snapshots,
   not replay). Audit A-5.
2. "verify() pinpoints the first bad row": removed (bool only).
   A-4.
3. Server "fail-open with a warning": replaced with fail-closed
   F2 behavior. A-2.
4. Test count 377: replaced with 409, dated. A-1.
5. "verify() is O(n) in time and memory" as current, and
   streaming verify as future work: replaced (F5 shipped). A-3.
6. Revision history as a settled "current failure": downgraded
   to unresolved (#002 failure vs #003 ceiling) in six files.
   A-6 and dependents.
7. "CI runs ruff and mypy on Python 3.11 to 3.13": corrected to
   the 3.12-only lint job. A-10.
8. Three-status evidence preamble: replaced with five statuses.
   A-9, A-17.
9. CI status row as a current claim: downgraded to a dated
   2026-11-02 record; current remote CI state is NEEDS
   VALIDATION. A-15.
10. No claim in the paper or README asserts peer review,
    external validation, general agent reliability, or
    hallucination prevention; where those topics appear, they
    are labeled NEEDS VALIDATION or PENDING.
