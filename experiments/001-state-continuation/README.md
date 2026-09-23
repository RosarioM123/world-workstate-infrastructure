# Experiment 001 — State Continuation Benchmark

**Research question:** does a canonical structured work-state
representation allow a fresh agent to continue ongoing work more
effectively than a transcript or a summary?

This is a rigorous, reproducible rebuild of the manual Experiment #001
(`docs/experiment-001-results.md`). Three handoff conditions — transcript,
summary, WORLD — one identical downstream task per scenario, pre-registered
metrics, and a scripted runner + scorer. The harness is explicitly built
to be able to show WORLD *losing*.

## Layout

| Path | Contents |
|------|----------|
| `methodology.md` | **Read first.** Pre-registered protocol: conditions, metrics (M1–M7), anti-bias rules, assumptions. Frozen before any run. |
| `dataset/tasks/` | 3 tasks. Each: `brief.md` (background + identical continuation brief), `ground_truth.json` (decisions, facts, open questions, next actions + pre-registered `must_mention` / `must_not_state` / `already_done` keys), `artifacts/` (the three handoff representations). |
| `runner/` | `run.py` (build-prompts / run / manifest), `prompts.py` (single prompt-composition code path), `adapters.py` (pluggable model adapters; manual flow needs no API keys). |
| `evaluation/` | `score.py` (deterministic M2–M7), `check_parity.py` (information-parity gate), `selftest.py` (proves WORLD can lose), `textutils.py` (matching heuristics), `rubric.md` + `judge_prompt.md` (blind grading for judged metrics). |
| `results/` | `README.md`, `schema.json`, and dated run directories. |

## Quick start (validate the harness, no model needed)

```bash
cd experiments/001-state-continuation
python3 evaluation/check_parity.py   # information parity across artifacts
python3 evaluation/selftest.py       # scorer ranks a deliberately-bad WORLD last
python3 runner/run.py run --adapter runner.adapters:EchoAdapter --out /tmp/smoke
```

## Running the benchmark

```bash
# 1. Preconditions (methodology §5): parity + selftest green (above).
# 2a. Programmatic: implement an adapter (see runner/adapters.py), then:
python3 runner/run.py run --adapter my_adapter:MyAdapter --out results/2026-09-23-run1
# 2b. Manual (any model, no keys):
python3 runner/run.py build-prompts --out /tmp/prompts
# paste each prompt into your model; save continuations to /tmp/raw/<task>__<condition>.md
python3 runner/run.py manifest --prompts /tmp/prompts --raw /tmp/raw --out results/2026-09-23-run1/manifest.json
# 3. Score:
python3 evaluation/score.py --raw results/2026-09-23-run1/raw \
    --manifest results/2026-09-23-run1/manifest.json \
    --out results/2026-09-23-run1/scored
# 4. Blind-grade the judged metrics (evaluation/judge_prompt.md), then tabulate.
# 5. Publish everything in results/, including null results.
```

## Metrics

M1 task completion · M2 factual accuracy · **M3 decision recovery
(primary)** · M4 question recovery · M5 contradiction rate ·
M6 repeated work · M7 token usage. No composite score. Definitions and
operationalizations are in `methodology.md` §4.

## Key assumptions (full list in methodology.md §8)

- All three artifacts derive from one ground truth (parity enforced by
  `check_parity.py`); the benchmark tests *representation*, not recall.
- The continuation brief and system prompt are byte-identical across
  conditions (single code path in `runner/prompts.py`).
- Answer keys are frozen before any run; the self-test must demonstrate
  a WORLD loss before real runs count.
- Deterministic metrics are keyword proxies with documented limits;
  judged metrics require blind grading.
