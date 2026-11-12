# Hypothesis

This file states the research hypothesis WORLD exists to test, what would
falsify it, and what the evidence so far supports. The fuller internal
version lives in `docs/hypothesis.md`; this is the research-facing
statement, kept in sync with the experiment record.

## The problem

AI agents increasingly do work that spans sessions: a research task
started by one agent (or one model, in one tool) is continued later by
another. What crosses that boundary today is usually a natural-language
summary, a raw transcript, or nothing. Summaries are lossy in ways the
writer cannot audit: decisions survive as prose, if at all, and their
rationales, confidence levels, supersession history, and binding
constraints are the first things compressed away. Transcripts preserve
everything but index nothing: the governance content is buried in
chronological narrative, and a successor must re-derive the project's
decisions, assumptions, and open questions from raw text. Neither format
can be mechanically checked: nothing verifies that a constraint still
holds, that a decision was superseded, or that the record itself was not
edited after the fact.

## Central hypothesis

> For work that moves between participants (agents, models, humans,
> tools) across sessions, maintaining an explicit, persistent,
> structured work-state, with stable labels for decisions, assumptions,
> evidence, constraints, and revision history, and with every proposed
> change judged against declared invariants and recorded in a
> tamper-evident log, preserves more decision-relevant information
> across handoffs, and makes that information more auditable, than
> relying on conversation summaries or raw transcripts.

This is a hypothesis, not a result. The demonstrated portion is narrow
(see below), and parts of it have already failed testing.

## Sub-claims

1. **Retention.** A successor given structured work-state preserves more
   decisions (with rationale), assumptions (with confidence), and
   provenance than a successor given a summary or a transcript of the
   same work.
2. **Constraint enforcement.** Invariants checked at write time prevent
   invalid state transitions (for example, a budget going negative, or
   a locked field changing) from ever entering the committed record,
   while still recording the rejected attempt as evidence.
3. **Auditability.** A hash-chained verdict log (COMMITTED and REJECTED
   rows alike) lets any later participant verify that the record was
   not altered after the fact, and replay it deterministically to the
   same state.
4. **Concurrency safety.** Optimistic concurrency (`expected_version`)
   eliminates silent lost updates between concurrent writers, at the
   cost of explicit conflicts that must be retried.

## What would falsify it

From `docs/hypothesis.md`, unchanged:

1. **Summary parity.** A plain-language summary retains as much
   decision-relevant information as structured state. Then WORLD is
   overhead, not infrastructure. Status: **open.** In the Experiment
   #002 replication, an independently written summary came within 0.36
   of the WORLD condition on the reference mean.
2. **Tool sufficiency.** Git plus a documents folder plus a tool
   protocol achieves the same handoff fidelity with less complexity.
   Status: **untested.**
3. **Ontology collapse.** The work-state schema cannot be defined
   generically enough to transfer across projects. Status: **untested**
   beyond two investment-research tasks and one earlier task in the
   same genre.
4. **Verification irrelevance.** Nobody audits provenance in practice.
   Status: **untested.** No human has yet traced a decision from WORLD
   state to its evidence as an audit exercise.

## What the evidence supports so far

- Sub-claim 1 is **partially supported, narrowly**: in Experiments #001
  and #002 (two domains, n=1 per run, same model family, blind grading
  against predeclared answer keys), the structured-state continuation
  preserved decision governance best, with the advantage concentrated
  in assumptions with confidence levels, provenance labels, and
  superseded decisions. The mechanism appears to be label stability:
  the transcript continuation renumbered inherited items under its own
  labels, and that relabeling is where governance items were lost.
- One part of sub-claim 1 **failed in #002, and is now unresolved**:
  revision history. The WORLD continuation scored 2 out of 5 on
  revision-history preservation in both #002 runs, losing the
  old-to-new-to-trigger revision chains the state was built to
  preserve. Experiment #003 (below) scored revision history at
  ceiling in all conditions, which neither confirms nor refutes the
  #002 failure. The discriminating experiment has not been run.
- Sub-claims 2 and 4 are supported at the mechanism level, not the
  agent level: the commit protocol is model-checked exhaustively over
  bounded configurations (1,220,255 explored states, properties P1 to
  P6, `docs/spec/protocol-verification.md`), and a preregistered
  scripted-agent experiment found lost updates in 33 of 50 unprotected
  trials versus 0 of 50 with `expected_version` plus retry
  (`experiments/lost-update/RESULTS.md`). The agents in that experiment
  were scripted, not LLM-driven.
- Sub-claim 3 is supported as an implementation property: `verify()`
  detects in-place tampering (500 of 500 seeded random mutations in
  fuzz testing, plus 450 more under alternate seeds), crash-consistency
  fault injection recovered cleanly in 15 of 15 mid-transaction kills,
  and an independent C# verifier with no shared code accepts valid
  chains and rejects tampered ones. Tamper-evident is not tamper-proof:
  see `research/LIMITATIONS.md`.

**Experiment #003 verdicts (added 2026-11-05, Prompt 6).** #003
(2026-11-03, preregistered, 8 tasks across financial, software
engineering, revision, and control categories, 3 conditions, 72
continuations, blind grading; PRELIMINARY, single model family;
condition A was hand-authored Markdown that never exercised the
`World` class) returned split verdicts per the #003 report's own
hypothesis mapping: H1 (preservation) supported for assumptions
only (M3 0.721 vs 0.500 vs 0.488; decisions slightly favored the
baselines, M1 0.948 vs 0.979); H2 and H3 not supported; H4 and H5
supported. Unverifiable additions appeared only under the
structured condition (12 vs 0 and 0), and structured bundles cost
2.7x to 3.3x the words. The Prompt 3 revalidation (2026-11-04),
the first run through the shipped code path on R1, R2, C1, found
preservation at or near the #003 structured level with no
revision regression from the projection view (PRELIMINARY). Full
record: `experiments/experiment-003/REPORT.md`,
`experiments/prompt3/revalidation/RESULTS.md`.

## What remains unproven

- Cross-model handoffs (every experiment so far used one model family).
- Human auditability in practice.
- Any use by real multi-agent systems, real users, or production
  workloads. There are zero customer or external-user conversations
  behind the current design.
- Statistical generality: #001 and #002 are n=1 per run by design
  (predeclared protocol, blind grading), and their means are
  reported as reference values, not effect sizes. #003 has n=24 per
  condition for most metrics but ran on one model family with no
  significance testing.
- Whether the revision-history result is a schema problem (the state
  does not carry revision chains explicitly enough) or a reading
  problem (continuations do not use them): #002 failed it, #003 tied
  at ceiling, and the question remains open. Prompt 3 shipped an
  explicit revision schema (F1) and the revalidation exercised it
  without regression, but no discriminating experiment has run.
