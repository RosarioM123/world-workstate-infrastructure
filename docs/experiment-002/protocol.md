# Experiment #002 — Protocol

**Status:** active (Day 1 of 7)
**Repository:** `RosarioM123/world` (public) — the persistent source of truth for this experiment.
**Date map:** Day 1 = 2026-09-17 · Day 2 = 2026-09-18 · Day 3 = 2026-09-19 · Day 4 = 2026-09-20 · Day 5 = 2026-09-21 · Day 6 = 2026-09-22 · Day 7 = 2026-09-23.

## 1. Hypothesis under test

> Structured persistent work-state preserves decision governance, revision history, constraints, and provenance better than conventional summaries or raw transcripts when complex work is handed from one agent to another.

This hypothesis is **not assumed true**. The experiment is designed to give conventional alternatives their strongest fair showing. If the evidence says WORLD is unnecessary, the results must say so.

## 2. Conditions

Three handoffs, built from the same Agent A research output:

- **A — Structured WORLD state.** The current WORLD state representation, per `docs/state-model.md`.
- **B — Independently written conventional summary.** A high-quality natural-language handoff created by a *separate, independent* context/model that receives only Agent A's raw material (journal + report). It is instructed: *"Create the best possible conventional handoff summary for another agent who must continue this work. Preserve as much decision rationale, assumptions, revisions, constraints, evidence, and unresolved questions as possible. Do not use WORLD's structured schema."* It never sees the WORLD state file. It has no incentive to make WORLD look better.
- **C — Raw transcript/journal.** Agent A's unedited running journal.

## 3. Required state complexity (Agent A output)

Agent A's research must contain at minimum:

- 10–15 meaningful decisions, each with rationale and linked evidence
- 10+ assumptions, each with an explicit confidence level (high / medium / low, with intermediates allowed)
- At least 3 genuine revisions to previous assumptions (old → new → triggering evidence)
- At least 2 decisions later **superseded** by newer decisions (history preserved, marked superseded)
- At least 2 explicit constraints/guardrails binding Phase 2
- Multiple pieces of evidence supporting *and* contradicting key decisions
- At least 3 unresolved open questions
- At least 1 failed research approach (documented)
- At least 1 decision whose rationale explicitly depends on a previous decision
- Clear provenance (source URLs) for important claims

## 4. Agent A specification

- **Task:** investment research on **Intel Corporation (NASDAQ: INTC)**, 3–5 year horizon. (Not Block/SQ — Experiment #001's company.)
- Must browse live sources; public sources only; no invented numbers/quotes; conflicts between sources disclosed.
- Coverage: foundry strategy (IFS), process roadmap (18A+), product divisions (Client, Data Center & AI), AI positioning vs NVIDIA/AMD, financial health (cash, debt, dividend, restructuring), competitive position vs AMD/NVIDIA/TSMC, government relationship (CHIPS Act, 2025 US equity stake), leadership changes, credible M&A/partnership developments.
- **Out of scope:** valuation modeling, the final buy/hold/sell recommendation, application code. Left unfinished for Phase 2.
- Produces: raw journal, final report (findings, evidence w/ URLs, assumptions w/ confidence, decisions w/ rationale, revisions, constraints, open questions, failed approaches, unfinished business), and a structured WORLD state bundle per the state model.
- Procedural note: Agent A research was launched during Day 1 setup (before the 7-day plan was received). Day 2 verifies and captures its outputs; it is not re-run unless the outputs are missing or fail the complexity minimums.

## 5. Agent B specification (Day 4)

- Three isolated continuations, one per handoff condition.
- Same model, same task, equivalent research access, equivalent time/token limits.
- No access to Agent A's original context, no access to other conditions, not told which condition it received.
- Outputs labeled with blind codes (X/Y/Z, randomly assigned); filename/format echoes stripped before grading.
- **No browsing** (matches Experiment #001; keeps the measurement on handoff retention, not live research).
- Identical continuation objective:

> Continue the research, resolve open questions, revisit assumptions where appropriate, perform the next analysis, update the thesis, and make the next research decisions while respecting inherited constraints and prior decisions.

## 6. Blind evaluation (Day 5)

Independent evaluator where possible. Score each continuation individually on:

1. Decision preservation
2. Decision rationale
3. Assumption preservation
4. Confidence preservation
5. Revision history
6. Constraint/guardrail preservation
7. Provenance
8. Superseded decisions
9. Open questions
10. Continuation quality
11. Unsupported assumptions
12. Contradictions
13. Information lost
14. Output efficiency

Do **not** collapse into a single score prematurely; record individual results. Also record cases where WORLD created unnecessary complexity or overhead. Predeclare the answer key from Agent A's decisions/assumptions *before* grading.

## 7. Replication (Day 6)

- Second investment-research task, different company, **predeclared here: Disney (DIS)** — different sector (media/streaming vs semiconductors), chosen now to prevent cherry-picking after seeing Day 1–5 results.
- Repeat the core portions: Agent A research (lighter is acceptable), three handoffs, three Agent B continuations, blind grading on the §6 metrics.
- Do not change the protocol because an earlier result favors or disfavors WORLD. If a methodological problem is discovered, document it rather than quietly changing the experiment.
- Record whether the result replicates.

## 8. Analysis and verdict (Day 7)

`docs/experiment-002/results.md` must include: protocol, tasks, Agent A research, all three handoffs, Agent B outputs, blind grading, individual metrics, token/input comparison, information loss, failure cases, replication results, where WORLD helped, where WORLD hurt, strongest evidence against WORLD, strongest evidence supporting WORLD, whether Experiment #001 replicated, updated WORLD hypothesis, whether another experiment is needed, whether prototype development is justified.

Then update `docs/hypothesis.md` if the evidence warrants it, update `docs/development-log.md`, and provide a concise final research verdict in the repo docs.

## 9. Critical research rule

Do not assume WORLD is correct. The purpose is to determine whether structured persistent work-state provides a meaningful advantage over increasingly strong conventional alternatives. If the evidence supports WORLD, identify **exactly what advantage was demonstrated**, not a broad claim. **Do not build the application during this experiment.** Move toward prototype development only if the evidence justifies it.

## 10. Known limitations (disclose, do not hide)

1. Subagents inherit parent-conversation context — no genuine context isolation between Agent A and Agent B.
2. Same model family throughout; different Agent A/Agent B models unavailable.
3. Single task (n=1) for the main run; replication is n=1 more, not a sample.
4. Blinding is imperfect; mitigation is filename-echo stripping and post-grading mapping disclosure.
5. Agent A authors the WORLD state (improvement over #001, where the experimenter authored both WORLD state and summary).
6. The evaluator's answer key is experimenter-built; grading corrections must be disclosed as in #001.

## 11. Validity conditions

The experiment remains valid only if: the three conditions derive from the same Agent A output; the summary writer never sees the WORLD schema; Agent B runs are blinded; grading uses a predeclared key; and all deviations are documented in `experiment-state.md` rather than silently absorbed.

## 12. Autonomous execution runbook

Each scheduled daily run must:

1. Determine the current date (local) and map it to the experiment day via the date map above. If the date is outside 2026-09-17…2026-09-23, stop and report.
2. Read `docs/experiment-002/experiment-state.md` from the repo (raw: `https://raw.githubusercontent.com/RosarioM123/world/main/docs/experiment-002/experiment-state.md`) and this protocol. Never redo a completed day; never silently skip a failed step.
3. Execute that day's phase per the day plan below.
4. Update `experiment-state.md`, write `day-0N.md`, append to `docs/development-log.md`.
5. Commit everything to `main` via the GitHub Contents API using `python3 ~/workspace/skills/github/bin/gh_files.py` (auth is via the stored `custom.github` credential; never ask for or print keys). If the helper is missing, reconstruct it from the skill at `~/workspace/skills/github/SKILL.md`. If auth fails, document the blocker in `experiment-state.md` — do not fake a commit.
6. Leave explicit next-day instructions in `experiment-state.md`.

### Day plans

- **Day 1 (Sep 17):** Finalize this protocol; create `experiment-state.md`; write `day-01.md`; update development log; commit. (Done in the founding session.)
- **Day 2 (Sep 18):** Verify Agent A's Intel research outputs (expected at `~/workspace/exp002/agent-a/`; re-run Agent A if missing/incomplete or below complexity minimums). Capture raw journal, evidence, claims, assumptions, decisions, rationale, confidence, revisions, superseded decisions, constraints, open questions, failed approaches, provenance. Write `day-02.md`. Do not let Agent B see this work. Commit.
- **Day 3 (Sep 19):** Build the three handoffs. A: structured WORLD state from Agent A's bundle (cleaned, schema-conformant). B: independent summary writer — separate context, receives journal + report only, never the WORLD state, instructed per §2 to maximize useful information without the schema. C: raw journal. Measure words (and tokens if available), structured-field counts, information density. Blind-label the handoffs X/Y/Z with a private mapping stored only in `experiment-state.md` (never in files the evaluator sees). Write `day-03.md`. Commit.
- **Day 4 (Sep 20):** Run three isolated Agent B continuations per §5. Strip filename/format echoes from outputs before storing. Store outputs as `agent-b-x.md` / `agent-b-y.md` / `agent-b-z.md` under `docs/experiment-002/`. Write `day-04.md`. Commit.
- **Day 5 (Sep 21):** Blind evaluation per §6 with a predeclared answer key (build the key from Agent A's decisions/assumptions *before* grading). Use an independent evaluator context. Record all 14 metrics individually plus WORLD-overhead observations. Write `day-05.md`. Commit. (Mapping X/Y/Z → conditions is revealed only after grading.)
- **Day 6 (Sep 22):** Replication on Disney (DIS) per §7 — lighter Agent A, three handoffs, three B continuations, blind grading on §6 metrics. Record whether the result replicates. Write `day-06.md`. Commit.
- **Day 7 (Sep 23):** Write `results.md` per §8; update `docs/hypothesis.md` if warranted; update development log; write `day-07.md`; commit; then disable the daily schedule (it has served its purpose).
