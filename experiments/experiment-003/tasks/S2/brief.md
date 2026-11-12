# Task S2: Checkout incident debugging

You are a software engineer agent investigating intermittent errors in a
checkout service. Work through the scenario materials in `scenario.md` in
order: Part 1 first, then the Part 2 update, which contains the results of
the log analysis and changes the leading hypothesis.

Produce three work products in `artifacts/S2/`:

1. `journal.md`: a chronological work journal: hypotheses, what you
   checked, what the evidence showed, what was fixed, what remains open.
2. `report.md`: the incident status report as it stands at the end of the
   session: what caused the main problem, what was fixed and merged, what
   was ruled out and why, what remains unexplained.
3. `state.md`: a WORLD state bundle following `docs/state-model.md`:
   Project context (goal, constraints), Decisions (id, statement,
   rationale, status, supersedes links), Assumptions (id, statement,
   confidence, status), Evidence (id, kind, reference, summary,
   provenance), open Questions, a StateChange log recording each revision
   in order with its reason, and a Handoff section.

Rules: use only the scenario materials. A hypothesis is not a finding:
label hypotheses as assumptions until evidence settles them. Record the
provenance of every finding. When a hypothesis is replaced, keep the old
one visible as superseded with the reason.
