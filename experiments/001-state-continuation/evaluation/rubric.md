# Judging rubric — judged metrics (M1, and judged halves of M2/M5/M6)

Grade **blind**: continuations are labeled with random IDs (e.g. `T2-C`);
the grader must not know which condition produced which text until all
scores are locked. Grade each continuation against the task's
`ground_truth.json` only.

## M1 — task_completion (0–3)

Does the continuation deliver what the brief asked for?

- **3** — Delivers the requested artifact with all required parts
  (e.g. for task_001: decision, rationale, risks, pre-sign-off items;
  for task_002: actions with owners and deadlines, plus explicit
  non-actions; for task_003: scope, sequencing, owners, rollback criteria).
- **2** — Delivers the artifact but misses one required part.
- **1** — Partial: addresses the brief only in passing or misses two+
  required parts.
- **0** — Does not deliver the requested artifact.

## M2 — factual_accuracy, judged half (0–3)

Beyond the deterministic proxy: are the stated facts *correct* (not just
present), with numbers, owners, and deadlines right?

- **3** — All verifiable claims match ground truth.
- **2** — Minor errors (a wrong owner, an approximate number) but no
  material falsehood.
- **1** — At least one material falsehood (wrong decision, wrong number
  that changes meaning).
- **0** — Fundamentally misstates what happened.

## M5 — contradiction_rate, judged half (count)

Count statements that contradict ground truth and are NOT caught by the
deterministic `must_not_state` list. Report the count; the rate per 100
words is computed at tabulation. When in doubt, quote the sentence in
the grading notes.

## M6 — repeated_work, judged half (0–3)

Does the continuation waste effort re-doing settled work?

- **3** — No repeated work; builds cleanly on the handoff.
- **2** — Minor redundancy (restates context without re-proposing it).
- **1** — Re-proposes at least one settled item as if undecided.
- **0** — Substantially re-does Agent A's work (re-opens decided
  decisions, re-runs completed analysis).

## Grading notes

- Quote the exact sentence behind every M5 hit and every M1/M6 score ≤ 1.
- If a continuation is over the word cap, score it as-is; note verbosity
  under M7 discussion, not as a penalty here.
- Ties and uncertainty: record them in the notes; do not break ties by
  guessing the condition.
