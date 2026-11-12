# Continuation Document: Team Notes v2

## 1. Where things stand

Team Notes v2 is a shared note-taking app. The current, authoritative requirements for the v2 launch are:

- Launch date: December 15. This date is fixed by marketing commitments and does not move. It has not changed at any point in the work so far.
- Platform: mobile-only at launch.
- Offline support: not part of the launch at all. Full offline editing has been deferred out of the launch scope and into the following release, known as v2.1.
- Sign-in: single sign-on only, with no passwords.

This launch scope is considerably narrower than the original draft. The earlier versions described in section 5 are superseded and must not be built to.

## 2. Decisions in force

Decisions that currently govern the spec:

- **Launch on December 15, with the date held fixed.** Reason: the date is fixed by marketing commitments.
- **Launch mobile-only, and move desktop to a later release rather than cancelling it.** Reason: engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, so keeping the fixed date intact meant narrowing the platform scope instead of moving the date.
- **Move offline support out of the launch scope entirely and into v2.1.** Reason: evidence from prototype work showed offline editing on the old sync engine produces unresolvable sync conflicts, and fixing the problem properly would need a sync rewrite that cannot land by launch. This recommendation from the engineering lead was agreed with the product manager.
- **Sign-in by single sign-on only, with no passwords.** Reason: no reason for a change is recorded in the handoff material. This requirement has not changed from the original draft through both updates.

Decisions or requirements that are no longer in force:

- Launch covering both desktop and mobile. Superseded by the mobile-only launch decision.
- Full offline editing at launch. Superseded by the decision to defer offline support to v2.1.

## 3. Assumptions and facts

Assumptions:

- **Assumption that did not hold:** the sync engine from the earlier version could be reused for offline support without major changes. Confidence when first recorded: medium. This assumption turned out not to hold. The engineering lead's note states directly that the assumption did not hold for offline editing. The original offline requirement rested on this assumption, and no current launch requirement depends on it anymore.

No other assumptions are recorded in the handoff material.

Facts, kept distinct from assumptions:

- The launch date of December 15 is fixed by marketing commitments and has not changed.
- The desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- Prototype work found that offline editing built on top of the old sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions.
- Fixing the offline problem properly would need a sync rewrite that cannot land by launch.
- No scope has been added so far. Every change so far has narrowed or deferred the launch rather than expanded it.
- Neither the product manager's scope message nor the engineering lead's note changed the authentication requirement, the launch date, or the standing constraints, beyond the specific changes each of them made.

## 4. Constraints

Every standing constraint on the v2 scope:

- The December 15 launch date is fixed and does not move.
- No scope may be added to this version without the product manager's approval.
- Both standing rules above come from the original draft and remain in force unchanged.

## 5. What changed and why

**Platform scope**

- Changed from: launch covering both desktop and mobile, in the original draft.
- Changed to: mobile-only at launch, with desktop moved to a later release rather than cancelled.
- Why it changed: engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, so keeping the fixed date intact meant narrowing the platform scope instead of moving the date.
- Authoritative version now: mobile-only at launch.
- Source of the change: a written scope message from the product manager. The product manager is the approver named in the rule against adding scope without approval, which is why that message was treated as authoritative for scope.

**Offline support**

- Changed from: full offline editing required at launch, in the original draft.
- Changed to: offline support removed from the launch scope entirely and moved into the following release, known as v2.1.
- Why it changed: the assumption that the sync engine from the earlier version could be reused without major changes failed. Prototype work found unresolvable sync conflicts in about 1 in 20 editing sessions on the old engine, and a proper fix would need a sync rewrite that cannot land by launch.
- Authoritative version now: no offline support at launch; offline support is in v2.1.
- Source of the change: a note from the engineering lead reporting on prototype work, with a recommendation that was agreed with the product manager.

No other requirements are recorded as having changed. Authentication, the launch date, and the standing constraints did not change.

## 6. Open questions and missing information

The following are still undecided or unknown. They are flagged here, not answered:

- Which later release desktop will ship in, and on what date. The handoff material gives no date or release name for the desktop release.
- What the planned date for v2.1 is. No planned date for v2.1 is given.
- Whether any limited offline behavior is expected at launch. The material defers offline support as a whole without specifying any partial form, so it is unclear whether any limited offline behavior is expected at launch or whether there will be no offline support at all until v2.1.

## 7. Next actions

In order:

1. Build to the current mobile-only launch, with single sign-on only and no offline support.
2. Hold the December 15 launch date.
3. Seek the product manager's approval before adding any scope.
4. Pursue an answer to when and in which release desktop will ship.
5. Pursue an answer to what the planned date for v2.1 is.
6. Pursue an answer to whether any limited offline behavior is wanted at launch, despite full offline editing having been deferred.

No step above proposes building desktop or offline support for this launch, since the current scope excludes both.

## 8. Authoritative spec summary

Team Notes v2 launches on December 15, a date fixed by marketing commitments that does not move. The launch is mobile-only, with sign-in by single sign-on only and no passwords, and with no offline support. No scope may be added without the product manager's approval.

Change history: the original draft covered desktop and mobile with full offline editing at launch. A written scope message from the product manager then made the launch mobile-only for engineering capacity reasons, deferring desktop to a later, unnamed release. Later, an engineering lead note reported that offline editing on the old sync engine caused unresolvable conflicts in about 1 in 20 sessions, disproving the assumption that the engine could be reused. Offline support was therefore deferred to v2.1, with the product manager's agreement. Authentication never changed. Open items are the desktop release and date, the v2.1 date, and whether any limited offline behavior is wanted at launch.
