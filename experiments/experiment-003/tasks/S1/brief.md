# Task S1: API rate limiting implementation (gateway service)

You are a software engineer agent implementing rate limiting for an API
gateway service. Work through the scenario materials in `scenario.md` in
order: Part 1 first, then the Part 2 update, which arrives partway through
the session and changes a design decision.

Produce three work products in `artifacts/S1/`:

1. `journal.md`: a chronological work journal: what you examined, what you
   built, what you decided, test results, and how the update changed the
   design.
2. `report.md`: the engineering status report as it stands at the end of
   the session: current design, what is merged, what is failing, what
   remains.
3. `state.md`: a WORLD state bundle following `docs/state-model.md`:
   Project context (goal, constraints), Decisions (id, statement,
   rationale, status, supersedes links), Assumptions (id, statement,
   confidence, status), Evidence (id, kind, reference, summary,
   provenance), open Questions, a StateChange log recording each revision
   in order with its reason, and a Handoff section.

Rules: use only the scenario materials. Record the provenance of test
results and measurements (which run, which test). When the update changes
a decision, keep the superseded decision visible; do not silently
overwrite it. Distinguish what is merged from what is only planned.
