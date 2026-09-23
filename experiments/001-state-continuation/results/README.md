# Results

Every benchmark run gets a dated subdirectory here, e.g.
`results/2026-09-23-pilot/`, containing:

- `manifest.json` — from `runner/run.py` (prompts, word counts, adapter,
  timestamps). The manifest is the run's identity; scores without a
  manifest are not results.
- `raw/<task>__<condition>.md` — the continuations, verbatim.
- `scored/` — output of `evaluation/score.py` (`scores.json`,
  `scores.csv`, `scores.md`).
- `judged/<task>.json` — blind rubric grades (see
  `evaluation/judge_prompt.md`), pasted verbatim.
- `notes.md` — operator notes: model name and version, date, who graded,
  any deviations from `methodology.md`, and a plain-language read of the
  table. **Negative and null results are published verbatim.**

`schema.json` (next to this file) is the JSON schema for one scored row.

## What lives here now

- `pilot/` — harness-validation pilot (2026-09-23): 3 tasks × 3
  conditions, continuations written by the benchmark author acting as the
  successor agent, graded author-blind against the pre-registered keys.
  Purpose: prove the pipeline runs end-to-end and the metrics
  discriminate — **not** evidence for the research question. Read
  `pilot/notes.md` before citing any number.
