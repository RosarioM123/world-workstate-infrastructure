# Continuation Document

## 1. **Where things stand:**

The current, authoritative requirements for the Team Notes v2 launch are:

- **REQ-A version 2:** Launch mobile-only. Desktop moves to a later release.
- **REQ-B version 2:** Offline support is not part of the v2 launch. It moves to release v2.1.
- **REQ-C version 1 (unchanged):** Sign-in via SSO only; no passwords.
- **Launch date (unchanged):** December 15, fixed by marketing commitments.

## 2. **Decisions in force:**

Decisions and requirements currently governing the spec:

- **D2:** The v2 launch is mobile-only. Desktop moves to a later release.
  Reason: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, and the December 15 date does not move (Constraint C1).
- **D3:** Offline support is not part of the v2 launch. It moves to release v2.1.
  Reason: Prototype evidence (E3) shows offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. A proper fix needs a sync rewrite that cannot land by launch, and the December 15 date does not move (Constraint C1). The assumption that made offline editing feasible at launch (A1) was invalidated by the same evidence.
- **D4:** REQ-C remains sign-in via SSO only with no passwords, and the launch date remains December 15.
  Reason: Neither official update changed authentication or the launch date. Both updates narrowed scope to protect the fixed date rather than moving it.
- **REQ-A2:** REQ-A version 2 (current, authoritative): Launch mobile-only. Desktop moves to a later release.
- **REQ-B2:** REQ-B version 2 (current, authoritative): Offline support moves out of the launch scope to release v2.1.
- **REQ-C1:** REQ-C version 1 (current, authoritative, unchanged): Sign-in via SSO only; no passwords.
- **REQ-DATE1:** Launch date (current, authoritative, unchanged): December 15, fixed by marketing commitments.

Decisions and requirements no longer in force:

- **D1 [superseded]:** Team Notes v2 launches on desktop and mobile on December 15, with full offline editing required at launch and sign-in via SSO only with no passwords.
- **REQ-A1 [superseded]:** REQ-A version 1: Launch on desktop and mobile.
- **REQ-B1 [superseded]:** REQ-B version 1: Full offline editing is required at launch.
- The offline element of D1 is also superseded by D3; the original bundle records D1 as superseded in part by D2 and by D3, and the schema records one successor link per superseded decision (held by D2), so this link is preserved in text.

## 3. **Assumptions and facts:**

Assumptions:

- **A1 [invalidated, confidence: medium]:** The v1 sync engine can be reused for offline support without major changes.
  This assumption turned out not to hold. Evidence E3 states the v1 sync engine assumption did not hold for offline editing.

No other assumptions are recorded in the handoff material.

Facts, distinct from assumptions:

- The original spec draft (E1) specified REQ-A desktop and mobile, REQ-B full offline editing required at launch, REQ-C SSO only with no passwords, and launch date December 15 fixed by marketing commitments.
- Update 1 (E2) changed the scope to mobile-only, with desktop moving to a later release, for engineering capacity; the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- Prototype finding (E3): offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. Fixing this properly needs a sync rewrite that cannot land by launch.

## 4. **Constraints:**

- **C1:** The December 15 launch date does not move. Source: E1, original spec draft, where the date is described as fixed by marketing commitments.
- **C2:** No scope may be added to v2 without the product manager's approval. Source: E1, original spec draft.

## 5. **What changed and why:**

- **REQ-A changed:**
  From: Version 1 - Launch on desktop and mobile.
  To: Version 2 - Launch mobile-only. Desktop moves to a later release.
  Why: Engineering capacity; the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
  Authoritative now: REQ-A version 2 (REQ-A2).
  Source of change: E2, scenario.md, Part 2, Update 1 (source: PM, in writing). This is also recorded as D2, which supersedes D1 and REQ-A1.

- **REQ-B changed:**
  From: Version 1 - Full offline editing is required at launch.
  To: Version 2 - Offline support moves out of the launch scope to release v2.1.
  Why: Prototype evidence of unresolvable sync conflicts on the v1 sync engine (about 1 in 20 editing sessions), and a proper fix needs a sync rewrite that cannot land by launch.
  Authoritative now: REQ-B version 2 (REQ-B2).
  Source of change: E3, scenario.md, Part 2, Update 2 (source: engineering lead), with the recommendation agreed with the PM. This is also recorded as D3, which supersedes the offline element of D1 and supersedes REQ-B1.

- **REQ-C did not change:**
  It remains version 1: Sign-in via SSO only; no passwords.
  Authoritative now: REQ-C version 1 (REQ-C1).
  Source: E1, original spec draft. Neither E2 nor E3 changed it.

- **Launch date did not change:**
  It remains December 15, fixed by marketing commitments.
  Authoritative now: REQ-DATE1.
  Source: E1, original spec draft. Neither E2 nor E3 changed it.

## 6. **Open questions and missing information:**

The following are still undecided or unknown in the handoff material. No answers are invented for them:

- Which release, and on what date, will desktop ship in, following its move to a later release under D2?
- What is the planned date for release v2.1, which now carries offline support under D3?
- Is any limited offline behavior expected in the v2 launch, or is there no offline support at all until v2.1?
- No next actions were recorded in the handoff material.

## 7. **Next actions:**

No next actions are recorded in the handoff material. Concrete next steps for the spec and build are therefore missing information and are not invented here.

## 8. **Authoritative spec summary:**

Team Notes v2 launches on December 15, on mobile only. Sign-in is via SSO only, with no passwords. Offline support is not included in the v2 launch; it moves to release v2.1. Desktop is also excluded from v2 and moves to a later release.

Change history: The original spec required desktop and mobile, full offline editing at launch, SSO-only sign-in, and a December 15 launch. Update 1 from the PM narrowed REQ-A to mobile-only because the desktop redesign cannot be finished by December 15 without cutting quality. Update 2 from the engineering lead, agreed with the PM, moved offline support to v2.1 after prototype work showed unresolvable sync conflicts in about 1 in 20 sessions on the v1 sync engine, invalidating the assumption that that engine could be reused without major changes. REQ-C and the December 15 date are unchanged.
