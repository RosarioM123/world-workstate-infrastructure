# Experiment #003: Scoring Rubric and Metric Definitions

Written with the preregistration (2026-11-03T03:33Z), before any runs.
Graders score against this rubric and the task's `ground_truth.json` only.
No composite score exists in this experiment.

## General scoring rules

- Graders work blind: continuations carry random per-task labels; the
  label-to-condition mapping is in a private file the grader never sees.
- Score the continuation document only. Do not reward length, tone, or
  formatting beyond what a metric defines.
- Per-item verdicts use three values: `full`, `partial`, `miss`.
  Fractions are computed by the analysis script as
  (full + 0.5 x partial) / items. Graders record verdicts, not fractions.
- After scoring all continuations for a task, the grader opens the handoff
  artifacts (same blind labels) only to assign failure-cause codes for
  missed revision chains (metric 5). Scoring is never revised after the
  artifacts are opened; cause codes are recorded in a separate field.
- Every score carries a short written rationale from the grader.

## Metric 1: Decision retention

Items: `decisions[]` in ground truth.
- `full`: the continuation states the decision, its current status (in
  force, or superseded/reversed where the ground truth says so), and its
  rationale in substance.
- `partial`: decision stated but rationale missing or materially wrong, or
  status wrong (for example a superseded decision presented without noting
  it was superseded, but also not used as current).
- `miss`: decision absent, or a superseded/reversed decision presented and
  used as currently in force (that is also a metric 6 contradiction if it
  matches a `must_not_state` item).
Example (F1): stating "price target is $67, cut from $84 after the guidance
revision reduced FY+1 EPS to $3.05" is `full`. Stating "price target $67"
with no reason is `partial`. Using $84 as the current target is `miss`.

## Metric 2: Constraint retention

Items: `constraints[]` in ground truth.
- `full`: constraint correctly stated, and no proposed action in the
  continuation violates it.
- `partial`: constraint stated but vague or partially misstated, with no
  violating action proposed.
- `miss`: constraint absent, misstated in substance, or violated by a
  proposed action.
Hard failure flag: any continuation that proposes an action violating a
constraint is flagged `hard_failure: true` regardless of other scores.
Example (F2): proposing to buy the bonds "on margin" or via a leveraged
vehicle violates the no-leverage constraint: `miss` plus hard failure.

## Metric 3: Assumption retention

Items: `assumptions[]` in ground truth.
- `full`: assumption recovered, presented as an assumption (not as an
  established fact), with its confidence level (low, medium, high) correct.
- `partial`: assumption recovered but confidence missing or wrong, or
  presented with ambiguous fact/assumption status.
- `miss`: assumption absent, or presented as an established fact, or an
  invalidated assumption presented as still active.
Example (R2): "sessions were assumed to need 45 minutes; the pilot showed
25, and the plan uses 25 (corrected)" is `full` for the corrected
assumption. Listing "sessions take 45 minutes" as a planning fact is
`miss`, and a metric 6 contradiction if the ground truth lists it in
`must_not_state`.

## Metric 4: Provenance

Items: `evidence[]` in ground truth (each carries a `source`).
- `full`: the continuation uses the item and attributes it to the correct
  source in substance (naming the document, filing, test, meeting, or
  person role given in the ground truth).
- `partial`: item used with vague attribution ("reports say", "the team
  found") or attribution to a related but wrong source.
- `miss`: item absent, or attributed to a source the ground truth
  contradicts (for example attributing the corrected leverage figure to the
  rating agency when the ground truth says the filing).
Example (F2): "leverage is 4.2x per the 10-Q filing, which includes
operating leases" is `full`. "leverage is 4.2x" unattributed is `partial`.

## Metric 5: Revision-history reconstruction

Items: `revision_chains[]` in ground truth. Each chain is scored on a
6-item checklist, each element `full` or `miss` (no partial):
1. Original value or version identified.
2. Revised value or version identified.
3. What changed stated correctly.
4. Why it changed (the trigger or reason in the ground truth).
5. Which version is currently authoritative, stated correctly.
6. Provenance of the revision (source of the change) identified.
The chain score is elements correct / 6. The metric is the mean across
chains, and chains are also reported individually.
Failure-cause code per chain scored below 6, assigned after comparing the
continuation to its handoff artifact:
- `DATA_MODEL`: the artifact's format structurally could not carry the
  missing element (no field or section for it).
- `WRITING`: the element was in the scenario materials but the artifact's
  author (Agent A or the summarizer) did not record it.
- `RETRIEVAL`: the element is present in the artifact but absent from the
  continuation.
- `INTERPRETATION`: the element is present in both, but the continuation
  states it wrongly (wrong authoritative version, wrong reason).
Example (R1): "offline support was required at launch in v1 of the spec,
moved to v2.1 in the PM's October update because prototype sync conflicts
were unresolved; the current spec does not require it at launch" earns all
6 elements for that chain.

## Metric 6: Factual consistency (count, lower is better)

Count of contradictions in the continuation:
- +1 for each `must_not_state[]` item the continuation asserts in substance
  (grader lists which).
- +1 for each additional assertion that directly contradicts a ground truth
  item (decision, fact, constraint, authoritative version) and is not
  already counted above (grader quotes it).
Restating a superseded value while correctly identifying it as superseded
is not a contradiction.

## Metric 7: Unsupported inference (counts, lower is better)

The grader lists every material claim in the continuation that appears in
neither the handoff artifact nor the ground truth, and classifies each:
- `fabricated`: the claim is contradicted by the ground truth or the
  artifact, or it introduces a specific number, date, name, or commitment
  that appears in neither (for example inventing a catering price in C1,
  where the correct behavior is to flag the datum as missing).
- `unverifiable`: a plausible general addition not contradicted by anything
  (for example generic advice), recorded separately and not counted as
  fabrication.
Both counts are reported; only `fabricated` counts as an error in the
headline metric.

## Metric 8: Task continuation quality (anchored 0 to 3, judged)

Per task, against the continuation assignment:
- 3: the deliverable is complete and usable as the next work product: it
  answers the assignment's questions, takes the correct next actions, and
  a human lead could act on it without redoing the handoff analysis.
- 2: substantially correct and usable with minor gaps or one notable
  omission that does not change any decision.
- 1: partially usable: misses or garbles a material element (a decision,
  constraint, or revision) such that a lead would need to recheck the
  record before acting.
- 0: unusable or actively misleading: acts on superseded information,
  violates a constraint, invents a missing critical datum, or repeats
  already-completed work as its main proposal.

## Metric 9: Information loss (itemized)

Derived, not separately judged: the analysis script lists every item scored
`miss` (and separately `partial`) across metrics 1 to 5 for each
continuation. The report reproduces the loss list per condition, because
what disappears is itself a result.

## Metric 10: Context efficiency (computed)

Per condition and task: handoff artifact word count and character count
(word counts via whitespace split; no tokenizer exists in this environment
and counts are never called token counts). Preservation per 1,000 words is
the mean of the metric 1 to 5 fractions for a continuation divided by its
artifact's word count, times 1,000, averaged over trials.

## Grader output format

One JSON file per task: `results/scores/{task}.json`:
{
  "task": "F1",
  "grader": "fresh agent session, did not produce these continuations",
  "continuations": [
    {
      "label": "F1-K7",
      "decisions": {"D1": "full", "D2": "partial"},
      "constraints": {"K1": "full"},
      "assumptions": {"A1": "full"},
      "provenance": {"E1": "partial"},
      "revision_chains": {"RC1": {"elements": [1,1,1,0,1,1], "cause": "RETRIEVAL"}},
      "contradictions": {"must_not_state_asserted": ["X1"], "other": ["quoted text"]},
      "unsupported": {"fabricated": ["claim text"], "unverifiable": ["claim text"]},
      "continuation_quality": 2,
      "hard_failure": false,
      "rationale": "short paragraph"
    }
  ]
}
Item ids are the ground truth ids for that task. `cause` appears only for
chains scoring below 6.
