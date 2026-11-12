# Continuation Document: Team Notes v2 Specification (R1)

## 1. Where things stand

The current, authoritative requirements for the v2 launch are:

- **REQ-A version 2:** Launch mobile-only. Desktop moves to a later release.
- **REQ-B version 2:** Offline support is not part of the v2 launch. It moves to release v2.1.
- **REQ-C version 1 (unchanged):** Sign-in via SSO only; no passwords.
- **Launch date (unchanged):** December 15, fixed by marketing commitments.

## 2. Decisions in force

**Decisions and requirements currently in force:**

- **D2 [accepted]:** The v2 launch is mobile-only. Desktop moves to a later release.
  - Reason: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, and the December 15 date does not move (Constraint C1).
- **D3 [accepted]:** Offline support is not part of the v2 launch. It moves to release v2.1.
  - Reason: Prototype evidence (E3) shows offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. A proper fix needs a sync rewrite that cannot land by launch, and the December 15 date does not move (Constraint C1). The assumption that made offline editing feasible at launch (A1) was invalidated by the same evidence.
- **D4 [accepted]:** REQ-C remains sign-in via SSO only with no passwords, and the launch date remains December 15.
  - Reason: Neither official update changed authentication or the launch date. Both updates narrowed scope to protect the fixed date rather than moving it.
- **REQ-A2 [accepted]:** REQ-A version 2 (current, authoritative): Launch mobile-only. Desktop moves to a later release.
  - Reason: Engineering capacity; the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- **REQ-B2 [accepted]:** REQ-B version 2 (current, authoritative): Offline support moves out of the launch scope to release v2.1.
  - Reason: Prototype evidence of unresolvable sync conflicts on the v1 sync engine, and a proper fix needs a sync rewrite that cannot land by launch.
- **REQ-C1 [accepted]:** REQ-C version 1 (current, authoritative, unchanged): Sign-in via SSO only; no passwords.
  - Reason: Original spec draft (E1). Neither E2 nor E3 changed it.
- **REQ-DATE1 [accepted]:** Launch date (current, authoritative, unchanged): December 15, fixed by marketing commitments.
  - Reason: Original spec draft (E1). Neither E2 nor E3 changed it.

**Decisions and requirements no longer in force:**

- **D1 [superseded]:** Team Notes v2 launches on desktop and mobile on December 15, with full offline editing required at launch. The original bundle records D1 as superseded in part by D2 and by D3; the schema records one successor link per superseded decision (held by D2), so the D3 link is preserved in text in D3.
- **REQ-A1 [superseded]:** REQ-A version 1: Launch on desktop and mobile. Superseded by REQ-A2.
- **REQ-B1 [superseded]:** REQ-B version 1: Full offline editing is required at launch. Superseded by REQ-B2.

## 3. Assumptions and facts

**Assumptions:**

- **A1 [invalidated, confidence: medium]:** The v1 sync engine can be reused for offline support without major changes.
  - This assumption turned out not to hold. Evidence E3 states the v1 sync engine assumption did not hold for offline editing.

No other assumptions are recorded in the handoff material.

**Facts:**

- The original spec draft (E1) specified REQ-A desktop and mobile, REQ-B full offline editing required at launch, REQ-C SSO only with no passwords, and a launch date of December 15 fixed by marketing commitments.
- Update 1 (E2) changed the launch scope to mobile-only, with desktop moving to a later release, for engineering capacity reasons, because the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- Prototype finding (E3): offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. Fixing this properly needs a sync rewrite that cannot land by launch.

Facts are distinct from the assumption above: A1 was an assumption, and E3 is the evidence that invalidated it.

## 4. Constraints

- **C1:** The December 15 launch date does not move. Source: E1, original spec draft, where the date is described as fixed by marketing commitments.
- **C2:** No scope may be added to v2 without the product manager's approval. Source: E1, original spec draft.

## 5. What changed and why

- **REQ-A: Launch platforms**
  - Changed from: Version 1 - Launch on desktop and mobile.
  - Changed to: Version 2 - Launch mobile-only. Desktop moves to a later release.
  - Why: Engineering capacity; the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
  - Authoritative now: Version 2 (REQ-A2).
  - Source of change: E2, scenario.md, Part 2, Update 1 (source: PM, in writing). This is also recorded as decision D2, which supersedes D1 and REQ-A1.

- **REQ-B: Offline editing**
  - Changed from: Version 1 - Full offline editing is required at launch.
  - Changed to: Version 2 - Offline support moves out of the launch scope to release v2.1.
  - Why: Prototype evidence shows offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. A proper fix needs a sync rewrite that cannot land by launch, and the December 15 date does not move (C1). Assumption A1 was invalidated by the same evidence.
  - Authoritative now: Version 2 (REQ-B2).
  - Source of change: E3, scenario.md, Part 2, Update 2 (source: engineering lead). This is also recorded as decision D3, which supersedes the offline element of D1.

- **REQ-C: Authentication**
  - No change.
  - Version 1 remains authoritative: Sign-in via SSO only; no passwords.
  - Source: E1, original spec draft. Neither E2 nor E3 changed it. Confirmed by D4.

- **Launch date**
  - No change.
  - December 15 remains authoritative, fixed by marketing commitments.
  - Source: E1, original spec draft. Neither E2 nor E3 changed it. Confirmed by D4.

## 6. Open questions and missing information

The following are still undecided or unknown in the handoff material. No answers are invented here:

- Which release, and on what date, will desktop ship in, following its move to a later release under D2?
- What is the planned date for release v2.1, which now carries offline support under D3?
- Is any limited offline behavior expected in the v2 launch, or is there no offline support at all until v2.1?
- Next actions: none were recorded in the handoff material (see Section 7).

## 7. Next actions

No next actions were recorded in the handoff material.

Therefore no concrete next steps for the spec and build can be listed from the material provided without inventing them. This information is missing and needs to be supplied.

## 8. Authoritative spec summary

Team Notes v2 launches on December 15, mobile-only, with sign-in via SSO only and no passwords. Offline support is not part of the v2 launch and moves to release v2.1. Desktop is not part of the v2 launch and moves to a later release.

Change history: The original draft specified desktop and mobile launch, full offline editing at launch, SSO-only sign-in, and the December 15 date. REQ-A changed to mobile-only because the desktop redesign cannot be finished by December 15 without cutting quality. REQ-B changed to exclude offline support because prototype testing found unresolvable sync conflicts in about 1 in 20 offline editing sessions on the v1 sync engine, requiring a sync rewrite that cannot land by launch, invalidating the assumption that the v1 sync engine could be reused for offline support without major changes. REQ-C and the December 15 date are unchanged.
