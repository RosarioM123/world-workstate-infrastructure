# Revalidation Mapping Notes

How each task's preserved Agent A production
(`experiments/experiment-003/artifacts/{task}/state.md`) was loaded
into the new `AgentState` schema for the Prompt 3 revalidation. The
mapped states are in `mapped/{task}.json`; `build_bundles.py` saves
them through `save_state` (so the F1 validation ran on real data) and
renders both bundle types with one renderer.

General rules:

- The bundle's Decisions section maps to `Decision` items with the
  bundle's ids, statements as `text`, rationales, statuses, evidence
  links, and supersession links.
- Assumptions map with the bundle's confidence and status. Evidence
  maps with the bundle's own ids (in R1, bundle E1 is the original
  draft while ground truth E1 is the PM scope message; graders grade
  provenance in substance, as they did in #003).
- Open questions map to `open_questions` strings.
- Constraints have no `AgentState` section (a pre-existing schema
  gap; the approved F1 scope did not add one). They are stored as a
  sibling `constraints` key in the world document, which `save_state`
  preserves, and rendered identically in both bundle types.

Per-task notes and frictions found (these are findings, reported in
RESULTS.md):

1. R1 requirements: the bundle keeps Requirements (REQ-A, REQ-B,
   REQ-C, launch date) as a list separate from Decisions. AgentState
   has only decisions, so requirements are mapped as decisions with
   `REQ-` ids and their own supersession chains (REQ-A1 to REQ-A2,
   REQ-B1 to REQ-B2). This preserves the graded revision chains
   RC1 and RC2 as first-class revision structure.
2. R1 partial supersession friction: the bundle marks D1
   "superseded (in part)", superseded by D2 (platform element) and
   D3 (offline element). The approved F1 validation admits exactly
   one successor per superseded decision, so D2 holds the recorded
   link and D3's supersession of D1's offline element is preserved
   in D3's rationale text. Multi-successor partial supersession is
   not representable in the approved rules.
3. R2 reversed-with-successor: D-01 is marked reversed and D-02
   supersedes it. The first implementation of `validate_state`
   additionally required a supersession target to be marked
   "superseded", which rejects R2's graph. That requirement was not
   in the approved spec (audit section G requires only that the
   target exists and that superseded decisions have exactly one
   successor); validation was aligned to the spec and the R2 shape
   is pinned by a test.
4. Assumption supersession has no field: R2's A-02 supersedes A-01,
   but the approved `Assumption` schema has no `supersedes`. The
   relationship is carried by the statuses (A-01 invalidated, A-02
   active) and A-02's text and `validated_by` link.
5. Invalidation provenance has no field: `Assumption` has
   `validated_by` only. That R1's A1 was invalidated by E3 (and
   R2's A-01 by E-02) is carried in the evidence claims and decision
   rationales, not in a structured link.
6. Next actions: C1's bundle has no Next actions section; its two
   start-here items in the Handoff section are mapped as
   `next_actions`. R1 and R2 bundles have no next actions; the
   field is empty, as in the originals.
7. Not carried: the prose bundles' provenance paragraphs,
   StateChange logs, and artifact lists have no AgentState fields
   and do not appear in the A-prime bundles. This is the main
   reason A-prime word counts are far below #003 condition A, and
   it is a representation loss to weigh alongside the efficiency
   gain, not a pure win.
