# Experiment #002 — Control State

> This file is the control file for autonomous execution. It must be accurate
> at all times. Daily runs: read this first, then `protocol.md`.

> **BLINDING WARNING:** the "Blind mapping" section below must NOT be read by the Day 4 Agent B runs or the Day 5 evaluator until grading is complete. The
mapping is disclosed only after Day 5 grading.

- **Current experiment day:** Day 5

- **Current date:** 2026-09-21

- **Current phase:** Day 5 complete — blind evaluation per protocol §6 done: predeclared answer key built from Agent A's decisions/assumptions BEFORE grading; independent evaluator subagent scored all 14 metrics individually for agent-b-x/y/z.md under blinded relabeled IDs (cand-p/q/r, fresh random shuffle, identifying headers stripped, mapping off-limits instruction — grader confirmed compliance); mapping revealed only after grading; `day-05.md` written.

- **Completed phases:** Day 1 (2026-09-17), Day 2 (2026-09-18), Day 3 (2026-09-19), Day 4 (2026-09-20), Day 5 (2026-09-21)

- **Next action:** Day 6 run fires automatically Tue 2026-09-22 ~09:42 ET (cron `world-exp002-daily`): Disney (DIS) replication per protocol §7 — lighter Agent A research, three handoffs (WORLD state / independent summary / raw journal), three blind Agent B continuations, blind grading on the §6 metrics with a FRESH blind X/Y/Z mapping (do not reuse the Day 5 mapping). Do NOT change the protocol based on Day 5 results; document methodological problems instead. Record whether the result replicates. Write `day-06.md`, commit. No user prompting needed.

- **Files produced:**

 - `docs/experiment-002/protocol.md`

 - `docs/experiment-002/experiment-state.md` (this file)

 - `docs/experiment-002/day-01.md`

 - `docs/experiment-002/day-02.md`

 - `docs/experiment-002/agent-a-journal.md`

 - `docs/experiment-002/agent-a-report.md`

 - `docs/experiment-002/agent-a-world-state.md`

 - `docs/experiment-002/handoff-x.md` (blind handoff X)

 - `docs/experiment-002/handoff-y.md` (blind handoff Y)

 - `docs/experiment-002/handoff-z.md` (blind handoff Z)

 - `docs/experiment-002/day-03.md` (build log, measurements, blinding procedure; contains no mapping)

 - `docs/experiment-002/agent-b-x.md` (new — blind continuation X)

 - `docs/experiment-002/agent-b-y.md` (new — blind continuation Y)

 - `docs/experiment-002/agent-b-z.md` (new — blind continuation Z)

 - `docs/experiment-002/day-04.md` (new — run log, blinding verification, methodological notes; contains no mapping)

 - `docs/experiment-002/day-05-answer-key.md` (new — predeclared grading key, built from Agent A's record BEFORE grading)

 - `docs/experiment-002/day-05.md` (new — blind grading results, post-grading mapping reveal, analysis)

 - `docs/development-log.md` (appended)

- **Important findings:** Day 5 blind grading (14 protocol metrics, independent blinded evaluator, answer key predeclared): Y (WORLD state) 3.92 · X (raw journal) 3.58 · Z (independent summary) 3.33 (means of metrics 1–10+14, reference only). WORLD-state continuation preserved decision governance best — assumption preservation 5/5 and confidence preservation 5/5 vs 3/3 for the other two; mild schema echo paid off in explicit confidence bookkeeping. Evidence AGAINST WORLD on one dimension: revision history weak in ALL conditions (Y=2, X=3, Z=2) — even the WORLD continuation lost the R1–R3 old→new→trigger chains. 0 unsupported assumptions and 0 contradictions in all three; continuation quality 5/5/5 everywhere. No gratuitous WORLD overhead found. Input efficiency ≠ retention: the summary was the shortest handoff but weakest preservation. Full analysis in day-05.md. Prior: Day 4 Agent B output measurements (words; tokens ≈ words×4/3): X = 2,760 words (~3,680 tokens); Y = 2,518 words (~3,357 tokens); Z = 2,628 words (~3,504 tokens).

- **Errors/blockers:** Day 5 blinding note (documented in day-05.md, not hidden): subagents inherit the parent transcript, which contained the blind mapping because the full experiment-state.md returns whole on fetch at run start. Mitigated by relabeling outputs to cand-p/q/r via a fresh random shuffle, stripping identifying headers, and an explicit off-limits instruction; the grader confirmed it used, sought, and recovered no mapping and mentioned no conditions. Residual imperfection stands per protocol §10.4. Prior: Day 4 procedural incident (documented in day-04.md, not hidden): the first spawn for run X was created with a placeholder instead of its handoff sourcing and was closed at pending_init before producing any output; all three runs were re-spawned with identical briefs sourcing handoffs from disk. No contamination. Otherwise none.

- **Experiment still valid:** yes.

- **Blind mapping (X/Y/Z → conditions):** X→C (raw journal) · Y→A (WORLD state) · Z→B (independent summary). Assigned 2026-09-19 by single `python3 random` shuffle of conditions over labels. **Revealed to the Day 5 process only after grading completed (2026-09-21);** the evaluator graded blinded relabeled copies and confirmed no mapping use. Kept ONLY in this file; no evaluator-visible file names the mapping. Handoff letters are stable through Days 4–5 (Agent B outputs are `agent-b-x/y/z.md`). Day 6 replication must use a FRESH blind mapping — do not reuse these labels.

- **Procedural note:** Agent A research on Intel (INTC) was launched during Day 1 setup, before the 7-day plan was received (prior instruction was "draft and run Experiment #002"). This is documented, not hidden. Day 2 verified outputs and captured them into day-02.md; no re-run was needed.

- **Agent A outputs (verified 2026-09-18):** `docs/experiment-002/agent-a-journal.md` (3,616 words), `agent-a-report.md` (2,376 words), `agent-a-world-state.md`

 (3,173 words); Agent A completed 2026-09-17 17:33 ET. Verification vs protocol §3: 14 decisions (D1, D7 superseded), 13 assumptions with confidence, 3

 revisions (R1–R3), 4 guardrails (G1–G4), 6 open questions (Q1–Q6), 2 failed approaches (FA1, FA2), D13 depends on D5, D12 supersedes D1/depends on D5, 32

 evidence entries (E1–E32). Journal pre-registered the three naive priors before research; all three were reversed by R1–R3 with named trigger evidence.

- **Agent B outputs (2026-09-20):** `docs/experiment-002/agent-b-x.md` (2,760 words), `agent-b-y.md` (2,518 words), `agent-b-z.md` (2,628 words). Each run received ONLY its own blind handoff (identical §5 brief, no browsing). Blinding leak-scan clean.

- **Replication company (predeclared):** Disney (DIS) — Day 6.

- **Autonomous schedule:** cron `world-exp002-daily`, daily ~09:42 ET America/New_York, owner `goal:world-experiment-002-7-day-workflow`, timeout 2h, 1 retry on

 runtime failure. Retires itself after Day 7.

- **Last updated:** 2026-09-21 10:05 ET (Day 5 — blind evaluation complete, answer key predeclared, 14 metrics scored per continuation, mapping revealed post-grading, day-05.md written)
