# WORLD State Bundle: Task R1

## Objective

Specify version 2 of Team Notes, a shared note-taking app, for a December 15 launch, tracking every requirement version so a successor can tell what each requirement used to be, what it is now, and why it changed.

## Decisions

### D1 [status: superseded]
- statement: Team Notes v2 launches on desktop and mobile on December 15, with full offline editing required a...
- rationale: 
- supersedes: none
- evidence_ids: none

### D2 [status: accepted]
- statement: The v2 launch is mobile-only. Desktop moves to a later release.
- rationale: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, and the December 15 date does not move (Constraint C1).
- supersedes: D1
- evidence_ids: E2

### D3 [status: accepted]
- statement: Offline support is not part of the v2 launch. It moves to release v2.1.
- rationale: Prototype evidence (E3) shows offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. A proper fix needs a sync rewrite that cannot land by launch, and the December 15 date does not move (Constraint C1). The assumption that made offline editing feasible at launch (A1) was invalidated by the same evidence. This decision supersedes the offline element of D1; the original bundle records D1 as superseded in part by D2 and by this decision, and the schema records one successor link per superseded decision (held by D2), so this link is preserved in text.
- supersedes: none
- evidence_ids: E3

### D4 [status: accepted]
- statement: REQ-C remains sign-in via SSO only with no passwords, and the launch date remains December 15.
- rationale: Neither official update changed authentication or the launch date. Both updates narrowed scope to protect the fixed date rather than moving it.
- supersedes: none
- evidence_ids: E1, E2, E3

### REQ-A1 [status: superseded]
- statement: REQ-A version 1: Launch on desktop and mobile.
- rationale: 
- supersedes: none
- evidence_ids: none

### REQ-A2 [status: accepted]
- statement: REQ-A version 2 (current, authoritative): Launch mobile-only. Desktop moves to a later release.
- rationale: Engineering capacity; the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- supersedes: REQ-A1
- evidence_ids: E2

### REQ-B1 [status: superseded]
- statement: REQ-B version 1: Full offline editing is required at launch.
- rationale: 
- supersedes: none
- evidence_ids: none

### REQ-B2 [status: accepted]
- statement: REQ-B version 2 (current, authoritative): Offline support moves out of the launch scope to release v2.1.
- rationale: Prototype evidence of unresolvable sync conflicts on the v1 sync engine, and a proper fix needs a sync rewrite that cannot land by launch.
- supersedes: REQ-B1
- evidence_ids: E3

### REQ-C1 [status: accepted]
- statement: REQ-C version 1 (current, authoritative, unchanged): Sign-in via SSO only; no passwords.
- rationale: Original spec draft (E1). Neither E2 nor E3 changed it.
- supersedes: none
- evidence_ids: E1

### REQ-DATE1 [status: accepted]
- statement: Launch date (current, authoritative, unchanged): December 15, fixed by marketing commitments.
- rationale: Original spec draft (E1). Neither E2 nor E3 changed it.
- supersedes: none
- evidence_ids: E1

## Assumptions

### A1 [status: invalidated, confidence: medium]
- statement: The v1 sync engine can be reused for offline support without major changes.
- validated_by: none

## Evidence

### E1 (kind: document)
- claim: Team Notes v2 requirements as originally drafted: REQ-A desktop and mobile, REQ-B full offline editing required at launch, REQ-C SSO only with no passwords, launch date December 15 fixed by marketing commitments. Standing constraints: the December 15 date does not move, and no scope may be added to v2 without the PM's approval. Also records Assumption A1 at medium confidence.
- source: scenario.md, Part 1 (original spec draft, v1 of the spec)

### E2 (kind: document)
- claim: Scope change for the v2 launch: launch mobile-only, desktop moves to a later release. Reason given: engineering capacity; the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- source: scenario.md, Part 2, Update 1 (source: PM, in writing)

### E3 (kind: document)
- claim: Prototype finding: offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. Fixing this properly needs a sync rewrite that cannot land by launch. Recommendation, agreed with the PM: offline support moves out of the launch scope to release v2.1. The note states the v1 sync engine assumption did not hold for offline editing.
- source: scenario.md, Part 2, Update 2 (source: engineering lead)

## Constraints

- C1: The December 15 launch date does not move. Source: E1, original spec draft, where the date is described as fixed by marketing commitments.
- C2: No scope may be added to v2 without the product manager's approval. Source: E1, original spec draft.

## Open questions

- Which release, and on what date, will desktop ship in, following its move to a later release under D2?
- What is the planned date for release v2.1, which now carries offline support under D3?
- Is any limited offline behavior expected in the v2 launch, or is there no offline support at all until v2.1?

## Next actions

(none recorded)
