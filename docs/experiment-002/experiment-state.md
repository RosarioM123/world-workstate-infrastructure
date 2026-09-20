# Experiment #002 — Control State

> This file is the control file for autonomous execution. It must be accurate
> at all times. Daily runs: read this first, then `protocol.md`.

> **BLINDING WARNING:** the "Blind mapping" section below must NOT be read by the Day 4 Agent B runs or the Day 5 evaluator until grading is complete. The
mapping is disclosed only after Day 5 grading.

- **Current experiment day:** Day 4

- **Current date:** 2026-09-20

- **Current phase:** Day 4 complete — three isolated Agent B continuations (one per blind handoff X/Y/Z, protocol §5), identical brief, no browsing, blinded; filename/format echoes stripped; outputs committed.

- **Completed phases:** Day 1 (2026-09-17), Day 2 (2026-09-18), Day 3 (2026-09-19), Day 4 (2026-09-20)

- **Next action:** Day 5 run fires automatically Mon 2026-09-21 ~09:42 ET (cron `world-exp002-daily`): blind evaluation per protocol §6. Build the answer key from Agent A's decisions/assumptions BEFORE grading; use an independent evaluator context; score all 14 protocol metrics individually for each of `agent-b-x.md` / `agent-b-y.md` / `agent-b-z.md`; record cases where WORLD created unnecessary complexity/overhead. Reveal the X/Y/Z → condition mapping ONLY after grading is complete — do NOT read the "Blind mapping" section of this file until then. Write `day-05.md`, commit. No user prompting needed.

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

 - `docs/development-log.md` (appended)

- **Important findings:** Day 4 Agent B output measurements (words; tokens ≈ words×4/3): X = 2,760 words (~3,680 tokens); Y = 2,518 words (~3,357 tokens); Z = 2,628 words (~3,504 tokens). Continuation effort comparable across runs (within ~10%). Day 3 input measurements for reference: X = 3,616 words (~4,821, raw journal); Y = 3,173 words (~4,230, WORLD state, 10 sections); Z = 2,446 words (~3,261, summary). Whether handoff structure translates to better Phase 2 retention is what Day 5 tests. Blinding verification: leak-scan of all three Agent B outputs for run codes, condition names, and filename echoes came back clean (see day-04.md); the X/Y/Z letters remain stable through Days 4–5.

- **Errors/blockers:** Day 4 procedural incident (documented in day-04.md, not hidden): the first spawn for run X was created with a placeholder instead of its handoff sourcing and was closed at pending_init before producing any output; all three runs were re-spawned with identical briefs sourcing handoffs from disk. No contamination. Otherwise none.

- **Experiment still valid:** yes.

- **Blind mapping (X/Y/Z → conditions):** X→C (raw journal) · Y→A (WORLD state) · Z→B (independent summary). Assigned 2026-09-19 by single `python3 random` shuffle of conditions over labels. **Reveal to Day 5 evaluator only after grading is complete.** Kept ONLY in this file; no evaluator-visible file names the mapping. Handoff letters are stable through Days 4–5 (Agent B outputs are `agent-b-x/y/z.md`).

- **Procedural note:** Agent A research on Intel (INTC) was launched during Day 1 setup, before the 7-day plan was received (prior instruction was "draft and run Experiment #002"). This is documented, not hidden. Day 2 verified outputs and captured them into day-02.md; no re-run was needed.

- **Agent A outputs (verified 2026-09-18):** `docs/experiment-002/agent-a-journal.md` (3,616 words), `agent-a-report.md` (2,376 words), `agent-a-world-state.md`

 (3,173 words); Agent A completed 2026-09-17 17:33 ET. Verification vs protocol §3: 14 decisions (D1, D7 superseded), 13 assumptions with confidence, 3

 revisions (R1–R3), 4 guardrails (G1–G4), 6 open questions (Q1–Q6), 2 failed approaches (FA1, FA2), D13 depends on D5, D12 supersedes D1/depends on D5, 32

 evidence entries (E1–E32). Journal pre-registered the three naive priors before research; all three were reversed by R1–R3 with named trigger evidence.

- **Agent B outputs (2026-09-20):** `docs/experiment-002/agent-b-x.md` (2,760 words), `agent-b-y.md` (2,518 words), `agent-b-z.md` (2,628 words). Each run received ONLY its own blind handoff (identical §5 brief, no browsing). Blinding leak-scan clean.

- **Replication company (predeclared):** Disney (DIS) — Day 6.

- **Autonomous schedule:** cron `world-exp002-daily`, daily ~09:42 ET America/New_York, owner `goal:world-experiment-002-7-day-workflow`, timeout 2h, 1 retry on

 runtime failure. Retires itself after Day 7.

- **Last updated:** 2026-09-20 10:00 ET (Day 4 — three Agent B continuations run, outputs stored, committed)
