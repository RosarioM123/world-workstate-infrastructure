# Experiment #002 — Control State

> This file is the control file for autonomous execution. It must be accurate
> at all times. Daily runs: read this first, then `protocol.md`.

> **BLINDING WARNING:** the "Blind mapping" section below must NOT be read by the Day 4 Agent B runs or the Day 5 evaluator until grading is complete. The mapping is disclosed only after Day 5 grading.

- **Current experiment day:** Day 3

- **Current date:** 2026-09-19

- **Current phase:** Day 3 complete — three handoffs built from the same Agent A Phase 1 output per protocol §2, blind-labeled X/Y/Z, committed.

- **Completed phases:** Day 1 (2026-09-17), Day 2 (2026-09-18), Day 3 (2026-09-19)

- **Next action:** Day 4 run fires automatically Sun 2026-09-20 ~09:42 ET (cron `world-exp002-daily`): three isolated Agent B continuations per protocol §5 — one run per blind handoff file (`handoff-x.md` / `handoff-y.md` / `handoff-z.md`), identical brief, no browsing. Runs are not told which condition each letter maps to; strip filename/format echoes before storing outputs as `docs/experiment-002/agent-b-x.md` / `agent-b-y.md` / `agent-b-z.md`. Write `day-04.md`, commit. No user prompting needed.

- **Files produced:**

  - `docs/experiment-002/protocol.md`

  - `docs/experiment-002/experiment-state.md` (this file)

  - `docs/experiment-002/day-01.md`

  - `docs/experiment-002/day-02.md`

  - `docs/experiment-002/agent-a-journal.md`

  - `docs/experiment-002/agent-a-report.md`

  - `docs/experiment-002/agent-a-world-state.md`

  - `docs/experiment-002/handoff-x.md` (new — blind handoff X)

  - `docs/experiment-002/handoff-y.md` (new — blind handoff Y)

  - `docs/experiment-002/handoff-z.md` (new — blind handoff Z)

  - `docs/experiment-002/day-03.md` (new — build log, measurements, blinding procedure; contains no mapping)

  - `docs/development-log.md` (appended)

- **Important findings:** Day 3 handoff measurements (words; tokens ≈ words×4/3): blind handoff X = 3,616 words (~4,821 tokens, raw journal, prose); Y = 3,173 words (~4,230 tokens, structured WORLD state, 10 sections); Z = 2,446 words (~3,261 tokens, independent conventional summary, prose). The summary is the most input-efficient (32% shorter than the raw journal, 23% shorter than the WORLD state). The WORLD state is the only handoff with machine-readable governance structure (decision supersession graph D1←D12 / D7←D6, revision chain R1–R3, dependency D13→D5, 39-row append-only changelog). The independent summary writer confirmed it never saw the WORLD state file (spawned before the parent read it; summary contains no schema IDs or state-model references). These are input-side measurements only; whether efficiency/structure translates to better Phase 2 retention is what Days 4–5 test.

- **Errors/blockers:** none.

- **Experiment still valid:** yes.

- **Blind mapping (X/Y/Z → conditions):** X→C (raw journal) · Y→A (WORLD state) · Z→B (independent summary). Assigned 2026-09-19 by single `python3 random` shuffle of conditions over labels. **Reveal to Day 5 evaluator only after grading is complete.** Kept ONLY in this file; no evaluator-visible file names the mapping. Handoff letters are stable through Days 4–5 (Agent B outputs are `agent-b-x/y/z.md`).

- **Procedural note:** Agent A research on Intel (INTC) was launched during Day 1 setup, before the 7-day plan was received (prior instruction was "draft and run Experiment #002"). This is documented, not hidden. Day 2 verified outputs and captured them into day-02.md; no re-run was needed.

- **Agent A outputs (verified 2026-09-18):** `docs/experiment-002/agent-a-journal.md` (3,616 words), `agent-a-report.md` (2,376 words), `agent-a-world-state.md`
 (3,173 words); Agent A completed 2026-09-17 17:33 ET. Verification vs protocol §3: 14 decisions (D1, D7 superseded), 13 assumptions with confidence, 3
 revisions (R1–R3), 4 guardrails (G1–G4), 6 open questions (Q1–Q6), 2 failed approaches (FA1, FA2), D13 depends on D5, D12 supersedes D1/depends on D5, 32
 evidence entries (E1–E32). Journal pre-registered the three naive priors before research; all three were reversed by R1–R3 with named trigger evidence.

- **Replication company (predeclared):** Disney (DIS) — Day 6.

- **Autonomous schedule:** cron `world-exp002-daily`, daily ~09:42 ET America/New_York, owner `goal:world-experiment-002-7-day-workflow`, timeout 2h, 1 retry on
 runtime failure. Retires itself after Day 7.

- **Last updated:** 2026-09-19 09:50 ET (Day 3 — three handoffs built, measured, blind-labeled, committed)
