# Experiment #002 — Control State

> This file is the control file for autonomous execution. It must be accurate
> at all times. Daily runs: read this first, then `protocol.md`.

> **BLINDING WARNING:** the "Blind mapping" section below must NOT be read by the Day 4 Agent B runs or the Day 5 evaluator until grading is complete. The
mapping is disclosed only after Day 5 grading.

- **Current experiment day:** Day 7

- **Current date:** 2026-09-23

- **Current phase:** Day 7 complete: final verdict per protocol §8 done: `results.md` written (all 19 required sections: protocol, tasks, Agent A research, handoffs, Agent B outputs, blind grading, individual metrics, token/input comparison, information loss, failure cases, replication results, where WORLD helped/hurt, strongest evidence for and against, #001 replication verdict, updated hypothesis, further experiments, prototype verdict); `docs/hypothesis.md` updated with the Experiment #002 verdict section; `day-07.md` written; development log appended; everything committed to `main`; the `world-exp002-daily` schedule retired after commit verification.

- **Completed phases:** Day 1 (2026-09-17), Day 2 (2026-09-18), Day 3 (2026-09-19), Day 4 (2026-09-20), Day 5 (2026-09-21), Day 6 (2026-09-22), Day 7 (2026-09-23)

- **Next action:** None. The 7-day workflow is complete. No further scheduled runs; the `world-exp002-daily` cron is disabled (self-retired 2026-09-23). Any follow-up work (revision-history experiment, cross-model handoffs, human auditability) is a new experiment with its own schedule, not this one.

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

 - `docs/experiment-002/dis-agent-a-journal.md` (new — Disney Agent A research journal, 1,147 words)

 - `docs/experiment-002/dis-agent-a-report.md` (new — Disney Agent A report, 1,908 words)

 - `docs/experiment-002/dis-agent-a-world-state.md` (new — Disney Agent A WORLD state bundle, 2,199 words)

 - `docs/experiment-002/dis-handoff-x.md` (new — blind handoff X)

 - `docs/experiment-002/dis-handoff-y.md` (new — blind handoff Y)

 - `docs/experiment-002/dis-handoff-z.md` (new — blind handoff Z)

 - `docs/experiment-002/dis-agent-b-x.md` (new — blind continuation X)

 - `docs/experiment-002/dis-agent-b-y.md` (new — blind continuation Y)

 - `docs/experiment-002/dis-agent-b-z.md` (new — blind continuation Z)

 - `docs/experiment-002/day-06-answer-key.md` (new — predeclared grading key, built from Agent A's Disney record BEFORE grading)

 - `docs/experiment-002/day-06-grading.md` (new — blind evaluator report, cand-p/q/r relabeled)

 - `docs/experiment-002/day-06.md` (new — replication results, post-grading mapping reveal, analysis)

 - `docs/experiment-002/results.md` (new: Day 7 final verdict per protocol §8, all 19 required sections)

 - `docs/experiment-002/day-07.md` (new: Day 7 run log)

 - `docs/hypothesis.md` (updated: new "Experiment #002 verdict (2026-09-23)" section)

 - `docs/development-log.md` (appended)

- **Important findings:** Day 7 final verdict (full analysis in `results.md`): the WORLD-state continuation preserved decision governance best in BOTH runs (Intel: 3.92 vs 3.58 vs 3.33; Disney: 4.45 vs 4.09 vs 2.82, reference means), so the WORLD-best direction replicates; the alternative ordering does NOT (journal vs summary flipped between runs, instance-sensitive, n=1). Strongest evidence FOR WORLD: assumption/confidence governance (main run 5/5 vs 3/3), provenance 5 vs 4/2 and superseded decisions 3 vs 0/0 in the replication, and the label-stability mechanism ("relabeling is not neutral reformatting; it is where items get lost"). Strongest evidence AGAINST WORLD, replicated: revision history weak in the WORLD continuation in both runs (metric 5 = 2 twice; the journal scored 4 in the replication), and an independent summary came within 0.36 in the Disney run, keeping falsifiability condition 1 (summary parity) open. Hypothesis now narrowed in `docs/hypothesis.md`: partially supported, specifically scoped; success criteria 2 (human auditability) and 3 (cross-model consistency) untested. Prototype development justified only for the narrow demonstrated advantage (stable labeled governance records) with revision-history preservation as the first test, not the full WORLD vision. Experiment #001's direction replicated in the harder #002 design; #001's clean sweep did not. Prior: Day 6 Disney replication (blind grading, 14 protocol metrics, predeclared key, fresh mapping X→B summary / Y→C journal / Z→A WORLD, revealed post-grading): A (WORLD state) 4.45 · B (independent summary) 4.09 · C (raw journal) 2.82 (means of metrics 1–10+14, reference only). WORLD-best direction REPLICATES; alternative ordering does NOT (Day 5: journal 3.58 > summary 3.33; Day 6: summary 4.09 > journal 2.82 — instance-sensitive, n=1). Mechanism-level finding: the journal continuation renumbered every decision/assumption/question under its own labels, and that is where governance items were lost (entire Epic thread D7/A8/Q5, D11, Q4, inherited confidences, provenance IDs). "Relabeling is not neutral reformatting; it is where items get lost." Evidence AGAINST WORLD, replicated: revision history weak in the WORLD continuation again (metric 5 = 2, tied with summary; journal = 4) — the structured state still does not carry old→new→trigger chains into the continuation. Superseded decisions only partially preserved (A=3, D3a named but formal chain not spelled out; B and C = 0). 0 contradictions everywhere. Mild decorative WORLD overhead: second-order confidence phrasing ("medium, trending toward a formal downgrade"). Full analysis in day-06.md. Prior: Day 5 blind grading (14 protocol metrics, independent blinded evaluator, answer key predeclared): Y (WORLD state) 3.92 · X (raw journal) 3.58 · Z (independent summary) 3.33 (means of metrics 1–10+14, reference only). WORLD-state continuation preserved decision governance best — assumption preservation 5/5 and confidence preservation 5/5 vs 3/3 for the other two; mild schema echo paid off in explicit confidence bookkeeping. Evidence AGAINST WORLD on one dimension: revision history weak in ALL conditions (Y=2, X=3, Z=2) — even the WORLD continuation lost the R1–R3 old→new→trigger chains. 0 unsupported assumptions and 0 contradictions in all three; continuation quality 5/5/5 everywhere. No gratuitous WORLD overhead found. Input efficiency ≠ retention: the summary was the shortest handoff but weakest preservation. Full analysis in day-05.md. Prior: Day 4 Agent B output measurements (words; tokens ≈ words×4/3): X = 2,760 words (~3,680 tokens); Y = 2,518 words (~3,357 tokens); Z = 2,628 words (~3,504 tokens).

- **Errors/blockers:** Day 7: no new errors or blockers. The schedule retired itself after commit verification. Prior: Day 6 blinding improvement (documented in day-06.md): the fresh mapping was kept in a local-only private file until grading completed, then recorded here — unlike Days 3-4 where it sat in this file from the start; residual imperfection stands per §10.4 (subagents inherit parent context). Day 6 minor procedural incident: the blind-file copy step first failed on an uppercase/lowercase filename mismatch and was re-run correctly; no contamination, no files lost. Prior: Day 5 blinding note (documented in day-05.md, not hidden): subagents inherit the parent transcript, which contained the blind mapping because the full experiment-state.md returns whole on fetch at run start. Mitigated by relabeling outputs to cand-p/q/r via a fresh random shuffle, stripping identifying headers, and an explicit off-limits instruction; the grader confirmed it used, sought, and recovered no mapping and mentioned no conditions. Residual imperfection stands per protocol §10.4. Prior: Day 4 procedural incident (documented in day-04.md, not hidden): the first spawn for run X was created with a placeholder instead of its handoff sourcing and was closed at pending_init before producing any output; all three runs were re-spawned with identical briefs sourcing handoffs from disk. No contamination. Otherwise none.

- **Experiment still valid:** yes (complete — all 7 days executed per protocol §12, validity conditions held throughout).

- **Blind mapping (X/Y/Z → conditions):** X→C (raw journal) · Y→A (WORLD state) · Z→B (independent summary). Assigned 2026-09-19 by single `python3 random` shuffle of conditions over labels. **Revealed to the Day 5 process only after grading completed (2026-09-21);** the evaluator graded blinded relabeled copies and confirmed no mapping use. Kept ONLY in this file; no evaluator-visible file names the mapping. Handoff letters are stable through Days 4–5 (Agent B outputs are `agent-b-x/y/z.md`). Day 6 replication must use a FRESH blind mapping — do not reuse these labels.

- **Blind mapping, Day 6 replication (X/Y/Z → conditions):** X→B (independent summary) · Y→C (raw journal) · Z→A (WORLD state). Assigned 2026-09-22 by a fresh single `python3 random` shuffle, different from the Day 5 mapping. **Revealed to the Day 6 process only after grading completed (2026-09-22);** kept in a local-only private file until then, then recorded here. The evaluator graded blinded relabeled copies (cand-p = X, cand-r = Y, cand-q = Z, second fresh shuffle) and confirmed no mapping use. Day 6 outputs are `dis-agent-b-x/y/z.md`.

- **Procedural note:** Agent A research on Intel (INTC) was launched during Day 1 setup, before the 7-day plan was received (prior instruction was "draft and run Experiment #002"). This is documented, not hidden. Day 2 verified outputs and captured them into day-02.md; no re-run was needed.

- **Agent A outputs (verified 2026-09-18):** `docs/experiment-002/agent-a-journal.md` (3,616 words), `agent-a-report.md` (2,376 words), `agent-a-world-state.md`

 (3,173 words); Agent A completed 2026-09-17 17:33 ET. Verification vs protocol §3: 14 decisions (D1, D7 superseded), 13 assumptions with confidence, 3

 revisions (R1–R3), 4 guardrails (G1–G4), 6 open questions (Q1–Q6), 2 failed approaches (FA1, FA2), D13 depends on D5, D12 supersedes D1/depends on D5, 32

 evidence entries (E1–E32). Journal pre-registered the three naive priors before research; all three were reversed by R1–R3 with named trigger evidence.

- **Agent B outputs (2026-09-20):** `docs/experiment-002/agent-b-x.md` (2,760 words), `agent-b-y.md` (2,518 words), `agent-b-z.md` (2,628 words). Each run received ONLY its own blind handoff (identical §5 brief, no browsing). Blinding leak-scan clean.

- **Replication company (predeclared):** Disney (DIS) — Day 6.

- **Autonomous schedule:** cron `world-exp002-daily`, daily ~09:42 ET America/New_York, owner `goal:world-experiment-002-7-day-workflow`, timeout 2h, 1 retry on runtime failure. Retired (disabled) after Day 7, 2026-09-23.

- **Last updated:** 2026-09-23 09:50 ET (Day 7: final verdict: results.md written per protocol §8, docs/hypothesis.md updated with the Experiment #002 verdict section, day-07.md written, development log appended, all committed to main, world-exp002-daily schedule retired)
