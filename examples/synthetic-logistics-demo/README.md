# Synthetic logistics demo

This is a **synthetic domain used to stress-test the WORLD constraint engine** (concurrency, invalid deltas, tamper detection). It is **not the product demo** and not a validated operations model: wind speed derating port capacity is a fixed, auditable rule invented for demonstration, and Rotterdam was chosen only because it is a real port city with free, no-key weather data (Open-Meteo).

Run it from the repo root:

```bash
python examples/synthetic-logistics-demo/weather_ingest.py --dry-run
python examples/synthetic-logistics-demo/weather_ingest.py --demo
```

Run its tests:

```bash
python -m pytest examples/synthetic-logistics-demo/tests -q
```

The product itself is the deterministic state kernel in `src/world_engine/` (hash-chained ledger, constraint engine, `verify_chain()`); this directory only exercises it.
