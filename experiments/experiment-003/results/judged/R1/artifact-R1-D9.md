# WORLD State Bundle: Team Notes v2 Specification (Task R1)

Format: Following docs/state-model.md (Draft v0.1). Current state is a projection over the StateChange log in this bundle. Nothing superseded has been deleted; superseded items remain visible with their reason and source.

## Project

- id: team-notes-v2-spec-r1
- name: Team Notes v2
- goal: Specify version 2 of Team Notes, a shared note-taking app, for a December 15 launch, tracking every requirement version so a successor can tell what each requirement used to be, what it is now, and why it changed.
- scope (current): Mobile-only launch on December 15, with sign-in via SSO only. Desktop is deferred to a later release. Offline support is deferred to release v2.1.
- status: active
- definition_of_done: Current requirements are stated in report.md, the full revision history is preserved in this bundle, and open questions are listed for the successor.
- provenance: created_by Agent A, Experiment 003, Task R1; source materials are Evidence E1, E2, and E3 below. No source outside the scenario materials was used.

### Constraints

- C1: The December 15 launch date does not move. Source: E1, original spec draft, where the date is described as fixed by marketing commitments.
- C2: No scope may be added to v2 without the product manager's approval. Source: E1, original spec draft.
- Provenance for constraints: created_by Agent A, from E1; neither constraint was changed by E2 or E3.

## Requirements as State

Only the latest version of each requirement is authoritative. Earlier versions are listed as superseded.

- REQ-A, Platforms:
  - Version 1 (superseded): Launch on desktop and mobile. Source: E1.
  - Version 2 (current, authoritative): Launch mobile-only. Desktop moves to a later release. Source: E2. Reason: engineering capacity; the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- REQ-B, Offline support:
  - Version 1 (superseded): Full offline editing is required at launch. Source: E1.
  - Version 2 (current, authoritative): Offline support moves out of the launch scope to release v2.1. Source: E3. Reason: prototype evidence of unresolvable sync conflicts on the v1 sync engine, and a proper fix needs a sync rewrite that cannot land by launch.
- REQ-C, Authentication:
  - Version 1 (current, authoritative, unchanged): Sign-in via SSO only; no passwords. Source: E1. Neither E2 nor E3 changed it.
- Launch date:
  - Version 1 (current, authoritative, unchanged): December 15, fixed by marketing commitments. Source: E1. Neither E2 nor E3 changed it.

## Decisions

### D1: Adopt the original spec draft as the v2 baseline

- statement: Team Notes v2 launches on desktop and mobile on December 15, with full offline editing required at launch and sign-in via SSO only with no passwords.
- rationale: This was the requirement set as originally drafted in Part 1 of the scenario materials.
- status: superseded (in part: the platform element is superseded by D2 and the offline element is superseded by D3; the authentication element and the launch date remain accepted through D2 and D3)
- supersedes: none
- evidence_ids: E1
- provenance: created_by Agent A, from E1 (original spec draft).

### D2: Launch mobile-only; move desktop to a later release

- statement: The v2 launch is mobile-only. Desktop moves to a later release.
- rationale: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, and the December 15 date does not move (Constraint C1).
- status: accepted
- supersedes: D1 (platform element only; REQ-A version 1)
- evidence_ids: E2
- provenance: created_by Agent A, from E2 (scope message from the product manager, in writing). The decision maker named in the source is the PM, who is also the scope approver under Constraint C2.

### D3: Move offline support out of launch scope to release v2.1

- statement: Offline support is not part of the v2 launch. It moves to release v2.1.
- rationale: Prototype evidence (E3) shows offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. A proper fix needs a sync rewrite that cannot land by launch, and the December 15 date does not move (Constraint C1). The assumption that made offline editing feasible at launch (A1) was invalidated by the same evidence.
- status: accepted
- supersedes: D1 (offline element only; REQ-B version 1)
- evidence_ids: E3
- provenance: created_by Agent A, from E3 (engineering review note from the engineering lead). The source states the recommendation was agreed with the PM, satisfying Constraint C2.

### D4: Keep authentication and launch date unchanged

- statement: REQ-C remains sign-in via SSO only with no passwords, and the launch date remains December 15.
- rationale: Neither official update changed authentication or the launch date. Both updates narrowed scope to protect the fixed date rather than moving it.
- status: accepted
- supersedes: none (it confirms the corresponding elements of D1)
- evidence_ids: E1, E2, E3
- provenance: created_by Agent A, by inspection of E1, E2, and E3 in order.

## Assumptions

### A1: v1 sync engine can be reused for offline support

- statement: The sync engine from v1 can be reused for offline support without major changes.
- confidence: medium (as recorded in the original draft)
- status: invalidated
- validated_by_evidence_id: none. Invalidated by E3.
- provenance: created_by Agent A, from E1 (assumption recorded in the original spec draft). Status changed to invalidated on the basis of E3, which states: "The v1 sync engine assumption did not hold for offline editing."
- note for successor: Do not plan offline support on the v1 sync engine. E3 states that a proper fix needs a sync rewrite.

## Evidence

### E1: Original spec draft

- kind: document
- reference: scenario.md, Part 1 (original spec draft, v1 of the spec)
- summary: Team Notes v2 requirements as originally drafted: REQ-A desktop and mobile, REQ-B full offline editing required at launch, REQ-C SSO only with no passwords, launch date December 15 fixed by marketing commitments. Standing constraints: the December 15 date does not move, and no scope may be added to v2 without the PM's approval. Also records Assumption A1 at medium confidence.
- provenance: captured_by Agent A, from the scenario materials provided for Task R1.

### E2: Product manager scope message

- kind: document
- reference: scenario.md, Part 2, Update 1 (source: PM, in writing)
- summary: Scope change for the v2 launch: launch mobile-only, desktop moves to a later release. Reason given: engineering capacity; the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- provenance: captured_by Agent A, from the scenario materials provided for Task R1. Author as stated in the source: the product manager.

### E3: Engineering review note, including prototype finding

- kind: document (with observation: prototype result)
- reference: scenario.md, Part 2, Update 2 (source: engineering lead)
- summary: Prototype finding: offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. Fixing this properly needs a sync rewrite that cannot land by launch. Recommendation, agreed with the PM: offline support moves out of the launch scope to release v2.1. The note states the v1 sync engine assumption did not hold for offline editing.
- provenance: captured_by Agent A, from the scenario materials provided for Task R1. Author as stated in the source: the engineering lead.

## Questions (open)

### Q1: Desktop release timing

- question: Which release, and on what date, will desktop ship in, following its move to a later release under D2?
- status: open
- provenance: created_by Agent A. E2 says desktop moves to a later release and gives no release name or date.

### Q2: Release v2.1 timing

- question: What is the planned date for release v2.1, which now carries offline support under D3?
- status: open
- provenance: created_by Agent A. E3 names release v2.1 and gives no date.

### Q3: Offline behavior at launch

- question: Is any limited offline behavior expected in the v2 launch, or is there no offline support at all until v2.1?
- status: open
- provenance: created_by Agent A. E3 defers offline support as a whole to v2.1 and does not specify a partial form for launch. Any addition here would also need PM approval under Constraint C2.

## StateChange Log

Append-only log, in order. Current state above is the projection of this log.

- seq 1, entity_type: Project, entity_id: team-notes-v2-spec-r1, change: created, before: none, after: Project created with goal, December 15 launch, and Constraints C1 and C2, actor: Agent A, reason: Start of the R1 work session, on the basis of E1.
- seq 2, entity_type: Requirement, entity_id: REQ-A, change: created, before: none, after: Version 1, launch on desktop and mobile, actor: Agent A, reason: Original spec draft, source E1.
- seq 3, entity_type: Requirement, entity_id: REQ-B, change: created, before: none, after: Version 1, full offline editing is required at launch, actor: Agent A, reason: Original spec draft, source E1.
- seq 4, entity_type: Requirement, entity_id: REQ-C, change: created, before: none, after: Version 1, sign-in via SSO only, no passwords, actor: Agent A, reason: Original spec draft, source E1.
- seq 5, entity_type: Assumption, entity_id: A1, change: created, before: none, after: Active, statement that the v1 sync engine can be reused for offline support without major changes, confidence medium, actor: Agent A, reason: Assumption recorded in the original spec draft, source E1.
- seq 6, entity_type: Decision, entity_id: D1, change: created, before: none, after: Baseline decision adopting the original draft requirement set, actor: Agent A, reason: Original spec draft, source E1.
- seq 7, entity_type: Requirement, entity_id: REQ-A, change: superseded, before: Version 1, launch on desktop and mobile, after: Version 2, launch mobile-only, desktop moves to a later release, actor: Agent A, reason: Engineering capacity; the desktop redesign cannot be finished by December 15 without cutting quality, source E2 (PM scope message, in writing).
- seq 8, entity_type: Decision, entity_id: D2, change: created, before: none, after: Accepted, launch mobile-only and move desktop to a later release, supersedes the platform element of D1, actor: Agent A, reason: Same as seq 7, source E2.
- seq 9, entity_type: Evidence, entity_id: E3, change: created, before: none, after: Prototype finding recorded, unresolvable sync conflicts in about 1 in 20 offline editing sessions on the v1 sync engine, actor: Agent A, reason: Engineering review note, source E3.
- seq 10, entity_type: Assumption, entity_id: A1, change: status_changed, before: Active, confidence medium, after: Invalidated, actor: Agent A, reason: E3 states the v1 sync engine assumption did not hold for offline editing, source E3.
- seq 11, entity_type: Requirement, entity_id: REQ-B, change: superseded, before: Version 1, full offline editing is required at launch, after: Version 2, offline support moves out of launch scope to release v2.1, actor: Agent A, reason: Unresolvable sync conflicts in the prototype and a sync rewrite that cannot land by launch; recommendation agreed with the PM, source E3.
- seq 12, entity_type: Decision, entity_id: D3, change: created, before: none, after: Accepted, offline support moves to release v2.1, supersedes the offline element of D1, actor: Agent A, reason: Same as seq 11, source E3.
- seq 13, entity_type: Decision, entity_id: D4, change: created, before: none, after: Accepted, REQ-C and the December 15 launch date confirmed unchanged, actor: Agent A, reason: Neither E2 nor E3 changed authentication or the launch date.
- seq 14, entity_type: Question, entity_id: Q1, change: created, before: none, after: Open, desktop release timing unknown, actor: Agent A, reason: E2 gives no later release name or date.
- seq 15, entity_type: Question, entity_id: Q2, change: created, before: none, after: Open, release v2.1 date unknown, actor: Agent A, reason: E3 gives no date for v2.1.
- seq 16, entity_type: Question, entity_id: Q3, change: created, before: none, after: Open, whether any limited offline behavior is expected at launch is unspecified, actor: Agent A, reason: E3 defers offline support as a whole and specifies no partial launch form.

## Artifacts

- ART1: journal.md, kind: work journal, location: experiments/experiment-003/artifacts/R1/journal.md, version: 1, provenance: produced_by Agent A in the R1 session.
- ART2: report.md, kind: specification summary, location: experiments/experiment-003/artifacts/R1/report.md, version: 1, provenance: produced_by Agent A in the R1 session.
- ART3: state.md (this file), kind: WORLD state bundle, location: experiments/experiment-003/artifacts/R1/state.md, version: 1, provenance: produced_by Agent A in the R1 session.

## Handoff

For the next participant continuing Team Notes v2:

- Context snapshot: Team Notes v2 launches mobile-only on December 15, with SSO-only sign-in and no passwords. Desktop is deferred to a later release. Offline support is deferred to release v2.1. The December 15 date does not move, and no scope may be added to v2 without PM approval.
- Accepted decisions: D2 (mobile-only launch), D3 (offline support to v2.1), D4 (authentication and launch date unchanged). D1 is the superseded baseline; do not build to its platform or offline elements.
- Current requirements: REQ-A version 2, REQ-B version 2, REQ-C version 1. Full text is in report.md.
- Assumptions: A1 is invalidated. There are no active assumptions in this bundle. Do not rely on reuse of the v1 sync engine for offline support; E3 says a proper fix needs a sync rewrite.
- Key evidence: E1 (original draft), E2 (PM scope message: mobile-only, for engineering capacity), E3 (engineering review note: about 1 in 20 offline sessions hit unresolvable conflicts on the v1 engine).
- Open questions to start with: Q1 desktop release timing, Q2 release v2.1 date, Q3 whether any limited offline behavior is expected at launch.
- Recent state changes: The last substantive changes are seq 7 and 8 (REQ-A superseded to mobile-only) and seq 9 to 12 (A1 invalidated, REQ-B superseded to v2.1). The full ordered log is above.
- Warning: Both superseded version 1 requirements look plausible in isolation. The revision history, not memory of the original draft, is authoritative: desktop at launch and offline editing at launch are both out of the v2 launch scope.
