# Continuation Document: Team Notes v2

## 1. Where things stand

The current, authoritative requirements for the v2 launch are:

- **REQ-A version 2:** Launch mobile-only. Desktop moves to a later release.
- **REQ-B version 2:** Offline support is not part of the v2 launch. It moves to release v2.1.
- **REQ-C version 1 (unchanged):** Sign-in via SSO only; no passwords.
- **Launch date (unchanged):** December 15, fixed by marketing commitments.

## 2. Decisions in force

### Decisions currently governing the spec

- **D2:** The v2 launch is mobile-only. Desktop moves to a later release.
  - Reason: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, and the December 15 date does not move (Constraint C1).

- **D3:** Offline support is not part of the v2 launch. It moves to release v2.1.
  - Reason: Prototype evidence (E3) shows offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. A proper fix needs a sync rewrite that cannot land by launch, and the December 15 date does not move (Constraint C1). The assumption that made offline editing feasible at launch (A1) was invalidated by the same evidence.

- **D4:** REQ-C remains sign-in via SSO only with no passwords, and the launch date remains December 15.
  - Reason: Neither official update changed authentication or the launch date. Both updates narrowed scope to protect the fixed date rather than moving it.

### Decisions and requirements no longer in force

- **D1 [superseded]:** Team Notes v2 launches on desktop and mobile on December 15, with full offline editing required at launch.
  - Superseded by D2. The handoff material also records that D3 supersedes the offline element of D1; the original bundle records D1 as superseded in part by D2 and by D3, and the schema records one successor link per superseded decision (held by D2), so this link is preserved in text.

- **REQ-A1 / REQ-A version 1 [superseded]:** Launch on desktop and mobile.
  - Superseded by REQ-A2.

- **REQ-B1 / REQ-B version 1 [superseded]:** Full offline editing is required at launch.
  - Superseded by REQ-B2.

## 3. Assumptions and facts

### Assumptions

- **A1 [invalidated, confidence: medium]:** The v1 sync engine can be reused for offline support without major changes.
  - This assumption turned out not to hold. Evidence E3 states the v1 sync engine assumption did not hold for offline editing.

No other assumptions are recorded in the handoff material.

### Facts

Facts are distinct from assumptions and are drawn from the evidence in the handoff material:

- **From E1:** The original draft specified REQ-A desktop and mobile, REQ-B full offline editing required at launch, REQ-C SSO only with no passwords, and a launch date of December 15 fixed by marketing commitments. It also recorded the standing constraints and Assumption A1 at medium confidence.
- **From E2:** The scope changed to launch mobile-only, with desktop moving to a later release, for reasons of engineering capacity and the unfinished desktop redesign.
- **From E3:** A prototype found that offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. Fixing this properly needs a sync rewrite that cannot land by launch. The recommendation, agreed with the PM, was to move offline support out of the launch scope to release v2.1.

## 4. Constraints

- **C1:** The December 15 launch date does not move.
  - Source: E1, original spec draft, where the date is described as fixed by marketing commitments.

- **C2:** No scope may be added to v2 without the product manager's approval.
  - Source: E1, original spec draft.

## 5. What changed and why

- **REQ-A: Launch platforms**
  - Changed from: Version 1 - launch on desktop and mobile.
  - Changed to: Version 2 - launch mobile-only; desktop moves to a later release.
  - Why: Engineering capacity; the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
  - Authoritative now: Version 2 (REQ-A2).
  - Source of change: E2, scenario.md, Part 2, Update 1 (source: PM, in writing).

- **REQ-B: Offline editing**
  - Changed from: Version 1 - full offline editing is required at launch.
  - Changed to: Version 2 - offline support moves out of the launch scope to release v2.1.
  - Why: Prototype evidence of unresolvable sync conflicts on the v1 sync engine in about 1 in 20 editing sessions, and a proper fix needs a sync rewrite that cannot land by launch.
  - Authoritative now: Version 2 (REQ-B2).
  - Source of change: E3, scenario.md, Part 2, Update 2 (source: engineering lead). The recommendation was agreed with the PM.

- **REQ-C: Sign-in**
  - No change.
  - Version 1 remains current and authoritative: sign-in via SSO only; no passwords.
  - Source: E1, original spec draft. Neither E2 nor E3 changed it.

- **Launch date**
  - No change.
  - December 15 remains current and authoritative, fixed by marketing commitments.
  - Source: E1, original spec draft. Neither E2 nor E3 changed it.

## 6. Open questions and missing information

The following are still undecided or unknown in the handoff material. No answers are provided in the material, and none are invented here:

- Which release, and on what date, will desktop ship in, following its move to a later release under D2?
- What is the planned date for release v2.1, which now carries offline support under D3?
- Is any limited offline behavior expected in the v2 launch, or is there no offline support at all until v2.1?
- Next actions: none were recorded in the handoff material (see Section 7).

## 7. Next actions

No next actions were recorded in the handoff material. No concrete next steps for the spec and build can be listed from the material without inventing them.

## 8. Authoritative spec summary

Team Notes v2 launches on December 15 on mobile only. Sign-in is via SSO only, with no passwords. Offline support is not included in the v2 launch and moves to release v2.1. Desktop also moves to a later release.

Change history: The original draft required desktop and mobile at launch, with full offline editing. Update 1 (PM, in writing) narrowed REQ-A to mobile-only because the desktop redesign cannot be finished by December 15 without cutting quality. Update 2 (engineering lead, agreed with the PM) removed offline support from the launch after prototype testing showed unresolvable sync conflicts in about 1 in 20 sessions on the v1 sync engine, invalidating the assumption that that engine could be reused without major changes. REQ-C and the December 15 date are unchanged.
