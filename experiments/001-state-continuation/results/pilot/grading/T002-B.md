**Corrective actions**

| # | Action | Owner | Deadline |
|---|--------|-------|----------|
| 1 | Add connection-pool saturation alert | on-call | Oct 21 |
| 2 | Require separate review for config changes in release PRs | eng manager | — |
| 3 | Canary load test at 10% traffic, 30 min minimum | platform | — |
| 4 | Audit pool sizes across all services | Priya | — |

**Rationale.** The outage (14:02–14:47 UTC, 45 minutes, 312 failed checkouts, ≈$18,400) was pool exhaustion: v2.14 cut the pool from 100 to 20 in an unreviewed config change, and the 5-minute 1% canary was too small to surface it. Rollback to v2.13 completed 14:20; the v2.14 UI stays behind a feature flag on re-release.

**Will NOT do:**

- Blame the on-call engineer — the unreviewed change is a process failure.
- Increase the pool to 200 as the remedy — detection and prevention are the fix, not a bigger pool.
- Reopen the root-cause question — the database was never down; the DB was fine.

**Open:** who approved bundling the config change into the release PR; whether other services have silently reduced pool sizes; why the canary duration and traffic level were insufficient.
