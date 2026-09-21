# Task 001: Write research/comparisons.md

A real deliverable for this repo: a comparison doc contrasting WORLD's
deterministic, hash-chained ledger against the probabilistic memory
approaches of Mem0, Zep, and Letta (including Cognee and Supermemory).
The doc should cover, at minimum:

- How each system stores and retrieves agent state (deterministic ledger
  vs vector/probabilistic recall).
- What "verifiable" means in each system, and what it does not.
- Where WORLD's hash-chained, constraint-checked ledger is strictly
  stronger, and where the probabilistic systems are more practical.
- A comparison table (system x dimensions: determinism, auditability,
  tamper-evidence, latency, operational cost).
- At least one unresolved open question, e.g. how to frame
  compliance-readiness without overclaiming.

This task is the vehicle for the handoff experiment, not the point of
it. The point is the handoff. The doc may end up incomplete; an
incomplete doc with honest trial data beats a polished doc with none.

## 5-trial protocol

The operator (you) plays Model A and Model B manually across two chat
windows. Nothing is automated on day one.

Each trial:

1. Model A works the doc for roughly 8-10 exchanges: research
   findings, deterministic-vs-probabilistic framing decisions, the
   comparison table, and at least one unresolved open question (e.g.
   compliance-readiness framing). Save the session transcript to
   `experiments/trials/trial_NNN_a.md`.
2. Run the transcript through the importer and commit state to the
   ledger:

       python import_transcript.py experiments/trials/trial_NNN_a.md --source handoff_001/trial_NNN

   Then commit the trial to the experiment log:

       python experiments/handoff_001.py run --trial NNN \
           --task-file experiments/tasks/task_001.md \
           --transcript experiments/trials/trial_NNN_a.md

   The committed state carries, at minimum: objective, decisions,
   current_state (the parser's NOTE items), open_questions,
   next_action. Note: the deterministic parser cannot infer next_action
   from a transcript, so that field is intentionally absent from the
   bundle. Whether Model B proposes the right next action from state
   alone is part of what the experiment measures.
3. Kill the session completely. New tab/window, not the same context.
4. In the fresh session, Model B gets ONLY the extracted state bundle
   plus the word "continue":

       python experiments/handoff_001.py bundle --trial NNN

   Paste that output, then the word "continue". Nothing else.
5. Save Model B's response to `experiments/trials/trial_NNN_b.md` and
   score by hand (see scoring rubric below):

       python experiments/handoff_001.py score --trial NNN \
           --model-b-output experiments/trials/trial_NNN_b.md \
           --success true|false --reason "..."

### Cut points (vary per trial)

- Trial 1: cut early, 2 exchanges in.
- Trial 2: cut mid-document.
- Trial 3: cut right before a framing decision (e.g. just before Model A
  decides how to frame determinism vs probability).
- Trials 4 and 5: the operator's choice of two different cut points not
  used above.

### Scoring rubric (hand-scored per trial, be honest not generous)

- Did Model B identify the next section to write without being told?
- Did it respect the determinism-framing decision instead of
  re-litigating it?
- Did it address the open question, or drop it?
- `handoff_success`: true only if Model B continued correctly with no
  re-explaining. Otherwise false, plus a specific `failure_reason`
  (e.g. "re-litigated the determinism framing", "dropped the
  compliance-readiness open question", "invented a section not in state").

### Pre-registration rule (anti-generous-grading)

> For each of the 5 trials, BEFORE touching Model B, the operator writes
> down (on paper or a notes file, not in the tool): what she expects
> Model B needs to know to continue correctly. This prediction is
> written before seeing Model B's output. Then run Model B, and record:
> did it match the prediction (yes/no, and where it diverged), plus one
> sentence answering: would a stranger reading Model B's output believe
> it had full context, or would they notice something was off? The
> stranger test is the real test; slightly-off continuations must not
> be scored as "basically worked".

Store each trial's prediction in
`experiments/trials/trial_NNN_prediction.md` before running Model B.

## Done means

- 5 JSON files in `experiments/results/` (trial_001.json ..
  trial_005.json), every one hand-scored, failures included.
- A real `research/comparisons.md`, however incomplete.
- The literal output of `python experiments/summarize.py`.

A 2/5 or worse result still ships into the README with the failure
reasons listed plainly. The goal is evidence, not a good outcome.
