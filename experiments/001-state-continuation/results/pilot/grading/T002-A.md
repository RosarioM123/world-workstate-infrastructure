**Corrective actions**

1. **Connection-pool saturation alert** — owner: on-call, due Oct 21. Page before exhaustion, not after.
2. **Separate review required for config changes in release PRs** — owner: eng manager. The pool cut from 100 to 20 shipped unreviewed inside the v2.14 release PR; that path is now closed.
3. **Canary load test: 10% traffic for 30 min minimum** — owner: platform. The 5-minute, 1% canary was structurally unable to catch pool exhaustion; the canary duration and traffic level must reflect production load.
4. **Audit connection pool sizes across all services** — owner: Priya. Open question: are there other services with silently reduced pool sizes?

**What we will NOT do**

- **No blame on the on-call engineer.** The unreviewed config change was a process failure, not an individual one.
- **No pool-size bump as the fix.** Restoring 100 connections is assumed; raising the pool to 200 treats the symptom. The fix is detection (alerts), prevention (review), and realistic canaries.
- **No re-investigation of the database.** The database was never down — this was pool exhaustion. Root cause is confirmed.

**Still open:** who approved bundling the config change into the release PR; whether the canary policy change fully covers this failure class.
