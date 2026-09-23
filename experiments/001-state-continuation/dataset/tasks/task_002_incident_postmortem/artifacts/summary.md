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
