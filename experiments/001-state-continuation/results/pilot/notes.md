# Pilot run — notes (2026-09-23)

## What this is

A **harness-validation pilot**, not evidence for the research question.
Purpose: prove the pipeline runs end-to-end (prompts → continuations →
manifest → deterministic scores → blind grades → table) and that the
metrics discriminate. n = 3 tasks × 3 conditions. **Do not cite these
numbers as findings.**

## How it was run

- Continuations were written by the benchmark author acting as the
  successor agent, working from each condition's artifact only
  (`results/pilot/prompts/`), following the brief. No access to
  `ground_truth.json` during writing (beyond having authored it —
  see limitations).
- Grading was blind: continuations were copied to `grading/` with random
  IDs (`T001-A` …), condition labels stripped, graded against
  `evaluation/rubric.md` from text alone, locked, then unblinded via
  `grading_key.json`.
- Deterministic scoring: `evaluation/score.py` on the pre-registered keys.

## Amendments to the method (during pilot calibration)

Methodology §5 requires amendments to be recorded here, not silently
folded in:

1. **Spaceless phrase fallback** (`evaluation/textutils.py::phrase_match`):
   "roll back" now matches "rollback". Without this, a semantically
   present phrase failed on orthography. Applies equally to all
   conditions; re-scored after the change.
2. **Markdown-aware sentence splitting**: sentence boundaries now require
   a capital letter or markdown block marker (`*`, `#`, `-`) after
   terminal punctuation. Previously a table-adjacent sentence bled into
   a `**Will NOT do:**` header, causing one false repeated-work hit.
3. Both fixes were validated by `evaluation/selftest.py` (still green)
   and `evaluation/check_parity.py` (still green) before re-scoring.

## Results (verbatim)

| task | cond | M1 | M2 proxy | M2 judged | M3 | M4 | M5/100w | M5 judged | M6 count | M6 judged | in-words | out-words |
|------|------|----|----------|-----------|----|----|---------|-----------|----------|-----------|----------|-----------|
| 001 | transcript | 3 | 0.833 | 3 | 0.250 | 0.667 | 0.0 | 0 | 0 | 3 | 785 | 182 |
| 001 | summary | 3 | 0.500 | 3 | 0.750 | 1.000 | 0.0 | 0 | 0 | 3 | 522 | 183 |
| 001 | world | 3 | 0.333 | 3 | 0.750 | 1.000 | 0.0 | 0 | 0 | 3 | 637 | 176 |
| 002 | transcript | 3 | 0.333 | 3 | 0.333 | 1.000 | 0.0 | 0 | 0 | 3 | 674 | 202 |
| 002 | summary | 3 | 0.667 | 3 | 0.000 | 1.000 | 0.0 | 0 | 0 | 3 | 566 | 206 |
| 002 | world | 3 | 1.000 | 3 | 0.333 | 0.667 | 0.0 | 0 | 0 | 3 | 493 | 185 |
| 003 | transcript | 3 | 0.800 | 3 | 0.500 | 0.667 | 0.0 | 0 | 0 | 3 | 601 | 205 |
| 003 | summary | 3 | 0.600 | 3 | 0.750 | 0.667 | 0.0 | 0 | 0 | 3 | 412 | 167 |
| 003 | world | 3 | 0.600 | 3 | 1.000 | 1.000 | 0.0 | 0 | 0 | 3 | 495 | 186 |

Condition means (deterministic): M3 — world 0.694, summary 0.500,
transcript 0.361. M2 proxy — transcript 0.655, world 0.644, summary 0.589.
Mean input words — transcript 687, world 566, summary 476.

## Read of the table

- WORLD does **not** sweep. It leads the primary metric (M3) on average
  but loses the factual-accuracy proxy (M2) to transcript on average, and
  on task_002 its M3 (0.333) merely ties transcript while summary scores
  0.000. The harness shows losses where they occur — as designed.
- The judged metrics (M1, M2-judged, M5, M6) are **saturated**: every
  continuation scored 3/0. With a competent successor agent and
  information-complete handoffs, rubric grading does not discriminate.
- Cost (M7): the summary is the cheapest handoff (~476 input words vs
  ~566 for WORLD vs ~687 for transcript) — verbosity is part of each
  representation's trade-off, per methodology §3.3.

## Calibration findings (for future runs)

1. The deterministic proxies carry the discrimination in this pilot; the
   judged rubric needs harder tasks, noisier handoffs, or weaker
   successor agents to bite.
2. M3 (decision recovery) was the most discriminating metric (range
   0.000–1.000 across cells); M5/M6 saw zero hits — the pilot's
   continuations were too clean to exercise the contradiction and
   repeated-work machinery (the self-test covers those paths synthetically).
3. Author-as-agent is the pilot's biggest limitation: the continuations
   reflect one writer's habits, and true blinding is impossible when the
   grader wrote the texts. A real run needs an independent model and an
   independent grader.

## Limitations of this pilot

- n=1 author, unblinded in the strong sense; treat as a worked example.
- Synthetic tasks (methodology §7) — mechanism test, not ecological.
- English only; one successor-agent style; no tool use or multi-turn.
