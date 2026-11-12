# Continuation Document: Team Notes v2 Specification (R1)

## 1. Where things stand

The current, authoritative requirements for the Team Notes v2 launch are:

- **Launch date:** December 15, fixed. This is unchanged from the original draft.
- **REQ-A version 2 (current, authoritative):** Launch mobile-only. Desktop moves to a later release.
- **REQ-B version 2 (current, authoritative):** Offline support is not part of the v2 launch. It moves to release v2.1.
- **REQ-C version 1 (current, authoritative, unchanged):** Sign-in via SSO only; no passwords.

No other current requirements are recorded in the handoff material.

## 2. Decisions in force

### Decisions currently in force

- **D2 [accepted]:** The v2 launch is mobile-only. Desktop moves to a later release.
  - Reason: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, and the December 15 date does not move (Constraint C1).
  - Source: E2

- **D3 [accepted]:** Offline support is not part of the v2 launch. It moves to release v2.1.
  - Reason: Prototype evidence (E3) shows offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. A proper fix needs a sync rewrite that cannot land by launch, and the December 15 date does not move (Constraint C1). The assumption that made offline editing feasible at launch (A1) was invalidated by the same evidence.
  - Source: E3
  - Note on supersession: This decision supersedes the offline element of D1. The original bundle records D1 as superseded in part by D2 and by this decision, and the schema records one successor link per superseded decision (held by D2), so this link is preserved in text.

- **D4 [accepted]:** REQ-C remains sign-in via SSO only with no passwords, and the launch date remains December 15.
  - Reason: Neither official update changed authentication or the launch date. Both updates narrowed scope to protect the fixed date rather than moving it.
  - Sources: E1, E2, E3

- **REQ-A2 [accepted]:** REQ-A version 2 (current, authoritative): Launch mobile-only. Desktop moves to a later release.
  - Reason: Engineering capacity; the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
  - Supersedes: REQ-A1
  - Source: E2

- **REQ-B2 [accepted]:** REQ-B version 2 (current, authoritative): Offline support moves out of the launch scope to release v2.1.
  - Reason: Prototype evidence of unresolvable sync conflicts on the v1 sync engine, and a proper fix needs a sync rewrite that cannot land by launch.
  - Supersedes: REQ-B1
  - Source: E3

- **REQ-C1 [accepted]:** REQ-C version 1 (current, authoritative, unchanged): Sign-in via SSO only; no passwords.
  - Reason: Original spec draft (E1). Neither E2 nor E3 changed it.
  - Source: E1

- **REQ-DATE1 [accepted]:** Launch date (current, authoritative, unchanged): December 15, fixed by marketing commitments.
  - Reason: Original spec draft (E1). Neither E2 nor E3 changed it.
  - Source: E1

### Decisions and requirements no longer in force

- **D1 [superseded]:** Team Notes v2 launches on desktop and mobile on December 15, with full offline editing required at launch and sign-in via SSO only with no passwords.
  - This was the requirement set as originally drafted in Part 1 of the scenario materials (E1). It was superseded by D2, and superseded in part as described under D3 above. Its SSO-only and December 15 elements remain in force via D4, REQ-C1, and REQ-DATE1.

- **REQ-A1 [superseded]:** REQ-A version 1: Launch on desktop and mobile.
  - Superseded by REQ-A2.

- **REQ-B1 [superseded]:** REQ-B version 1: Full offline editing is required at launch.
  - Superseded by REQ-B2.

## 3. Assumptions and facts

### Facts

Facts are distinct from assumptions and are taken from the evidence in the handoff material:

- **From E1 (scenario.md, Part 1, original spec draft):** Team Notes v2 requirements as originally drafted were REQ-A desktop and mobile, REQ-B full offline editing required at launch, REQ-C SSO only with no passwords, launch date December 15 fixed by marketing commitments. Standing constraints recorded there were that the December 15 date does not move, and no scope may be added to v2 without the PM's approval. Assumption A1 was also recorded there at medium confidence.
- **From E2 (scenario.md, Part 2, Update 1, source: PM, in writing):** Scope change for the v2 launch: launch mobile-only, desktop moves to a later release. Reason given: engineering capacity; the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- **From E3 (scenario.md, Part 2, Update 2, source: engineering lead):** Prototype finding: offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. Fixing this properly needs a sync rewrite that cannot land by launch. Recommendation, agreed with the PM: offline support moves out of the launch scope to release v2.1. The note states the v1 sync engine assumption did not hold for offline editing.

### Assumptions

- **A1 [invalidated, confidence: medium]:** The v1 sync engine can be reused for offline support without major changes.
  - Validated by: none
  - Status: This assumption turned out not to hold. It was invalidated by E3, as recorded under D3 and E3.

No other assumptions are recorded in the handoff material.

## 4. Constraints

Every standing constraint on the v2 scope recorded in the handoff material:

- **C1:** The December 15 launch date does not move.
  - Source: E1, original spec draft, where the date is described as fixed by marketing commitments.

- **C2:** No scope may be added to v2 without the product manager's approval.
  - Source: E1, original spec draft.

## 5. What changed and why

- **REQ-A: Launch platforms**
  - Changed from: REQ-A version 1: Launch on desktop and mobile. (REQ-A1)
  - Changed to: REQ-A version 2: Launch mobile-only. Desktop moves to a later release. (REQ-A2)
  - Why it changed: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, and the December 15 date does not move (C1).
  - Authoritative now: REQ-A version 2 (REQ-A2)
  - Where the change came from: E2, scenario.md, Part 2, Update 1 (source: PM, in writing); recorded as D2 superseding D1 and REQ-A2 superseding REQ-A1.

- **REQ-B: Offline support**
  - Changed from: REQ-B version 1: Full offline editing is required at launch. (REQ-B1)
  - Changed to: REQ-B version 2: Offline support moves out of the launch scope to release v2.1. (REQ-B2)
  - Why it changed: Prototype evidence (E3) shows offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. A proper fix needs a sync rewrite that cannot land by launch, and the December 15 date does not move (C1). Assumption A1, which made offline editing feasible at launch, was invalidated by the same evidence.
  - Authoritative now: REQ-B version 2 (REQ-B2)
  - Where the change came from: E3, scenario.md, Part 2, Update 2 (source: engineering lead), with the recommendation agreed with the PM; recorded as D3 and REQ-B2 superseding REQ-B1. D3 also supersedes the offline element of D1, as noted in Section 2.

- **Overall requirement set D1**
  - Changed from: D1: Launch on desktop and mobile on December 15, with full offline editing required at launch and sign-in via SSO only with no passwords.
  - Changed to: The current set in Section 1: mobile-only launch on December 15, no offline support at launch (moved to v2.1), SSO only with no passwords.
  - Why it changed: The platform change for engineering capacity (E2) and the offline change for prototype sync-conflict evidence (E3), both to protect the fixed December 15 date.
  - Authoritative now: D2, D3, and D4, together with REQ-A2, REQ-B2, REQ-C1, and REQ-DATE1.
  - Where the changes came from: E2 and E3, as above.

- **REQ-C: Authentication — no change**
  - REQ-C version 1 remains current and authoritative, unchanged: Sign-in via SSO only; no passwords.
  - Neither E2 nor E3 changed it. Recorded in D4 and REQ-C1.

- **Launch date — no change**
  - December 15 remains current and authoritative, unchanged, fixed by marketing commitments.
  - Neither E2 nor E3 changed it. Recorded in D4 and REQ-DATE1.

## 6. Open questions and missing information

The following are still undecided or unknown in the handoff material. No answers are invented here:

- Which release, and on what date, will desktop ship in, following its move to a later release under D2?
- What is the planned date for release v2.1, which now carries offline support under D3?
- Is any limited offline behavior expected in the v2 launch, or is there no offline support at all until v2.1?

Additional missing information:

- No next actions were recorded in the handoff material (see Section 7).

## 7. Next actions

No next actions are recorded in the handoff material: the Next actions field is recorded as "(none recorded)".

Therefore no concrete next steps for the spec and build can be stated from the handoff material without inventing them. The open questions in Section 6 remain flagged as undecided or unknown.

No action is proposed here that would build anything the current scope excludes, in particular desktop at v2 launch or offline support at v2 launch.

## 8. Authoritative spec summary

Team Notes v2 launches on December 15, a fixed date set by marketing commitments that does not move. The launch is mobile-only; desktop moves to a later release. Offline support is not part of the launch and moves to release v2.1. Sign-in is via SSO only, with no passwords. No scope may be added to v2 without the product manager's approval.

Change history: The original draft required desktop and mobile, full offline editing at launch, SSO only, and the December 15 date. Update 1 from the PM changed the launch to mobile-only for engineering capacity, as the desktop redesign cannot be finished by December 15 without cutting quality. Update 2 from the engineering lead moved offline support to v2.1 after prototype evidence showed unresolvable sync conflicts in about 1 in 20 editing sessions on the v1 sync engine, invalidating the assumption that the v1 engine could be reused without major changes; a sync rewrite cannot land by launch. Authentication and the launch date were unchanged by both updates.
