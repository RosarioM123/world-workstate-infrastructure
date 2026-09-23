# Methodology — Experiment 001: State Continuation Benchmark

**Status:** pre-registered. This document defines the research question,
conditions, metrics, and scoring procedure. It must be written before any
benchmark run, and it must not be edited to favor an outcome after results
are in. Amendments require a dated entry in `results/` explaining what
changed and why.

## 1. Research question

> Does a canonical structured work-state representation allow a fresh
> agent to continue ongoing work more effectively than a transcript or
> a summary?

"In ongoing work" means: a predecessor agent did real work (decisions,
findings, open questions, next actions) and stopped; a successor agent,
with no other context, must continue. "More effectively" is operationalized
by the metrics in §4 — no single composite score.

This benchmark is motivated by Experiment #001 (`docs/experiment-001-results.md`)
and #002 (`docs/experiment-002/results.md`), which were manual, n=1,
hand-scored studies. This rebuild makes the design reproducible:
fixed tasks, fixed handoff artifacts, fixed answer keys, scripted runner,
deterministic scoring where possible.

## 2. Conditions

Three handoff representations, built from the **same ground truth**
(§3). The downstream task (the continuation brief) is byte-identical
across conditions; only the handoff artifact differs.

| Condition | Artifact | Format tag in prompt |
|-----------|----------|----------------------|
| A. Transcript | `artifacts/transcript.md` — chronological narrative of Agent A's work | `[Format: chronological transcript]` |
| B. Summary | `artifacts/summary.md` — concise written summary of Agent A's work | `[Format: written summary]` |
| C. WORLD | `artifacts/world.json` — structured `AgentState` (objective, decisions, evidence, open questions, next actions) | `[Format: structured JSON state]` |

The runner (`runner/run.py`) composes every prompt from one system prompt
plus one brief plus one artifact (`runner/prompts.py`). There is exactly
one code path; conditions cannot receive different instructions.

## 3. Information parity (anti-rigging rule)

The benchmark tests *representation*, not recall. Therefore:

1. All three artifacts are derived from a single `ground_truth.json`.
   No artifact may contain a material fact absent from the other two.
2. **Parity gate (automated):** every `must_mention` key phrase in the
   ground truth must appear (after normalization) in **all three**
   artifacts. `evaluation/check_parity.py` enforces this; a task whose
   artifacts fail parity is excluded until fixed.
3. Artifact length is reported but not equalized: verbosity is part of
   the representation. Token cost (M7) captures the trade-off.

## 4. Metrics (pre-registered)

No composite score (per Experiment #002's protocol: no premature score
collapse). M3 is the primary metric, chosen because decision governance
was the headline finding of #001/#002.

| ID | Metric | Operational definition | Type | Better |
|----|--------|------------------------|------|--------|
| M1 | task_completion | 0–3 rubric: delivers what the brief asked, all required parts present | judged | ↑ |
| M2 | factual_accuracy | fraction of ground-truth facts correctly stated (`must_mention` proxy) + 0–3 judged | both | ↑ |
| M3 | **decision_recovery** (primary) | fraction of ground-truth decisions recovered *with correct rationale* (`must_mention` proxy) | deterministic | ↑ |
| M4 | question_recovery | fraction of open questions carried forward or explicitly resolved | deterministic | ↑ |
| M5 | contradiction_rate | `must_not_state` hits + judged contradictions, per 100 output words | both | ↓ |
| M6 | repeated_work | `already_done` items re-proposed as new work (count) + 0–3 judged | both | ↓ |
| M7 | token_usage | input/output words, chars (deterministic); provider tokens if the adapter reports them | deterministic | ↓ (cost) |

Deterministic proxies use normalized substring matching (lowercase,
punctuation stripped). They are *proxies*: documented limitations are in
`evaluation/score.py`. Judged metrics use `evaluation/rubric.md` and the
fixed `evaluation/judge_prompt.md`.

## 5. Procedure

1. Write `methodology.md` (this file) and all `ground_truth.json` files
   with `must_mention` / `must_not_state` / `already_done` keys **before
   any continuation is generated**.
2. Run `evaluation/check_parity.py`; fix artifacts until all tasks pass.
3. Run `evaluation/selftest.py`: synthetic continuations where the WORLD
   condition is deliberately worst. The benchmark is only valid if the
   scorer ranks WORLD last there — i.e., the harness **can show WORLD
   losing**.
4. Build prompts: `python runner/run.py build-prompts --out <dir>`.
5. Generate continuations with a model adapter (`runner/adapters.py`).
   The manual adapter supports human- or copy-paste-driven runs with any
   model; no provider integration ships with the repo.
6. Collect: `python runner/run.py manifest --prompts <dir> --raw <dir>`.
7. Score: `python evaluation/score.py --raw <dir> --out <dir>`.
8. Judge the rubric metrics blind: strip condition labels, shuffle,
   grade with `evaluation/judge_prompt.md`, then unblind.
9. Publish the full score table in `results/`. **Report all tasks and
   all metrics.** No cherry-picking, no post-hoc metrics.

## 6. Rules against optimizing for a WORLD win

- Information parity (§3) is enforced by script, not by intention.
- The continuation brief is identical across conditions (single code path).
- Answer keys are frozen before any run.
- The self-test (§5.3) must demonstrate a WORLD loss before real runs count.
- The pilot/runner operator must not regenerate continuations to improve
  a condition's score ("best of N" per condition is forbidden unless
  pre-registered with N fixed and all N reported).
- Negative or null results are results: publish them verbatim.

## 7. Threats to validity

- **Synthetic tasks.** The tasks are authored, not real agent logs. They
  test the mechanism (representation → continuation quality), not
  ecological validity.
- **Proxy metrics.** `must_mention` matching rewards keyword presence,
  not understanding. The judged metrics exist to compensate; they carry
  grader noise.
- **Grader bias.** LLM judges may favor well-formatted (JSON-like)
  inputs. Mitigation: blind grading, human spot-checks, and reporting
  deterministic and judged metrics separately.
- **Single brief style.** All briefs ask for a short written deliverable.
  Results may not transfer to interactive or tool-using continuations.
- **n is small.** Three tasks. This benchmark detects large, consistent
  effects; it cannot resolve small ones. Do not overclaim.

## 8. Assumptions (documented, not hidden)

1. A successor agent reads the handoff artifact once, then writes the
   deliverable. No multi-turn clarification, no tool use.
2. The predecessor's work is faithfully captured by the ground truth;
   artifact authors did not inject errors.
3. Word count is the cross-provider cost proxy; provider token counts
   are recorded only when the adapter supplies them.
4. English-language tasks; one domain family (engineering knowledge work).
5. The `world.json` artifact is a fair rendering of "the WORLD
   representation" — i.e., what `save_state`/`load_state` would carry.
6. Continuations are capped by instruction ("under 300 words"); overlong
   outputs are scored as-is (verbosity is data, not a disqualifier).
7. The deterministic scorer's normalization is dumb on purpose: any
   smarter matching (embeddings, LLM extraction) would itself need
   validation and is out of scope for v1.
