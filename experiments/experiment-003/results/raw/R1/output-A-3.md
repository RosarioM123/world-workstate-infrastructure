# Continuation Document: Team Notes v2 Specification

## 1. Where things stand

The current, authoritative requirements for the Team Notes v2 launch are:

- Platforms (REQ-A, Version 2, authoritative): Launch mobile-only. Desktop moves to a later release.
- Offline support (REQ-B, Version 2, authoritative): Offline support is not part of the v2 launch. It moves to release v2.1.
- Authentication (REQ-C, Version 1, authoritative, unchanged): Sign-in via SSO only. No passwords.
- Launch date (authoritative, unchanged): December 15. The date is fixed by marketing commitments.

Current scope summary: Mobile-only launch on December 15, with sign-in via SSO only. Desktop is deferred to a later release. Offline support is deferred to release v2.1.

Project status in the handoff material is active. The definition of done recorded in the handoff material is that current requirements are stated in report.md, the full revision history is preserved in the state bundle, and open questions are listed for the successor.

## 2. Decisions in force

Decisions that currently govern the spec:

- D2: Launch mobile-only; move desktop to a later release. Status: accepted. Reason: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, and the December 15 date does not move under Constraint C1. Source: E2, scope message from the product manager, in writing. The decision maker named in the source is the PM, who is also the scope approver under Constraint C2.
- D3: Move offline support out of launch scope to release v2.1. Status: accepted. Reason: Prototype evidence in E3 shows offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. A proper fix needs a sync rewrite that cannot land by launch, and the December 15 date does not move under Constraint C1. The assumption that made offline editing feasible at launch, A1, was invalidated by the same evidence. Source: E3, engineering review note from the engineering lead. The source states the recommendation was agreed with the PM, satisfying Constraint C2.
- D4: Keep authentication and launch date unchanged. Status: accepted. Statement: REQ-C remains sign-in via SSO only with no passwords, and the launch date remains December 15. Reason: Neither official update changed authentication or the launch date. Both updates narrowed scope to protect the fixed date rather than moving it. Sources: E1, E2, and E3.

Decisions and requirements that are no longer in force:

- D1: Adopt the original spec draft as the v2 baseline. Status: superseded in part. Its original statement was that Team Notes v2 launches on desktop and mobile on December 15, with full offline editing required at launch and sign-in via SSO only with no passwords. The platform element is superseded by D2. The offline element is superseded by D3. The authentication element and the launch date remain accepted through D2 and D3, as confirmed by D4.
- REQ-A Version 1: Launch on desktop and mobile. Status: superseded by REQ-A Version 2. Source of the superseded version: E1.
- REQ-B Version 1: Full offline editing is required at launch. Status: superseded by REQ-B Version 2. Source of the superseded version: E1.

Do not build to the platform or offline elements of D1, REQ-A Version 1, or REQ-B Version 1.

## 3. Assumptions and facts

Assumptions:

- A1: The v1 sync engine can be reused for offline support without major changes. Confidence as recorded in the original draft: medium. Status: invalidated. It did not hold. E3 states: "The v1 sync engine assumption did not hold for offline editing." Note from the handoff material: Do not plan offline support on the v1 sync engine. E3 states that a proper fix needs a sync rewrite.
- No other assumptions are recorded as active in the handoff material. The bundle states there are no active assumptions.

Facts, kept distinct from assumptions:

- Fact: The launch date is December 15 and is described in E1 as fixed by marketing commitments.
- Fact: The original spec draft in E1 required desktop and mobile, full offline editing at launch, and SSO only with no passwords.
- Fact: The PM scope message in E2 changed the launch to mobile-only and moved desktop to a later release, giving engineering capacity as the reason, and stating that the desktop redesign cannot be finished by December 15 without cutting quality.
- Fact: The engineering review note in E3 reports a prototype finding that offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions.
- Fact: E3 states that a proper fix for the sync conflicts needs a sync rewrite that cannot land by launch.
- Fact: E3 states that its recommendation to move offline support to release v2.1 was agreed with the PM.
- Fact: Neither E2 nor E3 changed authentication or the launch date.

## 4. Constraints

Every standing constraint on the v2 scope recorded in the handoff material:

- C1: The December 15 launch date does not move. Source: E1, original spec draft, where the date is described as fixed by marketing commitments.
- C2: No scope may be added to v2 without the product manager's approval. Source: E1, original spec draft.

Provenance in the handoff material: both constraints were created from E1, and neither constraint was changed by E2 or E3.

## 5. What changed and why

REQ-A, Platforms:

- Changed from: Version 1, launch on desktop and mobile.
- Changed to: Version 2, launch mobile-only. Desktop moves to a later release.
- Why it changed: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- Authoritative version now: Version 2.
- Where the change came from: E2, scope message from the product manager, in writing. Recorded as Decision D2, which supersedes the platform element of D1 and REQ-A Version 1.

REQ-B, Offline support:

- Changed from: Version 1, full offline editing is required at launch.
- Changed to: Version 2, offline support moves out of the launch scope to release v2.1.
- Why it changed: Prototype evidence of unresolvable sync conflicts on the v1 sync engine, in about 1 in 20 editing sessions, and a proper fix needs a sync rewrite that cannot land by launch. The related assumption A1 was invalidated by the same evidence.
- Authoritative version now: Version 2.
- Where the change came from: E3, engineering review note from the engineering lead, including the prototype finding. Recorded as Decision D3, which supersedes the offline element of D1 and REQ-B Version 1. The source states the recommendation was agreed with the PM.

Assumption A1 status change, related to REQ-B:

- Changed from: Active, confidence medium.
- Changed to: Invalidated.
- Why it changed: E3 states the v1 sync engine assumption did not hold for offline editing.
- Where the change came from: E3.

Requirements that did not change:

- REQ-C, Authentication: Version 1 remains authoritative and unchanged. Sign-in via SSO only, no passwords. Source: E1. Neither E2 nor E3 changed it. Confirmed by D4.
- Launch date: December 15 remains authoritative and unchanged. Source: E1. Neither E2 nor E3 changed it. Confirmed by D4.

## 6. Open questions and missing information

The following are still undecided or unknown in the handoff material. They are flagged here. No answers are invented.

- Q1, Desktop release timing: Which release, and on what date, will desktop ship in, following its move to a later release under D2? Status: open. E2 says desktop moves to a later release and gives no release name or date. Missing information: the desktop release name and date.
- Q2, Release v2.1 timing: What is the planned date for release v2.1, which now carries offline support under D3? Status: open. E3 names release v2.1 and gives no date. Missing information: the v2.1 date.
- Q3, Offline behavior at launch: Is any limited offline behavior expected in the v2 launch, or is there no offline support at all until v2.1? Status: open. E3 defers offline support as a whole to v2.1 and does not specify a partial form for launch. Missing information: whether any limited offline behavior is in launch scope. Any addition here would also need PM approval under Constraint C2.

No other open questions are listed in the handoff material.

## 7. Next actions

Concrete next steps for the spec and build, in order, based only on the handoff material:

1. Seek answers to the open questions from the appropriate sources, starting with Q1, Q2, and Q3. Desktop timing and any scope question require the PM under Constraint C2. Do not assume a desktop release name or date, a v2.1 date, or any limited offline behavior at launch until those answers are recorded.
2. Ensure report.md states the current requirements exactly as in Section 1 of this document: REQ-A Version 2, REQ-B Version 2, and REQ-C Version 1, with the December 15 launch date, and preserves the full revision history from the state bundle.
3. Send the authoritative spec summary in Section 8 to the build team, with the explicit warning that desktop at launch and offline editing at launch are out of the v2 launch scope.
4. Plan and build the v2 launch as mobile-only, with SSO-only sign-in and no passwords, for the fixed December 15 date, within Constraints C1 and C2.
5. Do not build desktop for the v2 launch and do not build offline support for the v2 launch. Both are excluded from current launch scope. Desktop is deferred to a later release and offline support is deferred to release v2.1.
6. For release v2.1 planning only, note that offline support cannot be planned on reuse of the v1 sync engine, because A1 is invalidated and E3 states a proper fix needs a sync rewrite. Do not schedule that work for the v2 launch.

## 8. Authoritative spec summary

Team Notes v2 launches mobile-only on December 15, with sign-in via SSO only and no passwords. The December 15 date is fixed by marketing commitments and does not move. No scope may be added to v2 without the product manager's approval.

Desktop is not part of the launch. It is deferred to a later release, whose name and date are not yet specified. Offline support is not part of the launch. It is deferred to release v2.1, whose date is not yet specified, and whether any limited offline behavior is expected at launch is still an open question.

Change history: The original draft required desktop and mobile, full offline editing at launch, and SSO only. The PM then changed the launch to mobile-only because the desktop redesign cannot be finished by December 15 without cutting quality. Engineering evidence then moved offline support to v2.1, because prototype testing on the v1 sync engine produced unresolvable sync conflicts in about 1 in 20 sessions and a proper fix needs a sync rewrite that cannot land by launch. Authentication and the launch date did not change.
