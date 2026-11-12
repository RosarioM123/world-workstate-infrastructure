# Reproducing WORLD's results

This file is the research reproduction workflow for the WORLD
repository. Every command below was executed in the Prompt 6 session
(2026-11-05) on the environment described next, and the expected
outputs are the outputs those runs produced. Nothing in this file is
aspirational: a command that was not run is not documented here.

## Reference environment

- Date of verification: 2026-11-05
- OS: Linux 7.0.0-39-generic x86_64, glibc 2.39 (Ubuntu userland)
- CPU: x86_64, 4 cores (virtualized host; timings are indicative only)
- Python: 3.12.3 (repository virtualenv `.venv`)
- Repository state: commit `cbcbc66` plus uncommitted Prompt 3
  changes (F1 to F6) and the uncommitted `experiments/experiment-003/`
  directory. The suite count below corresponds to that tree.

Timing values vary by host. Counts, state totals, and pass/fail
outcomes are the reproducible content; wall-clock numbers are not.

## 1. Setup

```bash
git clone https://github.com/RosarioM123/world-workstate-infrastructure.git
cd world-workstate-infrastructure
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"     # adds pytest, pytest-cov, hypothesis, httpx, fastapi
pip install -e ".[server]"   # optional: fastapi and uvicorn for `world serve`
```

The core package (`src/world`) has zero runtime dependencies
(standard library only). The extras pull from PyPI and therefore need
network access; the test suite and every check below run offline
once the extras are installed.

Quick sanity check (runs in seconds, prints a judged update, a
rejection, a checkpoint list, and a chain check):

```bash
python examples/quickstart.py
```

Expected output (timestamps differ per run):

```
committed version 1: {'balance': 100, 'task': 'draft memo'}
rejected version 2: no_negative: balance = -5
state untouched: {'balance': 100, 'task': 'draft memo'}
checkpoints: [{'name': 'v1', 'seq': 1, 'timestamp': '...'}]
chain valid: True
```

## 2. Full test suite

```bash
.venv/bin/python -m pytest tests/ -q
```

Expected result on the reference tree:

```
409 passed, 1 warning in 78.14s
```

The count is a property of this tree: 377 tests at the pre-Prompt-3
baseline plus 32 added by Prompt 3. If tests are added or removed,
the count changes; what must not change is zero failures. The
crash-consistency tests write temporary directories under the system
temp dir and clean up after themselves only partially; on a small
tmpfs, clear stale debris first (`rm -rf /tmp/world-soak-*
/tmp/crash-* /tmp/pytest-of-root`) or the suite can fail with disk
errors that are environmental, not code failures.

## 3. Model checker

```bash
.venv/bin/python spec/model_check.py
```

Expected output (state counts are exact and host-independent;
times vary):

```
2 writers x 2 ops (full domains): OK (165579 states, 331404 transitions, 4.3s)
3 writers x 2 ops (race-focused): OK (935111 states, 1911456 transitions, 28.6s)
2 writers x 3 ops (sequential): OK (119565 states, 193680 transitions, 3.2s)
all properties P1..P6 hold on every reachable state
mutation test: bug injected -> checker found it (P4 violated: second winner for expected_version=0 (w1/op0))
```

Total explored states: 1,220,255. The mutation line matters as much
as the totals: with atomic re-validation removed, the checker must
find the P4 counterexample, and it does. The CI entry point for the
same check is `.venv/bin/python -m pytest tests/test_protocol_model.py -q`.

Note: `spec/world.tla` is a TLA+ transcription that has never been
run through TLC. The Python checker above is the executed
verification artifact; do not cite the TLA+ file as checked.

## 4. Benchmarks

```bash
.venv/bin/python experiments/prompt3/bench.py
```

The script builds fresh worlds in a temp dir and measures single
and batched updates, checkpoint and resume, and `verify()` time and
peak memory on a 20,000-version chain. Reference run output
(2026-11-05, this host; rates vary, the memory delta is the
Prompt 3 F5 result and should stay near 1 MB):

```
python: 3.12.3
single update: 1000 updates in 0.598s = 1672.5 updates/s
update_many: 2000 updates in 0.067s = 29750.0 updates/s
checkpoint create: 0.54 ms
resume: 0.95 ms
verify: 20000 versions, ok=True, 0.154s (129763 rows/s), peak RSS 25.8 -> 26.9 MB (delta 1.1 MB)
state(version=N): 0.71 ms (counter=499)
history(): 20000 rows in 90.9 ms
blame('meta.owner'): 92.4 ms (seq=10001, change=modified)
large-chain db size: 8.9 MB for 20000 versions
```

The historical benchmark records (2026-10-15, a different machine)
live in `docs/benchmarks/world-primitive.md`,
`docs/benchmarks/contention.md`, and `experiments/soak/RESULTS.md`.
They are dated records, not targets; this script is the
re-runnable check. The 1.06M-row soak was not re-run in this
session.

## 5. Experiment #003 analysis (fully reproducible from preserved outputs)

The agent runs of Experiment #003 are not reproducible (section 6),
but the published analysis is a pure function of the preserved
scores and mapping. Verify it in a scratch copy so the preserved
tree is never written to:

```bash
cp -r experiments/experiment-003 /tmp/exp003-repro
cd /tmp/exp003-repro
python3 analysis/analyze.py
diff analysis/results.json ../world-workstate-infrastructure/experiments/experiment-003/analysis/results.json
diff analysis/tables.md ../world-workstate-infrastructure/experiments/experiment-003/analysis/tables.md
```

(Adjust the diff paths to wherever the scratch copy sits relative
to the repository.) Verified 2026-11-05: `analyze.py` reported
`continuations scored: 72`, and both regenerated files were
byte-identical to the preserved ones. Headline values in
`analysis/tables.md` (per-condition means): metric 3 (assumptions)
A 0.721, B 0.500, C 0.488; metric 1 (decisions) A 0.948, B 0.979,
C 0.979; metric 5 (revision history) 1.000 in all three conditions;
metric 10 bundle sizes A 20,382 words, B 6,142, C 7,488.

The same pattern reproduces the Prompt 3 revalidation scores from
`experiments/prompt3/revalidation/` inputs; its agent runs are
likewise not reproducible (section 6).

## 6. What is NOT reproducible here

Be precise about the boundary:

- **The agent experiments themselves (#001, #002, #003, and the
  Prompt 3 revalidation) cannot be re-run from this repository.**
  They were executed by in-environment agent sessions: a single
  model family, the exact model version not reported by the
  platform, no seed or temperature control, and no model API
  credential available in this environment. Their raw outputs,
  prompts, scoring rubrics, and grading records are preserved
  verbatim (`docs/experiment-001-results.md`,
  `docs/experiment-002/`, `experiments/experiment-003/`,
  `experiments/prompt3/revalidation/`), and their analyses
  reproduce exactly (section 5). The results are PRELIMINARY and
  must be cited as such.
- **The lost-update experiment's LLM-agent replication** was never
  run (blocked on model credentials); the scripted-agent version is
  recorded in `experiments/lost-update/` and was not re-run in this
  session.
- **Anything requiring external services** (PyPI for the optional
  extras, a JVM for TLC) is outside the offline reproduction set.
  No step in sections 1 to 5 needs an API key or a third-party
  service once dependencies are installed.

## 7. Clean-install verification (package outside the repository)

Verified 2026-11-05: the package installs from the local tree into
a fresh virtualenv and works from an unrelated working directory.

```bash
python3 -m venv ~/cleanroom/venv
~/cleanroom/venv/bin/pip install ~/workspace/world-workstate-infrastructure
~/cleanroom/venv/bin/pip show world-engine   # Name: world-engine, Version: 0.1.0, License: MIT
~/cleanroom/venv/bin/world --help            # CLI entry point responds
```

A smoke script run with the cleanroom interpreter from
`~/cleanroom/` (source preserved with the Prompt 6 working notes)
created a world in a temp dir, committed an update, pinned a
checkpoint, saved and reloaded a handoff state using the Prompt 3
schema (a decision superseded by a successor, an assumption with
confidence `high`), derived the two-entry revision chain for the
superseded decision, and finished with `verify(): True` and
`SMOKE OK`. No packaging defects blocked installation. Two cosmetic
metadata gaps were observed and are recorded in
`experiments/prompt6/RELEASE_READINESS.md`: `pip show` reports an
empty Author field (pyproject declares no `authors`) and an empty
Home-page line in this pip version despite `[project.urls]`.
