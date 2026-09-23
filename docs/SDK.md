# WORLD Client SDK

The SDK (`src/world_sdk/`) is the client-owned half of the WORLD
architecture: a thin, offline-first Python client with a local intent
ledger and disposable index sidecars. It is stdlib-only (plus `sqlite3`,
which ships with Python): no embedding model, no API keys, no network,
no paid services.

```python
from world_sdk import WorldClient

client = WorldClient()  # ~/.world/world_client.db + ~/.world/world_index.db
r = client.intent("node_rotterdam_hub", "ALLOCATE",
                  deltas={"capacity": -50.0}, note="repositioning for Q4")
print(r["status"])          # COMMITTED or REJECTED, decided locally
print(client.verify())      # (True, None): hash chain intact
```

## What the SDK owns

- **Local ledger** (`world_sdk.ledger.LocalLedger`): a client-owned,
  hash-chained intent ledger in the same entry format as the server
  ledger. `intent()` runs the same constraint policy as the server (the
  policy function is imported, not copied, so verdicts cannot drift) and
  appends every attempt, COMMITTED or REJECTED. Only COMMITTED intents
  mutate materialized state. `register_entity()` adds a new node with
  initial capacity/liquidity, validated like an intent and logged as a
  COMMITTED `REGISTER_ENTITY` row, so entity creation is auditable too.
- **Embedding sidecar** (`world_sdk.index.EmbeddingSidecar`): a sqlite3
  table mapping block height to vector blob, with pure-Python cosine
  search. Bring-your-own embeddings: the SDK never calls an embedding
  model or API, the caller supplies vectors via `add_embedding()`.
- **Timestamp index** (same sidecar): block height to block time. This is
  the client-side timestamp resolution from the time-travel design: the
  server stays block-height canonical and stdlib-pure, while the client
  answers "what did we know at time T" by resolving T to a height locally
  and replaying its ledger to that height (`state_at_time(T)`).

## Multi-agent fields

Every intent carries three optional fields, recorded into the ledger
payload (hence hash-covered) but unenforced:

- `actor`: who submitted the intent. Self-asserted today; no auth behind
  it (see ADR 0006).
- `kind`: `INTERNAL_STATE` (default) or `EXTERNAL_EFFECT`. Recorded only;
  it never changes the constraint verdict.
- `idempotency_key`: a client-supplied request id. A second submission
  with the same key returns the first submission's verdict without
  appending a new row, so retries are safe. Empty keys are rejected.
  Keys are rebuilt from ledger payloads on `import_ledger_rows()`, so a
  synced ledger keeps deduplicating.

See docs/adr/0005-multi-agent-conflict-policy.md for why contention still
surfaces as ordinary REJECTED rows until a second real agent exists.

## The guarantee boundary
The ledger is the sole system of record. Both sidecars are derived and
disposable: delete the index file and nothing of value is lost, rebuild it
from the ledger. Verification (`verify()`) walks the SHA-256 hash chain
only: deterministic, LLM-free, no second store in the integrity path. A
timestamp or embedding index may never participate in COMMIT/REJECT and is
never required for `verify_chain()` to pass.

## Interop with the server

Client rows are byte-compatible with server rows: same table, same hash
material, same payload shape. `import_ledger_rows()` copies server ledger
rows into the local ledger verbatim, verifies the merged chain, and
rebuilds materialized state from it, so an offline client can sync history
and time-travel over it. The test suite pins this: the server's own
`verify_chain()` accepts a client-built ledger file.

## Time-travel reads

```python
state = client.state_at_block(1024)            # replay to a block height
state = client.state_at_time("2026-09-01T00:00:00+00:00")  # via timestamp index
```

`resolve(T)` returns the latest block with `block_time <= T`, or `None`
when no block exists at or before T. Equal timestamps resolve to the
highest block height among them. Naive (timezone-unaware) datetimes are
rejected: an ambiguous wall clock has no place in an audit index.
