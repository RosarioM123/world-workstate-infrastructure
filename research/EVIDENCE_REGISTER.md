# Evidence Register

**Purpose.** Every quantitative or guarantee claim made in
`README.md` and `research/PAPER.md`, mapped to the artifact in
this repository that supports it, its evidence classification,
and its caveat. If a claim cannot be traced to an artifact here,
it does not belong in either document; the removals section at
the end lists what Phase F of Prompt 6 took out on exactly that
ground.

**Compiled:** 2026-11-05 (Prompt 6, Phase F). Claims were checked
against the working tree as of that date, which includes the
uncommitted Prompt 3 changes and Experiment #003.

**Classifications** (defined in `research/RESEARCH_OVERVIEW.md`):
VERIFIED, EXPERIMENTALLY OBSERVED, DOCUMENTED, PRELIMINARY,
NEEDS VALIDATION.

## Claims in README.md

| Claim (as stated) | Source artifact | Classification | Caveat |
|---|---|---|---|
| 409 tests in the suite, count as of 2026-11-05 | Full suite runs 2026-11-04 (`experiments/prompt3/REPORT.md` section E) and 2026-11-05 (Prompt 6 sessions, three runs, 409 passed each) | VERIFIED | Count changes when tests are added; it demonstrates software behavior, not agent reliability |
| Model checker: 1,220,255 explored states, P1 to P6 hold, mutation test produces the P4 counterexample | `spec/model_check.py`; `docs/spec/protocol-verification.md`; re-run 2026-11-05 in the Prompt 6 audit and reproduction sessions | VERIFIED | Bounded configurations (2 to 3 writers, 2 to 3 operations); the TLA+ transcription has never been run through TLC |
| Tamper fuzzing: 500 of 500 seeded mutations detected, plus 450 under alternate seeds | `tests/test_verify_fuzz.py` and its 2026-10-15 commit record | DOCUMENTED | Counts not re-measured in the 2026-11-02 audit or in Prompt 6 |
| Hypothesis stateful testing against a reference model (1,526 operations, zero divergences) | `docs/spec/stateful-testing.md` (recorded 2026-10-15) | DOCUMENTED | Exact operation counts from the recorded run |
| Crash consistency: 15 of 15 recorded kills recovered; 39 further rounds (2026-11-02), zero durability violations | `experiments/crash-consistency/RESULTS.md`; `experiments/crash-consistency/FINDINGS-2026-11-02.md` | DOCUMENTED as recorded; underlying property VERIFIED by re-exercise | Process death only; host and power failures out of scope |
| Lost-update: 33 of 50 lost unprotected (95% CI 0.52 to 0.78), 0 of 50 with `expected_version` plus retry | `experiments/lost-update/RESULTS.md`; `experiments/lost-update/PREREGISTRATION.md` | DOCUMENTED | Agents were scripted, not LLMs |
| Experiment #001: 5/5 decisions with rationales, 7/7 assumptions with confidence, zero errors | `docs/experiment-001-results.md` | DOCUMENTED, preliminary | n=1, one model family |
| Experiment #002: reference means Intel 3.92 vs 3.58 vs 3.33; Disney 4.45 vs 4.09 vs 2.82; summary within 0.36 in the replication; revision history 2/5 in both runs | `docs/experiment-002/results.md` sections 7, 11, 12 | DOCUMENTED, preliminary | n=1 per run, one model family, exploratory; means are reference values, not effect sizes |
| Experiment #003: M3 assumptions A 0.721 vs B 0.500 vs C 0.488; M1 decisions A 0.948 vs B/C 0.979; M5 revision 1.000 in all conditions; unverifiable additions 12 under A only; bundles 20,382 vs 6,142 vs 7,488 words (2.7x to 3.3x) | `experiments/experiment-003/REPORT.md`; `experiments/experiment-003/analysis/results.json` (regenerable byte-identically from preserved scores, verified 2026-11-05) | PRELIMINARY | Single model family; blind agent grading, no human grading; condition A was hand-authored Markdown and never exercised the `World` class |
| Prompt 3 revalidation: preservation at or near the #003 structured level through the shipped code path; no revision regression from projection | `experiments/prompt3/revalidation/RESULTS.md` | PRELIMINARY | Tasks R1, R2, C1 only; n=3 per cell; blind agent grading; includes a documented filing incident and re-grade (`PROVENANCE_NOTE.md`) |
| Performance table: update 1,339 ops/s; `expected_version` 692 ops/s; `state()` 3,794 ops/s; `verify()` 200,081 rows/s; `update_many` 54,975 ops/s | `docs/benchmarks/world-primitive.md` (measured 2026-10-15, one machine) | DOCUMENTED | Dated records, not guarantees; re-run before quoting |
| Contention: throughput plateaus near 810 ops/s past 8 threads; p99 degrades; correctness holds | `docs/benchmarks/contention.md` | DOCUMENTED | Same dated record set |
| Streaming `verify()`: peak-RSS delta 19.7 MB to 0.8 MB on a 20,000-version chain | `experiments/prompt3/BENCHMARKS.md`; re-measured 2026-11-05 via `experiments/prompt3/bench.py` (delta 1.1 MB) | VERIFIED at the 20,000-version scale | The 1.06M-row soak predates F5 and was not re-run at scale |
| Soak: 1.06M rows; `verify()` 75,921 rows/s at 659 MB RSS (2026-10-15) | `experiments/soak/RESULTS.md`, `experiments/soak/results.json` | DOCUMENTED | Pre-F5 record; stated in the README as historical |
| Checkpoints carry a pinned row hash, verified on read and resume (F3a) | `src/world/core.py` (`checkpoint`, `_verify_checkpoint_pin`); `tests/test_redteam.py::test_checkpoint_repoint_detected` | VERIFIED | Pin lives in the same database; rewriting seq and pin together defeats it; pre-F3a checkpoints carry no pin |
| HTTP writes fail closed by default; `--allow-unauthenticated` is the explicit opt-in (F2) | `src/world/server.py` `_guard`; `tests/test_world_server_security.py`; `docs/SECURITY.md` | VERIFIED | Read routes stay open in every mode, by design |
| `verify()` detects in-place edits, middle-row deletion, reordering; does not detect tail truncation, full consistent rewrite, or forks | `tests/test_redteam.py` (detection tests and `*_undetected_documents_limit` tests); `docs/SECURITY.md` Part A | VERIFIED | Signed tips are the out-of-band defense and only help a holder who stored a tip |
| Coverage 92.71% (stated in STATUS.md, measured for the release assessment) | CI coverage command run 2026-11-05: `pytest tests/ -q --cov`, total 92.71% branch coverage | VERIFIED as measured | The CI gate is 85%; coverage is a test-thoroughness measure, not a correctness proof |
| WORLD improves AI agent reliability in general | No artifact supports the general claim | NEEDS VALIDATION | Stated in the README only as unproven; the narrow #003 assumption-metadata result is the strongest current evidence |
| Revision-history preservation quality | #002 (failure) vs #003 (ceiling) conflict | NEEDS VALIDATION (unresolved) | The discriminating experiment has not been run |
| External validation of the reproduction package | `experiments/prompt6/VALIDATION_PROTOCOL.md` | NEEDS VALIDATION (status PENDING) | Zero external reviewers have completed the protocol |

## Claims in research/PAPER.md

The paper cites its source inline for nearly every number; this
table registers the load-bearing claims by section.

| Paper claim | Source artifact | Classification | Caveat |
|---|---|---|---|
| Abstract and Section 5: model checker explored 1,220,255 states (165,579 + 935,111 + 119,565), P1 to P6 hold, mutation test catches the injected P4 violation | `spec/model_check.py`; `docs/spec/protocol-verification.md` | VERIFIED | Bounded configurations; TLA+ transcription never run through TLC (stated in the paper) |
| Section 7.1: #001 governance result (5/5, 7/7, zero errors) | `docs/experiment-001-results.md` | DOCUMENTED, preliminary | n=1 |
| Section 7.2: #002 reference means, revision 2/5 both runs (journal 3 on Intel, 4 on Disney), summary within 0.36, relabeling mechanism | `docs/experiment-002/results.md` sections 7, 11, 12, 14 | DOCUMENTED, preliminary | n=1 per run; Disney unsupported-assumption counts recorded as unverifiable against the key, stated as such in the paper |
| Section 7.3 and 7.4: #003 full metric table (M1 to M10), verdict composition 24/15/6 vs 6/30/9 vs 6/29/10 over 45 items, hypothesis verdicts H1 to H5 and N1 to N4, unverifiable additions 12 vs 0 vs 0, word counts | `experiments/experiment-003/REPORT.md`; `analysis/results.json`; `analysis/tables.md` | PRELIMINARY (M3 also labeled EXPERIMENTALLY OBSERVED within the design) | Single model family; no significance tests; condition A hand-authored, never exercised the code (stated in the abstract and Sections 6.2, 7.4) |
| Section 7.5: revalidation per-task scores (R1 at ceiling; R2 full 0.958/0.500/0.963, projected 0.875/0.500/0.981; C1 decision retention 1.000 vs #003 A 0.750, unverifiable additions 0 vs 12; projection savings 3.5%, 13.8%, 4.0%) | `experiments/prompt3/revalidation/RESULTS.md` | PRELIMINARY | n=3 per cell; R2 M1 projection dip recorded at equal prominence in the paper |
| Section 7.6: lost-update 33/50 vs 0/50; fuzz 500/500 plus 450; crash 15/15 plus 39 rounds; Hypothesis 1,526 operations, zero divergences; C# verifier 4 tests; soak 1.06M rows, 69,714 and 2,473 ops/s, p50 0.36 to 0.39 ms, verify 75,921 rows/s at about 659 MB RSS | `experiments/lost-update/RESULTS.md`; `tests/test_verify_fuzz.py`; `experiments/crash-consistency/`; `docs/spec/stateful-testing.md`; `tests/test_csharp_verifier.py`; `experiments/soak/RESULTS.md` | DOCUMENTED (crash property VERIFIED by re-exercise; C# verifier VERIFIED) | As tabled in `research/RESEARCH_OVERVIEW.md`; the paper names the classification source per item |
| Section 8: security guarantees and limits, F2 fail-closed, F3a pin and its residual, F4 actor override, self-asserted actor, invariants on the handle | `docs/SECURITY.md` Part A; `tests/test_redteam.py`; `tests/test_world_server_security.py`; `experiments/prompt3/AUDIT.md` sections A, D, E | VERIFIED (behavior under tested conditions) | Field crypto construction is custom and not independently reviewed; Ed25519 implementation is not constant-time; both stated in the paper |
| Section 9: performance records (1,339 / 692 / 3,794 / 200,081 / 54,975 ops/s; contention plateau near 810 ops/s, p99 0.93 ms to 216.70 ms; Prompt 3 before/after verify 0.109 s to 0.096 s, RSS delta 19.7 MB to 0.8 MB, blame 130.7 ms to 60.7 ms; Ed25519 about 147 signs/s and 109 verifies/s) | `docs/benchmarks/world-primitive.md`; `docs/benchmarks/contention.md`; `experiments/prompt3/BENCHMARKS.md`; `docs/SECURITY.md` | DOCUMENTED (F5 memory result VERIFIED at 20,000-version scale) | Single machines, dated; the paper states figures are records, not guarantees, and notes the single-update variance reading as host variance per the source |
| Section 4.6 and elsewhere: Prompt 3 changes F1 to F6 as implemented; F3b not approved and not built; suite 377 to 409 | `experiments/prompt3/REPORT.md`; `experiments/prompt3/AUDIT.md` | VERIFIED against the working tree | All Prompt 3 work is uncommitted; the paper states the manuscript reflects the working tree |
| Section 12 and closing statement: the paper is an unpublished manuscript, not peer-reviewed | Statement of fact about the document itself | VERIFIED | No external validation has occurred; the validation protocol is PENDING |

## External citations in research/PAPER.md

Each external reference was verified for existence and
bibliographic details by web search during the Phase C session
on 2026-11-05, before inclusion. References that could not be
verified were excluded by rule; none of the nine below failed
verification.

| Reference | Verified details |
|---|---|
| [1] Packer et al., MemGPT: Towards LLMs as Operating Systems, 2023 | arXiv:2310.08560 |
| [2] Park et al., Generative Agents: Interactive Simulacra of Human Behavior, UIST 2023 | arXiv:2304.03442; DOI 10.1145/3586183.3606763 |
| [3] Martin Fowler, Event Sourcing, 12 December 2005 | martinfowler.com/eaaDev/EventSourcing.html |
| [4] Josefsson and Liusvaara, EdDSA, RFC 8032, January 2017 | rfc-editor.org/info/rfc8032 |
| [5] Shinn et al., Reflexion: Language Agents with Verbal Reinforcement Learning, NeurIPS 2023 | arXiv:2303.11366 |
| [6] Yao et al., ReAct: Synergizing Reasoning and Acting in Language Models, ICLR 2023 | arXiv:2210.03629 |
| [7] SQLite Project, Write-Ahead Logging documentation | sqlite.org/wal.html |
| [8] W3C, PROV-DM: The PROV Data Model, Recommendation 30 April 2013 | w3.org/TR/2013/REC-prov-dm-20130430 |
| [9] Leslie Lamport, Specifying Systems, Addison-Wesley, 2002 | ISBN 9780321143068 |

## Claims removed or downgraded in Phase F

Removed from `README.md` (old text contradicted the code or the
recorded evidence; audit references are to
`experiments/prompt6/AUDIT.md`):

1. **"Deterministic replay" as a primitive feature** (opening and
   Correctness contract). Removed. The primitive stores full
   snapshots; `state(version=N)` is retrieval. Replay exists only
   in the legacy `world_engine`, and the README now says so in the
   Legacy section. (A-5)
2. **"`verify()` pinpoints the first bad row."** Removed.
   `verify()` returns a bool only. The README now states it
   recomputes every link and returns False on any mismatch. (A-4)
3. **API-key gate "fail-open with a warning when unset".**
   Replaced with the F2 fail-closed behavior and the
   `--allow-unauthenticated` opt-in. (A-2)
4. **Test count 377 (three places).** Replaced with 409, dated
   2026-11-05. (A-1)
5. **"`verify()` is O(n) in time and memory" as a current
   limitation, and "Streaming `verify()`" as roadmap future
   work.** Replaced: time is O(n), memory is constant in chain
   length since F5; the 659 MB figure remains only as the dated
   pre-F5 soak record. (A-3)
6. **Revision history framed as "a current failure, not just an
   untested area", and Experiment #003 listed as future roadmap
   work.** Replaced with the unresolved framing (#002 failure
   against #003 ceiling) in the README, STATUS.md,
   `research/RESEARCH_OVERVIEW.md`, `research/LIMITATIONS.md`,
   `research/HYPOTHESIS.md`, and `research/RELATED_WORK.md`; #003
   is reported as executed. (A-6, A-16, A-19, A-21, A-22)
7. **"CI also runs ruff and mypy on Python 3.11 to 3.13".**
   Corrected: pytest runs on 3.11 to 3.13; the lint job runs on
   Python 3.12 only. (A-10)
8. **Three-status evidence preamble (VERIFIED, DOCUMENTED,
   NEEDS VALIDATION).** Replaced with the five-status list in the
   README and `research/RESEARCH_OVERVIEW.md`. (A-9, A-17)
9. **CI status row presented as current ("CI on the current
   remote main ... lint job fails").** Downgraded in
   `research/RESEARCH_OVERVIEW.md` to a dated 2026-11-02 record;
   the current remote CI state is labeled NEEDS VALIDATION (not
   re-queried in the Prompt 6 session). (A-15)

Flagged but NOT changed (code changes outside Prompt 6 scope;
recorded as recommendations in the audit and the release
readiness document):

- Top-level exports: `Assumption`, `project_state`,
  `revision_chain`, `validate_state` are importable only from
  `world.handoff`, not from `world`. The README now documents
  the `world.handoff` import path (documentation half of A-26);
  the export change itself is a separate approval.
- `src/world/server.py` builds FastAPI with version "0.2.0"
  while the package version is 0.1.0 (A-27). Recommend deriving
  from `world.__version__`.
- Distribution name `world-engine` vs import package `world`,
  and the legacy `world-import` / `world-server` console scripts
  (A-28). The README Install section now documents the split;
  any rename is a maintainer decision.
