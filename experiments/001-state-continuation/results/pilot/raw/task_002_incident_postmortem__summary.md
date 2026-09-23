**Corrective actions — checkout API outage (14:02–14:47 UTC, 312 failed checkouts, ≈$18,400 impact)**

1. **Add a connection-pool saturation alert** (on-call, due Oct 21).
2. **Require separate review for config changes inside release PRs** (eng manager) — the 100→20 pool cut shipped unreviewed.
3. **Canary policy: 10% traffic for a 30 min minimum** (platform) — the 5-minute 1% canary could not have caught pool exhaustion.
4. **Audit pool sizes across all services** (Priya) — other services may carry silently reduced pools.

**Explicitly not doing:**

- Blaming the on-call engineer — process failure, not individual.
- Raising the pool to 200 as "the fix" — the pool is restored to 100; the real fixes are the alert, the review gate, and the canary policy.
- Re-litigating the database — the database was never down and the DB was fine; root cause (pool exhaustion from the v2.14 config change) is settled.

**Open questions carried forward:** who approved bundling the config change into the release PR? Why was the canary duration and traffic level insufficient to catch pool exhaustion — and does the new policy fully close that gap?
