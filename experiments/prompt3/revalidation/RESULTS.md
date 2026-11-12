# Prompt 3 Revalidation Results (Section 9)

PRELIMINARY. Single model family, in-environment agents, n=3
continuations per cell, blind agent grading. No significance claims
are made or supported at this sample size.

## What was run

For tasks R1, R2, and C1 from Experiment #003, the preserved Agent A
production (`experiments/experiment-003/artifacts/{task}/state.md`)
was mapped into the new F1 `AgentState` schema (mapping decisions
and frictions: `MAPPING.md`), saved through the real `save_state`
code path, and rendered two ways with one renderer: the full
`load_state` bundle (condition A-prime full) and the F6
`project_state` bundle (condition A-prime projected). Three fresh
continuations per task per bundle type (18 total) were run with the
#003 continuation prompts, preserved under `raw/`, and graded blind
by fresh grader agents against the #003 rubric (`scores/`), on
metrics M1, M3, M5, M7, M8; M10 is the bundle word count. The label
mapping is in `judged/mapping.private.json`. A filing incident and
its correction are documented in `PROVENANCE_NOTE.md`.

## Results

| Task | Bundle | M1 | M3 | M5 | M7 fab | M7 unv | M8 | Words (M10) |
|---|---|---|---|---|---|---|---|---|
| R1 | A-prime full | 1.000 | 1.000 | 1.000 | 0 | 0 | 3.00 | 913 |
| R1 | A-prime projected | 1.000 | 1.000 | 1.000 | 0 | 0 | 3.00 | 881 |
| R1 | #003 condition A | 1.000 | 1.000 | 1.000 | 0 | n/r | 2.00 | 2,314 |
| R2 | A-prime full | 0.958 | 0.500 | 0.963 | 0 | 1 | 3.00 | 506 |
| R2 | A-prime projected | 0.875 | 0.500 | 0.981 | 0 | 1 | 3.00 | 436 |
| R2 | #003 condition A | 1.000 | 0.500 | 1.000 | 0 | n/r | 3.00 | 2,370 |
| C1 | A-prime full | 1.000 | 1.000 | n/a | 0 | 0 | 2.67 | 1,323 |
| C1 | A-prime projected | 1.000 | 1.000 | n/a | 0 | 0 | 2.67 | 1,270 |
| C1 | #003 condition A | 0.750 | 1.000 | n/a | 0 | 12 | 2.00 | 2,652 |

#003 condition A figures are taken from
`experiments/experiment-003/analysis/results.json` (means over the
same 3 trials per task) and, for the C1 unverifiable total, from
`experiments/experiment-003/results/scores/C1.json` joined with its
private mapping (the three A trials carry 4 unverifiable claims
each; A-prime carries none). n/r: not re-derived for R1 and R2.

## Reading

- **The new code path carries the state.** A-prime through
  `save_state` / `load_state` matches #003 condition A's retention
  on R1 exactly, improves C1 decision retention (1.000 vs 0.750)
  and continuation quality (2.67 vs 2.00) with zero unverifiable
  additions (vs 12), and is within noise of A on R2 (below).
  EXPERIMENTALLY OBSERVED, preliminary.
- **R2 M3 replicates the #003 weakness exactly.** Both A-prime
  bundle types score 0.500, the #003 A figure. The cause is in the
  mapped state, not the bundle type: the R2 production records the
  two assumptions at low and high confidence while the ground truth
  scores them at medium, so every continuation that faithfully
  restates the bundle loses the confidence element. Neither the
  schema change nor the projection affects this; the loss happened
  when Agent A first recorded the confidences.
- **R2 revision chains are near ceiling in both bundle types.**
  The only missed element anywhere is RC1 element 6 (provenance of
  the format revision) in 3 of 6 continuations, graded RETRIEVAL:
  the source is present in both bundles and some continuations did
  not name it. Full: M5 0.963. Projected: M5 0.981.
- **F6 projection and M5: no regression.** Projected M5 equals full
  on R1 (1.000 vs 1.000), is higher on R2 (0.981 vs 0.963), and M5
  does not apply on C1. Under the audit's rule (withdraw the
  projection on an M5 regression), the projection stands.
  One honest counter-note: R2 M1 is lower under projection
  (0.875 vs 0.958), because all three projected trials present the
  reversed D-01 without its original-plan rationale (partial),
  against one of three full trials. At n=3 this is one verdict in
  two trials, not a demonstrated effect, and the audit's withdrawal
  rule is defined on M5; the difference is recorded here rather
  than smoothed over.
- **Efficiency.** Word counts are NOT like-for-like against #003
  condition A: the A-prime bundles omit the prose sections of the
  original productions (provenance paragraphs, StateChange logs,
  artifact lists have no AgentState fields; MAPPING.md item 7),
  which is a representation loss to weigh, not a pure win. The
  like-for-like comparison is full vs projected (same renderer,
  same state): projection saves 3.5 percent (R1), 13.8 percent
  (R2), and 4.0 percent (C1), because these states carry few dead
  items. F6's measured benefit on realistic states is modest.
- **Fabrications are zero in all 18 continuations**, as they were
  for condition A in #003.

## Limits

One model family; n=3 per cell; graders are agents from the same
environment, as in #003; the mapping from prose productions into
the schema was done by the implementer, and mapping choices
(MAPPING.md) shape what the bundles can carry. Nothing here
supports a general claim beyond these three tasks.
