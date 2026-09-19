# Development Log

Newest entries first.

## 2026-09-19 — Experiment #002 Day 3: three handoffs built and blind-labeled

- Built the three Day 3 handoffs from the same Agent A Phase 1 Intel output per protocol §2: (A) structured WORLD state — cleaned copy of Agent A's `world_state.md`, mechanical path-reference fixes only; (B) independent conventional summary, 2,446 words, written by a separate subagent given only the journal + report and the protocol §2 instruction, spawned before the parent had read the WORLD state file so blinding held — writer confirmed it never saw the state file and used no schema; (C) byte-identical raw journal.
- Measurements (words; tokens ≈ words×4/3): X = 3,616 (~4,821, journal) · Y = 3,173 (~4,230, WORLD state: 14 decisions, 13 assumptions w/ confidence, 3 revisions, 32 evidence entries, 6 open questions, 4 guardrails, 12 tasks, 39-row changelog) · Z = 2,446 (~3,261, summary). The summary is the most input-efficient handoff (32% shorter than journal, 23% shorter than WORLD state); the WORLD state is the only handoff with machine-readable governance structure (supersession graph, revision chain, D13→D5 dependency, append-only changelog).
- X/Y/Z labels assigned by one `python3 random` shuffle of conditions over labels; private mapping stored ONLY in `experiment-state.md` (with an explicit warning not to read that section before Day 5 grading completes). Handoff files carry no condition identifiers; leak-scan clean.
- Build log written as `docs/experiment-002/day-03.md` (no mapping inside). Next: Day 4 (Sep 20) runs three isolated Agent B continuations, identical brief, no browsing, outputs `agent-b-x/y/z.md` with filename echoes stripped.

## 2026-09-18 — Experiment #002 Day 2: Agent A Intel outputs verified & captured

- Day 2 autonomous run verified Agent A's Phase 1 Intel (INTC) research against protocol §3 complexity minimums — all passed, no re-run: 14 decisions (D1–D14;
D1, D7 superseded with history preserved), 13 assumptions with confidence (A1′–A13), 3 genuine revisions (R1–R3), 4 guardrails (G1–G4), 6 open questions
(Q1–Q6), 2 failed approaches (FA1 official-18A-yield disclosure, FA2 primary 10-Q debt narrative), D13's rationale explicitly depending on D5, 32
provenance-tagged evidence entries (E1–E32).

- Journal (3,616 words), report (2,376 words), WORLD state (3,173 words) archived into `docs/experiment-002/` as `agent-a-journal.md`, `agent-a-report.md`,
`agent-a-world-state.md`; capture log written as `day-02.md` with verification table, decision/assumption/revision inventories, and the Day 5 answer-key seed
facts.

- Notable integrity detail: the journal pre-registered Agent A's three naive priors *before* research began (13:30 entry); all three were reversed by R1–R3 with
 named trigger evidence.

- Next: Day 3 (Sep 19) builds the three handoffs — (A) WORLD state, (B) independent summary (writer gets journal + report only, never the WORLD state file), (C)
 raw journal — blind-labeled X/Y/Z with the private mapping in `experiment-state.md` only.

## 2026-09-17 — Experiment #001 complete: WORLD state wins narrowly

- Ran the cross-agent work-state handoff experiment manually per

 `docs/experiment-handoff.md`. Agent A researched Block, Inc. (SQ/XYZ) for a

 3–5y horizon (findings, 7 assumptions, 5 decisions, 8 open questions, one

 genuine correction: the lending assumption revised from "clean growth

 lever" to "highest-upside AND highest-risk engine" after the Q3 2025 loss

 spike).

- Built three handoffs from the same Agent A output: (A) WORLD structured

 state, 1,450 words; (B) conventional summary, 1,241 words; (C) raw Agent A

 journal, 1,054 words. WORLD structuring overhead vs summary: +17% input.

- Ran three Agent B continuations (same model, same brief, no browsing),

 then blind-graded them against a predeclared answer key on the ten

 protocol measures.

- Result: WORLD 5/5 — 13/13 facts, 5/5 decisions with rationale, 7/7

 assumptions with confidence, full revision trail, zero errors, zero loss,

 shortest output (1,902 words). Summary 5/5 but lost D-002 as an explicit

 decision. Transcript 4/5 — all facts survived but the decision taxonomy

 did not (1/5 decisions, dropped D-004's "no buy thesis without a stress

 case" guardrail).

- Headline finding: facts survive every format; *governance* (decisions,

 rationale, confidence, guardrails) survives only where stated explicitly.

 WORLD's input premium was repaid in output compression.

- Verdict: supports WORLD's core claim narrowly; proceed to Experiment #002

 with a harder design (independent summary-writer, more decisions, cleaner

 blind). Full record: `docs/experiment-001-results.md`.

- Limitations disclosed in the results doc: no true context isolation

 (subagents inherit conversation), same model family throughout, n=1,

 imperfect blind (outputs echoed handoff filenames; mapping disclosed

 post-evaluation).

## 2026-09-17 — Project founded, docs-first approach

- Created the `world` repository (public) as the single home of the WORLD

 project.

- Decision: **docs before code**. The thesis-challenge (`thesis-challenge.md`)

 and the handoff experiment (`experiment-handoff.md`) must land before any

 application architecture is designed. Rationale: the biggest risks are

 conceptual (is WORLD a real abstraction?), not technical.

- Wrote the initial state model draft (`state-model.md`, v0.1) covering the

 11 state domains: context, tasks, decisions, assumptions, evidence,

 artifacts, provenance, actions, state changes, outstanding questions,

 handoff state.

- Open: choice of company for the investment-research experiment; whether

 the WORLD interface should be MCP-shaped (leaning yes — see

 thesis-challenge §5).

## 2026-09-17 — Experiment #002 launched as 7-day autonomous workflow

- Finalized the Experiment #002 protocol (`docs/experiment-002/protocol.md`): tests whether structured WORLD state preserves decision governance, revision
history, constraints, and provenance better than (A) WORLD state vs (B) an independently written conventional summary vs (C) raw transcript, on a harder task
than #001.

- Agent A task: Intel (INTC), 3–5 year horizon. Complexity minimums: 10–15 decisions, 10+ assumptions with confidence, ≥3 assumption revisions, ≥2 superseded
decisions, ≥2 guardrails, supporting/contradicting evidence, ≥3 open questions, ≥1 failed approach, ≥1 decision depending on a prior decision, provenance for
key claims.

- Key design changes vs #001: the conventional summary is written by an independent context that never sees the WORLD schema; Agent A authors its own WORLD
state (in #001 the experimenter authored both); 14-metric blind rubric recorded individually; filename-echo stripping before grading; predeclared answer key;
Day 6 replication on a predeclared second company (Disney) to prevent cherry-picking.

- Set up autonomous execution: `docs/experiment-002/experiment-state.md` is the control file; one daily scheduled run (~09:00 ET, Sep 18–23) executes each day's
phase from protocol + state and commits to `main`. Added a Contents-API file helper (`~/workspace/skills/github/bin/gh_files.py`) so scheduled runs can commit
without interactive credentials.

- Procedural note: Agent A Intel research was launched during Day 1 setup, before the 7-day plan arrived; Day 2 verifies/captures its outputs. Documented in
`experiment-state.md`.

- Critical rule restated in protocol: do not assume WORLD is correct; no application build during the experiment; prototype development only if evidence
justifies it.

- Next: Day 2 (Sep 18) verifies Agent A outputs and captures them into `day-02.md`.
