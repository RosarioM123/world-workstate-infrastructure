# Experiment #002 — Day 3 (2026-09-19): Three handoffs built and blind-labeled

## What was done

Built the three handoff conditions from the same Agent A Phase 1 Intel (INTC) output, per protocol §2 and the Day 3 runbook:

- **A — Structured WORLD state.** Cleaned copy of Agent A's `world_state.md` (authored 2026-09-17). Cleaning was minimal and mechanical only: `/tmp/exp002/` and `/tmp/world/docs/` path references updated to their repo equivalents. No substantive content added, removed, or edited.
- **B — Independent conventional summary.** Written by a separate subagent ("summary writer") that received **only** the journal + report and was explicitly instructed per protocol §2: *"Create the best possible conventional handoff summary for another agent who must continue this work. Preserve as much decision rationale, assumptions, revisions, constraints, evidence, and unresolved questions as possible. Do not use WORLD's structured schema."* The writer was spawned **before** the parent read the WORLD state file, so the state content was never in the writer's inherited context; the writer confirmed it never opened or referenced the state file, used no schema IDs, and wrote in natural prose. 2,446 words.
- **C — Raw journal.** Byte-identical copy of Agent A's unedited research journal (`agent-a-journal.md`).

Integrity verification:
- The day-3 working copies of the journal and report are byte-identical to the archived Day 2 versions (no drift).
- Summary checked for leakage: no "world_state"/"state-model" references, no schema-style decision IDs (no `D\d` patterns), no blind labels, no condition identifiers.
- All three blind-labeled files scanned for condition-identifying language; the only match is the WORLD state's own section header "## 10. Handoff bundle", which is Agent A's original content and identifies no condition.

## Measurements

| Handoff | Form | Words | Est. tokens¹ | Structured schema fields |
|---|---|---|---|---|
| X | raw journal (unedited, chronological) | 3,616 | ~4,821 | 0 (prose) |
| Y | structured WORLD state (10 sections) | 3,173 | ~4,230 | 14 decision entries · 13 assumptions w/ confidence · 3 revisions · 32 evidence entries · 6 open questions · 4 guardrails · 12 tasks · 39 changelog rows |
| Z | independent conventional summary (prose) | 2,446 | ~3,261 | 0 (prose); covers all 3 revisions, both superseded-decision histories, guardrails, 6+ open questions, both failed approaches in narrative form |

¹ Token estimate ≈ words × 4/3 (English prose heuristic).

Information-density notes:
- The summary (B) is the most input-efficient handoff: 32% shorter than the raw journal, 23% shorter than the WORLD state.
- The WORLD state (A) carries the only machine-readable governance structure (decision supersession graph D1←D12, D7←D6; revision chain R1–R3; dependency D13→D5; append-only changelog).
- The raw journal (C) is longest but its governance content (decisions, revisions) is embedded in chronological narrative — recoverable but not indexed.

## Blinding

X/Y/Z labels were assigned by random draw (`python3 random`, one shuffle of conditions over labels). The private mapping is recorded **only** in `experiment-state.md`, the single location the Day 5 evaluator is instructed to defer reading until after grading. No evaluator-visible file names the mapping. Files committed as `docs/experiment-002/handoff-x.md`, `handoff-y.md`, `handoff-z.md`.

## Stored in repo (docs/experiment-002/)

- `handoff-x.md` — blind handoff X
- `handoff-y.md` — blind handoff Y
- `handoff-z.md` — blind handoff Z
- `day-03.md` — this file

## For Day 4

Three isolated Agent B continuations, identical brief, no browsing, per protocol §5 — one run per blind handoff file (x/y/z). Runs are not told which condition each letter maps to, and their outputs must have filename/format echoes stripped before storing as `agent-b-x.md` / `agent-b-y.md` / `agent-b-z.md`.
