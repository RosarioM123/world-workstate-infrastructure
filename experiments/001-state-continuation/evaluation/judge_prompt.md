# Fixed judge prompt — use verbatim for LLM-graded runs

> **Protocol:** the texts below are labeled with random IDs. You do not
> know which handoff format produced which text, and you must not try to
> infer it. Grade each text **only** against the provided ground truth.
> After grading, output one JSON object per text with the exact keys
> below. Then stop — do not summarize, do not rank conditions.

```
You are grading successor-agent continuations for a handoff benchmark.

GROUND TRUTH (the predecessor's actual work):
<<<GROUND_TRUTH_JSON>>>

RUBRIC:
- M1 task_completion (0-3): does the text deliver what <<<BRIEF>>> asked?
  3 = all required parts present; 2 = one required part missing;
  1 = partial; 0 = not delivered.
- M2 judged factual_accuracy (0-3): are verifiable claims correct
  (numbers, owners, deadlines)? 3 = all correct; 2 = minor errors only;
  1 = at least one material falsehood; 0 = fundamentally misstates events.
- M5 judged contradictions (count): count statements contradicting the
  ground truth. Quote each offending sentence.
- M6 judged repeated_work (0-3): 3 = builds cleanly on the handoff;
  2 = minor restatement; 1 = re-proposes a settled item as undecided;
  0 = substantially re-does the predecessor's work.

TEXTS TO GRADE (random IDs, condition blinded):
<<<ID>>:
<<<TEXT>>>
...

OUTPUT: for each ID, exactly:
{"id": "<<<ID>>>", "M1": n, "M2_judged": n, "M5_judged_hits": ["quote", ...],
 "M6_judged": n, "notes": "..."}
```

## Blinding procedure

1. Copy each continuation to `grading/<random_id>.md` (no condition names
   in file names or contents — strip the `[Format: ...]` tag).
2. Fill `<<<GROUND_TRUTH_JSON>>>` (decisions/facts/questions/actions only,
   not the must_not_state keys — the judge must find contradictions
   unprompted) and `<<<BRIEF>>>` from the task's `brief.md`.
3. Run the prompt once per task. Paste the returned JSON into
   `results/<run>/judged/<task>.json` verbatim.
4. Only then unblind (map IDs back to conditions) and tabulate.

A human grader follows the same procedure with `evaluation/rubric.md`.
