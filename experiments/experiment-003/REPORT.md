# Experiment #003: Report

**Status:** complete. **All results PRELIMINARY, single model family,
in-environment agents only.** Protocol and preregistration:
`protocol.md` (preregistered 2026-11-03T03:33Z, before any runs).
Machine-readable results: `analysis/results.json`; full tables:
`analysis/tables.md`. Raw outputs preserved verbatim under
`results/raw/`; per-trial records in `results/raw/records.jsonl`.
Nothing in this experiment was committed or pushed.

## Design as executed

- 8 tasks (F1, F2 financial; S1, S2 software engineering; R1, R2
  revision history; C1 constraint-heavy; C2 low-governance control).
- 3 conditions: A = WORLD state bundle (fuller state model from
  `docs/state-model.md`), B = natural-language summary written by an
  independent worker from journal and report only, C = raw journal.
- 8 Agent A productions, 8 summaries, 72 continuations (3 trials per
  task per condition, fresh worker session each, randomized order,
  seed 20261102), 72 of 72 blind-graded by 8 fresh grader sessions.
  Zero failed, refused, or malformed trials; zero retries.
- Information parity gate passed for all 8 tasks before continuations
  ran (failures and fixes in the protocol run log, including two ground
  truth errata recorded before any continuation or grading).

## Results per metric (per-condition means across tasks and trials)

| Metric | A (WORLD) | B (summary) | C (transcript) | Paired A-B | Paired A-C |
|---|---|---|---|---|---|
| 1 Decisions | 0.948 | 0.979 | 0.979 | -0.031 | -0.031 |
| 2 Constraints | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 |
| 3 Assumptions | 0.721 | 0.500 | 0.488 | +0.221 | +0.233 |
| 4 Provenance | 0.880 | 0.872 | 0.880 | +0.008 | 0.000 |
| 5 Revision history | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 |
| 6 Contradictions (count) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 7 Fabricated (count) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 8 Quality (0 to 3) | 2.625 | 2.625 | 2.583 | 0.000 | +0.042 |
| 9 Loss count (items missed) | 0.250 | 0.375 | 0.417 | -0.125 | -0.167 |

n = 24 continuations per condition for most metrics (21 for metric 3,
18 for metric 5). No significance tests, per preregistration. Full
per-task tables in `analysis/tables.md`.

### The one consistent WORLD advantage: assumptions (metric 3)

Condition A scored higher on assumption retention in 5 of 7 tasks that
have assumptions, and never lower. The mechanism is visible in the
verdict composition (45 assumption items per condition): A earned
24 full, 15 partial, 6 miss; B earned 6 full, 30 partial, 9 miss; C
earned 6 full, 29 partial, 10 miss. Continuations in all conditions
usually recovered the assumption's substance; B and C continuations
typically lost its confidence level or its fact-vs-assumption status
(partial), because summaries and journals rarely carry those fields
explicitly. The state bundle carries them as fields, and they survived.
This is the clearest evidence in the experiment for a structured state
model, and it is narrow: it concerns metadata about assumptions, not
the assumptions themselves.

### Negative findings, stated plainly

1. **Revision history showed no WORLD advantage and no weakness.**
   Metric 5 was 1.000 in all three conditions: all 33 chain instances
   per condition in the revision subset (R1, R2, F1, S1) were
   reconstructed with all 6 checklist elements, and no failure-cause
   codes arose. This contradicts Experiment #002, where WORLD scored
   2 of 5 on revision history in both runs. Under this protocol
   (parity-gated artifacts, these tasks, this model family) the
   revision problem did not reproduce in any condition, so the
   experiment cannot distinguish the representations on the metric
   H2 singled out. Possible contributors: the parity gate forced
   revision elements into every artifact; the chains here were fewer
   and cleaner than #002's; graders may be lenient at ceiling.
2. **Decision retention slightly favored the baselines.** A scored
   0.948 against 0.979 for both B and C (paired -0.031). The gap is
   one task: on C1, all three A continuations earned only partial
   credit on decision D1 while all B and C continuations earned full,
   and judged quality on C1 was A 2.0 against B 3.0 and C 3.0.
3. **WORLD was the least context-efficient condition on every task.**
   State bundles totaled 20,382 words against 6,142 for summaries and
   7,488 for journals (3.3x and 2.7x). Preservation per 1,000 words
   was lowest for A on all 8 tasks (for example R2: A 0.380, B 1.648,
   C 1.211). The structure costs several times the words for
   preservation that is equal on most metrics.
4. **Unverifiable additions appeared only under A.** Fabrications
   were zero in all conditions, but graders recorded 12 unverifiable
   additions (plausible material in neither artifact nor ground
   truth) in A continuations and zero in B and C. H3 predicted the
   opposite direction on unsupported inference overall.
5. **Provenance was a tie** (0.880 / 0.872 / 0.880), against H2's
   prediction of a WORLD advantage. Residual provenance losses were
   shared across conditions (vague attribution on the same items:
   C2 E1 to E3, S1 E3, S2 E4, C1 E5 and E6 partial nearly everywhere).

### Hypothesis verdicts

- H1 (A higher on decisions, assumptions, provenance, revision):
  supported for assumptions only; not supported for the other three.
- H2 (largest A advantage on revision and provenance): not supported.
  Both metrics tied; revision had zero variance at ceiling.
- H3 (A fewer contradictions and unsupported inferences): not
  supported. Contradictions were zero everywhere; unverifiable
  additions were highest under A.
- H4 (constraints at ceiling in all conditions): supported. Metric 2
  was 1.000 everywhere and there were zero hard failures in 72
  continuations, including on C1's missing-datum trap, which no
  continuation invented a value for.
- H5 (C2 parity, B most efficient): supported. C2 was at or near
  ceiling in all conditions, and B was the most efficient condition.
- N1 (summary parity): largely stands. B matched A on 7 of 9 metrics
  and beat it on efficiency by a wide margin.
- N2 (transcript advantage on revisions): did not recur; all
  conditions tied at ceiling on metric 5.
- N3 (structure overhead without benefit): supported on efficiency;
  the overhead bought assumption metadata and nothing else measurable.
- N4 (writing bottleneck): no revision-chain failures occurred, so
  N4 was not exercised for chains. Two assumption items were missed
  by every condition in every trial (F2 A1, S1 A2), and S1 A1 was
  missed by B and C only; losses no representation prevented.

### Information loss (metric 9), itemized misses

Missed-item instances out of 3 trials each. Condition A (6 total):
F2 assumption A1 (3), S1 assumption A2 (3). Condition B (9 total):
F2 A1 (3), S1 A1 (3), S1 A2 (3). Condition C (10 total): F2 A1 (3),
F2 A2 (1), S1 A1 (3), S1 A2 (3). No decision, constraint, provenance,
or revision item was scored a full miss in any condition. Partial
losses are listed per continuation in `analysis/results.json` inputs
(`results/scores/*.json`).

### Code-inspection finding (not a trial result)

The flat AgentState schema in the 001-state-continuation harness has
no fields for assumption confidence, assumption status, revision
chains, or supersession. Per the fixed design, no trials were spent
on it; its inability to carry the content metric 3 and metric 5 grade
is recorded here as a code-inspection finding, consistent with
metric 3's result that exactly those fields are what summaries and
journals lose.

## Reproducibility

1. Read `protocol.md` (preregistration, analysis plan, run log).
2. Prompts: `python3 runner/build_prompts.py` regenerates every
   continuation prompt from `tasks/`, `artifacts/`, and the single
   compose path in `runner/prompts.py` (system prompt SHA-256 in each
   record of `results/raw/records.jsonl`).
3. Parity: `python3 runner/parity_gate.py` re-checks all artifacts
   against ground truth must_mention lists.
4. Blinding: `python3 runner/blind.py` (seed 20261103) and
   `python3 runner/blind_artifacts.py` reproduce the judged copies.
5. Analysis: `python3 analysis/analyze.py` regenerates
   `analysis/results.json` and `analysis/tables.md` from
   `results/scores/` and the private mapping.
6. Trial order: `runner/trial_order.json` (seed 20261102).
The only non-reproducible element is the agent sessions themselves:
in-environment agents, single model family, exact model version not
reported by the platform, no seed or temperature control.

## Limitations

Small n (3 trials per cell, 8 tasks); single model family;
session-only independence (same platform, same underlying model);
blind grading by agents, one grader per task, no inter-rater
reliability and no human grading (raw outputs are preserved so a
human can grade a 25 percent subset later); blinding is imperfect
because artifact format can reveal condition; word and character
counts only, never token counts; ceiling effects on metrics 2, 5,
and 6 leave no room to distinguish conditions; the parity gate
guaranteed must_mention content in every artifact, which likely
compressed differences relative to unfiltered real-world handoffs;
Agent A productions and summaries are single instances per task, so
artifact quality variance is confounded with condition.

## Research assessment

- VERIFIED (by this experiment's own records): the benchmark ran as
  preregistered; 72 of 72 continuations completed and were graded;
  counts, sizes, and scores above are computed from preserved raw
  outputs by `analysis/analyze.py`.
- PRELIMINARY (single model family, n = 3 per cell): a WORLD state
  bundle preserved assumption confidence and fact-vs-assumption
  status better than a summary or a journal (paired +0.22 and +0.23
  on metric 3), at 2.7x to 3.3x the words and with no measured
  advantage on decisions, constraints, provenance, revision history,
  contradiction avoidance, or judged quality.
- DOCUMENTED only: the claim that structured state helps revision
  history. #002 suggested a weakness, #003 found ceiling performance
  in all conditions; the honest summary is that revision behavior is
  protocol-sensitive and unresolved.
- NEEDS VALIDATION: any claim that WORLD improves agent reliability
  in general. This experiment supports, at most, a narrow claim
  about assumption metadata preservation under a parity-gated
  handoff, pending cross-model runs, human grading of a subset, and
  harder revision tasks that break the ceiling.

## Recommended next steps

1. Human-grade a 25 percent subset (18 continuations) to check the
  agent graders, especially at the metric 5 ceiling.
2. Harder revision tasks: more chains per task, chains whose elements
   are split across sources, and no parity gate on revision elements,
   so metric 5 can discriminate.
3. A Prompt 3 is justified only if it targets those two gaps
   (discriminating revision difficulty and cross-model or human
   validation). Another same-shape run would mostly re-measure the
   metric 3 effect and the efficiency cost, both of which are now
   characterized at this scale.
