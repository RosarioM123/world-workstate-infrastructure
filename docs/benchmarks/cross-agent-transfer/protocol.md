# Cross-Agent Transfer Test — Protocol

**Goal:** test whether the WORLD state bundle is portable across agent vendors. Portability is the thesis's defense against native agent memory: if only one model family can use the bundle, the wedge collapses the day a vendor ships built-in memory.

**Baseline to compare against:** same-vendor WORLD-state continuation scored **3.92/5** (experiment #002, n=1, blinded). A transfer run that holds near that number is evidence of portability.

## Materials (all in this directory)

- `frozen-bundle.md` — the bundle to hand over (frozen 2026-09-21 from experiment #002's WORLD-state handoff; do not edit).
- `continuation-brief.md` — the exact brief to paste alongside it.
- `answer-key.md` — the predeclared scoring key. **Sealed:** the runner must never see it. Only the scorer uses it.
- `scoring-sheet.md` — the 14 metrics.

## Running it on another vendor (10 minutes)

1. Open a fresh chat in the other vendor's app. No prior context, no system-prompt tricks.
2. Paste the entire contents of `continuation-brief.md`, then the entire contents of `frozen-bundle.md`.
3. Forbid browsing/research in the prompt (the measurement is handoff retention, not live research).
4. Do not name the condition or the experiment. The runner should not know it is holding a WORLD-state bundle.
5. Save the full output verbatim.

## Scoring

- An independent scorer (a different session, or a third party) grades the output against `answer-key.md` on the 14 metrics, without knowing which condition produced it.
- Record the mean and the per-metric deltas vs. the 3.92 baseline.

## What counts as evidence

- **Evidence:** a run on a **different vendor and different model family** from the baseline.
- **Not evidence:** a run on the same model family. That is a *shakedown*: useful for checking the kit's mechanics, worthless for the portability claim. Label it as such.

## The rigorous version (2x2)

A single transfer run has a confound: if the other vendor scores lower, is the bundle unportable or is the vendor weaker? The clean design crosses vendor with handoff type: the other vendor also continues from the *journal* and the *summary* handoffs. Portability is proven if WORLD-state beats that vendor's own alternatives, not if it matches our 3.92.

## Result template

- Date, vendor, model, which bundle version.
- Mean score, per-metric deltas vs. baseline.
- Verdict in one sentence: portable / not portable / inconclusive, and why.
