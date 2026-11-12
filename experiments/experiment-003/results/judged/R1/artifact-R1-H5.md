# Work Journal: Team Notes v2 Specification (Task R1)

Agent: Agent A, Experiment 003, Task R1
Session scope: Draft the specification for Team Notes v2 from the scenario materials in order, track every requirement version, and preserve the reason and source for each change.

## Entry 1: Original spec draft (Part 1)

Source: Part 1 of scenario.md, the original spec draft (v1 of the spec).

I drafted the initial specification with four items:

- REQ-A, Platforms, version 1: Launch on desktop and mobile.
- REQ-B, Offline support, version 1: Full offline editing is required at launch.
- REQ-C, Authentication, version 1: Sign-in via SSO only; no passwords.
- Launch date: December 15, fixed by marketing commitments.

I recorded the two standing constraints given in the draft:

- Constraint 1: The December 15 launch date does not move.
- Constraint 2: No scope may be added to v2 without the product manager's approval.

I recorded one assumption exactly as stated in the draft:

- Assumption A1: The sync engine from v1 can be reused for offline support without major changes. Confidence: medium. Status at draft time: active.

Reasoning at this stage: The draft presented all three requirements as launch scope. REQ-B appeared feasible only because Assumption A1 said the v1 sync engine could be reused without major changes. That dependency mattered: if A1 failed, REQ-B would be at risk under the fixed December 15 date, because there would be no room for a sync rewrite without either moving the date, which Constraint 1 forbids, or adding unapproved scope, which Constraint 2 forbids.

## Entry 2: Update 1, product manager scope message

Source: Part 2, Update 1, from the product manager (PM), in writing.

What the update changed:

- REQ-A changed from version 1 to version 2.
- From: Launch on desktop and mobile.
- To: Launch mobile-only. Desktop moves to a later release.
- REQ-B, REQ-C, and the December 15 launch date were not changed by this update.

Reason given in the update: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality.

My reasoning: The fixed launch date (Constraint 1) was kept intact by narrowing launch scope rather than by moving the date. I treated the PM message as authoritative for scope because the PM is the approver named in Constraint 2. I marked REQ-A version 1 as superseded, not deleted, so a successor can see both the original dual platform plan and the current mobile-only plan. I recorded the desktop work as moved to a later release, not cancelled, because the update says it moves to a later release and gives no date for that release.

## Entry 3: Update 2, engineering review note

Source: Part 2, Update 2, from the engineering lead.

New evidence recorded from the update:

- Prototype finding: Offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions.
- Fixing this properly needs a sync rewrite that cannot land by launch.

What the update changed:

- REQ-B changed from version 1 to version 2.
- From: Full offline editing is required at launch.
- To: Offline support moves out of the launch scope to release v2.1.
- Assumption A1 changed status from active to invalidated. The update states directly: "The v1 sync engine assumption did not hold for offline editing."
- REQ-A, REQ-C, and the December 15 launch date were not changed by this update.

Decision basis given in the update: The recommendation to move offline support to v2.1 was agreed with the PM.

My reasoning: This was not a preference change. It was an evidence driven change. The prototype result invalidated the assumption that made REQ-B feasible at launch. Because a proper fix requires a sync rewrite that cannot land by December 15, and because the launch date does not move, the only option consistent with the constraints was to defer REQ-B to v2.1. I marked REQ-B version 1 as superseded and A1 as invalidated, keeping both visible. Deleting either would hide why the launch scope narrowed and could lead a successor to re-propose offline editing on the v1 engine.

## Entry 4: End of session consolidation

I consolidated the three work products:

- report.md states only the current, authoritative requirements, plus a change history section that preserves each superseded version with its reason and source.
- state.md records the full state bundle: project context, decisions with supersedes links, the invalidated assumption, evidence with provenance, open questions, an ordered StateChange log, and a handoff section.

Final check against the constraints:

- December 15 launch date: unchanged.
- Scope added to v2: none. Both updates removed or deferred scope; no new requirement was introduced.
- REQ-C authentication: unchanged through both updates, still SSO only with no passwords.

Open items I could not resolve from the scenario materials, carried forward as open questions in the state bundle: the date or release name for the desktop release, the date for release v2.1, and whether any limited offline behavior is expected at launch now that full offline editing is deferred.
