# Continuation Document: Team Notes v2 Specification (R1)

## 1. Where things stand

The current, authoritative requirements for the v2 launch are:

- REQ-A, Platforms, version 2: Launch mobile-only. Desktop moves to a later release.
- REQ-B, Offline support, version 2: Offline support is out of the launch scope. It moves to release v2.1.
- REQ-C, Authentication, version 1: Sign-in via SSO only; no passwords. This requirement is unchanged.
- Launch date: December 15. This date is fixed by marketing commitments and is unchanged.

No scope was added to v2 during the prior session. Both updates removed or deferred scope.

## 2. Decisions in force

Decisions that currently govern the spec:

- REQ-A version 2, mobile-only launch, with desktop moved to a later release. Reason: engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- REQ-B version 2, offline support deferred from launch to release v2.1. Reason: prototype evidence showed offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions, and fixing this properly needs a sync rewrite that cannot land by launch. The recommendation to move offline support to v2.1 was agreed with the product manager (PM).
- REQ-C version 1, SSO only with no passwords. Reason: no reason for this requirement was recorded in the handoff material. It was present in the original spec draft and was not changed by either update.
- Launch date of December 15. Reason: fixed by marketing commitments.

Decisions or requirements that are no longer in force:

- REQ-A version 1: Launch on desktop and mobile. Superseded by REQ-A version 2.
- REQ-B version 1: Full offline editing is required at launch. Superseded by REQ-B version 2.
- Assumption A1 as an active assumption: see Section 3. It was invalidated and no longer holds.

## 3. Assumptions and facts

Assumptions:

- Assumption A1: The sync engine from v1 can be reused for offline support without major changes. Confidence: medium. Status at draft time: active. Current status: invalidated. This assumption turned out not to hold. The handoff material states directly: "The v1 sync engine assumption did not hold for offline editing."

No other assumptions were recorded in the handoff material.

Facts, kept distinct from assumptions:

- A prototype found that offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions.
- Fixing the sync problem properly needs a sync rewrite that cannot land by launch.
- The desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- The December 15 launch date was not changed by either update.
- REQ-C was not changed by either update.

## 4. Constraints

- Constraint 1: The December 15 launch date does not move.
- Constraint 2: No scope may be added to v2 without the product manager's approval.

Final check recorded in the prior session: the December 15 launch date is unchanged, and no scope was added to v2.

## 5. What changed and why

Change 1: REQ-A, Platforms

- From: Version 1, launch on desktop and mobile.
- To: Version 2, launch mobile-only. Desktop moves to a later release.
- Why: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality. Narrowing launch scope kept the fixed launch date intact rather than moving the date.
- Authoritative now: Version 2.
- Source: Part 2, Update 1, from the product manager, in writing. The PM was treated as authoritative for scope because the PM is the approver named in Constraint 2.
- Not changed by this update: REQ-B, REQ-C, and the December 15 launch date.
- Note: Desktop work was recorded as moved to a later release, not cancelled.

Change 2: REQ-B, Offline support, and Assumption A1

- From: Version 1, full offline editing is required at launch.
- To: Version 2, offline support moves out of the launch scope to release v2.1.
- Why: Evidence from a prototype. Offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. A proper fix needs a sync rewrite that cannot land by December 15, and the launch date does not move. The change was evidence driven, not a preference change.
- Authoritative now: Version 2.
- Source: Part 2, Update 2, from the engineering lead. The update recorded that the recommendation to move offline support to v2.1 was agreed with the PM.
- Related change: Assumption A1 changed status from active to invalidated, from the same source, because the v1 sync engine assumption did not hold for offline editing.
- Not changed by this update: REQ-A, REQ-C, and the December 15 launch date.

No other requirements changed during the prior session. REQ-C remained at version 1 throughout.

## 6. Open questions and missing information

The following items could not be resolved from the scenario materials and remain open. No answers are invented here:

- The date or release name for the desktop release is unknown.
- The date for release v2.1 is unknown.
- Whether any limited offline behavior is expected at launch, now that full offline editing is deferred, is unknown.

## 7. Next actions

In order:

1. Resolve the open questions in Section 6 with the appropriate decision makers, including the PM where scope approval is required under Constraint 2: confirm whether any limited offline behavior is expected at launch, and obtain the date or release name for the desktop release and the date for release v2.1 when they are decided.
2. Finalize the spec on the basis of the authoritative requirements in Section 1, preserving the superseded versions and the invalidated assumption in the change history so offline editing on the v1 engine is not re-proposed for launch.
3. Build for the v2 launch to the current scope only: mobile-only, sign-in via SSO only with no passwords, for the fixed December 15 launch date.
4. Plan desktop work for its later release and offline support for release v2.1 as separate later work, once their dates are known. Do not build desktop or full offline editing as part of the v2 launch scope.

## 8. Authoritative spec summary

Team Notes v2 launches on December 15, a date fixed by marketing commitments that does not move. Launch is mobile-only under REQ-A version 2. Sign-in is via SSO only, with no passwords, under REQ-C version 1, which is unchanged from the original draft. Full offline editing is not part of the launch scope; it is deferred to release v2.1 under REQ-B version 2. No scope may be added to v2 without the product manager's approval, and no scope was added during the prior session.

Change history: The original draft required desktop and mobile, full offline editing at launch, and SSO only. Update 1 from the product manager changed REQ-A to mobile-only because the desktop redesign cannot be finished by December 15 without cutting quality; desktop moves to a later release, whose date is not yet known. Update 2 from the engineering lead changed REQ-B because a prototype showed offline editing on the v1 sync engine causes unresolvable conflicts in about 1 in 20 sessions, invalidating Assumption A1 that the v1 sync engine could be reused without major changes. A sync rewrite cannot land by launch, so offline support moves to v2.1, whose date is also not yet known, and whether any limited offline behavior is expected at launch remains an open question.
