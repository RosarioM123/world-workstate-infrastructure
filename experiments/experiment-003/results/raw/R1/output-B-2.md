# Continuation Document: Team Notes v2

## 1. Where things stand

The current, authoritative requirements for the v2 launch are:

- Launch date: December 15. This date is fixed by marketing commitments and does not move. It has not changed at any point in the work so far.
- Platform: mobile-only at launch.
- Offline support: not part of the launch at all.
- Authentication: sign-in by single sign-on only, with no passwords.

This is narrower than the original draft. The earlier versions described in the handoff material are superseded and must not be built to.

## 2. Decisions in force

Decisions that currently govern the spec, with the reason for each:

- **Launch on December 15, date fixed.** Reason: marketing commitments. The date shapes everything else in the spec.
- **No scope may be added to this version without the product manager's approval.** This standing rule remains in force unchanged. No scope has been added.
- **Launch mobile-only; desktop moved to a later release rather than cancelled.** Reason: engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, so keeping the fixed date intact meant narrowing the platform scope instead of moving the date.
- **Move offline support out of the launch scope entirely and into the following release, known as v2.1.** Reason: evidence from prototype work showed offline editing on the old sync engine produces unresolvable sync conflicts, and a proper fix would need a sync rewrite that cannot land by launch. This recommendation was agreed with the product manager.
- **Sign-in via single sign-on only, with no passwords.** This requirement has not changed. No reason for a change is recorded, and neither update touched it.

Decisions or requirements that are no longer in force:

- Desktop included in the launch, as in the original draft covering both desktop and mobile at launch. Superseded by the mobile-only decision.
- Full offline editing required at launch, as in the original draft. Superseded by the deferral of offline support to v2.1.

## 3. Assumptions and facts

### Facts

- The launch date is December 15 and is fixed by marketing commitments.
- No scope has been added to this version. Every change so far has narrowed or deferred the launch rather than expanded it.
- The desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- A note from the engineering lead, reporting on prototype work, found that offline editing built on top of the old sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions.
- Fixing the offline problem properly would need a sync rewrite that cannot land by launch.
- Sign-in has remained single sign-on only, with no passwords, from the original draft through both updates.
- Neither the product manager's scope message nor the engineering lead's note touched authentication, the launch date, or the standing constraints, beyond the specific changes each of them made.

### Assumptions

- **Assumption that the sync engine from the earlier version could be reused for offline support without major changes.** Confidence when first recorded: medium. Status: this assumption did not hold. The engineering lead's note states directly that it did not hold for offline editing. The original offline requirement rested on this assumption. No current launch requirement depends on the failed assumption anymore.

No other assumptions are recorded in the handoff material.

## 4. Constraints

Every standing constraint on the v2 scope recorded in the handoff material:

- The December 15 launch date is fixed and does not move.
- No scope may be added to this version without the product manager's approval.
- Engineering capacity limits the launch scope. The desktop redesign cannot be finished by December 15 without cutting quality.
- A sync rewrite cannot land by launch, so offline support cannot be fixed properly within the launch scope.
- Changes must narrow or hold scope under the constraints above. So far, every change has narrowed or deferred the launch rather than expanded it.

## 5. What changed and why

### Change 1: Platform scope

- **Changed from:** Both desktop and mobile at launch, as in the original draft.
- **Changed to:** Mobile-only at launch. Desktop moved to a later release rather than being cancelled.
- **Why it changed:** Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality. Keeping the fixed date intact meant narrowing the platform scope instead of moving the date.
- **Authoritative version now:** Mobile-only at launch.
- **Where the change came from:** A written scope message from the product manager. The product manager is the approver named in the rule against adding scope without approval, which is why that message was treated as authoritative for scope.

### Change 2: Offline support

- **Changed from:** Full offline editing required at launch, as in the original draft.
- **Changed to:** Offline support is not part of the launch at all. Offline support moved out of the launch scope entirely and into the following release, known as v2.1.
- **Why it changed:** The requirement rested on the assumption, held with medium confidence, that the sync engine from the earlier version could be reused without major changes. That assumption failed. Prototype work found unresolvable sync conflicts in about 1 in 20 editing sessions on the old engine, and a proper fix would need a sync rewrite that cannot land by launch.
- **Authoritative version now:** No offline support at launch; offline support deferred to v2.1.
- **Where the change came from:** A note from the engineering lead reporting on prototype work, with a recommendation that was agreed with the product manager.

### Requirements that did not change

- Authentication: single sign-on only, with no passwords, unchanged from the original draft through both updates.
- Launch date December 15 and both standing rules remain in force unchanged.

## 6. Open questions and missing information

The following are still undecided or unknown. They are flagged here; no answers are invented.

- Which later release desktop will ship in, and on what date. The handoff material gives no date or release name for desktop.
- What the planned date for v2.1 is. No planned date for v2.1 is given.
- Whether any limited offline behavior is expected at launch, or whether there will be no offline support at all until v2.1. The material defers offline support as a whole without specifying any partial form.

## 7. Next actions

In order:

1. Build to the current launch scope only: mobile-only, single sign-on only with no passwords, and no offline support.
2. Hold the December 15 launch date.
3. Seek the product manager's approval before adding any scope.
4. Pursue an answer to when and in which release desktop will ship.
5. Pursue an answer to what the planned date for v2.1 is.
6. Pursue an answer to whether any limited offline behavior is wanted at launch despite full offline editing having been deferred.

Do not build desktop for the launch and do not build offline support for the launch, as the current scope excludes both.

## 8. Authoritative spec summary

Team Notes v2 launches on December 15, a date fixed by marketing commitments that has not changed. The launch is mobile-only, with sign-in by single sign-on only and no passwords, and with no offline support at launch. No scope may be added without the product manager's approval, and no scope has been added.

Change history: The original draft covered desktop and mobile with full offline editing. A written scope message from the product manager made the launch mobile-only for engineering capacity reasons, deferring desktop to a later, unnamed release. Later, an engineering lead note showed the assumed reuse of the old sync engine failed, causing unresolvable conflicts in about 1 in 20 sessions, so offline support was deferred entirely to v2.1, as agreed with the product manager. Authentication did not change.

Open items for the build team: the desktop release and date, the v2.1 date, and whether any limited offline behavior is wanted at launch are all undecided in the handoff material.
