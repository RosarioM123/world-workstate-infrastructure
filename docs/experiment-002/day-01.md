# Day 1 — September 17, 2026: Finalize Experiment #002

## What was done

- Wrote the full Experiment #002 protocol (`protocol.md`), incorporating:
  - the #002 design from the prior session (new company, complexity minimums, independent summary writer, three conditions),
  - the 7-day autonomous workflow (date map, daily phases, runbook),
  - the critical research rule (do not assume WORLD is correct; no application build during the experiment),
  - predeclared replication company (Disney, Day 6) to prevent cherry-picking,
  - the 14-metric blind evaluation rubric (individual scores, no premature collapse),
  - known limitations carried from #001 (no true context isolation, same model family, n=1, imperfect blind) plus mitigations (Agent A authors its own WORLD state; filename-echo stripping; predeclared answer key).
- Created the control file (`experiment-state.md`) with the fields required for autonomous resume.
- Added a GitHub Contents-API file helper (`~/workspace/skills/github/bin/gh_files.py`, get/put) so scheduled daily runs can commit without interactive credentials. Verified read access against the live repo.
- Updated `docs/development-log.md`.

## Decisions

- **Intel (INTC)** selected as the Agent A research task: foundry bet, leadership turnover, dividend suspension, 2025 US government equity stake, and 18A execution risk give it the decision/revision density the complexity minimums require. Not Block/SQ.
- **Disney (DIS)** predeclared for the Day 6 replication: different sector, chosen before any results exist.
- Agent B continuations keep **no browsing** (matches #001; measures handoff retention, not live research).
- One daily scheduled run (~09:00 ET, Sep 18–23) executes each day's phase from `protocol.md` + `experiment-state.md`; the Day 7 run disables the schedule afterward.

## Procedural note (disclosed, not hidden)

Agent A research on Intel was launched during Day 1 setup, before the 7-day plan arrived (the prior instruction was "draft and run Experiment #002"). Day 2 verifies and captures its outputs rather than re-running it. If outputs are missing or fall short of the complexity minimums, Day 2 re-runs Agent A.

## Next experiment day

**Day 2 (Sep 18):** verify Agent A's Intel outputs at `~/workspace/exp002/agent-a/` (journal, report, WORLD state); check complexity minimums; capture everything into `day-02.md`; commit. Do not let Agent B see this work.
