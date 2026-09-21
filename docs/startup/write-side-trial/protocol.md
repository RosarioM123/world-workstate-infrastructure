# WORLD — Write-Side Trial Protocol

**Dates:** 2026-09-21 through 2026-09-26 (5 days)
**Purpose:** Test the existential risk from `docs/startup/mvp.md` §7.2 and §8.3: *will an agent actually maintain the state bundle across real sessions, or does it rot?*
**Subject project:** The WORLD startup-validation work itself (this repo, the validation program, experiment #002). The trial is dogfooded: the recorder is an AI agent, so it directly tests agent write compliance.

## Method

Each session (each day of real work on this project):

1. **Read at session start.** Before doing project work, read `WORLD.md`. Run the rot check (below) against what you now know. Log findings in `rot-log.md`.
2. **Work normally.** No special care for the bundle during the session.
3. **Record at session end.** Append one file to `sessions/YYYY-MM-DD-NN.md` with only state-change events: decisions made/superseded, assumptions added/validated/invalidated, questions opened/answered, guardrails set. Then regenerate the bundle from the log.
4. **Time it.** Record minutes spent on steps 1 and 3.

## Rot check

Against each bundle entity, ask:
- **Stale:** Is this still true? (e.g., a decision the repo no longer reflects, a confidence label that evidence has moved)
- **Skipped:** Did a state change happen in the last session that never got recorded?
- **Wrong:** Was something recorded inaccurately?

Log each hit with date and a one-line fix. The bundle is edited; the log is append-only.

## Metrics

| Metric | Target |
|---|---|
| Sessions recorded | 5 of 5 |
| Avg write time per session | < 5 minutes |
| Stale entries at trial end | < 20% of entities |
| Skipped state changes | counted honestly, no target |

## Honest biases

- The recorder is the assistant itself, which is unusually motivated. This tests *agent* compliance, not *developer* compliance. A developer trial (Maya) remains the real test.
- Seeding is retroactive (bundle built from the last 4 days of work), so Day 1 rot detection is partly synthetic. The check still runs.

## Success bar

The trial passes if the bundle is maintained all 5 days, average write time stays under 5 minutes, and fewer than 1 in 5 entities are stale at the end. If the bundle is abandoned or rots badly, that is a valid negative result: it would mean the write side needs enforcement, which is the first honest argument for building infrastructure.
