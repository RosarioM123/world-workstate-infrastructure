# WORLD: Week 1 Founder and Technical Review

**Date:** 2026-09-20 · **Mission:** Day 3 of 10, startup validation program (BOTH day)
**Scope:** everything committed to the repo so far, plus the week's startup work
(Friday wedge research, the state model, experiment #001).
**Nature of this document:** a review, not new research. No new evidence was
gathered today; the judgments below are read off the existing record, and every
unsupported claim is marked as such.

---

## 1. Strongest evidence

The evidence worth trusting is the **measured continuation-quality gap** from
experiment #001 (2026-09-17, investment-research handoff, three conditions,
blind-graded):

- The summary condition lost a real decision (D-002) as an explicit decision:
  it survived as prose, not as a committable, auditable choice.
- The transcript condition recovered only 1 of 5 decisions canonically, 0 of 7
  canonical confidence labels, and **dropped a binding guardrail** ("no buy
  thesis without a stress case").
- The WORLD structured state recovered 5/5 decisions with rationales, 7/7
  assumptions with confidence levels, and the full revision trail, at +17%
  input overhead, and produced the shortest faithful output.

Narrative formats preserve *facts*; structured state preserves *governance*
(what was decided, why, what was assumed, what rules bind the next session).
That distinction is the thesis's load-bearing wall, and it is measured, not
philosophical.

Second line of evidence (demand, not mechanism): community feature-request
tracking across Claude Code, Gemini CLI, Copilot, OpenCode, and Pi shows
"deafening" demand for persistent memory, with context loss on restart/compact
flagged as a critical workflow flaw. Practitioner estimates put 15–20% of
developer time as re-explaining context to agents. The pain is acute, current,
and unsolved by static prompt files or vendor memory features.

---

## 2. Biggest unresolved assumption

**The write side.** Read-side value is measured; nobody has yet shown that
developers, or their agents, will reliably *maintain* the bundle. The wedge
doc states it plainly: a state file nobody updates is worse than none, because
stale authority misleads successor sessions. The assumption that agent-driven
writes under a minute of session time suffice is the existential risk of the
whole product, and it is untested.

Closely behind:

- **Zero customer interviews.** "Maya" is a persona, not a quote. Willingness
  to adopt, and to let an agent write to a state file every session, is
  unknown.
- **n=1 evidence.** Experiment #001 ran one domain (investment research), one
  model family, once. Transfer to coding workflows is hypothesized from the
  mechanism (governance loss), not measured. Experiment #002's results are
  pending.

---

## 3. Most dangerous technical mistake

**Building infrastructure before the convention earns its keep.** The repo
already contains a FastAPI backend (`app.py`), an ingest pipeline, a frontend,
and a deployment manifest, all of which are premature if Git + a docs folder
+ a good prompt achieves the same handoff fidelity. That is falsifiability
criterion #2 in `docs/hypothesis.md`, and it is still open.

The dangerous mistake is not a bug; it is a **category error**: treating "the
platform" as the product when the measured evidence supports only the bundle
format. Every infrastructure decision made now is a bet against that criterion
failing. The criterion deserves to be tested first, while it is still cheap.

Concretely: treat the existing backend as an **experiment harness**, not as the
MVP. Do not let it become load-bearing for the wedge.

---

## 4. Most promising next experiment

The **coding-domain handoff experiment**, already scoped in the wedge doc and
feeding the 09-23 benchmark mission: run the same three-condition protocol as
`docs/experiment-handoff.md` in Maya's actual domain. Does a successor agent
given the bundle avoid re-litigating settled decisions and violating recorded
constraints, versus summary and transcript baselines?

Why this is the right experiment:

- It tests the convention, not the infrastructure: file format plus
  measurement, no backend, no auth, no hosting.
- It attacks both open flanks at once: cross-domain transfer (evidence flank)
  and, if run with a real developer in the loop, the first write-side signal.
- A clean result (bundle wins) or a clean kill (summary parity, write-side
  failure) both move the program forward. Ambiguity is the only bad outcome.

In parallel: 3–5 conversations with developers doing multi-session agent work,
asking the adoption question directly: would you let an agent write to a
state file every session?

---

## 5. What should NOT be built yet

- The **ledger-as-service**, multi-user auth, hosted deployment
  (`render.yaml` stays a scaffold, not a launch plan), hash-chaining or
  enforcement layers. Nothing in the evidence yet says the convention needs
  enforcement that files can't provide.
- A dashboard as a product. UI beyond what's needed to run experiments.
- Any feature that does not serve the handoff experiment or the wedge
  validation. No UI polish, no new dependencies.
- **Guard respected:** the autonomous experiment #002 is running through
  2026-09-23. `docs/experiment-002/`, `docs/development-log.md`, and all
  experiment files were not touched by this mission and must not be touched by
  upcoming missions either.

---

## Verdict in one line

The thesis has the strongest evidence of the two startup projects (a measured
gap), and the weakest adoption story (the write side is a hope, not a fact).
This week's work should be sized to convert that hope into a measurement,
not to build the platform that assumes the answer.
