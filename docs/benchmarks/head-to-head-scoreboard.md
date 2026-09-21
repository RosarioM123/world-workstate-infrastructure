# WORLD — Head-to-Head Handoff Scoreboard

**Maintained by:** startup validation program · **First row:** 2026-09-21
**Question answered:** does structured WORLD state preserve decision governance across a handoff better than the conventional alternatives?

## Method (frozen for all rows)

- Three handoff conditions from the same source work: **WORLD state**, **raw journal/transcript**, **independent summary** (written by a separate context that never saw the WORLD state, instructed to maximize useful info).
- Same model, identical continuation brief, no browsing, blinded grading against a **predeclared answer key** built before grading.
- 14 metrics: decision preservation, decision rationale, assumption preservation, confidence preservation, revision history, constraint/guardrail preservation, provenance, superseded decisions, open questions, continuation quality, unsupported assumptions (count), contradictions (count), information lost, output efficiency.
- Full method: `docs/experiment-002/protocol.md` §5–§6.

## Row 1 — Experiment #002, equity-research domain (2026-09-21)

Source: `docs/experiment-002/day-05.md` (verified). Blinded; mapping revealed only after grading.

| # | Metric | Journal (X) | WORLD (Y) | Summary (Z) |
|---|---|---|---|---|
| 1 | Decision preservation | 4 | 4 | 3 |
| 2 | Decision rationale | 4 | 4 | 3 |
| 3 | Assumption preservation | 3 | **5** | 3 |
| 4 | Confidence preservation | 4 | **5** | 3 |
| 5 | Revision history | 3 | 2 | 2 |
| 6 | Constraint/guardrail preservation | 5 | 5 | 4 |
| 7 | Provenance | 4 | 4 | 4 |
| 8 | Superseded decisions | 4 | 4 | 4 |
| 9 | Open questions | 4 | 5 | 5 |
| 10 | Continuation quality | 5 | 5 | 5 |
| 11 | Unsupported assumptions (lower better) | 0 | 0 | 0 |
| 12 | Contradictions (lower better) | 0 | 0 | 0 |
| 14 | Output efficiency | 3 | 4 | 4 |
| | **Mean, metrics 1–10 + 14 (reference only)** | **3.58** | **3.92** | **3.33** |

**Headline:** WORLD state wins overall (+0.34 over journal, +0.59 over summary), driven by assumption and confidence preservation (5/5 on both). Revision history is weak across all conditions, and WORLD scored worst there (2) — an honest limit, not a win. No contradictions in any condition.

**Caveats (do not drop these when citing the score):** n=1, one domain, one model family, imperfect blinding (documented in day-05.md §2), means are reference-only.

## Planned rows

- **Row 2 — coding-domain handoff benchmark.** Three conditions (bundle vs. strong auto-summary vs. transcript) on a real multi-session coding task. Owned by the 09-23 startup mission (`docs/startup/mvp.md` §7.1).
- **Row 3 — Disney (DIS) replication.** Experiment #002 Day 6 reruns the protocol on a second domain. Tests whether Row 1 replicates.
- **Row 4 — cross-agent transfer.** Same bundle handed to a different vendor's agent. Kit: `docs/benchmarks/cross-agent-transfer/`.

## Adding a row (template)

Copy this block, fill it, keep the caveats line:

- **Row N — <domain> (<date>):** conditions, n, blinding method, answer-key link.
- Scores per condition (mean + the metrics where the winner won).
- Headline delta in one sentence.
- Caveats: sample size, domains, model families, blinding imperfections.
