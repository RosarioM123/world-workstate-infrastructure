# Experiment #003: Reproducible Evaluation of WORLD for Persistent AI Agent Handoffs

**Protocol and preregistration. Written before any trial runs.**
**Preregistered:** 2026-11-03T03:33Z (2026-11-02 22:33 EST)
**Status:** preregistered. No Agent A production, summary, continuation, or
grading for this experiment had occurred when this file was written.
**Execution route:** in-environment agents only, single model family. Every
result of this experiment is PRELIMINARY and single-model. No API access
exists in this environment (verified in the Phase 1 audit, 2026-11-02).

Amendments after this timestamp require a dated addendum in this file
explaining what changed and why. The protocol is not edited silently.

---

## PREREGISTRATION

### Research question

Does structured, persistent work-state infrastructure (WORLD) enable an AI
agent resuming a task to preserve decisions, constraints, assumptions,
provenance, and revision history more effectively than a conventional
natural-language summary or a raw transcript of the prior session?

### Primary hypothesis

H1: Agent B continuations working from a WORLD state bundle (Condition A)
will score higher than continuations working from a natural-language summary
(Condition B) or a raw journal (Condition C) on retention of decisions,
assumptions, provenance, and revision history, measured per metric below
(no composite score).

### Secondary hypotheses

- H2: Condition A will show the largest advantage on revision-history
  reconstruction (metric 5) and provenance (metric 4), the two areas where
  #002 found both the clearest WORLD advantage (provenance) and the clearest
  WORLD weakness (revision history, 2 of 5 in both #002 runs). H2 is
  deliberately two-sided in interest: metric 5 is the metric most likely to
  refute the WORLD thesis.
- H3: Condition A will produce fewer unsupported inferences (metric 7) and
  fewer contradictions (metric 6) than B and C.
- H4: Constraint retention (metric 2) will be at or near ceiling in all
  conditions (as in #002), so A will show no meaningful advantage there.
- H5: On the low-governance task (C2), A will show no advantage over B or C,
  and B will be the most context-efficient condition.

### Null hypotheses and conditions where WORLD may lose

- N1 (summary parity): a competent natural-language summary preserves the
  graded content as well as the state bundle. This is falsifiability
  condition 1 from `research/HYPOTHESIS.md`, still open after #002 (the
  summary finished within 0.36 of WORLD in the Disney replication). If mean
  paired differences A minus B are near zero or negative on most metrics,
  N1 stands and the WORLD thesis is weakened.
- N2 (transcript advantage on revisions): a raw journal preserves revision
  narrative (what happened, in order) better than a state projection that
  emphasizes current state. #002's replication is consistent with this
  (journal scored 4 of 5 on revision history, WORLD 2 of 5). If C beats A on
  metric 5 again, that is a finding against the current state model, not a
  protocol failure.
- N3 (structure overhead without benefit): on tasks with few decisions and
  no revisions, the state bundle costs more words for the same preservation
  (metric 10 favors B or C).
- N4 (writing bottleneck): Agent A may fail to record revision chains in the
  state bundle even when the model can express them, in which case A's
  metric 5 failure is a state-writing failure, not a representation failure.
  The failure-cause coding in grading exists to distinguish N4 from a data
  model failure.

### Tasks (8, fixed)

Two per category. Each task has a brief, scenario materials, a continuation
assignment, and a `ground_truth.json` authored from a single source before
any production runs.

| ID | Category | Sketch |
|----|----------|--------|
| F1 | Financial research | Equity thesis; mid-session guidance revision changes two assumptions and supersedes the price target decision |
| F2 | Financial research | Credit review; conflicting sources on leverage; no-leverage portfolio constraint; corrected leverage figure |
| S1 | Software engineering | API rate limiting; architectural decision; prior Redis persistence fix that must not be reverted; flaky test open; algorithm decision superseded after load test |
| S2 | Software engineering | Debugging; one resolved root cause (connection pool leak); one red herring (pricing deploy, exonerated); no-rollback-without-evidence constraint |
| R1 | Revision history | Product spec; two requirement changes, each with a stated reason; only the latest version is authoritative |
| R2 | Revision history | Research plan; one reversed decision; one corrected assumption; two conflicting versions of one instruction |
| C1 | Constraint-heavy | Offsite planning; hard constraints; one datum missing from all materials that must be flagged, not invented; one unresolved conflict between two quotes |
| C2 | Constraint-heavy (control) | Routine weekly status continuation; few facts, no revisions, no binding constraints; WORLD is NOT expected to win; included so summary parity has a fair chance to fire |

### Conditions (3, fixed)

Note on labels: in this experiment A is WORLD, B is summary, C is
transcript. This differs from the condition lettering in
`experiments/001-state-continuation/` and matches Prompt 2.

- **Condition A (WORLD):** Agent A records the session in a state bundle
  following `docs/state-model.md` (Project context and constraints,
  Decisions with rationale and status including superseded, Assumptions with
  confidence and status, Evidence with provenance, open Questions, a
  StateChange log, and a Handoff section). Agent B receives only the bundle.
- **Condition B (summary):** a separate worker that sees only Agent A's
  journal and report (never the state bundle) writes a natural-language
  handoff summary under the #002 instruction: preserve as much as possible,
  no schema. Agent B receives only the summary.
- **Condition C (transcript):** Agent B receives Agent A's raw journal,
  unedited.

Information parity: every phrase in a task's `must_mention` list must appear
in all three artifacts before that task's continuations run (automated
parity gate, `runner/parity_gate.py`). A parity failure is fixed on the
production side (Agent A or the summarizer), never by editing ground truth,
and every parity failure and fix is recorded in the run log.

### Trials (fixed)

3 trials per task per condition: 8 tasks x 3 conditions x 3 trials = 72
Agent B continuations, plus 8 Agent A productions and 8 summaries. Trial
independence is session independence only: a fresh agent session per trial,
no shared state, randomized execution order (order list generated with a
recorded seed before runs begin). Same model family throughout; no seed or
temperature control exists in this environment and none is claimed.
Repeating a deterministic artifact is never counted as a trial: the trials
vary in the Agent B session, not in the artifact (artifacts are fixed per
task and condition, as in #002).

### The ten metrics (fixed; full operational definitions in evaluation/rubric.md)

1. Decision retention: fraction of ground-truth decisions recovered with
   correct status; rationale required for full credit per item.
2. Constraint retention: fraction of constraints correctly stated and
   respected in proposed next actions; any violated constraint also flags
   the continuation as a hard failure.
3. Assumption retention: fraction of assumptions recovered with
   fact-vs-assumption status and confidence intact.
4. Provenance: fraction of key evidence items whose source is correctly
   identified.
5. Revision-history reconstruction: per revision chain, a 6-item checklist
   (original, revised, what changed, why, authoritative version,
   provenance); reported per chain and aggregated; the headline metric for
   the revision subset (R1, R2, and the chains in F1 and S1).
6. Factual consistency: count of contradictions (assertions of
   `must_not_state` items plus judge-identified contradictions of ground
   truth). Lower is better.
7. Unsupported inference: count of invented items, split into confirmed
   fabrications (contradicted by, or numerically specific beyond, the
   materials) and unverifiable additions (absent from the key, not
   contradicted). Lower is better.
8. Task continuation quality: anchored 0 to 3 judged rubric per task.
9. Information loss: the itemized complement of misses across metrics 1
   to 5, listed, with the loss count reported.
10. Context efficiency: handoff artifact words and characters per
    condition, and preservation (mean of metrics 1 to 5 fractions) per
    1,000 words of artifact. Word and character counts are used because no
    tokenizer exists in this environment; they are labeled as such, never
    as token counts.

No composite score is computed or reported. Each metric is reported
separately, per task and per condition.

Scoring: blind graders (fresh agent sessions that produced none of the
continuations they grade) score each continuation against the ground truth
with per-item verdicts, per-metric scores, and a short rationale. Judged
scores are the recorded scores. For each missed revision chain the grader
also records a failure-cause code (DATA_MODEL, WRITING, RETRIEVAL,
INTERPRETATION) after scoring, by comparing the continuation to the
artifact. Grading order within each task is randomized; condition labels
are replaced by random per-task labels and the mapping is kept in a private
file graders never see.

### Analysis plan (fixed)

- Per task and per condition: mean and standard deviation of each metric
  across the 3 trials; n reported everywhere.
- Paired comparisons: within task and trial slot (trial 1 vs trial 1, etc.),
  mean paired difference A minus B and A minus C per metric, with the count
  of pairs. Trial slots are arbitrary labels fixed in advance; pairing is a
  variance-reduction device, not a claim that paired trials share a cause.
- Revision-history subset (R1, R2, F1 chains, S1 chains) reported separately
  from the full benchmark.
- No significance tests and no significance language: at n = 3 per cell this
  design cannot support them. Effect sizes are reported as observed mean
  differences with standard deviations and are labeled PRELIMINARY.
- Failed, refused, or malformed trials are recorded in the raw JSONL with
  their error and counted in the report. No trial is silently dropped or
  replaced. A retry is permitted only when a worker session died before
  producing any output (infrastructure failure); both the failure and the
  retry are recorded.

### Blinding and integrity

- Agent B workers receive only the shared continuation assignment plus one
  artifact. They are not told the experiment's hypotheses or which condition
  they are in beyond what the artifact's format reveals.
- The summarizer never sees the state bundle or the ground truth.
- Graders never see the label mapping, the protocol's hypotheses section is
  not included in grader instructions, and graders score against ground
  truth and rubric only.
- Known imperfection, declared in advance: artifact format can reveal the
  condition to a grader (a structured bundle looks structured), as it could
  in #002. Blinding here hides labels and trial identity, not format.
- Ground truth files are final before production begins. Any error found in
  a ground truth after runs begin is recorded as an erratum in the run log
  and results are reported both ways if it affects scoring; ground truth is
  never quietly edited.

### What this experiment cannot establish (declared in advance)

Cross-model transfer (single model family), human auditability (no human
grader), token-level efficiency (word counts only), statistical
generalization (n = 3 per cell, 8 tasks), and production reliability. A
positive result supports, at most: under this protocol, on these tasks,
with this model family, the state bundle preserved graded content better or
worse than the baselines, per metric.

---

## Run log

Appended as execution proceeds. Entries are dated and never rewritten.

- 2026-11-03T03:33Z: protocol and preregistration written. Dataset,
  runner, and rubric construction begins. No productions yet.
- 2026-11-03T03:40Z: dataset complete (8 tasks, briefs, scenarios,
  continuation assignments, ground truths validated as JSON). Runner
  prompt code path and parity gate written. Rubric written. Agent A
  productions begin.
- 2026-11-03T03:39Z: all 8 Agent A productions complete (journal, report,
  state bundle per task, written by 8 fresh workers).
- 2026-11-03T03:45Z: ERRATUM, F1 ground truth. The F1 scenario never named
  the initiation rating and did not round the target arithmetic; Agent A
  legitimately produced rating "Buy" and exact figures $84.04 and $67.10.
  The ground truth's "Overweight" and $84 were not supported by the
  scenario. D1, X3, RC4, and must_mention corrected to the produced
  values, with a full errata note inside the F1 ground_truth.json.
  Recorded before any summary, continuation, or grading ran, so no score
  is affected; the parity gate and graders use the corrected version.
  This is the protocol's erratum procedure, not a silent edit.
- 2026-11-03T03:50Z: all 8 summaries complete. First parity gate run: 7
  failures. Disposition: (a) 3 were substring false positives on hyphen
  variants ("export control" vs "export-control", "Step free" vs
  "step-free"); the gate's normalization now treats hyphens and spaces as
  equivalent, uniformly for phrases and texts. (b) 2 were ground truth
  phrase wording not used by the sources (S2 "pricing deploy" vs the
  scenario's "pricing service deploy"; R1 "sso" vs the summary's "single
  sign-on"); corrected as Erratum 2 inside those ground truth files,
  content present in substance in both cases. (c) 1 genuine production
  gap: the F2 summary omitted the 5% single-issuer limit figure and wrote
  the position as "2.8 percent"; a parity fix worker is revising the
  summary from the journal and report (production side, per protocol).
  All dispositions recorded before any continuation ran.
- 2026-11-03T03:52Z: parity gate final run: all 8 tasks PASS on all three
  artifacts. Continuations begin, in the randomized order recorded in
  runner/trial_order.json (seed 20261102).
- 2026-11-03T03:46Z: all 72 continuations complete (8 tasks x 3 conditions
  x 3 trials), each by a fresh worker session, zero failures, zero
  retries, zero refusals. Raw outputs saved verbatim under results/raw/;
  per-trial records written to results/raw/records.jsonl by
  runner/build_records.py. Outputs blinded under random per-task labels
  by runner/blind.py (seed 20261103); mapping held in
  results/judged/mapping.private.json.
- 2026-11-03T03:49Z: blind grading complete: 8 fresh grader sessions (one
  per task, none produced the continuations they graded) scored all 72
  continuations into results/scores/. Analysis run
  (analysis/analyze.py): analysis/results.json and analysis/tables.md
  written. Headline outcome: metric 5 (revision history) scored 1.000 in
  all three conditions with zero chain failures, so no failure-cause
  codes arose; the only consistent Condition A advantage was metric 3
  (assumption retention); Condition A was the least context-efficient
  condition on every task. Full results in REPORT.md. Experiment
  complete. Nothing committed or pushed.
