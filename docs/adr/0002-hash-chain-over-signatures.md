# ADR 0002: Hash chain over digital signatures

Date: 2026-09-17
Status: Accepted

## Context

Every ledger record must be tamper-evident: anyone replaying history
should detect edits, deletions, or reordering. Options were a plain
SHA-256 hash chain (each record commits to the previous record's hash)
or keyed signatures (each record signed with a private key).

## Decision

Use an unkeyed SHA-256 hash chain. `record_hash` covers timestamp,
entity, action, payload, previous hash, and verdict. `verify_chain()`
recomputes every link and names the first broken record.

## Consequences

- Good: no key management, no PKI, no signing service. Verification is
  a pure function of the data, so any participant (including the
  independent C# verifier in `tools/ChainVerify`) can check the chain
  with zero secrets.
- Good: chain verification is fast (100k rows in ~0.6s, see README
  benchmarks), so full verification on every read is affordable.
- Bad: an attacker with database write access can rewrite the entire
  chain consistently and remain undetected, because the hash is unkeyed.
  The chain detects accidental corruption and casual tampering, not a
  sophisticated adversary. This is stated plainly in `docs/SECURITY.md`.
- Revisit when: the threat model requires attribution or
  tamper-resistance against DB writers. The planned step is signed
  checkpoints (see `docs/SECURITY.md`), not per-record signatures.
