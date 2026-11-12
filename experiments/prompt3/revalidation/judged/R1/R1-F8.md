# Continuation Document: Team Notes v2 Specification (R1)

## 1. Where things stand

The current, authoritative requirements for the v2 launch are:

- **Launch date:** December 15, fixed. This date has not changed.
- **REQ-A version 2 (current, authoritative):** Launch mobile-only. Desktop moves to a later release.
- **REQ-B version 2 (current, authoritative):** Offline support is not part of the v2 launch. It moves to release v2.1.
- **REQ-C version 1 (current, authoritative, unchanged):** Sign-in via SSO only; no passwords.
- **Launch scope as currently defined:** mobile-only, no offline support at launch, SSO-only sign-in, on December 15.

No other current requirements are recorded in the handoff material.

## 2. Decisions in force

### Decisions currently in force

- **D2 [accepted]:** The v2 launch is mobile-only. Desktop moves to a later release.
  - Reason: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, and the December 15 date does not move (Constraint C1).

- **D3 [accepted]:** Offline support is not part of the v2 launch. It moves to release v2.1.
  - Reason: Prototype evidence (E3) shows offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. A proper fix needs a sync rewrite that cannot land by launch, and the December 15 date does not move (Constraint C1). The assumption that made offline editing feasible at launch (A1) was invalidated by the same evidence.

- **D4 [accepted]:** REQ-C remains sign-in via SSO only with no passwords, and the launch date remains December 15.
  - Reason: Neither official update changed authentication or the launch date. Both updates narrowed scope to protect the fixed date rather than moving it.

- **REQ-A2 [accepted]:** REQ-A version 2: Launch mobile-only. Desktop moves to a later release.
  - Reason: Engineering capacity; the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.

- **REQ-B2 [accepted]:** REQ-B version 2: Offline support moves out of the launch scope to release v2.1.
  - Reason: Prototype evidence of unresolvable sync conflicts on the v1 sync engine, and a proper fix needs a sync rewrite that cannot land by launch.

- **REQ-C1 [accepted]:** REQ-C version 1: Sign-in via SSO only; no passwords.
  - Reason: Original spec draft (E1). Neither E2 nor E3 changed it.

- **REQ-DATE1 [accepted]:** Launch date: December 15, fixed by marketing commitments.
  - Reason: Original spec draft (E1). Neither E2 nor E3 changed it.

### Decisions and requirements no longer in force

- **D1 [superseded]:** Team Notes v2 launches on desktop and mobile on December 15, with full offline editing required at launch and sign-in via SSO only with no passwords.
  - This was the requirement set as originally drafted in Part 1 of the scenario materials. It was superseded by D2. The handoff material also records that D1 was superseded in part by D3 for its offline element; the schema records one successor link per superseded decision (held by D2), so that link is preserved in text in D3.

- **REQ-A1 [superseded]:** REQ-A version 1: Launch on desktop and mobile.
  - Superseded by REQ-A2.

- **REQ-B1 [superseded]:** REQ-B version 1: Full offline editing is required at launch.
  - Superseded by REQ-B2.

## 3. Assumptions and facts

### Assumptions

- **A1 [invalidated, confidence: medium]:** The v1 sync engine can be reused for offline support without major changes.
  - Validated by: none recorded.
  - This assumption turned out not to hold. Evidence E3 states the v1 sync engine assumption did not hold for offline editing, and D3 records A1 as invalidated by that evidence.

No other assumptions are recorded in the handoff material.

### Facts

Facts are kept distinct from assumptions:

- The original spec draft (E1) specified: REQ-A desktop and mobile, REQ-B full offline editing required at launch, REQ-C SSO only with no passwords, and a launch date of December 15 fixed by marketing commitments.
- Update 1 (E2, source: PM, in writing) changed the launch scope to mobile-only, with desktop moving to a later release, for engineering capacity reasons: the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- Prototype finding (E3, source: engineering lead): offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. Fixing this properly needs a sync rewrite that cannot land by launch.
- The recommendation in E3, agreed with the PM, was that offline support moves out of the launch scope to release v2.1.
- Neither E2 nor E3 changed REQ-C or the December 15 launch date.

## 4. Constraints

Every standing constraint recorded in the handoff material:

- **C1:** The December 15 launch date does not move. Source: E1, original spec draft, where the date is described as fixed by marketing commitments.
- **C2:** No scope may be added to v2 without the product manager's approval. Source: E1, original spec draft.

No other constraints are recorded in the handoff material.

## 5. What changed and why

- **REQ-A: Desktop and mobile → Mobile-only**
  - From: REQ-A version 1 (REQ-A1): Launch on desktop and mobile.
  - To: REQ-A version 2 (REQ-A2): Launch mobile-only. Desktop moves to a later release.
  - Why: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, and the December 15 date does not move (C1).
  - Authoritative now: REQ-A version 2 (REQ-A2 / D2).
  - Source of change: E2, scenario.md, Part 2, Update 1 (source: PM, in writing).

- **REQ-B: Full offline editing required at launch → No offline support at launch; offline moves to v2.1**
  - From: REQ-B version 1 (REQ-B1): Full offline editing is required at launch.
  - To: REQ-B version 2 (REQ-B2): Offline support moves out of the launch scope to release v2.1.
  - Why: Prototype evidence shows offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. A proper fix needs a sync rewrite that cannot land by launch, and the December 15 date does not move (C1). Assumption A1, that the v1 sync engine could be reused for offline support without major changes, was invalidated by the same evidence.
  - Authoritative now: REQ-B version 2 (REQ-B2 / D3).
  - Source of change: E3, scenario.md, Part 2, Update 2 (source: engineering lead), with the recommendation agreed with the PM.

- **D1 as a combined requirement set: superseded**
  - From: D1: Launches on desktop and mobile on December 15, with full offline editing required at launch and sign-in via SSO only with no passwords.
  - To: The current set in D2, D3, and D4 / REQ-A2, REQ-B2, REQ-C1, and REQ-DATE1.
  - Why: The platform element changed under D2 and the offline element changed under D3, for the reasons above. The SSO and date elements did not change.
  - Authoritative now: D2, D3, and D4, as listed in Section 2.
  - Source of change: E2 and E3.

- **REQ-C: No change**
  - REQ-C version 1 remains current and authoritative: Sign-in via SSO only; no passwords.
  - Source: E1; neither E2 nor E3 changed it. Confirmed by D4.

- **Launch date: No change**
  - December 15 remains current and authoritative, fixed by marketing commitments.
  - Source: E1; neither E2 nor E3 changed it. Confirmed by D4.

## 6. Open questions and missing information

The following are still undecided or unknown in the handoff material. No answers are recorded; none are invented here:

- Which release, and on what date, will desktop ship in, following its move to a later release under D2?
- What is the planned date for release v2.1, which now carries offline support under D3?
- Is any limited offline behavior expected in the v2 launch, or is there no offline support at all until v2.1?
- Next actions: none are recorded in the handoff material (see Section 7).

## 7. Next actions

No next actions are recorded in the handoff material.

Missing information: the handoff material records "(none recorded)" for next actions, so no concrete next steps for the spec and build, and no order for them, can be stated from that material without inventing them.

Nothing in this section proposes building anything the current scope excludes. Desktop is excluded from the v2 launch and offline support is excluded from the v2 launch until v2.1, as recorded in Sections 1, 2, and 5.

## 8. Authoritative spec summary

Team Notes v2 launches on December 15, a date fixed by marketing commitments that does not move. The launch is mobile-only; desktop moves to a later release. Offline support is not part of the launch; it moves to release v2.1. Sign-in is via SSO only, with no passwords. No scope may be added to v2 without the product manager's approval.

Change history: The original draft required desktop and mobile, full offline editing at launch, SSO-only sign-in, and the December 15 date. REQ-A then changed to mobile-only because the desktop redesign cannot be finished by December 15 without cutting quality. REQ-B then changed to remove offline support from launch because prototype testing found unresolvable sync conflicts in about 1 in 20 sessions on the v1 sync engine, invalidating the assumption that that engine could be reused without major changes, and a sync rewrite cannot land by launch. REQ-C and the launch date are unchanged.
