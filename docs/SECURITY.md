# WORLD Ledger: Threat Model

This document states plainly what the hash-chained ledger guarantees,
what it does not, and what would have to change for stronger claims.
It is written for a technical reviewer doing diligence, not for
marketing.

## What the ledger guarantees

1. **Append-only by convention.** All writes go through
   `execute_deterministic_transition()`, which only ever INSERTs into
   `state_ledger` and UPDATEs the derived `entities` table on commit.
   No code path UPDATEs or DELETEs ledger rows.
2. **Tamper-evidence for stored history.** Each record's `record_hash`
   (SHA-256) covers its timestamp, entity, action, payload, previous
   hash, and verdict. `verify_chain()` recomputes every link in order.
   - Editing any field of a record breaks its `record_hash`.
   - Deleting a middle record breaks the next record's `previous_hash`
     link.
   - Reordering records breaks the links the same way.
   - In each case `verify_chain()` returns `(False, bad_id)` naming the
     first broken record.
3. **Complete audit trail.** Committed and rejected intents alike are
   appended, including attempts against unknown entities, so an attack
   leaves evidence even when it fails.
4. **Atomic check-then-act.** The read-check-write sequence runs inside
   one `BEGIN IMMEDIATE` transaction, so concurrent writers cannot both
   pass the constraint checks against stale state
   (`tests/test_concurrency.py` proves this with 16 racing threads).
5. **Independent verification.** `tools/ChainVerify` (C#) reimplements
   chain verification with no shared code, so a bug in the Python
   verifier cannot mask a broken chain.

## What it does NOT guarantee

1. **Not immutable against a database writer.** The hash chain is
   unkeyed (ADR 0002). Anyone with write access to the database file can
   rewrite history and recompute a consistent chain that verifies
   cleanly. The chain detects accidental corruption and casual
   tampering; it does not stop a sophisticated adversary holding the
   file. File permissions are currently the only access control.
2. **Only interim authentication.** When `WORLD_API_KEY` is set, the
   write endpoints require it as the `X-API-Key` header and are
   per-IP rate-limited (`src/world_engine/api/auth.py`,
   `world_engine/api/middleware.py`). Reads are open, and there is
   still no per-actor identity and no per-entity permission model:
   `actor` remains self-asserted (ADR 0006).
3. **No confidentiality.** Ledger payloads (including intent notes) are
   stored in cleartext. Anyone who can read the database file can read
   every decision, assumption, and note ever imported.
4. **No protection against a compromised host.** If the machine running
   the engine is compromised, all bets are off: the attacker owns the
   process, the file, and the verification function itself.
5. **Timestamps are not trusted time.** Record timestamps come from the
   host clock. A skewed or malicious clock produces misleading ordering
   evidence (the hash links still hold; the wall-clock story may not).

## What a database-write attacker can and cannot do

- CAN: rewrite the full chain consistently (undetectable by
  `verify_chain()`), delete recent history and re-link, backdate
  records by editing timestamps and recomputing hashes.
- CANNOT (without detection): make a *surgical* edit to one record and
  leave the rest of the chain intact. Any partial edit breaks a link
  that `verify_chain()` will name.

## Planned hardening (not yet built)

1. **Signed checkpoints.** Periodically sign the tip hash with a
   server-held key (HMAC or ed25519) and publish the signature
   out-of-band. A full rewrite then requires the signing key, not just
   the database file. This is the single highest-value upgrade.
2. **Append-only storage.** Ship ledger segments to WORM storage (or a
   write-once file) so history cannot be rewritten even by a file holder.
3. **Authentication and per-entity authorization** on the API, before
   any multi-tenant deployment. Interim step done: `WORLD_API_KEY`
   gates the write routes and per-IP rate limiting is in place; full
   RBAC per ADR 0006 is still open.
4. **Encrypted notes.** Envelope encryption for sensitive intent notes,
   with key management outside the database.

## Reporting

This is a personal research prototype. If you find a flaw in the
guarantees above, open an issue. Please do not commit exploit code
against the demo data.
