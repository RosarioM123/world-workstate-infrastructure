# R1 scenario materials

## Part 1: original spec draft (v1 of the spec)

Product: Team Notes v2, a shared note-taking app.
Requirements as originally drafted:
- REQ-A Platforms: launch on desktop and mobile.
- REQ-B Offline support: full offline editing is required at launch.
- REQ-C Authentication: sign-in via SSO only; no passwords.
- Launch date: December 15 (fixed by marketing commitments).
Standing constraints:
- The December 15 launch date does not move.
- No scope may be added to v2 without the product manager's approval.
Assumption recorded in the draft: the sync engine from v1 can be reused
for offline support without major changes (confidence: medium).

## Part 2: official updates

### Update 1: product manager's scope message (source: PM, in writing)
"Scope change for v2 launch: we launch mobile-only. Desktop moves to a
later release. Reason: engineering capacity; the desktop app needs a
redesign we cannot finish by December 15 without cutting quality."

### Update 2: engineering review note (source: engineering lead)
"Prototype finding: offline editing on top of the v1 sync engine produces
unresolvable sync conflicts in about 1 in 20 editing sessions. Fixing this
properly needs a sync rewrite we cannot land by launch. Recommendation,
agreed with the PM: offline support moves out of the launch scope to
release v2.1. The v1 sync engine assumption did not hold for offline
editing."
