# Continuation Document: Team Notes v2 Specification

## 1. Where things stand

The current, authoritative requirements for the v2 launch are:

- REQ-A, Platforms, version 2: Launch mobile-only. Desktop moves to a later release.
- REQ-B, Offline support, version 2: Offline support moves out of the launch scope to release v2.1. Full offline editing is not required at launch.
- REQ-C, Authentication, version 1: Sign-in via SSO only; no passwords. This requirement is unchanged.
- Launch date: December 15, fixed by marketing commitments. This date is unchanged.

No scope was added to v2 during the prior session. Both changes during that session removed or deferred scope.

## 2. Decisions in force

Decisions that currently govern the spec:

- Launch mobile-only at v2 launch (REQ-A, version 2). Reason: engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- Defer offline support from the v2 launch to release v2.1 (REQ-B, version 2). Reason: prototype evidence showed offline editing on top of the v1 sync engine produces unresolvable sync conflicts, and fixing this properly needs a sync rewrite that cannot land by launch. The recommendation to move offline support to v2.1 was agreed with the product manager.
- Require sign-in via SSO only, with no passwords (REQ-C, version 1). Reason: no reason for a change was recorded in the handoff material, and this requirement was not changed by either update.
- Keep the December 15 launch date fixed. Reason: the date is fixed by marketing commitments and is recorded as a standing constraint.

Decisions or requirements that are no longer in force:

- REQ-A, version 1: Launch on desktop and mobile. Superseded by REQ-A, version 2.
- REQ-B, version 1: Full offline editing is required at launch. Superseded by REQ-B, version 2.

## 3. Assumptions and facts

Assumptions:

- Assumption A1: The sync engine from v1 can be reused for offline support without major changes. Confidence: medium. Status at draft time: active. Current status: invalidated. This assumption turned out not to hold. The handoff material states directly: "The v1 sync engine assumption did not hold for offline editing."
- No other assumptions are recorded in the handoff material.

Facts, kept distinct from assumptions:

- Prototype finding: Offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions.
- Fixing the sync problem properly needs a sync rewrite that cannot land by launch.
- The desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- REQ-C was unchanged through both updates.
- The December 15 launch date was unchanged through both updates.
- No new requirement was introduced during the prior session. Both updates removed or deferred scope.

## 4. Constraints

Every standing constraint on the v2 scope recorded in the handoff material:

- Constraint 1: The December 15 launch date does not move.
- Constraint 2: No scope may be added to v2 without the product manager's approval.

## 5. What changed and why

REQ-A, Platforms:

- Changed from: Version 1, launch on desktop and mobile.
- Changed to: Version 2, launch mobile-only. Desktop moves to a later release.
- Why it changed: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality. Narrowing the launch scope kept the fixed launch date intact.
- Authoritative now: Version 2.
- Source: Part 2, Update 1, a scope message from the product manager, in writing.

REQ-B, Offline support:

- Changed from: Version 1, full offline editing is required at launch.
- Changed to: Version 2, offline support moves out of the launch scope to release v2.1.
- Why it changed: Prototype evidence invalidated Assumption A1. Offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions, and fixing this properly needs a sync rewrite that cannot land by launch. Because the launch date does not move, offline support was deferred.
- Authoritative now: Version 2.
- Source: Part 2, Update 2, a review note from the engineering lead. The recommendation to move offline support to v2.1 was agreed with the product manager.
- Related change: Assumption A1 changed status from active to invalidated under the same update.

REQ-C, Authentication, and the launch date:

- REQ-C did not change. Version 1, SSO only with no passwords, remains authoritative.
- The December 15 launch date did not change.

## 6. Open questions and missing information

The following items are still undecided or unknown in the handoff material. No answers are invented here:

- The date or release name for the desktop release. The handoff material says desktop moves to a later release but gives no date or release name for it.
- The date for release v2.1. The handoff material names release v2.1 for offline support but gives no date for it.
- Whether any limited offline behavior is expected at launch now that full offline editing is deferred. The handoff material does not state whether limited offline behavior is expected.

## 7. Next actions

In order:

1. Resolve the open questions in Section 6 with the product manager, who is the approver named in Constraint 2: the date or release name for the desktop release, the date for release v2.1, and whether any limited offline behavior is expected at launch.
2. Finalise the v2 launch spec using only the authoritative requirements in Section 1, without adding scope without the product manager's approval.
3. Send the authoritative spec summary in Section 8 to the build team.
4. Build the v2 launch scope as specified: a mobile-only launch, with SSO-only sign-in and no passwords, for the December 15 launch date. Do not build desktop for the v2 launch and do not build full offline editing for the v2 launch, because the current scope excludes both from launch.

## 8. Authoritative spec summary

Team Notes v2 launches on December 15, and that date does not move. The launch is mobile-only. Desktop moves to a later release, whose date and release name are not stated in the handoff material. Sign-in is via SSO only, with no passwords. Full offline editing is not part of the launch scope. Offline support moves to release v2.1, whose date is not stated, and whether any limited offline behavior is expected at launch is still an open question. No scope may be added to v2 without the product manager's approval.

Brief change history: The original draft required desktop and mobile at launch and full offline editing at launch. Update 1 from the product manager changed platforms to mobile-only because the desktop redesign cannot be finished by December 15 without cutting quality. Update 2 from the engineering lead deferred offline support to v2.1 because prototype testing found unresolvable sync conflicts in about 1 in 20 offline editing sessions on the v1 sync engine, invalidating the assumption that that engine could be reused without major changes. Authentication did not change.
