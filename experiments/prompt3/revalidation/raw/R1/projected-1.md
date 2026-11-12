1. **Where things stand:** the current, authoritative requirements for the v2 launch.

- REQ-A version 2 (current, authoritative): Launch mobile-only. Desktop moves to a later release.
- REQ-B version 2 (current, authoritative): Offline support moves out of the launch scope to release v2.1. Offline support is not part of the v2 launch.
- REQ-C version 1 (current, authoritative, unchanged): Sign-in via SSO only; no passwords.
- Launch date (current, authoritative, unchanged): December 15, fixed by marketing commitments.

2. **Decisions in force:** every decision that currently governs the spec, with the reason it was made. Separately list any decisions or requirements that are no longer in force.

Decisions in force:

- D2 [accepted]: The v2 launch is mobile-only. Desktop moves to a later release.
  Reason: Engineering capacity. The desktop app needs a redesign that cannot be finished by December 15 without cutting quality, and the December 15 date does not move (Constraint C1).
- D3 [accepted]: Offline support is not part of the v2 launch. It moves to release v2.1.
  Reason: Prototype evidence (E3) shows offline editing on the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions. A proper fix needs a sync rewrite that cannot land by launch, and the December 15 date does not move (Constraint C1). The assumption that made offline editing feasible at launch (A1) was invalidated by the same evidence.
- D4 [accepted]: REQ-C remains sign-in via SSO only with no passwords, and the launch date remains December 15.
  Reason: Neither official update changed authentication or the launch date. Both updates narrowed scope to protect the fixed date rather than moving it.
- REQ-A2 [accepted]: REQ-A version 2 (current, authoritative): Launch mobile-only. Desktop moves to a later release.
  Reason: Engineering capacity; the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
- REQ-B2 [accepted]: REQ-B version 2 (current, authoritative): Offline support moves out of the launch scope to release v2.1.
  Reason: Prototype evidence of unresolvable sync conflicts on the v1 sync engine, and a proper fix needs a sync rewrite that cannot land by launch.
- REQ-C1 [accepted]: REQ-C version 1 (current, authoritative, unchanged): Sign-in via SSO only; no passwords.
  Reason: Original spec draft (E1). Neither E2 nor E3 changed it.
- REQ-DATE1 [accepted]: Launch date (current, authoritative, unchanged): December 15, fixed by marketing commitments.
  Reason: Original spec draft (E1). Neither E2 nor E3 changed it.

Decisions and requirements no longer in force:

- D1 [superseded]: Team Notes v2 launches on desktop and mobile on December 15, with full offline editing required at launch, as recorded in the original bundle in truncated form. Superseded by D2; D3 states that it supersedes the offline element of D1, and that the original bundle records D1 as superseded in part by D2 and by D3, with the schema recording one successor link per superseded decision (held by D2), so the D3 link is preserved in text.
- REQ-A1 [superseded]: REQ-A version 1: Launch on desktop and mobile. Superseded by REQ-A2.
- REQ-B1 [superseded]: REQ-B version 1: Full offline editing is required at launch. Superseded by REQ-B2.

3. **Assumptions and facts:** the assumptions the spec rests on, labeled as assumptions, with confidence, including any assumption that turned out not to hold. Keep facts distinct from assumptions.

Assumptions:

- A1 [status: invalidated, confidence: medium] - Assumption: The v1 sync engine can be reused for offline support without major changes.
  This assumption turned out not to hold. Evidence E3 states that the v1 sync engine assumption did not hold for offline editing.

No other assumptions are recorded in the handoff material.

Facts:

- The original spec draft (E1) recorded: REQ-A desktop and mobile, REQ-B full offline editing required at launch, REQ-C SSO only with no passwords, and launch date December 15 fixed by marketing commitments.
- E2 records that the desktop app needs a redesign that cannot be finished by December 15 without cutting quality, for reasons of engineering capacity.
- E3 records a prototype finding that offline editing on top of the v1 sync engine produces unresolvable sync conflicts in about 1 in 20 editing sessions.
- E3 records that fixing this properly needs a sync rewrite that cannot land by launch.
- Neither E2 nor E3 changed REQ-C or the launch date.

4. **Constraints:** every standing constraint on the v2 scope.

- C1: The December 15 launch date does not move. Source: E1, original spec draft, where the date is described as fixed by marketing commitments.
- C2: No scope may be added to v2 without the product manager's approval. Source: E1, original spec draft.

5. **What changed and why:** every requirement that changed during the prior session, what it changed from and to, why it changed, which version is authoritative now, and where each change came from.

- REQ-A:
  From: Version 1 - Launch on desktop and mobile.
  To: Version 2 - Launch mobile-only. Desktop moves to a later release.
  Why: Engineering capacity; the desktop app needs a redesign that cannot be finished by December 15 without cutting quality.
  Authoritative now: Version 2 (REQ-A2).
  Source of change: E2, scenario.md, Part 2, Update 1 (source: PM, in writing). Also recorded as decision D2, which supersedes D1.

- REQ-B:
  From: Version 1 - Full offline editing is required at launch.
  To: Version 2 - Offline support moves out of the launch scope to release v2.1.
  Why: Prototype evidence of unresolvable sync conflicts on the v1 sync engine, in about 1 in 20 editing sessions, and a proper fix needs a sync rewrite that cannot land by launch. The assumption A1 that the v1 sync engine could be reused for offline support without major changes was invalidated by the same evidence.
  Authoritative now: Version 2 (REQ-B2).
  Source of change: E3, scenario.md, Part 2, Update 2 (source: engineering lead), with the recommendation agreed with the PM. Also recorded as decision D3.

- REQ-C:
  No change.
  Version 1 remains current and authoritative: Sign-in via SSO only; no passwords.
  Source: E1, original spec draft. Neither E2 nor E3 changed it. Confirmed by D4.

- Launch date:
  No change.
  December 15 remains current and authoritative, fixed by marketing commitments.
  Source: E1, original spec draft. Neither E2 nor E3 changed it. Confirmed by D4.

6. **Open questions and missing information:** what is still undecided or unknown. Flag it; do not invent answers.

- Which release, and on what date, will desktop ship in, following its move to a later release under D2? Unknown from the handoff material.
- What is the planned date for release v2.1, which now carries offline support under D3? Unknown from the handoff material.
- Is any limited offline behavior expected in the v2 launch, or is there no offline support at all until v2.1? Undecided / unknown from the handoff material.
- Next actions: none were recorded in the handoff material, so that information is missing.

7. **Next actions:** the concrete next steps for the spec and build, in order. Do not propose building anything the current scope excludes.

No next actions were recorded in the handoff material. No concrete next steps can be listed from the material provided without inventing them.

8. **Authoritative spec summary:** a short summary (at most about 300 words) of the v2 launch spec as it currently stands, suitable to send to the build team, with a brief change history.

Team Notes v2 launches on December 15, mobile-only. Sign-in is via SSO only, with no passwords. Offline support is not part of the v2 launch.

Change history: The original spec required launch on desktop and mobile with full offline editing. REQ-A changed to mobile-only because the desktop redesign cannot be finished by December 15 without cutting quality; desktop moves to a later release, on a release and date not yet specified in the material. REQ-B changed to move offline support to v2.1 because prototype testing found unresolvable sync conflicts in about 1 in 20 offline editing sessions on the v1 sync engine, and a sync rewrite cannot land by launch. REQ-C and the December 15 date are unchanged. Standing constraints are that the December 15 date does not move and no scope may be added to v2 without the product manager's approval.
