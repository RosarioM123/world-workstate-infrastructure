# Team Notes v2: Specification Summary

Status: Current as at the end of the R1 work session. Only the requirements in the Current Requirements section below are authoritative. Superseded versions appear only in the Change History section and must not be built to.

## Product

Team Notes v2, a shared note-taking app.

## Current Requirements

### REQ-A: Platforms (version 2, current)

- Launch mobile-only.
- Desktop is not part of the v2 launch. Desktop moves to a later release.

### REQ-B: Offline support (version 2, current)

- Offline support is not part of the v2 launch scope.
- Offline support moves to release v2.1.

### REQ-C: Authentication (version 1, current and unchanged)

- Sign-in via SSO only.
- No passwords.

### Launch date (current and unchanged)

- Launch date: December 15.
- The date is fixed by marketing commitments and does not move.

## Standing Constraints

- Constraint 1: The December 15 launch date does not move.
- Constraint 2: No scope may be added to v2 without the product manager's approval.

## Key Assumption Status

- Assumption A1, that the sync engine from v1 could be reused for offline support without major changes (confidence at draft time: medium), is invalidated. See Change History, item 2. No current launch requirement depends on A1.

## Change History

This section preserves every superseded version, what it changed to, why it changed, and where the change came from.

### Change 1: REQ-A, Platforms

- Version 1 (superseded): Launch on desktop and mobile.
- Source of version 1: Part 1 of the scenario materials, the original spec draft.
- Version 2 (current): Launch mobile-only. Desktop moves to a later release.
- Source of the change: Part 2, Update 1, a scope message from the product manager (PM), in writing.
- Reason for the change: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- Effect on other items: Launch date unchanged. No other requirement changed by this update.

### Change 2: REQ-B, Offline support, and Assumption A1

- Version 1 (superseded): Full offline editing is required at launch.
- Source of version 1: Part 1 of the scenario materials, the original spec draft.
- Version 2 (current): Offline support moves out of the launch scope to release v2.1.
- Source of the change: Part 2, Update 2, an engineering review note from the engineering lead. The recommendation in the note was agreed with the PM.
- Reason for the change: A prototype found that offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. Fixing this properly needs a sync rewrite that cannot land by launch.
- Related assumption change: Assumption A1 (the sync engine from v1 can be reused for offline support without major changes, confidence: medium) changed status from active to invalidated. The engineering review note states that the v1 sync engine assumption did not hold for offline editing.
- Effect on other items: Launch date unchanged. No other requirement changed by this update.

### Items with no changes

- REQ-C, Authentication: Version 1 remains current. Sign-in via SSO only; no passwords. Neither update changed it.
- Launch date: December 15 remains current and fixed. Neither update changed it.
- Standing constraints: Both constraints from the original draft remain in force unchanged.

## Deferred Scope Summary

- Desktop: deferred from the v2 launch to a later release (Update 1, PM). No later release date or name is given in the materials.
- Offline support: deferred from the v2 launch to release v2.1 (Update 2, engineering lead, agreed with the PM).

## Open Questions

- Q1: Which release, and on what date, will desktop ship in, following its move to a later release?
- Q2: What is the planned date for release v2.1, which now carries offline support?
- Q3: Is any limited offline behavior expected in the v2 launch, or is there no offline support at all until v2.1? The materials defer offline support as a whole and do not specify a partial form for launch.
