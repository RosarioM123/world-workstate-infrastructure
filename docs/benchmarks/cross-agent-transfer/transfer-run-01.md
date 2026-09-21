# Transfer Run 01 — 2026-09-21

First external-vendor run of the cross-agent transfer test.

**Date:** 2026-09-21
**Vendor:** Anthropic (user reported "Claude"; exact model ID unconfirmed)
**Bundle:** `frozen-bundle.md` (frozen 2026-09-21, sha `5aa6fc5933`) + `continuation-brief.md`, pasted verbatim per `protocol.md`
**Runner:** user, in the vendor's chat app (fresh-chat status unconfirmed)
**Scorer:** separate subagent session applying the rubric mechanically against the sealed key; vendor identity withheld from the scorer at scoring time; answer key never shown to runner or user
**Output:** `transfer-run-01-output.md` (verbatim, saved same day)

## Scores (14 metrics)

| # | Metric | Score | Note |
|---|---|---|---|
| 1 | Decision preservation | 5 | All 14 decisions present, correctly stated |
| 2 | Decision rationale | 4 | Why survives for most; D12's joint-KPI rationale implied, not stated |
| 3 | Assumption preservation | 5 | All 13 carried, every change explicitly marked |
| 4 | Confidence preservation | 4 | Label system intact; changes reasoned, not silent |
| 5 | Revision history | 3 | Supersessions named, but R1-R3 old/new/trigger chains not reconstructed |
| 6 | Constraint/guardrail preservation | 5 | G1-G4 restated, weak sources excluded from base case |
| 7 | Provenance | 4 | Evidence IDs throughout; some section-1 figures lack inline tags |
| 8 | Superseded decisions | 5 | D1/D7 stay dead; naive priors retired, not resurrected |
| 9 | Open questions | 5 | All six carried, none closed; Q7-Q9 added as labeled new items |
| 10 | Continuation quality | 4 | D15-D20 sound and operational; one dangling "N3" cross-reference |
| 11 | Unsupported assumptions | 1 (count) | A14: escrowed-share MTM moves with share price (self-flagged "not stated in the record") |
| 12 | Contradictions | 0 (count) | All spot-checked figures match the bundle |
| 13 | Information lost | (list) | R1-R3 trigger chains; D12->D5 dependency; Ireland SCIP 49% buyback caveat; D8 "real economic cost" nuance |
| 14 | Output efficiency | 4 | Dense, all 8 sections; minor thesis/section-2 repetition |

**Mean (metrics 1-10 + 14):** 4.36 vs WORLD-state baseline 3.92 (+0.44); journal 3.58; summary 3.33.

## Verdict

Provisional: **portable** — a different vendor's model scored 4.36, above the 3.92 same-vendor baseline, with zero contradictions and one honestly-flagged unsupported inference. Final confirmation pending: (1) the run used a fresh chat with no prior context, (2) the exact model ID. Single-run caveat: the 2x2 journal/summary conditions on the same vendor would be needed to separate bundle portability from vendor strength.

## Notes

- The earlier 2026-09-21 Claude-produced continuation (D15-D21, G5) predates the frozen paste package and was not produced under this protocol; it is logged as an Experiment #002 subject-project event, not counted as a transfer run.
- Answer key remains sealed; only scores and deltas are reported here.
