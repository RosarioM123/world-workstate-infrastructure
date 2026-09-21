# Pull request

## What changed

## How it was tested

- [ ] `python -m pytest tests/ -q --cov` green
- [ ] `ruff check src/ tests/` and `ruff format --check src/ tests/` clean
- [ ] `mypy src/` clean

## Guarantees affected

Does this touch a documented guarantee (determinism, tamper-evidence,
concurrency safety, idempotency)? If yes, which test proves it still
holds?
