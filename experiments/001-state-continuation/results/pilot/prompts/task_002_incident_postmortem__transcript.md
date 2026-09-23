You are a senior engineer continuing a colleague's work. You have received a handoff describing what they did and decided. Read it carefully, then complete the task below.

Rules:
- Use ONLY the handoff. Do not invent facts, numbers, owners, or deadlines.
- If the handoff leaves something open, say so explicitly instead of guessing.
- Write directly; no preamble about being an AI.


[Format: chronological transcript]

--- HANDOFF FROM PREVIOUS AGENT ---
# Agent A — incident work journal (task_002_incident_postmortem)

## 14:02 — pages fire

Checkout API p99 latency off a cliff. Error rate climbing. I pull the
deploy log: v2.14 went out at 13:55. Correlation is not causation, but it
is a strong hint.

## 14:09 — root cause found

Diffing v2.14 against v2.13, I find a config change buried in the release
PR: the database connection pool cut from 100 to 20. No separate review
— it rode along unreviewed inside the release PR. Under normal checkout
load, 20 connections exhaust almost immediately. The database was never down; the DB was fine. This is pool exhaustion, not a database
outage. Important distinction — the corrective actions are completely
different.

## 14:15 — why didn't the canary catch it?

The canary ran 5 minutes at 1% traffic. At 1% of normal load, 20
connections are plenty. The canary duration was simply too short. Pool exhaustion only shows up at real traffic.
The canary's duration and traffic level were structurally incapable of
catching this class of failure.

## 14:20 — rollback

Decision: roll back to v2.13 immediately, then fix forward. Rationale:
stop the bleeding first — none of the v2.14 features were urgent enough
to keep serving errors for. Rollback completed 14:20.

## 14:47 — recovery confirmed

Error rates back to baseline. Totals: outage 14:02–14:47 UTC, 45
minutes; 312 failed checkouts; ≈$18,400 in lost revenue.

## Decisions locked

1. **Roll back to v2.13 immediately (done 14:20), then fix forward.**
   Rationale: stop the bleeding first.
2. **Keep v2.14's new checkout UI behind a feature flag on re-release.**
   Rationale: decouple the UI rollout from backend changes.
3. **No blame on the on-call engineer.** Rationale: the config change
   shipped unreviewed — a process failure, not an individual one.

## Open questions

- Who approved bundling the config change into the release PR?
- Why did the canary duration and traffic level not catch pool exhaustion?
- Are there other services with silently reduced pool sizes?

## Next actions

- On-call: add a connection-pool saturation alert (due Oct 21).
- Eng manager: require separate review for config changes inside release PRs.
- Platform: load-test the canary at 10% traffic for a 30 min minimum.
- Priya: audit connection pool sizes across all services.

Handing off: the "Corrective actions" section is the next deliverable.

--- END HANDOFF ---

--- YOUR TASK ---
# Task 002 — Checkout API outage postmortem

## Background

On Oct 14, the checkout API suffered a 45-minute outage (14:02–14:47
UTC): p99 latency spiked, 312 checkouts failed, ≈$18,400 in lost revenue.
Root cause: deploy v2.14 shipped a config change cutting the database
connection pool from 100 to 20; the pool exhausted under normal load. The
canary ran 5 minutes at 1% traffic — far too little to surface pool
exhaustion. The config change rode along unreviewed inside the release
PR. The database itself was never down. Rollback to v2.13 completed at
14:20; full recovery at 14:47.

## Agent A's prior work

Agent A reconstructed the timeline, confirmed the root cause (pool
100→20, not a database failure), and locked three decisions: roll back
first and fix forward (done at 14:20); keep v2.14's new checkout UI
behind a feature flag on re-release to decouple it from backend changes;
and no blame on the on-call engineer — the unreviewed config change is a
process failure, not an individual one.

## Continuation brief (identical across conditions)

> Write the "Corrective actions" section of the postmortem: each action
> with owner and deadline, plus what explicitly will NOT be done. Keep
> it under 300 words.

--- END TASK ---