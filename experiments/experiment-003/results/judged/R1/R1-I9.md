# Continuation Document: Team Notes v2 Specification

## 1. Where things stand

The current, authoritative requirements for the v2 launch are:

- Platforms (REQ-A, Version 2): Launch mobile-only. Desktop moves to a later release.
- Offline support (REQ-B, Version 2): Offline support is not part of the launch scope. It moves to release v2.1.
- Authentication (REQ-C, Version 1): Sign-in via SSO only; no passwords.
- Launch date: December 15. The date is fixed by marketing commitments.

In summary, Team Notes v2 launches mobile-only on December 15, with sign-in via SSO only. Desktop is deferred to a later release, and offline support is deferred to release v2.1.

## 2. Decisions in force

### Decisions that currently govern the spec

- D2: Launch mobile-only; move desktop to a later release.
  Reason: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, and the December 15 date does not move (Constraint C1). Source: E2, scope message from the product manager, in writing.

- D3: Move offline support out of launch scope to release v2.1.
  Reason: Prototype evidence (E3) shows offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. A proper fix needs a sync rewrite that cannot land by launch, and the December 15 date does not move (Constraint C1). The recommendation was agreed with the PM. Source: E3, engineering review note from the engineering lead.

- D4: Keep authentication and launch date unchanged.
  Reason: Neither official update changed authentication or the launch date. Both updates narrowed scope to protect the fixed date rather than moving it. REQ-C remains sign-in via SSO only with no passwords, and the launch date remains December 15. Sources: E1, E2, and E3.

### Decisions and requirements no longer in force

- D1: Adopt the original spec draft as the v2 baseline. Status: superseded in part.
  The platform element of D1 is superseded by D2, and the offline element of D1 is superseded by D3. The authentication element and the launch date element of D1 remain accepted through D2 and D3, and are confirmed by D4.
- REQ-A Version 1: Launch on desktop and mobile. Superseded by REQ-A Version 2.
- REQ-B Version 1: Full offline editing is required at launch. Superseded by REQ-B Version 2.

## 3. Assumptions and facts

### Assumptions

- A1: The sync engine from v1 can be reused for offline support without major changes.
  Label: Assumption.
  Confidence: medium, as recorded in the original draft (E1).
  Status: Invalidated. This assumption turned out not to hold. E3 states: "The v1 sync engine assumption did not hold for offline editing." E3 also states that a proper fix needs a sync rewrite.
  Note: There are no active assumptions in the handoff material. Do not plan offline support on the v1 sync engine.

No other assumptions are recorded in the handoff material.

### Facts

Facts are kept distinct from assumptions:

- The launch date is December 15, fixed by marketing commitments (E1).
- The desktop app needs a redesign that cannot be finished by December 15 without cutting quality (E2).
- Prototype finding: offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions (E3).
- A proper fix for the offline sync conflicts needs a sync rewrite that cannot land by launch (E3).
- Sign-in is via SSO only, with no passwords (E1, unchanged by E2 and E3).

## 4. Constraints

Every standing constraint on the v2 scope recorded in the handoff material:

- C1: The December 15 launch date does not move. Source: E1, original spec draft, where the date is described as fixed by marketing commitments.
- C2: No scope may be added to v2 without the product manager's approval. Source: E1, original spec draft.

Neither constraint was changed by E2 or E3.

## 5. What changed and why

### REQ-A, Platforms

- Changed from: Version 1, launch on desktop and mobile.
- Changed to: Version 2, launch mobile-only. Desktop moves to a later release.
- Why it changed: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- Authoritative now: Version 2.
- Where the change came from: E2, scope message from the product manager, in writing. Recorded as Decision D2, which supersedes the platform element of D1 and REQ-A Version 1.

### REQ-B, Offline support

- Changed from: Version 1, full offline editing is required at launch.
- Changed to: Version 2, offline support moves out of the launch scope to release v2.1.
- Why it changed: Prototype evidence of unresolvable sync conflicts on the v1 sync engine, in about 1 in 20 editing sessions, and a proper fix needs a sync rewrite that cannot land by launch. The assumption that made offline editing feasible at launch (A1) was invalidated by the same evidence. The recommendation was agreed with the PM.
- Authoritative now: Version 2.
- Where the change came from: E3, engineering review note from the engineering lead. Recorded as Decision D3, which supersedes the offline element of D1 and REQ-B Version 1.

### Requirements that did not change

- REQ-C, Authentication: Version 1 remains current and authoritative. Sign-in via SSO only; no passwords. Source: E1. Neither E2 nor E3 changed it.
- Launch date: December 15 remains current and authoritative, fixed by marketing commitments. Source: E1. Neither E2 nor E3 changed it.
- Confirmation of both unchanged items is recorded as Decision D4.

## 6. Open questions and missing information

The following are still undecided or unknown. They are flagged here; no answers are invented.

- Q1, Desktop release timing: Which release, and on what date, will desktop ship in, following its move to a later release under D2? E2 says desktop moves to a later release and gives no release name or date. Status: open.
- Q2, Release v2.1 timing: What is the planned date for release v2.1, which now carries offline support under D3? E3 names release v2.1 and gives no date. Status: open.
- Q3, Offline behavior at launch: Is any limited offline behavior expected in the v2 launch, or is there no offline support at all until v2.1? E3 defers offline support as a whole to v2.1 and does not specify a partial form for launch. Any addition here would also need PM approval under Constraint C2. Status: open.

No other open questions are recorded in the handoff material, and no dates or release names for the deferred items are provided in that material.

## 7. Next actions

In order:

1. Seek answers to the open questions from the appropriate sources: Q1 on desktop release timing, Q2 on the release v2.1 date, and Q3 on whether any limited offline behavior is expected at launch. Do not add any scope to v2 without the product manager's approval under Constraint C2.
2. Confirm the current requirements are stated in report.md as specified in the definition of done: REQ-A Version 2, REQ-B Version 2, and REQ-C Version 1, with the December 15 launch date.
3. Send the authoritative spec summary in Section 8 to the build team, making clear that desktop at launch and offline editing at launch are out of the v2 launch scope.
4. Build and prepare the v2 launch to the current scope only: mobile-only, sign-in via SSO only with no passwords, for the fixed December 15 date.
5. Keep desktop and offline support tracked as deferred items, for a later release and for release v2.1 respectively, pending the answers to Q1 and Q2.

No step above proposes building desktop or offline support for the v2 launch, because the current scope excludes both.

## 8. Authoritative spec summary

Team Notes v2 launches on December 15, a fixed date set by marketing commitments. The launch is mobile-only, with sign-in via SSO only and no passwords. Desktop is not part of the launch; it moves to a later release, whose name and date are not yet specified. Offline support is not part of the launch; it moves to release v2.1, whose date is not yet specified, and whether any limited offline behavior is expected at launch is still an open question. No scope may be added to v2 without the product manager's approval.

Change history: The original draft required desktop and mobile at launch, full offline editing at launch, and SSO-only sign-in. The platform requirement then changed to mobile-only for engineering capacity, because the desktop redesign cannot be finished by December 15 without cutting quality. The offline requirement then changed to deferral to v2.1, because prototype work found unresolvable sync conflicts in about 1 in 20 offline editing sessions on the v1 sync engine, and a proper fix needs a sync rewrite that cannot land by launch. That finding also invalidated the assumption that the v1 sync engine could be reused for offline support without major changes. Authentication and the launch date did not change.
