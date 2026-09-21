# Contributing to WORLD

## Setup

```bash
pip install -e ".[test]"
python -m pytest tests/ -q --cov
```

This installs the package in editable mode plus the test tools
(pytest, pytest-cov, hypothesis, httpx).

## Before you push

```bash
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/
python -m pytest tests/ -q --cov
```

CI runs the same four gates on Python 3.11, 3.12, and 3.13. A
pre-commit config (`.pre-commit-config.yaml`) runs ruff automatically;
install it with `pre-commit install`.

## Ground rules

- **Determinism is the product.** Same inputs must produce the same
  ledger. No wall-clock reads, no randomness, no network calls in the
  kernel path (`src/world_engine/core/`).
- **Every attempt is on the ledger.** Rejected intents are appended,
  never dropped. Do not add a code path that mutates or deletes ledger
  rows.
- **Prove hard claims with tests.** If you document a guarantee
  (concurrency safety, tamper-evidence, idempotency), add a test that
  would fail if the guarantee broke. See `tests/test_concurrency.py`
  and `tests/test_chain_properties.py` for the pattern.
- **Keep the kernel stdlib-only.** `src/world_engine/core/engine.py`
  depends on the standard library plus `sqlite3` and nothing else.
- **No em dashes** in repo text, code comments, or commit messages.
- **No secrets, ever.** No API keys, tokens, passwords, or `.env`
  files. See the Rules section of the README.

## Commit messages

Few, meaningful commits: one per coherent change, each a complete
thought. Good:

- `Add coverage gate at 85% (pytest-cov, enforced in CI)`
- `Version the API under /api/v1 with deprecated aliases`

Not:

- `fix`, `update`, `wip`, ten one-line commits in a row.

Never rewrite published history (no force pushes, no rebasing `main`).

## Pull requests

Fill in the pull request template: what changed, how it was tested,
and which guarantee it affects (if any). Small PRs get reviewed
faster.
