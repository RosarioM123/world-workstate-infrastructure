# Continuation Document: Team Notes v2 Specification (R1)

## 1. Where things stand

Team Notes v2 is a shared note-taking app scheduled to launch on December 15. The current, authoritative requirements for the v2 launch are:

- REQ-A, Platforms, Version 2: Launch mobile-only. Desktop moves to a later release.
- REQ-B, Offline support, Version 2: Offline support is not part of the launch scope. It moves to release v2.1.
- REQ-C, Authentication, Version 1: Sign-in via SSO only, with no passwords. This requirement is unchanged.
- Launch date, Version 1: December 15. This is unchanged and is fixed by marketing commitments.

The project status is active. The definition of done in the handoff material is that current requirements are stated in report.md, the full revision history is preserved in the bundle, and open questions are listed for the successor.

## 2. Decisions in force

### Decisions currently governing the spec

- D2: Launch mobile-only; move desktop to a later release. Reason: engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, and the December 15 date does not move under Constraint C1. Source: E2, a scope message from the product manager, in writing. The product manager is also the scope approver under Constraint C2.
- D3: Move offline support out of launch scope to release v2.1. Reason: prototype evidence in E3 shows offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. A proper fix needs a sync rewrite that cannot land by launch, and the December 15 date does not move under Constraint C1. The assumption that made offline editing feasible at launch, A1, was invalidated by the same evidence. Source: E3, an engineering review note from the engineering lead. The handoff material states the recommendation was agreed with the PM, satisfying Constraint C2.
- D4: Keep authentication and launch date unchanged. REQ-C remains sign-in via SSO only with no passwords, and the launch date remains December 15. Reason: neither official update changed authentication or the launch date. Both updates narrowed scope to protect the fixed date rather than moving it. Sources: E1, E2, and E3.

### Decisions and requirements no longer in force

- D1, platform element: The original baseline decision to launch on desktop and mobile is superseded by D2. REQ-A Version 1 is no longer in force.
- D1, offline element: The original baseline decision to require full offline editing at launch is superseded by D3. REQ-B Version 1 is no longer in force.
- D1 is therefore superseded in part. Its authentication element and launch date element are not superseded; they remain in force and are confirmed by D4.

## 3. Assumptions and facts

### Assumptions

- A1: The sync engine from v1 can be reused for offline support without major changes.
  - Label: Assumption, recorded in the original spec draft, E1.
  - Confidence: Medium, as recorded in the original draft.
  - Status: Invalidated. It did not hold. E3 states: "The v1 sync engine assumption did not hold for offline editing."
  - Implication recorded in the handoff material: Do not plan offline support on the v1 sync engine. A proper fix needs a sync rewrite.

The handoff material states there are no active assumptions in the bundle.

### Facts

Facts are kept distinct from assumptions. The following are stated in the evidence recorded in the handoff material:

- E1, the original spec draft, set the original requirements: desktop and mobile launch, full offline editing required at launch, SSO only with no passwords, and a December 15 launch date fixed by marketing commitments. It also recorded Constraints C1 and C2 and Assumption A1.
- E2, the product manager scope message, changed the launch to mobile-only and moved desktop to a later release for engineering capacity reasons, specifically the desktop redesign that cannot be finished by December 15 without cutting quality.
- E3, the engineering review note, reports the prototype finding that offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions, and that a proper fix needs a sync rewrite that cannot land by launch. It also records the recommendation, agreed with the PM, to move offline support to release v2.1.

## 4. Constraints

- C1: The December 15 launch date does not move. Source: E1, the original spec draft, where the date is described as fixed by marketing commitments.
- C2: No scope may be added to v2 without the product manager's approval. Source: E1, the original spec draft.

The handoff material states that neither constraint was changed by E2 or E3.

## 5. What changed and why

- REQ-A, Platforms:
  - Changed from: Version 1, launch on desktop and mobile.
  - Changed to: Version 2, launch mobile-only, with desktop moving to a later release.
  - Why: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
  - Authoritative now: Version 2.
  - Source of change: E2, the product manager scope message, in writing. Recorded as Decision D2, which supersedes the platform element of D1.

- REQ-B, Offline support:
  - Changed from: Version 1, full offline editing is required at launch.
  - Changed to: Version 2, offline support moves out of the launch scope to release v2.1.
  - Why: Prototype evidence of unresolvable sync conflicts on the v1 sync engine, in about 1 in 20 editing sessions, and a proper fix needs a sync rewrite that cannot land by launch.
  - Authoritative now: Version 2.
  - Source of change: E3, the engineering review note from the engineering lead. The recommendation was agreed with the PM. Recorded as Decision D3, which supersedes the offline element of D1. The same evidence invalidated Assumption A1.

- REQ-C, Authentication:
  - Changed: No.
  - Current and authoritative: Version 1, sign-in via SSO only, with no passwords.
  - Source: E1. Neither E2 nor E3 changed it. Confirmed by Decision D4.

- Launch date:
  - Changed: No.
  - Current and authoritative: Version 1, December 15, fixed by marketing commitments.
  - Source: E1. Neither E2 nor E3 changed it. Confirmed by Decision D4.

## 6. Open questions and missing information

The following are open. No answers are provided in the handoff material, and no answers are invented here.

- Q1, Desktop release timing: Which release, and on what date, will desktop ship in, following its move to a later release under D2? E2 gives no release name or date. This information is missing.
- Q2, Release v2.1 timing: What is the planned date for release v2.1, which now carries offline support under D3? E3 names release v2.1 and gives no date. This information is missing.
- Q3, Offline behavior at launch: Is any limited offline behavior expected in the v2 launch, or is there no offline support at all until v2.1? E3 defers offline support as a whole to v2.1 and does not specify a partial form for launch. This information is missing. Any addition here would also need PM approval under Constraint C2.

## 7. Next actions

In order:

1. Start with the open questions Q1, Q2, and Q3, and obtain decisions on desktop release timing, the release v2.1 date, and whether any limited offline behavior is expected at launch. Do not assume answers that are not in the handoff material.
2. Obtain PM approval under Constraint C2 before adding any scope to v2, including any limited offline behavior if Q3 is answered in a way that would add it.
3. Finalize the spec so it states the current authoritative requirements: REQ-A Version 2, REQ-B Version 2, REQ-C Version 1, and the December 15 launch date, with the full revision history preserved.
4. Send the authoritative spec summary in Section 8 to the build team.
5. Build for the v2 launch to the current scope only: mobile-only, with sign-in via SSO only and no passwords, for the December 15 launch.
6. Do not build desktop for the v2 launch and do not build offline support for the v2 launch. Both are outside the current launch scope. Do not plan offline support on the v1 sync engine.

## 8. Authoritative spec summary

Team Notes v2 launches on December 15, and that date does not move. The launch is mobile-only, with sign-in via SSO only and no passwords. Desktop is not part of the launch; it is deferred to a later release, whose name and date are not yet specified. Offline support is not part of the launch; it is deferred to release v2.1, whose date is not yet specified, and whether any limited offline behavior is expected at launch is still an open question. No scope may be added to v2 without the product manager's approval.

Change history: the original draft required desktop and mobile at launch and full offline editing at launch. The platform requirement changed to mobile-only because the desktop redesign cannot be finished by December 15 without cutting quality. The offline requirement changed to a v2.1 deferral because prototype testing found unresolvable sync conflicts in about 1 in 20 offline editing sessions on the v1 sync engine, and a proper fix needs a sync rewrite. Authentication and the launch date did not change.
