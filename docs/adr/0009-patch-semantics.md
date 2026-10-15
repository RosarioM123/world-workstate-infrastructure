# ADR 0009: Whole-document updates stay whole; patches are a client concern

Date: 2026-10-15
Status: Accepted

## Context

`World.update(state)` replaces the entire document. Review feedback asked
for patch or merge semantics: a `patch()` that applies a partial change
(RFC 6902 JSON Patch, RFC 7386 merge-patch, or a deep-merge) instead of
requiring the caller to read, modify, and rewrite the whole document.

The attraction is ergonomic: agents editing one field should not have to
round-trip a 2 MB document. The risk is semantic: once the server accepts
partial writes, *it* must define merge behavior, and every merge rule is a
correctness decision that now lives in the trusted core instead of the
caller's code.

## Decision

**Keep `update()` whole-document. Do not add server-side merge.**

Three reasons:

1. **Judgment needs the whole document.** Invariants judge `(old, new)`
pairs. A patch is judged only after it is applied, so the server would
have to apply it to produce the `new` document anyway; a `patch()`
endpoint is `update(apply(old, patch))` with extra syntax. Nothing is
gained in the trust model, but a merge DSL is gained in the attack
surface.

2. **Merge rules are application policy, not infrastructure.** Last-writer
-wins per field, CRDTs, operational transforms: each is correct for some
workloads and wrong for others. Baking one into WORLD picks winners.
The optimistic-concurrency path (`expected_version`, exactly one winner
per race) already gives callers a sound primitive to build their own
merge on top of.

3. **The read-modify-write cost is measurable and small.** Benchmarks
(`docs/benchmarks/world-primitive.md`) show state reads at ~3.8k ops/s;
the round trip is not the bottleneck for documents that fit the intended
use (work-state, not blob storage).

## Consequences

- Client SDKs may ship a `patch()` *convenience* that does
  read-apply-`update(expected_version=...)` with a caller-chosen merge
  function. If the version moved underneath, the caller retries with its
  own merge policy. The server never merges.
- If a future workload proves the round trip is the bottleneck, revisit
  with measurements, not ergonomics.
- `world diff` (CLI) covers the observability half of the request:
  callers can see exactly what changed between versions.
