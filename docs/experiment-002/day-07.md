# Experiment #002, Day 7 (2026-09-23): Final verdict (protocol §8)

## What ran

- Read the control files: `experiment-state.md` (Day 6 complete, next action Day 7) and `protocol.md`. Day 7 was not marked complete, so the final phase proceeded.
- A dedicated subagent drafted `results.md` per protocol §8 from the on-disk experiment materials (protocol, day-01 through day-06, experiment-state.md, hypothesis.md, development-log.md); no browsing, no invented numbers, no em dashes. The draft was reviewed and finalized (one edit: the #001 comparison table was tightened to the documented #001 figures).
- Wrote `docs/experiment-002/results.md` with all 19 sections §8 requires.
- Updated `docs/hypothesis.md` with a new "Experiment #002 verdict (2026-09-23)" section (evidence warranted the update: the experiment directly tested the thesis).
- Updated `experiment-state.md` (Day 7 complete, all fields, fresh timestamp, "next action: none: schedule retired").
- Appended a dated entry to `docs/development-log.md` (newest-first).
- Committed everything to `main` and verified; then disabled the `world-exp002-daily` schedule (self-retire per protocol §12 Day 7 plan).

## Verdict in brief (full analysis in results.md)

The WORLD-state continuation preserved decision governance best in both runs (Intel: 3.92 vs 3.58 vs 3.33; Disney: 4.45 vs 4.09 vs 2.82, reference means), so the WORLD-best direction replicates. The alternative ordering does not (journal vs summary flipped between runs; instance-sensitive, n=1). Strongest evidence FOR WORLD: assumption/confidence governance (main run 5/5 vs 3/3), provenance and supersession in the replication, and the label-stability mechanism ("relabeling is not neutral reformatting; it is where items get lost"). Strongest evidence AGAINST WORLD, replicated: revision history weak in the WORLD continuation in both runs (metric 5 = 2 twice), and an independent summary came within 0.36 in the Disney run, keeping falsifiability condition 1 open. The hypothesis is narrowed: partially supported, specifically scoped; success criteria 2 (human auditability) and 3 (cross-model consistency) untested. Prototype development is justified only for the narrow demonstrated advantage (stable labeled governance records), with revision-history preservation as the first test, not the full WORLD vision.

## Files produced/committed

- `docs/experiment-002/results.md` (new: the Day 7 verdict per protocol §8)
- `docs/experiment-002/day-07.md` (this file)
- `docs/experiment-002/experiment-state.md` (updated: Day 7 complete, retired)
- `docs/hypothesis.md` (updated: Experiment #002 verdict section)
- `docs/development-log.md` (appended)

## Schedule retirement

After the commit verified on `main`, cron `world-exp002-daily` was set to enabled=false (self-retire per protocol §12 Day 7 plan). No further autonomous runs for Experiment #002. Follow-up experiments (revision-history test, cross-model handoffs, human auditability) would be new schedules, not this one.
