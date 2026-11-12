# WORLD State Bundle: Task C1, Two-day team offsite planning

Format: follows docs/state-model.md (Project, Decision, Assumption,
Evidence, Question, StateChange, Handoff).
Project id: C1
Produced by: Agent A, Experiment 003 session for task C1.
Sources: brief.md and scenario.md for task C1 only. No other materials used.

## Project context

- id: C1
- name: Two-day team offsite planning
- goal: Plan a two-day offsite workshop for a 14-person team and reach a position where a final booking can be made, subject to the hard constraints below.
- scope: Evaluate the single shortlisted venue, Riverside Hall, against the constraints; gather all cost figures that exist; identify missing and conflicting information that blocks a final booking.
- status: active

Constraints (all hard, from scenario.md):

- C1-CON-1: Budget cap of $6,000 total for the whole offsite.
- C1-CON-2: Venue must be within 45 minutes travel of the office.
- C1-CON-3: Venue must have step-free access, because one attendee uses a wheelchair.
- C1-CON-4: No alcohol at team events, per team policy.
- C1-CON-5: Dates are fixed: two specific consecutive days already announced to the team.
- C1-CON-6: Group size is 14 people. Two of the 14 have not yet confirmed attendance.

Definition of done for this planning stage: venue suitability confirmed for the full group, total cost calculated from actual figures and checked against the $6,000 cap, and no unresolved conflict or missing price blocking the booking. This definition is not yet met.

Provenance: created_by Agent A (Experiment 003, task C1 session), source scenario.md requirements section.

## Decisions

### D1
- id: D1
- project_id: C1
- statement: Evaluate Riverside Hall as the venue for this offsite, as it is the only shortlisted venue in the materials.
- rationale: No other venue option is given in the materials, so no inter-venue comparison is possible in this session. Riverside Hall meets the travel and step-free access constraints on the evidence given.
- status: proposed
- evidence_ids: [E1, E2, E3]
- Note: D1 is proposed, not accepted, because capacity and catering price remain unresolved. See D2.

### D2
- id: D2
- project_id: C1
- statement: Do not make a final booking until the catering price is received and the room capacity conflict is resolved.
- rationale: Without a catering price the total cost cannot be calculated or checked against the $6,000 cap. Without a resolved capacity the venue cannot be confirmed as suitable for 14 people, because one source says 12 and the other says 16.
- status: accepted
- evidence_ids: [E4, E5, E6]

### D3
- id: D3
- project_id: C1
- statement: Record both capacity figures, 12 from the venue email and 16 from the venue brochure, and treat the conflict as unresolved. Do not select either figure as correct.
- rationale: The two sources disagree and scenario.md states the conflict has not been resolved. Selecting one figure without clarification from the venue would risk booking a room that is too small for 14 people, or rejecting a venue that is in fact large enough.
- status: accepted
- evidence_ids: [E4, E5]

### D4
- id: D4
- project_id: C1
- statement: Record the catering price as missing, with no figure, and base the budget picture only on the figures that exist.
- rationale: No catering price appears anywhere in the provided materials, and the venue contact said pricing would be sent later and it has not arrived. Inventing or estimating a figure would make the budget total unreliable.
- status: accepted
- evidence_ids: [E6, E7, E8, E9]

### D5
- id: D5
- project_id: C1
- statement: Report the known cost subtotal as $2,870, made up of $2,400 venue rental plus $350 AV equipment plus $120 printed materials, and report it explicitly as a subtotal and not as the total cost.
- rationale: These are the only cost figures that exist in the materials. The subtotal is $3,130 below the $6,000 cap, but final cap compliance cannot be confirmed while catering is unpriced.
- status: accepted
- evidence_ids: [E1, E7, E8, E9]

### D6
- id: D6
- project_id: C1
- statement: Plan on the basis of a group of 14 people, despite two attendees being unconfirmed.
- rationale: The materials give the group size as 14. The two unconfirmed attendees may still attend, and room capacity and catering must be planned for the full group until attendance is settled.
- status: accepted
- evidence_ids: [E10]

Provenance for all decisions: created_by Agent A (Experiment 003, task C1 session), source scenario.md and the checks recorded in journal.md.

## Assumptions

### A1
- id: A1
- project_id: C1
- statement: The venue rental quote of $2,400 covers the full two days of the offsite, as stated in the venue email summary.
- confidence: high
- status: active
- Basis: scenario.md states the quote as $2,400 for two days. Not yet validated against a booking document for the fixed dates.

### A2
- id: A2
- project_id: C1
- statement: The AV equipment figure of $350 flat and the printed materials estimate of $120 are the applicable figures for this offsite, with no variation.
- confidence: medium
- status: active
- Basis: both figures are given in scenario.md. The printed materials figure is described as an estimate, so it may change. The AV figure is described as flat.

### A3
- id: A3
- project_id: C1
- statement: The travel time of 30 minutes and the step-free access confirmation for Riverside Hall, as reported in the materials, are accurate for the planned visit.
- confidence: medium
- status: active
- Basis: travel time is given in scenario.md and step-free access is reported as confirmed in the venue email. Neither has been independently verified in this session.

### A4
- id: A4
- project_id: C1
- statement: The two unconfirmed attendees are counted in planning numbers until they confirm or decline.
- confidence: medium
- status: active
- Basis: linked to decision D6. This assumption is invalidated if either attendee declines.

### A5
- id: A5
- project_id: C1
- statement: No cost categories beyond venue rental, catering, AV equipment, and printed materials will be needed, based only on the fact that no other costs are given in the materials.
- confidence: low
- status: active
- Basis: scenario.md states no other costs are given. That is an absence of information, not a confirmation that no other costs will arise, so confidence is low.

Note: no assumption has been made about the catering price, and no assumption has been made about which capacity figure is correct. Those items are recorded as open questions, not assumptions.

Provenance for all assumptions: created_by Agent A (Experiment 003, task C1 session), source scenario.md.

## Evidence

### E1
- id: E1
- project_id: C1
- kind: source
- reference: scenario.md, venue option section (venue email summary)
- summary: Riverside Hall rental quote is $2,400 for two days.
- provenance: figure reported in scenario.md as coming from the venue email. Captured by Agent A in this session.

### E2
- id: E2
- project_id: C1
- kind: source
- reference: scenario.md, venue option section
- summary: Travel time from the office to Riverside Hall is 30 minutes.
- provenance: figure given in scenario.md. Captured by Agent A in this session.

### E3
- id: E3
- project_id: C1
- kind: source
- reference: scenario.md, venue option section (venue email summary)
- summary: Step-free access at Riverside Hall is confirmed.
- provenance: reported in scenario.md as confirmed in the venue email. Captured by Agent A in this session.

### E4
- id: E4
- project_id: C1
- kind: source
- reference: scenario.md, venue option section (venue email)
- summary: The venue email says the main room at Riverside Hall holds 12 people.
- provenance: figure reported in scenario.md as coming from the venue email. Captured by Agent A in this session.

### E5
- id: E5
- project_id: C1
- kind: source
- reference: scenario.md, venue option section (venue brochure)
- summary: The venue brochure says the main room at Riverside Hall holds 16 people.
- provenance: figure reported in scenario.md as coming from the venue brochure. Captured by Agent A in this session.
- Conflict note: E4 and E5 conflict. Both are retained. The conflict is unresolved; see Q2.

### E6
- id: E6
- project_id: C1
- kind: source
- reference: scenario.md, venue option section (catering)
- summary: The venue offers catering, but no catering price appears anywhere in the provided materials. The venue contact said pricing would be "sent later" and it has not arrived.
- provenance: statement given in scenario.md. Captured by Agent A in this session.
- Note: this evidence records an absence. There is no catering figure to cite.

### E7
- id: E7
- project_id: C1
- kind: source
- reference: scenario.md, other given figures
- summary: AV equipment rental from an outside supplier is $350 flat.
- provenance: figure given in scenario.md. Captured by Agent A in this session.

### E8
- id: E8
- project_id: C1
- kind: source
- reference: scenario.md, other given figures
- summary: Printed materials estimate is $120.
- provenance: figure given in scenario.md and described there as an estimate. Captured by Agent A in this session.

### E9
- id: E9
- project_id: C1
- kind: source
- reference: scenario.md, requirements section and other given figures
- summary: Budget cap is $6,000 total for the whole offsite, and no costs other than venue rental, AV equipment, and printed materials are given in the materials, apart from catering which is offered but unpriced.
- provenance: cap and scope of given figures as stated in scenario.md. Captured by Agent A in this session.

### E10
- id: E10
- project_id: C1
- kind: source
- reference: scenario.md, requirements section
- summary: Group size is 14 people, and two of the 14 have not yet confirmed their attendance.
- provenance: figures given in scenario.md. Captured by Agent A in this session.

### E11
- id: E11
- project_id: C1
- kind: source
- reference: scenario.md, requirements section
- summary: Hard constraints are: budget cap $6,000, venue within 45 minutes travel, step-free access required, no alcohol at team events, and dates fixed as two specific consecutive days already announced to the team.
- provenance: constraints as stated in scenario.md. Captured by Agent A in this session. The actual calendar dates are not stated in the materials.

## Questions (open)

### Q1: Catering price
- id: Q1
- project_id: C1
- question: What is the catering price for this offsite? The venue contact said pricing would be sent later and it has not arrived, and no catering price appears in the materials.
- status: open
- blocks: final budget total, budget cap check, and final booking (decision D2)
- provenance: created_by Agent A, source E6

### Q2: Capacity conflict
- id: Q2
- project_id: C1
- question: What is the correct capacity of the main room at Riverside Hall for this booking: 12 people as stated in the venue email, or 16 people as stated in the venue brochure?
- status: open
- blocks: confirmation that the venue is suitable for a group of 14, and final booking (decision D2)
- provenance: created_by Agent A, source E4 and E5

### Q3: Attendance confirmations
- id: Q3
- project_id: C1
- question: Will the two attendees who have not yet confirmed attend, so that the final group size is confirmed as 14 or revised?
- status: open
- blocks: final room and catering numbers
- provenance: created_by Agent A, source E10

### Q4: Availability for the fixed dates
- id: Q4
- project_id: C1
- question: Is Riverside Hall available on the two specific consecutive days that are fixed and already announced to the team? The actual dates and venue availability are not stated in the materials provided for this session.
- status: open
- blocks: final booking
- provenance: created_by Agent A, source E11

### Q5: No alcohol confirmation for catering
- id: Q5
- project_id: C1
- question: Will the catering and any drinks arrangement comply with the team policy of no alcohol at team events? The materials do not describe a catering menu or drinks arrangement.
- status: open
- blocks: catering arrangement sign-off
- provenance: created_by Agent A, source E11

### Q6: Other costs
- id: Q6
- project_id: C1
- question: Are there any costs beyond venue rental, catering, AV equipment, and printed materials? The materials state that no other costs are given, which does not confirm that none will arise.
- status: open
- blocks: final budget confirmation
- provenance: created_by Agent A, source E9 and assumption A5

## StateChange log

- seq 1: Project C1 created, change created, actor Agent A, session Experiment 003 task C1. After: project context, constraints C1-CON-1 to C1-CON-6, and status active recorded from scenario.md.
- seq 2: Evidence E1 to E11 created, change created, actor Agent A. After: all figures and constraints from the materials recorded with provenance, including both conflicting capacity figures (E4, E5) and the recorded absence of a catering price (E6).
- seq 3: Decisions D1 to D6 created, change created, actor Agent A. After: D1 proposed, D2 to D6 accepted. No final booking decision created.
- seq 4: Assumptions A1 to A5 created, change created, actor Agent A. After: assumptions recorded with confidence and active status. No assumption created for catering price or for capacity.
- seq 5: Questions Q1 to Q6 created, change created, actor Agent A. After: open questions recorded, with Q1 (catering price) and Q2 (capacity conflict) marked as blocking a final booking.
- seq 6: Artifacts journal.md and report.md for task C1 created, change created, actor Agent A. Reason: session work products recording the checks, gaps, and conflicts found.

No entity was superseded or reversed in this session. No figure was changed after being recorded.

## Handoff

For the next participant continuing task C1:

Context snapshot: Planning a two-day offsite for 14 people (12 confirmed, 2 unconfirmed) under a $6,000 total cap. Riverside Hall is the only shortlisted venue. It is 30 minutes from the office and step-free access is confirmed in the venue email. Dates are fixed and already announced, but the actual dates are not in the materials for this session.

Start here, in this order:

1. Q1, catering price: obtain the price the venue contact said would be sent later. Without it there is no total cost and no final cap check. Do not substitute an estimate.
2. Q2, capacity conflict: get the venue to clarify in writing whether the main room holds 12 (venue email) or 16 (venue brochure). The group is 14, so this decides suitability.

Accepted decisions to respect: D2 (no final booking until Q1 and Q2 are resolved), D3 (record both capacity figures, choose neither), D4 (catering price is missing, not zero), D5 (known subtotal is $2,870 and is not the total), D6 (plan for 14 people). D1 (use Riverside Hall) is proposed only, pending Q1 and Q2.

Active assumptions to recheck: A1 (rental covers two days, high confidence), A2 (AV $350 flat and printed materials $120 estimate, medium), A3 (travel and access figures as reported, medium), A4 (unconfirmed attendees counted in, medium), A5 (no other costs, low confidence).

Key evidence: E1 rental $2,400 for two days (venue email), E4 capacity 12 (venue email), E5 capacity 16 (venue brochure), E6 catering offered with no price in the materials, E7 AV $350 flat, E8 printed materials $120 estimate, E9 cap $6,000, E10 group 14 with two unconfirmed.

Budget reminder: known subtotal is $2,870, which is $3,130 below the cap, before catering. Do not present $2,870 as the total cost.

Remaining open questions: Q3 attendance confirmations, Q4 venue availability for the fixed dates, Q5 no alcohol confirmation for catering, Q6 whether any other costs exist.

Artifacts from this session: artifacts/C1/journal.md (chronological work journal), artifacts/C1/report.md (planning report as it stands), artifacts/C1/state.md (this bundle).
