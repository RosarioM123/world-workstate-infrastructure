You are a senior engineer continuing a colleague's work. You have received a handoff describing what they did and decided. Read it carefully, then complete the task below.

Rules:
- Use ONLY the handoff. Do not invent facts, numbers, owners, or deadlines.
- If the handoff leaves something open, say so explicitly instead of guessing.
- Write directly; no preamble about being an AI.


[Format: structured JSON state]

--- HANDOFF FROM PREVIOUS AGENT ---
{
  "objective": "Resolve the checkout API outage and produce the postmortem with corrective actions.",
  "decisions": [
    {
      "text": "Roll back to v2.13 immediately (done 14:20), then fix forward.",
      "rationale": "Stop the bleeding first; the v2.14 features were not urgent."
    },
    {
      "text": "Keep v2.14's new checkout UI behind a feature flag on re-release.",
      "rationale": "Decouple the UI rollout from backend changes."
    },
    {
      "text": "No blame on the on-call engineer.",
      "rationale": "The config change shipped unreviewed; that is a process failure, not an individual one."
    }
  ],
  "evidence": [
    {
      "claim": "Outage ran 14:02\u201314:47 UTC, 45 minutes.",
      "source": "incident timeline"
    },
    {
      "claim": "312 failed checkouts, \u2248$18,400 in lost revenue.",
      "source": "payments dashboard"
    },
    {
      "claim": "Root cause: the v2.14 config change cut the DB connection pool from 100 to 20; the pool exhausted under normal load.",
      "source": "v2.14 diff"
    },
    {
      "claim": "The canary ran 5 minutes at 1% traffic \u2014 too little to surface pool exhaustion.",
      "source": "deploy logs"
    },
    {
      "claim": "The config change shipped unreviewed, bundled inside the release PR.",
      "source": "PR history"
    },
    {
      "claim": "The database was never down; the DB was fine throughout.",
      "source": "DB metrics"
    }
  ],
  "open_questions": [
    "Who approved bundling the config change into the release PR?",
    "Why was the canary duration and traffic level insufficient to catch pool exhaustion?",
    "Are there other services with silently reduced pool sizes?"
  ],
  "next_actions": [
    "Add a connection-pool saturation alert (owner: on-call, due Oct 21).",
    "Require separate review for config changes inside release PRs (owner: eng manager).",
    "Load-test the canary at 10% traffic for a 30 min minimum (owner: platform).",
    "Audit connection pool sizes across all services (owner: Priya)."
  ]
}

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