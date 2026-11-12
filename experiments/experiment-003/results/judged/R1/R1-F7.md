# Continuation Document: Team Notes v2

## 1. Where things stand

The current, authoritative requirements for the v2 launch are:

- Launch date: December 15. This date is fixed by marketing commitments and does not move. It has not changed at any point.
- Platform: mobile-only at launch.
- Offline support: not part of the launch at all. Full offline editing is deferred to v2.1.
- Authentication: sign-in by single sign-on only, with no passwords.

Earlier versions that included desktop at launch or full offline editing at launch are superseded and must not be built to.

## 2. Decisions in force

Decisions that currently govern the spec, with reasons:

- **Launch on December 15, with the date held fixed.** Reason: the date is fixed by marketing commitments.
- **Launch mobile-only, with desktop moved to a later release rather than cancelled.** Reason: engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, so keeping the fixed date required narrowing platform scope.
- **Remove offline support from the launch entirely and move it to v2.1.** Reason: prototype evidence showed offline editing on the old sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions, and a proper fix would need a sync rewrite that cannot land by launch. This recommendation from the engineering lead was agreed with the product manager.
- **Sign-in by single sign-on only, with no passwords.** This has been in force from the original draft through both updates and has not changed.
- **No scope may be added to this version without the product manager's approval.** No scope has been added. Every change so far has narrowed or deferred the launch rather than expanded it.

Decisions or requirements no longer in force:

- Desktop included at launch, as in the original draft. Superseded by the mobile-only decision.
- Full offline editing at launch, as in the original draft. Superseded by the deferral of offline support to v2.1.

## 3. Assumptions and facts

### Facts

- The launch date is December 15 and is fixed by marketing commitments.
- The desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- A note from the engineering lead, reporting on prototype work, found that offline editing built on top of the old sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions.
- Fixing the offline problem properly would need a sync rewrite that cannot land by launch.
- Authentication, the launch date, and the standing constraints were not changed by the product manager's scope message or the engineering lead's note, beyond the specific changes each made.
- No current launch requirement depends on the failed sync engine reuse assumption.

### Assumptions

- **Assumption: the sync engine from the earlier version could be reused for offline support without major changes.** Confidence when first recorded: medium. Status: this assumption did not hold. It turned out not to hold for offline editing, as reported in the engineering lead's note. The original offline requirement rested on this assumption. If it had held, offline editing looked feasible at launch. Because it failed, offline editing was at risk under the fixed date, with no room for a sync rewrite without moving the date or adding unapproved scope, neither of which is allowed.

No other assumptions are stated in the handoff material.

## 4. Constraints

Every standing constraint on the v2 scope:

- The December 15 launch date is fixed and does not move.
- No scope may be added to this version without the product manager's approval.
- Engineering capacity limits the launch: the desktop redesign cannot be completed by December 15 without cutting quality.
- A sync rewrite to fix offline editing cannot land by launch.

Both standing rules from the original draft, the fixed date and the product manager approval rule for added scope, remain in force unchanged.

## 5. What changed and why

**Platform scope**
- Changed from: desktop and mobile at launch, in the original draft.
- Changed to: mobile-only at launch, with desktop moved to a later release rather than cancelled.
- Why: engineering capacity. The desktop redesign cannot be finished by December 15 without cutting quality, and keeping the fixed date meant narrowing platform scope instead of moving the date.
- Authoritative now: mobile-only at launch.
- Source of change: a written scope message from the product manager. The product manager is the approver named in the rule against adding scope without approval, which is why that message was treated as authoritative for scope.

**Offline support**
- Changed from: full offline editing required at launch, in the original draft.
- Changed to: no offline support in the launch, with offline support moved to the following release, v2.1.
- Why: the assumption that the earlier sync engine could be reused without major changes did not hold. Prototype work found unresolvable sync conflicts in about 1 in 20 editing sessions, and a sync rewrite to fix this cannot land by launch.
- Authoritative now: no offline support at launch, deferred to v2.1.
- Source of change: a note from the engineering lead reporting on prototype work, with a recommendation that was agreed with the product manager.

**Requirements that did not change**
- Authentication remains single sign-on only, with no passwords, from the original draft through both updates.
- The launch date and the standing constraints did not change.

## 6. Open questions and missing information

The following are still undecided or unknown in the handoff material. No answers are invented here.

- Desktop timing: which later release desktop will ship in, and on what date. The material gives no date or release name for it.
- v2.1 timing: what the planned date for v2.1 is. No planned date is given.
- Limited offline behavior: whether any limited offline behavior is expected at launch, or whether there will be no offline support at all until v2.1. The material defers offline support as a whole without specifying any partial form, so this remains unclear.

## 7. Next actions

In order:

1. Build to the current launch scope: mobile-only, single sign-on only with no passwords, and no offline support.
2. Hold the December 15 launch date.
3. Seek the product manager's approval before adding any scope.
4. Pursue an answer on when and in which release desktop will ship.
5. Pursue an answer on what the planned date for v2.1 is.
6. Pursue an answer on whether any limited offline behavior is wanted at launch, despite full offline editing having been deferred.

Do not build desktop for the launch and do not build offline support for the launch, as the current scope excludes both.

## 8. Authoritative spec summary

Team Notes v2 launches on December 15, a fixed date set by marketing commitments that does not move. The launch is mobile-only, with sign-in by single sign-on only and no passwords, and with no offline support. No scope may be added without the product manager's approval.

Change history: the original draft included desktop and mobile at launch and required full offline editing. A written scope message from the product manager narrowed the launch to mobile-only for engineering capacity reasons, moving desktop to an unspecified later release. A note from the engineering lead then reported that the assumption that the old sync engine could be reused for offline support had failed, with unresolvable conflicts in about 1 in 20 prototype sessions, so offline support was deferred to v2.1, with agreement from the product manager. Authentication did not change.

Still open: the release and date for desktop, the planned date for v2.1, and whether any limited offline behavior is expected at launch.
