# ChainVerifyWorld: independent C# chain verifier

Re-verifies a `src/world` hash chain with **no shared code** with the
Python implementation: the chain rule (`world-genesis:{name}` seed,
`\n`-joined field hashing, link checks) is reimplemented from the spec
in C#. If the Python code had a bug that made `verify()` lie, this
verifier would still catch it, because it does not trust the Python
code at all. (The legacy engine has its own verifier in
`tools/ChainVerify` for its different chain format.)

- Reads the SQLite database directly (rows piped through the `sqlite3`
  CLI in `--readonly` mode; the CLI performs no chain logic).
- Zero NuGet dependencies: builds offline with the .NET 8 SDK.
- Exit 0: chain valid. Exit 1: first bad seq printed. Exit 2: bad input.

```
dotnet run --project tools/ChainVerifyWorld -- <world.db> <world-name>
```

Covered by `tests/test_csharp_verifier.py` (skipped when dotnet is
absent): accepts a valid mixed-verdict chain, rejects a tampered row,
a broken link, and a wrong world name (the genesis hash binds the name).
