# Scoring sheet — 14 handoff metrics

Grade the continuation against `answer-key.md` (sealed from the runner). Metrics 1–10 and 14 use 0–5 anchored scales; 11–12 are counts (lower is better); 13 is an itemized list.

| # | Metric | What to check against the key |
|---|---|---|
| 1 | Decision preservation | Are the key's decisions present and correctly stated? |
| 2 | Decision rationale | Is the *why* behind each decision preserved, not just the what? |
| 3 | Assumption preservation | Are the key's assumptions carried over? |
| 4 | Confidence preservation | Do confidence labels survive (low/medium/high)? |
| 5 | Revision history | Are supersessions shown as old → new → trigger? |
| 6 | Constraint/guardrail preservation | Are binding constraints respected, none dropped? |
| 7 | Provenance | Are claims traceable to their sources? |
| 8 | Superseded decisions | Are dead decisions marked dead, not resurrected? |
| 9 | Open questions | Are open questions carried, none silently closed? |
| 10 | Continuation quality | Is the new analysis sound and non-redundant? |
| 11 | Unsupported assumptions | Count of new assumptions with no basis in the bundle |
| 12 | Contradictions | Count of statements contradicting the bundle |
| 13 | Information lost | Itemized list of key items missing from the continuation |
| 14 | Output efficiency | Signal per token; no padding |

**Reference means** (metrics 1–10 + 14): baseline WORLD-state continuation = 3.92; journal = 3.58; summary = 3.33. Report the new run's mean the same way, then the per-metric deltas that matter.
