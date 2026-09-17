# Development Log

Newest entries first.

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
- Next: fill in `research/comparisons.md`, then run the handoff experiment
  manually (no app) before any build decision.
