You are a senior engineer continuing a colleague's work. You have received a handoff describing what they did and decided. Read it carefully, then complete the task below.

Rules:
- Use ONLY the handoff. Do not invent facts, numbers, owners, or deadlines.
- If the handoff leaves something open, say so explicitly instead of guessing.
- Write directly; no preamble about being an AI.


[Format: written summary]

--- HANDOFF FROM PREVIOUS AGENT ---
# Handoff summary — checkout API outage (task_002)

**What happened:** 14:02–14:47 UTC (45 minutes), 312 failed checkouts,
≈$18,400 lost revenue. Root cause was **not** a database failure — the
database was never down and the DB was fine. Deploy v2.14 shipped a config change cutting the
DB connection pool from 100 to 20; the pool exhausted under normal load.
The change rode along unreviewed inside the release PR. The canary (5
minutes at 1% traffic) was structurally unable to catch pool exhaustion.

**Decisions:** Roll back to v2.13 immediately — done 14:20 — then fix
forward (stop the bleeding first; v2.14 features weren't urgent). Keep
v2.14's new checkout UI behind a feature flag on re-release, to decouple
the UI rollout from backend changes. No blame on the on-call engineer:
the unreviewed config change is a process failure.

**Open questions:** Who approved bundling the config change into the
release PR? Why did the canary duration and traffic level not catch
pool exhaustion? Are there other services with silently reduced pool
sizes?

**Next:** connection-pool saturation alert (on-call, due Oct 21);
separate review required for config changes in release PRs (eng manager);
canary load-tested at 10% traffic for a 30 min minimum (platform);
Priya audits pool sizes across all services.

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