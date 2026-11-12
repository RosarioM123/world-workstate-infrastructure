# Continuation Document: Team Notes v2 Specification (R1)

## 1. Where things stand

The current, authoritative requirements for the v2 launch are:

- Launch date: December 15. This date is fixed.
- REQ-A, Platforms, version 2: Launch mobile-only. Desktop moves to a later release.
- REQ-B, Offline support, version 2: Offline support is out of the launch scope. It moves to release v2.1.
- REQ-C, Authentication, version 1: Sign-in via SSO only; no passwords.

No other requirements for the v2 launch are recorded in the handoff material.

## 2. Decisions in force

Decisions that currently govern the spec:

- Launch on December 15. Reason: The date is fixed by marketing commitments, recorded in the original spec draft.
- REQ-A version 2, launch mobile-only, with desktop moved to a later release. Reason: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- REQ-B version 2, offline support moved out of launch scope to release v2.1. Reason: Evidence from a prototype showed offline editing on the v1 sync engine produces unresolvable sync conflicts, and a proper fix needs a sync rewrite that cannot land by launch. The recommendation to move offline support to v2.1 was agreed with the product manager.
- REQ-C version 1, sign-in via SSO only with no passwords. Reason: No reason for this requirement is stated in the handoff material. It was present in the original spec draft and was not changed by either update.

Decisions or requirements that are no longer in force:

- REQ-A version 1: Launch on desktop and mobile. Superseded by REQ-A version 2.
- REQ-B version 1: Full offline editing is required at launch. Superseded by REQ-B version 2.

## 3. Assumptions and facts

Assumptions:

- Assumption A1: The sync engine from v1 can be reused for offline support without major changes. Confidence: medium. Status: invalidated. This assumption did not hold. The engineering review note states directly: "The v1 sync engine assumption did not hold for offline editing."
- No other assumptions are recorded in the handoff material.

Facts, distinct from assumptions:

- Prototype finding: Offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions.
- Fixing the offline sync problem properly needs a sync rewrite that cannot land by launch.
- The desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- Both updates in the prior session removed or deferred scope. No new requirement was added to v2, and the December 15 date did not change in either update.

## 4. Constraints

- Constraint 1: The December 15 launch date does not move.
- Constraint 2: No scope may be added to v2 without the product manager's approval.

These are the only standing constraints recorded in the handoff material.

## 5. What changed and why

REQ-A, Platforms:

- Changed from: Version 1, launch on desktop and mobile.
- Changed to: Version 2, launch mobile-only. Desktop moves to a later release.
- Why it changed: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality. Narrowing scope kept the fixed launch date intact.
- Authoritative version now: Version 2.
- Source of the change: Part 2, Update 1, a scope message from the product manager, in writing.

REQ-B, Offline support:

- Changed from: Version 1, full offline editing is required at launch.
- Changed to: Version 2, offline support moves out of the launch scope to release v2.1.
- Why it changed: Prototype evidence invalidated Assumption A1. Offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions, and a proper fix needs a sync rewrite that cannot land by December 15. With the launch date fixed, deferral was the option recorded as consistent with the constraints. The recommendation was agreed with the product manager.
- Authoritative version now: Version 2.
- Source of the change: Part 2, Update 2, an engineering review note from the engineering lead.

Assumption A1:

- Changed from: Active at draft time.
- Changed to: Invalidated.
- Why it changed: The prototype finding in Update 2 showed the v1 sync engine could not support offline editing as assumed.
- Authoritative status now: Invalidated.
- Source of the change: Part 2, Update 2, from the engineering lead.

No change:

- REQ-C, Authentication, remained at version 1 through both updates.
- The December 15 launch date remained unchanged through both updates.

## 6. Open questions and missing information

The following items are undecided or unknown in the handoff material. No answers are recorded, and none are invented here:

- The date or release name for the desktop release. The material says desktop moves to a later release, but gives no date or release name.
- The date for release v2.1, to which offline support moves.
- Whether any limited offline behavior is expected at launch now that full offline editing is deferred.

## 7. Next actions

In order:

1. Ask the product manager to resolve the open questions in Section 6: the desktop release date or release name, the date for release v2.1, and whether any limited offline behavior is expected at launch. Do not add any resulting scope to v2 without the product manager's approval, per Constraint 2.
2. Confirm the spec as authoritative on the basis in Section 1: mobile-only launch on December 15, SSO only with no passwords, and no offline support at launch.
3. Direct the build for the v2 launch to that scope only: mobile, with SSO sign-in. Do not build desktop for the v2 launch, and do not build offline editing for the v2 launch, because the current scope excludes both.
4. Keep REQ-A version 1, REQ-B version 1, and invalidated Assumption A1 visible in the record as superseded or invalidated, so the reasons for the narrowed launch scope are not lost.
5. Plan the deferred work separately from the v2 launch, for desktop in its later release and for offline support in release v2.1, once the product manager provides dates for those releases.

## 8. Authoritative spec summary

Team Notes v2 launches on December 15, a date fixed by marketing commitments that does not move. The launch is mobile-only. Sign-in is via SSO only, with no passwords. Offline support is not in the launch scope.

Change history: The original draft required launch on desktop and mobile, full offline editing at launch, and SSO only. Update 1 from the product manager changed platforms to mobile-only because the desktop redesign cannot be finished by December 15 without cutting quality, and desktop moved to a later release. Update 2 from the engineering lead moved offline support to release v2.1 because prototype testing found unresolvable sync conflicts in about 1 in 20 offline editing sessions on the v1 sync engine, invalidating the assumption that that engine could be reused without major changes, and a sync rewrite cannot land by launch. That move was agreed with the product manager. Authentication did not change. No scope was added to v2. Still unknown are the desktop release date, the v2.1 date, and whether any limited offline behavior is expected at launch.
