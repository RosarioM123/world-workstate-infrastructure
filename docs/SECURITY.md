# WORLD: Threat Model

## Part A: the `src/world` primitive (current)

This section covers the `World` primitive (`src/world/core.py`): versioned
JSON documents, invariant-judged transitions, hash-chained rows, optimistic
concurrency, checkpoints. Every claim below is pinned by an adversarial
test in `tests/test_redteam.py`: `*_detected` tests prove the guarantee,
`*_undetected_documents_limit` tests prove the limit (each asserts the
attack *succeeds*; if a future change closes one, the test fails and
forces this doc to be updated).

### Attacker model

- **A1: read access to the database file.** Sees everything. There is no
  confidentiality: documents, notes, actors, and rejected attempts are
  cleartext.
- **A2: write access to the database file.** Can run arbitrary SQL,
  bypassing the API entirely. This is the primary adversary below.
- **A3: API-constrained writer.** Can only call the public surface
  (`update`, `resume`, CLI, HTTP). Constrained by invariants and by the
  commit protocol (verified separately in `docs/spec/protocol-verification.md`).
- **A4: host compromise / clock control.** Out of scope for the chain to
  defend: a compromised host owns the process, the file, and the
  verifier. Timestamps come from the host clock and are not trusted time
  (they are, however, covered by the row hash: backdating is *detected*).

### What verify() detects (tested)

`World.verify()` recomputes every hash link over all rows by seq. It
returns False when the attacker:

1. Edits any field of any row in place: state, status, note, actor, or
   timestamp (`test_surgical_*_detected`, `test_timestamp_backdate_detected`).
   Every one of these fields is covered by the row hash.
2. Deletes a middle row (`test_middle_row_deletion_detected`): the next
   row's `prev_hash` no longer matches.
3. Reorders rows (`test_row_reorder_detected`): links no longer line up.

An API-constrained attacker additionally cannot commit an
invariant-violating document: the attempt is appended as REJECTED
evidence and the version does not move
(`test_api_cannot_commit_invariant_violation`). `resume()` of an old
checkpoint appends a new version; it never rewrites the past
(`test_resume_is_append_only`).

### What verify() does NOT detect (tested limits)

1. **Tail truncation (rollback).** Deleting the last N rows leaves a
   shorter but internally consistent chain, and `verify()` returns True
   (`test_tail_truncation_undetected_documents_limit`). The version
   silently moves backward. Detection requires pinning the tip hash
   out-of-band.
2. **Full chain rewrite.** The hash is unkeyed (ADR 0002): an attacker
   who recomputes every link with forged history produces a chain that
   verifies cleanly (`test_full_rewrite_undetected_documents_limit`).
   This is the fundamental limit. No better hash function fixes it;
   only a key (signed checkpoints) or an external anchor does.
3. **Checkpoint repointing.** The `checkpoints` table is not covered by
   the hash chain, so `UPDATE checkpoints SET seq = ...` is invisible
   to `verify()` (`test_checkpoint_repoint_undetected_documents_limit`).
4. **Idempotency-table deletion.** Exactly-once per key depends on the
   `idempotency` table, which is not tamper-evident. Deleting a key's
   row lets a retry commit a second time; the chain still verifies
   (`test_idempotency_deletion_enables_double_apply_documents_limit`).
5. **Forks.** Copying the file and extending each copy differently
   yields two chains that both verify; only tip-hash comparison reveals
   the divergence (`test_fork_produces_two_valid_chains_documents_limit`).

### Mitigation ranking

1. **Signed checkpoints** — **BUILT 2026-10-15** (`World.sign_tip` /
   `verify_tip`, HMAC-SHA256, stdlib-only; `tests/test_world_signing.py`).
   A tip signature held out-of-band closes limits (1) and (2) above for
   its holder: truncation and full rewrites are now detected
   (`test_signed_tip_detects_rollback`,
   `test_signed_tip_detects_rewrite`), while honest appends after
   signing keep old tips valid. `verify()` itself is unchanged: the
   unkeyed chain still cannot detect these on its own, which is why the
   red-team `*_undetected` tests remain green as documented.
   **Public-verifiability upgrade BUILT 2026-10-15**:
   `World.sign_tip_ed25519` / `verify_tip_ed25519` (Ed25519 over the same
   `(name, seq, hash)` message; vendored pure-Python backend in
   `src/world/ed25519.py`, stdlib-only, validated against RFC 8032
   section 7.1 vectors; `tests/test_world_signing_ed25519.py`, 13 tests).
   Anyone holding the *public* key verifies; only the private-key holder
   signs. Measured: ~147 signs/s, ~109 verifies/s (pure Python).
2. **Checkpoint table inclusion**: fold checkpoint pins into the hashed
   row (or a parallel chained table). Closes (3). Still open.
3. **WORM / append-only storage** for ledger segments. Closes (1), (2),
   (4) at the storage layer. Still open.
4. **Per-actor identity** on the API (ADR 0006): `actor` is currently
   self-asserted. Still open.
2. **Checkpoint table inclusion**: fold checkpoint pins into the hashed
   row (or a parallel chained table). Closes (3).
3. **WORM / append-only storage** for ledger segments. Closes (1), (2),
   (4) at the storage layer.
4. **Per-actor identity** on the API (ADR 0006): `actor` is currently
   self-asserted.

---

## Part B: legacy `world_engine` (pre-primitive engine)

*The following predates the `src/world` primitive and describes the
original `world_engine` ledger (`execute_deterministic_transition`,
`state_ledger`, `verify_chain`). Kept for the record; Part A above is
the current threat model.*

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
