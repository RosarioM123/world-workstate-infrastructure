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
