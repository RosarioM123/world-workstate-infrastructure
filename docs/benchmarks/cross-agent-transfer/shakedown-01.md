# Transfer-kit shakedown 01 — mechanics check (2026-09-21)

**Status: SHAKEDOWN, not evidence.** Same model family as the baseline. Per the protocol, this run validates the kit's mechanics only and says nothing about cross-vendor portability.

## What ran

A fresh subagent received ONLY the frozen bundle (`frozen-bundle.md`) plus `continuation-brief.md`, with no browsing and no other context. It produced a full 8-section continuation, stored verbatim as `shakedown-01-output.md`.

## Mechanics verdict: PASS

- All 8 brief sections present, in order.
- No format commentary, no blind-code mentions, no speculation about the bundle's origin.
- No browsing performed; no facts invented beyond the bundle (weak sources explicitly labeled weak).
- Output is gradable against `answer-key.md` as-is.

## Spot check against the answer key (not a full grade)

- Decisions: D1 kept with superseded-by-D12 noted; D7 kept as superseded by D6; D13 correctly tied to D5. D8 extended, D14 split into D14a (confirmed dilution) / D14b (reported $20B raise, downgraded to hypothesis). All changes carry rationale.
- Assumptions: all 13 carried with confidence levels; A4 and A6 flagged as time-decaying (correct).
- Guardrails: G1–G4 all respected and cited by ID.
- Open questions: Q1–Q6 retained with Phase 2 notes; Q7/Q8 opened.
- Failed approaches: FA1/FA2 honored, not repeated.

## What this does not show

Whether a different vendor's agent can do the same. That requires an actual external run. The kit is ready for it: paste `continuation-brief.md` + `frozen-bundle.md` into a fresh chat on another vendor and score with `scoring-sheet.md` + `answer-key.md`.
