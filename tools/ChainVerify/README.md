# ChainVerify

Independent verifier for the WORLD ledger hash chain. It re-implements the
chain rule from scratch in C# — no shared code with `engine.py` — so a bug
in the Python engine cannot vouch for itself.

## What it checks

For every row of a ledger export, in `transaction_id` order:

1. `record_hash == SHA256_HEX(timestamp|entity_id|action|payload|previous_hash|status)`
   where a null `previous_hash` is rendered as the literal `GENESIS`
2. Each row's `previous_hash` equals the previous row's `record_hash`
   (null for the genesis row)

It prints `OK: N records verified, chain intact.` and exits 0, or names
the first broken transaction id and exits 1.

## Usage

```bash
# 1. Export the ledger (JSON array, oldest first)
python tools/export_ledger.py ledger.json

# 2. Verify it — needs the .NET 8 SDK
dotnet run --project tools/ChainVerify -- ledger.json
```

## Build status

> **Not compiled in this environment.** The machine used to develop this
> repo has no .NET SDK installed, so this program has not been built or
> executed here. It is written against the .NET 8 base class library only
> (`System.Security.Cryptography`, `System.Text.Json` — no NuGet packages)
> and the chain rule is pinned by `tests/test_verify_chain.py` on the
> Python side. Build it with `dotnet build tools/ChainVerify` on any
> machine with the .NET 8 SDK.
