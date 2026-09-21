# WORLD: Work-State Bundle (write-side trial)

**Project:** WORLD startup validation (repo `RosarioM123/world-workstate-infrastructure`)
**Bundle maintained by:** the assistant, per `docs/startup/write-side-trial/protocol.md`
**Last regenerated:** 2026-09-21 (trial Day 1; session 02 update)

## Context

WORLD's thesis: structured work state beats transcripts and summaries for agent session handoffs. The program is validating that thesis across a 10-day startup-validation schedule (through 2026-09-27) plus the 7-day experiment #002 (through 2026-09-23). The MVP decision (2026-09-21) is that the product is a file convention (`WORLD.md` + `world-state.json`), not a platform, and the repo's existing backend is an experiment harness.

## Decisions

1. **MVP is a file convention, not a platform** (accepted 2026-09-21). Rationale: week-1 review concluded infrastructure must earn its keep; only measured gaps justify building. Source: `docs/startup/mvp.md`.
2. **Existing backend stays an experiment harness** (accepted 2026-09-21). No product claims on `app.py`/ingest/dashboard until the convention proves itself.
3. **Commits go through the direct GitHub helper, not the browser upload flow** (accepted 2026-09-21). Rationale: browser upload failed or timed out twice in a row (09-20, 09-21); the helper worked both times. Revisit only if the helper breaks.
4. **WORLD repo canonical name is `RosarioM123/world-workstate-infrastructure`** (accepted 2026-09-20). Old name `RosarioM123/world` redirects; mission schedule should use the new name.
5. **Experiment #002 protocol is frozen through 2026-09-23** (accepted 2026-09-18). No protocol changes based on interim results; document methodological problems instead.

## Assumptions

1. **Agents can maintain the state bundle reliably** (medium confidence). Untested. This trial exists to test it.
2. **A strong auto-summary does not match the bundle on governance retention** (medium confidence). Experiment #002 Day 5: bundle 3.92 vs summary 3.33, n=1 domain. Summary parity would collapse the thesis to a prompt convention.
3. **Developers will let an agent write state files every session** (low confidence). Maya is a persona; no interviews yet.
4. **Cross-vendor portability is the defense against native agent memory** (low confidence). Transfer kit + shakedown-01 committed 2026-09-21 (`docs/benchmarks/cross-agent-transfer/`); no external-vendor run yet.
5. **Browser upload unreliability is environmental, not transient** (medium confidence). Two consecutive failures; helper route verified twice.

## Open questions

1. Does the bundle survive a context compaction in a real session? (the trial's Day 2+ rot checks will show this)
2. What is the actual write cost per session in minutes?
3. Would summary parity kill the infrastructure case, or only the file case?

## Guardrails

- No em dashes in polished or repo-facing text.
- Never touch `docs/experiment-002/` or `docs/development-log.md` outside the experiment schedule (through 2026-09-23).
- No license changes, no secrets, no history rewrites, no new product features in the validation program.
- Paper-only constraints hold for the quant repos; out of scope here but binding everywhere.
- Report evidence honestly, including evidence against WORLD.
