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
