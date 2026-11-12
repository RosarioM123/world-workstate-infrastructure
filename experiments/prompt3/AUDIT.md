# WORLD Architecture Audit (Prompt 3, Phase 1: Read-Only Assessment)

Repo: `~/workspace/world-workstate-infrastructure`, local HEAD `cbcbc66`. No files were modified, created, or deleted during this audit. `experiments/experiment-003/` was read only. This file itself is uncommitted working documentation, saved for review.

Scope note that frames everything below: the repo contains two systems. `src/world/` is the current primitive (the `World` class: versioned JSON documents in SQLite, invariant judging, SHA-256 hash chain, optimistic concurrency, checkpoints, signed tips, per-field encryption). `src/world_engine/` is the legacy engine (entity ledger, `replay_ledger()`, its own FastAPI app and API key gate), kept for the record per `docs/SECURITY.md` Part B. Most guarantees below belong to `src/world/`; where a capability exists only in `world_engine` (notably deterministic replay), that is stated explicitly, because conflating the two would overstate the primitive.

A second framing fact: Experiment #003 did not exercise the `World` class at all. Condition A artifacts are hand-authored Markdown bundles (`experiments/experiment-003/artifacts/*/state.md`) written by an agent following `docs/state-model.md`. Experiment #003 therefore tested a document schema as prose, not the persistence layer, not `src/world/handoff.py`, and not any code path in `core.py`. Every experimental claim in section C inherits that limitation.

## A. Current guarantees

Each item is tagged and pinned to evidence.

1. **Append-only verdict log with tamper evidence over every row field. VERIFIED.**
   Schema `versions(seq, timestamp, actor, note, state, status, prev_hash, hash)` in `core.py` `_SCHEMA`. `_row_hash` computes SHA-256 over `prev_hash, seq, timestamp, actor, note, status, state_text`. `World.verify()` rewalks all rows in seq order and recomputes every link. Both COMMITTED and REJECTED proposals are appended (`World.update`), so rejected attempts are evidence. Tests: `tests/test_redteam.py` (`test_surgical_state_edit_detected`, `test_surgical_status_flip_detected`, `test_surgical_note_edit_detected`, `test_surgical_actor_spoof_detected`, `test_timestamp_backdate_detected`, `test_middle_row_deletion_detected`, `test_row_reorder_detected`), `tests/test_verify_chain.py` (9 tests), `tests/test_verify_fuzz.py` (500 seeded mutations plus 450 under alternate seeds, 100 percent detection, per prior verification records), `tests/test_ledger_integrity.py`, `tests/test_chain_properties.py`. Model checker property P2 covers the same linkage symbolically.

2. **Sequence integrity and committed-only version semantics. VERIFIED (model-checked).**
   `World.version` returns the max COMMITTED seq, 0 when empty (`core.py` `_latest_committed`, `version`). `state(version=N)` raises `KeyError` for a REJECTED seq and directs the caller to `proposal(seq)`. Model checker P1 (dense unique seqs 1..N) and P3 (version equals max COMMITTED seq) hold over 1,220,255 explored states in `spec/model_check.py`, exercised by `tests/test_protocol_model.py` (4 tests, including the mutation test in item 9 below).

3. **Optimistic concurrency: exactly one winner per expected version. VERIFIED (model-checked plus threaded tests).**
   `World.update` does a fast-path `expected_version` check, judges invariants lock-free, then revalidates inside `BEGIN IMMEDIATE` in `_append_guarded`, so the check and the append are atomic. Model checker P4 (at most one commit per expected version). Tests: `tests/test_world_occ.py` (5 tests), `tests/test_linearizability.py` (4 tests, Knossos-style search over recorded concurrent histories in `spec/linearizability.py`), `tests/test_concurrency.py`, `tests/test_world_concurrency.py`, `tests/test_detsim.py` (deterministic simulation in `spec/detsim.py`). Earlier lost-update experiment (from repo records): without `expected_version`, 33 of 50 concurrent writes lost; with `expected_version` plus retry, 0 of 50.

4. **Idempotency for committed updates. VERIFIED within the model, with a documented storage limit (see D5).**
   A repeated `idempotency_key` for a COMMITTED update returns the original seq without appending; dedupe happens inside the write transaction in `_append_guarded`. Every proposal is judged first, so a repeated key cannot mask a REJECTED row. Model checker P5 (table maps each key to the seq of its latest committed use) and P6 (every judged op appends exactly one row except the idempotent short-circuit). `update_encrypted` refuses `idempotency_key` outright (`core.py`, near line 1094) because a replay would orphan fresh field keys; the refusal is explicit, not silent.

5. **Invariant judging with recorded rejections. VERIFIED for single-handle and sequential use; see B2 for the concurrency and multi-handle caveats.**
   Invariants are callables `(old_state, new_state)` raising `InvariantViolation`; shipped helpers in `src/world/invariants.py`: `no_negative`, `monotonic`, `type_stable`, `immutable_fields`, `finite_numbers`, `require_keys`, `respect_locks`, `all_of`. Tests: `tests/test_world_invariants.py` (21 tests), `tests/test_invariant_composition.py` (4 tests), `tests/test_constraints.py`, `tests/test_locks.py`, `tests/test_stateful.py` (Hypothesis stateful testing, per prior records 1,526 generated ops with zero divergences), `tests/test_hardening.py`. `test_api_cannot_commit_invariant_violation` proves an API-constrained writer cannot commit a violating document.

6. **Checkpoints are named pins; resume is append-only. VERIFIED.**
   `World.checkpoint(name)` pins the current committed seq (names immutable, duplicates raise). `World.resume(name)` appends the checkpointed document as a new version, judged by current invariants; it never rewrites history. Test: `test_resume_is_append_only` in `tests/test_redteam.py`. The checkpoint table itself is not integrity-protected; see D4.

7. **Signed tips detect rollback and full rewrite for the signature holder. VERIFIED.**
   `sign_tip` (HMAC-SHA256 over `name:seq:tip_hash`, key held out-of-band, never written to the DB) and `sign_tip_ed25519` / `verify_tip_ed25519` (same message, Ed25519, publicly verifiable). `verify_tip` and `verify_tip_ed25519` return False when the chain no longer contains the signed `(seq, hash)` pair, which is what makes truncation and rewrite detectable. Tests: `tests/test_world_signing.py` (7), `tests/test_world_signing_ed25519.py` (11, including RFC 8032 section 7.1 vectors), and in `tests/test_redteam.py` the signed-tip detection tests cited in `docs/SECURITY.md` (`test_signed_tip_detects_rollback`, `test_signed_tip_detects_rewrite`). Ed25519 key rotation with an old-key-signed certificate binding the new public key to the current tip: `rotate_ed25519` / `verify_rotation_ed25519`, `tests/test_key_rotation.py` (8 tests). Tips carry a `kid` (default SHA-256 fingerprint prefix of the key) so verifiers can route among keys.

8. **Hash chain integrity is not authenticity, and the code and docs say so. VERIFIED as a documented and tested distinction.**
   The row hash is unkeyed (ADR 0002, cited in `docs/SECURITY.md`). `verify()` detects surgical edits, middle-row deletion, and reordering; it does not detect tail truncation, full recomputation, checkpoint repointing, idempotency table deletion, or forks. Each limit is pinned by a test that asserts the attack succeeds: `test_tail_truncation_undetected_documents_limit`, `test_full_rewrite_undetected_documents_limit`, `test_checkpoint_repoint_undetected_documents_limit`, `test_idempotency_deletion_enables_double_apply_documents_limit`, `test_fork_produces_two_valid_chains_documents_limit`. These are expected-counterexample tests by design: if a future change closes a limit, the test fails and forces the threat model to be updated.

9. **The model checker has teeth. VERIFIED.**
   `tests/test_protocol_model.py::test_protocol_checker_detects_injected_bug`: with the atomic revalidation removed (`inject_bug=True` in `spec/model_check.py`), the checker must find a P4 violation, and does.

10. **Crash consistency of committed rows under SIGKILL. EXPERIMENTALLY OBSERVED.**
    `tests/test_crash_consistency.py::test_sigkill_mid_transaction_leaves_clean_db` (6 rounds, seeds 20261015 to 20261020) plus `experiments/crash-consistency/` (`RESULTS.md`, `FINDINGS-2026-11-02.md`). Post-kill checks: world opens, `verify()` True, all states parse, `version()` equals highest COMMITTED seq. The 2026-11-02 investigation showed the one observed failure mode was a test setup race (worker had committed 0 rows before the kill on a slow disk), not a durability violation. Storage basis: WAL mode (`PRAGMA journal_mode=WAL`, `core.py:197`); no explicit `PRAGMA synchronous` is set anywhere in `core.py` (checked by grep), so durability rests on SQLite WAL defaults.

11. **Per-field authenticated encryption and cryptographic redaction. VERIFIED as implemented; construction is custom (see E4 in the delivered audit notes).**
    `src/world/fieldcrypto.py`: HMAC-CTR keystream with encrypt-then-MAC, domain-separated subkeys, envelope bound to AAD of world name plus field path plus key id. `World.encrypt_fields`, `update_encrypted`, `decrypt_fields`, `redact`, `redact_field`, `redaction_status`. Redaction deletes the wrapped data key from `field_keys`; ciphertext stays in the chain and `verify()` still passes. `redact` requires unwrapping with the master key first, so a wrong key shreds nothing. Tests: `tests/test_world_encryption.py` (13 tests).

12. **Merkle inclusion proofs over row hashes. VERIFIED.**
    `World.merkle_root`, `inclusion_proof(seq)`, `verify_inclusion(proof)` (standalone, no DB access), domain-separated internal nodes. Tests: `tests/test_world_merkle.py` (6 tests). Caveat: the root is only as trustworthy as its distribution channel.

13. **Independent chain verification exists. VERIFIED.**
    A C# verifier (`tools/ChainVerifyWorld`, zero NuGet dependencies, reads via the `sqlite3` CLI in read-only mode) reimplements chain verification with no shared code; `tests/test_csharp_verifier.py` (4 tests). A bug in the Python verifier therefore cannot mask a broken chain by itself.

14. **Full test surface. VERIFIED as baseline.**
    354 `def test_` functions across 47 files in `tests/` (counted by grep in this audit), expanding to the established 377 passing tests with parametrization. Inventory by area: core 22, invariants 21, SDK 34, intent metadata 22, CLI/server 16 plus 7 plus 12, signing 7 plus 11, encryption 13, key rotation 8, OCC 5, blame 6, batch 8, merkle 6, handoff 8 plus 2 regression, redteam 14, protocol model 4, crash consistency 1, soak 1 (the 1,060,000-row soak from prior records: `verify()` True, with the honest finding that `verify()` is O(n) memory, about 659 MB RSS at 1.06M rows; visible in code, `verify()` uses `fetchall()` over all rows).

## B. Attempted but not guaranteed

1. **Actor attribution. Attempted only.**
   `actor` is a free-text, nullable, caller-supplied string everywhere: `World.update(actor=...)`, CLI `--actor`, HTTP body `actor` (`src/world/server.py:149` passes `body.get("actor")` straight through). It is covered by the row hash, so it cannot be edited after the fact without detection, but nothing authenticates that the named actor made the write. `docs/SECURITY.md` lists per-actor identity as mitigation 4, still open (ADR 0006). Any audit conclusion of the form "agent X decided Y" rests on self-assertion.

2. **Invariant enforcement is per-handle, not per-world. Attempted only at the deployment level.**
   Invariants live on the `World` handle at construction; they are not stored in the database. Two handles on the same world with different invariant lists judge differently, and a handle with no invariants judges nothing. The CLI path proves the point: `cmd_update` in `src/world/cli.py` builds the handle via `_world(args)` with no invariants; only `world serve --invariants module:attribute` and `create_app(invariants=...)` install rules. `src/world/server.py`'s module docstring acknowledges this: the server is "the uniform-enforcement point that in-process callables alone cannot provide", which is true only if every writer actually goes through that server.

3. **Invariant judgment under concurrency without OCC. Attempted only.**
   In `update`, judgment runs lock-free against the fast-path read (an intentional, commented design decision in `core.py`). If two writers race without `expected_version`, the second judgment was made against a state that may no longer be current at commit, and the write is last-writer-wins. `spec/linearizability.py` documents this honestly: the abstract state is linearizable, a commit may legally land any proposed value on the non-OCC path, and a REJECTED row's seq order can diverge from the linearization order. Invariants are therefore guarantees about judged transitions, not about the committed sequence, unless callers use `expected_version`.

4. **Timestamps as ordering or time evidence. Attempted only.**
   `timestamp` is `_utcnow()` from the host clock at append time (`core.py` `_append`). It is hash-covered, so post-hoc backdating is detected, but `docs/SECURITY.md` attacker A4 states the host clock is not trusted time. Seq, not timestamp, is the real order.

5. **Deterministic replay in the primitive. Absent, despite the vocabulary.**
   `src/world/` has no replay function. It does not need one for state reconstruction: every version row stores the complete document, so `state(version=N)` is snapshot retrieval, not replay. `replay_ledger()` exists only in the legacy `world_engine` (`src/world_engine/core/engine.py`, `tests/test_replay.py`, 8 tests) for that engine's entity tables. The primitive's `World.resume` and CLI `import` are the nearest analogues, and CLI `import` explicitly builds a fresh chain with new timestamps and hashes and skips REJECTED rows (`src/world/cli.py`, `cmd_import` docstring): it is a content copy, not an audit-faithful transfer.

6. **The state model itself. DOCUMENTED, not implemented.**
   `docs/state-model.md` is headed "Draft v0.1" and states it "becomes real only after the handoff experiment validates that these entities... are what actually prevent information loss." Its entities (Project, Task, Decision with `status` and `supersedes_id`, Assumption with `confidence` and `status`, Evidence, Artifact, Action, StateChange, Question, Handoff) and its cross-cutting provenance block (`created_by`, `created_at`, `source`, `supersedes`) are not tables, not validated, and not enforced anywhere in `core.py`. Core storage is one opaque JSON document per version. The model exists only as a convention authors may follow inside that document, which is exactly how the #002 and #003 bundles used it (as Markdown).

7. **Confidentiality. Not attempted by the chain; partially attempted by field encryption.**
   Documents, notes, actors, and rejected attempts are cleartext in the DB file (attacker A1 in `docs/SECURITY.md`). Only fields explicitly passed to `encrypt_fields` are protected. Read endpoints in both HTTP servers are unauthenticated even when write keys are set (by design, for demo viewability).

## C. Experimentally validated vs unverified

Experiment #003 (preregistered 2026-11-03T03:33Z, `experiments/experiment-003/protocol.md`; results in `REPORT.md`, `analysis/tables.md`, `analysis/results.json`): 8 tasks, 3 conditions, 72 of 72 continuations completed and blind-graded, zero failures. All results PRELIMINARY, single model family, n=24 per condition (21 for M3, 18 for M5), no significance tests per preregistration.

**What #003 established (EXPERIMENTALLY OBSERVED, narrow):**

- M3 assumption retention: A 0.721 vs B 0.500 vs C 0.488 (paired +0.221 and +0.233). A higher in 5 of 7 assumption-bearing tasks, never lower. Verdict composition over 45 items per condition: A 24 full / 15 partial / 6 miss; B 6 / 30 / 9; C 6 / 29 / 10. The mechanism is visible in the data: baselines recovered assumption substance but lost confidence level or fact-vs-assumption status. This is evidence about explicit metadata fields in a document, nothing more.
- M2 constraint retention: 1.000 in all conditions, zero hard failures in 72 continuations, including C1's missing-datum trap, which no continuation filled with an invented value.
- M10 efficiency: WORLD bundles totaled 20,382 words vs 6,142 (summaries) and 7,488 (journals); preservation per 1,000 words lowest for A on all 8 tasks. The structure costs 2.7x to 3.3x the words.

**What #003 did not establish (and must not be cited as establishing):**

- Revision history. M5 scored 1.000 in all three conditions: all 33 chain instances per condition (R1, R2, F1, S1) reconstructed with all 6 checklist elements (original, revised, what changed, why, authoritative version, provenance), zero failure-cause codes. H2 predicted the largest WORLD advantage here; it failed. Three candidate explanations are recorded in `REPORT.md`: the parity gate forced revision elements into every artifact, the chains were fewer and cleaner than #002's, and single-grader leniency at ceiling. Consequence for Prompt 3 prioritization: #003 provides no positive evidence that revision representation needs engineering work, and no evidence that the current representation fails. The only failure evidence is Experiment #002 (next item), which used a different protocol without a parity gate.
- Decision retention superiority. M1: A 0.948 vs B 0.979 vs C 0.979 (paired -0.031 both). The entire gap is task C1: all three A continuations earned partial credit on decision D1 while all B and C continuations earned full credit, and judged quality on C1 was A 2.0 vs B 3.0 and C 3.0. Reading the C1 bundle (`artifacts/C1/state.md`) shows why this is plausibly a representation effect worth one targeted look: D1 is recorded with status "proposed" (correctly, since capacity and catering were unresolved) among five "accepted" decisions, and the bundle is explicit that D1 is not final. A successor skimming statuses can underweight the venue evaluation itself. But n=3 on one task, one grader, is a hypothesis, not a demonstrated defect.
- Provenance superiority. M4: A 0.880, B 0.872, C 0.880. Tie. Residual losses were shared across conditions on the same items (C2 E1 to E3, S1 E3, S2 E4, C1 E5 and E6 partial nearly everywhere), which points at source ambiguity in the tasks rather than representation.
- Unsupported inference safety. M7 confirmed fabrications: 0 in all conditions. But unverifiable additions (plausible material in neither artifact nor ground truth) occurred only under A: 12 across 24 continuations vs 0 and 0. H3 predicted the opposite direction. No storage-layer mechanism in WORLD was ever going to prevent a successor agent from adding plausible material; this is a consumption-behavior finding, and it cuts against any claim that structure alone disciplines inference.

**Experiment #002 (for the revision question, the only contrary evidence):**
WORLD revision history scored 2 of 5 in both runs (Intel and Disney), while the raw journal scored 3 and 4 of 5 respectively (`docs/experiment-002/results.md`, metric 5). WORLD won assumption preservation (5 vs 3 and 3 in the main run) and confidence preservation in #002 as well, consistent with #003's M3. Reference means: Intel WORLD 3.92 vs journal 3.58 vs summary 3.33; Disney WORLD 4.45 vs summary 4.09 vs journal 2.82. n=1 continuation set per condition per run, exploratory.

**Weighing the revision evidence:**
The honest position is DOCUMENTED and unresolved. #002 says a WORLD bundle lost revision narrative to a raw journal twice. #003 says that under parity-gated, cleaner chains, every representation reconstructed every chain perfectly. The #003 protocol differences (parity gate compressing differences, fewer chains, possible grader ceiling) are sufficient to explain the discrepancy without either experiment being wrong. What is not contestable is the code-inspection finding (section D1): neither shipped schema, `handoff.AgentState` nor the 001 harness schema, can even express the fields the M5 checklist grades. The bundles that scored 1.000 in #003 were hand-authored Markdown using `docs/state-model.md` fields that no code in the repo validates, stores as structure, or reconstructs. So revision-model work is justified as closing a demonstrated expressiveness gap between the research schema and the shipped schema, not as fixing a demonstrated experimental failure. Any Prompt 3 claim stronger than that would misrepresent #003.

**Unverified overall (NEEDS VALIDATION):** any claim that WORLD improves agent reliability in general; cross-model transfer; human grading (no human grader in #003; a 25 percent human-graded subset, 18 continuations, is preserved and possible); token-level efficiency (word counts only); behavior of the actual `World` class as a handoff medium (never used in #002 or #003).

## D. Weaknesses mapped to evidence

**D1. The shipped handoff schema cannot express what the research schema and the winning metric require.**
(i) Location: `src/world/handoff.py`. `Decision` is `text` plus `rationale` only (lines 33 to 46). `Evidence` is `claim` plus `source` only. `AgentState` has exactly five sections: `objective`, `decisions`, `evidence`, `open_questions` (plain strings), `next_actions` (plain strings). There is no assumptions section at all, no `confidence`, no `status`, no `supersedes`, no entity `id`, no provenance block. Compare `docs/state-model.md`: Decision requires `id`, `status` (proposed, accepted, superseded, reversed), `evidence_ids[]`, `supersedes_id?`; Assumption requires `confidence` (low, medium, high) and `status`; every entity requires provenance.
(ii) Failure mode: a successor using the supported API (`save_state` / `load_state`) cannot record that a decision was superseded, that an assumption is an assumption with medium confidence, or what evidence supports a decision, except by burying it in free text, which is precisely the loss mode #003 measured in summaries and journals. Persistence compounds it: `save_state` stores `state.to_dict()` under the `handoff` key of the opaque document, so core storage persists exactly these fields and no others. The fuller schema is serialization-free prose convention only.
(iii) Evidence: #003 M3 mechanism (the fields that survived were confidence and fact-vs-assumption status, present in the hand-authored bundles, absent from `AgentState`); #003 REPORT code-inspection finding (the 001 harness flat schema lacks confidence, status, revision chains, supersession); direct code inspection here. This is the single best-supported defect in this audit.

**D2. No explicit revision model in storage; revision history is whole-document snapshots plus free-text notes.**
(i) Location: `core.py` `_SCHEMA` (no revision, parent, or supersession columns beyond the chain's `prev_hash`); `World.history()` returns only `seq, timestamp, actor, note, status` per row (no state); `World.proposal(seq)` returns one full row; `World.blame(path)` walks committed snapshots comparing one dot-path between consecutive committed versions.
(ii) Failure mode: see section G. In short: version numbers order document snapshots, not entity revisions; REJECTED rows interleave with committed ones; unrelated edits share a version; the reason for a change exists only if the author put it in the `note` string or inside the document.
(iii) Evidence: code inspection; #002 revision score 2 of 5 twice (motivation, not proof, per section C).

**D3. HTTP write endpoints fail open when no API key is configured.**
(i) Location: `src/world/server.py`. `create_app(..., api_key=None)` default; `_guard` (near line 79 to 95) checks the key only `if api_key is not None`; startup logs a warning ("WORLD_API_KEY not set: write endpoints are unauthenticated") and serves anyway. The legacy engine has the same shape: `src/world_engine/api/auth.py` `require_api_key` returns silently when `expected_api_key()` is None.
(ii) Failure mode: a deployment mistake (env var unset) silently yields a fully writable public endpoint for update, checkpoint, and resume. Missing credentials do not merely fail to authenticate an actor; they disable authentication entirely. The design is documented as a local-dev convenience and is tested as intended behavior: `tests/test_api_security.py::test_write_routes_open_without_api_key` and the module docstring state that with no key, everything is open.
(iii) Evidence: documented security requirement (ADR 0006 trigger, `docs/SECURITY.md` Part B item 2: authentication required before any multi-tenant or public deployment) plus code inspection. This is a fail-open default, even if a deliberate one.

**D4. Checkpoints are not integrity-protected.**
(i) Location: `checkpoints` table in `_SCHEMA`; `verify()` reads only `versions`.
(ii) Failure mode: an attacker with DB write access can repoint a checkpoint name to a different seq; `state(checkpoint=...)` and `resume()` then serve the wrong snapshot with a clean `verify()`.
(iii) Evidence: `test_checkpoint_repoint_undetected_documents_limit` (asserts the attack succeeds); `docs/SECURITY.md` mitigation 2, still open.

**D5. Idempotency state is not tamper-evident.**
(i) Location: `idempotency` table in `_SCHEMA`; `verify()` does not cover it.
(ii) Failure mode: deleting a key row lets a retry commit a second time while the chain verifies cleanly; exactly-once degrades to at-least-once invisibly.
(iii) Evidence: `test_idempotency_deletion_enables_double_apply_documents_limit`; `docs/SECURITY.md` limit 4.

**D6. `verify()` alone cannot detect rollback or rewrite; protection is opt-in and out-of-band.**
(i) Location: `verify()` vs `sign_tip` / `verify_tip` split in `core.py`.
(ii) Failure mode: any consumer who calls only `verify()` (the CLI `world verify` path does exactly this) gets a True answer on a truncated or fully rewritten chain. Signed tips fix this only for a holder who stored a tip out-of-band before the attack and checks it after; nothing in the storage layer prompts or requires that workflow.
(iii) Evidence: redteam limit tests (section A8); `docs/SECURITY.md` mitigation ranking, where signed checkpoints are built but WORM storage (mitigation 3) remains open.

**D7. No per-actor authorization anywhere.**
(i) Location: `core.py` (no authorization concept in `update`), `server.py` (single shared API key; any key holder can write as any `actor`), `world_engine/api/auth.py` (same).
(ii) Failure mode: one leaked key is total write access with arbitrary self-asserted attribution; there is no way to permit agent A to propose while reserving commits to agent B.
(iii) Evidence: ADR 0006 deferred in `docs/SECURITY.md`; code inspection. Ranked lower than D3 because no multi-actor deployment requirement is documented yet; it becomes necessary the moment one is.

**D8. Whole-document storage and whole-chain verification scale linearly in memory and size.**
(i) Location: `_SCHEMA` stores the full document text in every row; `verify()` uses `fetchall()`; `blame()` loads all committed snapshots up to the target version.
(ii) Failure mode: storage grows as versions times document size with no delta encoding or compaction; verification RSS grows with row count (measured about 659 MB at 1.06M rows in the soak record); `blame` on a long history is O(history times document size) per call.
(iii) Evidence: soak test record (`tests/test_soak.py`); code inspection. Not a correctness defect; a documented performance ceiling (see F5 for the one cheap fix).

**D9. Handoff bundle size is a measured cost with no projection mechanism.**
(i) Location: `handoff.py` has no projection, selection, or summarization; `load_state` returns the full stored `AgentState`, and the #003 bundles were complete state dumps.
(ii) Failure mode: successors pay 2.7x to 3.3x the context for preservation that was equal on most metrics; on tasks with few decisions (C2, 281 words) the overhead ratio is worst (preservation per 1,000 words A 2.966 vs B 8.865).
(iii) Evidence: #003 M10 and `analysis/tables.md` efficiency table.

**D10. Minor: `kid` verification is permissive when a tip omits `kid`.**
(i) Location: `verify_tip` and `verify_tip_ed25519` in `core.py`: `if tip_kid is not None and tip_kid != want_kid: return False`.
(ii) Failure mode: a tip with no `kid` verifies under any key that produces a valid signature for the message, so `kid` is a routing hint, not a binding. The docstrings say exactly this ("It is a routing hint, not a security boundary"), so the behavior is documented, but a verifier who treats `kid` as identity will be misled.
(iii) Evidence: code inspection; documented in `sign_tip` docstring.

## E. Security and authorization findings

**Assets.** The versions chain (state documents, notes, actors, rejected attempts); checkpoint pins; the idempotency table; per-field data keys (`field_keys`, wrapped); signing keys (HMAC secret, Ed25519 private key, field master key), all held out-of-band by design and never written to the DB (verified by code inspection of `sign_tip`, `sign_tip_ed25519`, `encrypt_fields`: keys arrive as arguments and are not persisted; the exception is `field_keys.wrapped_key`, which is ciphertext under the master key).

**Threat actors** (from `docs/SECURITY.md`, confirmed against code): A1 read access to the DB file (sees everything not field-encrypted); A2 write access to the DB file (arbitrary SQL, bypasses the API); A3 API-constrained writer (bound by invariants and the commit protocol); A4 host compromise or clock control (out of scope, owns the verifier too).

**Trust boundaries.** (1) Caller to `World` handle: no authentication; invariants are the only gate, and only the invariants that handle was constructed with (B2). (2) HTTP client to server: one shared API key on writes when configured; reads open. (3) DB file holder to chain: unkeyed hash chain, tamper-evident only. (4) Tip holder to chain: keyed (HMAC) or public-key (Ed25519) authenticity for the tip only. (5) Master-key holder to encrypted fields: authenticated encryption; everyone else sees ciphertext envelopes inside otherwise cleartext documents.

**Fail-open findings.**
- F-open 1 (primary): `src/world/server.py`, `_guard`: `if api_key is not None` guard means `api_key=None` disables the check entirely; default `create_app` and default `world serve` (key from `--api-key` or `WORLD_API_KEY` env) both reach this state; the only signal is a startup log warning. Legacy twin: `src/world_engine/api/auth.py`, `require_api_key` early-returns when the env var is unset. Both are intentional local-dev behavior, tested as such (`tests/test_api_security.py`), and both violate the rule that missing credentials must not silently grant access the moment the process is reachable by anyone else. The CLI default host is 127.0.0.1 (`cmd_serve`), which mitigates but does not remove the issue: binding is one flag away from exposure.
- F-open 2: read routes (`/v1/state`, `/v1/history`, `/v1/proposals/{seq}`, `/v1/checkpoints`, `/v1/verify`) have no gate even when a key is set. Rejected proposals, including their full documents and notes, are readable by anyone who can reach the port. Documented as demo viewability; it is a data-exposure decision, not an oversight, but it belongs in any deployment checklist.
- No other fail-open path was found: `verify_tip` and `verify_tip_ed25519` return False on malformed input, algorithm confusion (an HMAC tip passed to the Ed25519 verifier is rejected on the `alg` field), name mismatch, and kid mismatch when a kid is present; `fieldcrypto.decrypt` raises on any tag mismatch (`hmac.compare_digest`); `redact` refuses on a wrong master key before deleting anything; server key comparison uses `hmac.compare_digest` (`server.py:84`).

**Key management facts.** Ed25519: vendored pure-Python implementation in `src/world/ed25519.py`, RFC 8032 construction, validated against RFC 8032 section 7.1 vectors in tests; the module itself warns it is not constant-time and runs at tens of operations per second (measured about 147 signs per second and 109 verifies per second in prior records). `create_keypair(seed=None)` uses `os.urandom(32)`. HMAC tip keys: arbitrary bytes or str supplied by the caller; fingerprint is the `kid` default. Rotation: Ed25519 only, via old-key-signed certificate (`rotate_ed25519`); HMAC rotation is a documented dual-signing protocol with no API. No key storage, escrow, or revocation exists in the repo; compromise of an old Ed25519 key cannot be un-done for signatures already issued (stated in the `rotate_ed25519` docstring).

**Hash chain vs authenticity, as the code actually implements it.** `_row_hash` is SHA-256 over a canonical field join with no key. Anyone who can write the file can recompute a fully consistent forged chain (proven by `test_full_rewrite_undetected_documents_limit`). The chain therefore provides tamper evidence against partial edits and accidental corruption, and nothing else. Authenticity exists only at the tip, only when a caller used `sign_tip` or `sign_tip_ed25519` and stored the result out-of-band. Merkle roots (`merkle_root`, `inclusion_proof`) are computed over the same unkeyed row hashes: an inclusion proof convinces a verifier that a row belongs to a chain with a given root, but the root itself is unauthenticated unless it was distributed or signed out-of-band (the `merkle_root` docstring suggests publishing or signing the root; `sign_tip` signs the tip `(name, seq, hash)`, not the Merkle root, so the suggested composition is a workflow, not a single API call).

**Malformed input and replay surface.** `update` rejects non-dict state and non-JSON-serializable state before any append; canonical JSON (`sort_keys`, `allow_nan=False`) makes row hashing deterministic. HTTP update bodies require `state` to be an object (400 otherwise). Replay of an HTTP write is bounded by the per-IP write rate limit (60 per minute default, in-memory deque in `server.py`; `X-Forwarded-For` honored only with `trust_forwarded_for=True`, a correct default) and by client-supplied `idempotency_key` when the client bothers to send one; the server generates no idempotency keys itself, so a retried POST without a key is a second commit by design (last-writer-wins absent `expected_version`).

## F. Proposed changes, ranked by necessity

Each change names its evidence. Nothing here is authorized by this audit; per standing rules, implementation requires review, and item F3b is flagged STOP AND ASK.

**F1. Bring the shipped handoff schema up to the research schema (highest necessity).**
Problem: D1. `handoff.AgentState` lacks assumptions entirely and lacks confidence, status, supersession, and evidence linkage on decisions, the exact fields #003 M3 showed are what structured representation preserves (paired +0.221 and +0.233) and that `docs/state-model.md` already specifies.
Minimal design: additive changes to `src/world/handoff.py` only. Add an `Assumption` dataclass (`text`, `confidence`, `status`) and an `assumptions` list on `AgentState`. Extend `Decision` with optional `id`, `status` (default "accepted"), `supersedes` (prior decision id or None), `evidence_ids` (list). Extend `Evidence` with optional `id` and `kind`. All new fields optional with defaults, and `from_dict` tolerant of their absence, so every existing stored handoff still loads.
Why existing architecture is insufficient: the fields do not exist in the only agent-facing schema; no amount of core work fixes a serialization layer that drops the data at `to_dict()` time.
Backward compatibility: full. Core storage is opaque JSON; no schema change, no migration. Old bundles load; new bundles written to old readers would drop unknown fields only if the old `from_dict` is used, which is a versioning note for the docs, not a data risk.
Tests: extend `tests/test_handoff.py` with round-trip tests proving confidence, status, and supersession survive `save_state` / `load_state` and survive a `World.resume`; add a loss test mirroring #003's grading (a Decision with `status="superseded"` and `supersedes` set must be recoverable as superseded, not as current). Model checking: no impact; the checker abstracts documents as opaque tokens, and P1 to P6 are unaffected. Revalidation hook: a small #003-style continuation check using the new schema is the honest follow-up experiment, with harder revision tasks per the #003 recommendations.

**F2. Fail closed on HTTP writes unless unauthenticated mode is explicit.**
Problem: D3 and E F-open 1.
Minimal design: `create_app` gains `allow_unauthenticated_writes: bool = False`; `world serve` gains `--allow-unauthenticated`. When no API key is configured and the flag is absent, write routes return 401 (or the app refuses to start; route-level refusal is the smaller change and testable). Reads unchanged.
Why existing architecture is insufficient: a log warning is the only barrier between an unset env var and a public write endpoint; the current default is the insecure state.
Backward compatibility: behavior change for local-dev server users only; no data or API-shape change. Tests asserting open-by-default (`tests/test_api_security.py`, parts of `tests/test_world_cli_server.py`) must be updated to pass the explicit flag, which is itself the point: openness becomes a visible choice in code.
Tests: new cases: no key and no flag gives 401 on POST `/v1/update`, `/v1/checkpoint`, `/v1/resume`; no key with flag gives current behavior; key set behaves exactly as today. No model-check impact (server is outside the checked protocol).

**F3a. Make checkpoints tamper-evident (additive).**
Problem: D4.
Minimal design: record each checkpoint creation as data covered by the chain without changing existing tables: when `checkpoint(name)` pins seq S, also store, inside the checkpoints row, the row hash of S at pin time, and have `state(checkpoint=...)` and `resume` verify that the current hash at S still equals the pinned hash before serving. A repoint to a different seq then fails the hash comparison unless the attacker also rewrites the chain (which signed tips cover).
Why existing architecture is insufficient: today nothing binds a checkpoint name to chain content.
Backward compatibility: additive column with a default; existing checkpoint rows would carry no pinned hash and should be treated as unverified (documented), or backfilled on first read from the current chain, which is safe because backfill only records current state. No breaking change.
Tests: a new redteam test asserting repointing is now detected, and the existing `test_checkpoint_repoint_undetected_documents_limit` updated only after the behavior change is approved, since it currently pins the limit.

**F3b. STOP AND ASK: binding idempotency keys into the row hash.**
Problem: D5. The clean fix (include `idempotency_key` in the `_row_hash` payload so the committed row itself proves its key binding) changes the hash function, which makes every existing database fail `verify()` under the new code. That is a breaking migration of the chain format and must not be designed around silently. Alternatives that avoid the break (a parallel chained table for key bindings; periodic signed tips covering the table) are weaker or operational. Recommendation: present the trade-off and ask before choosing. Do not implement in the same batch as F3a.

**F4. Server-side actor binding when a key is configured.**
Problem: B1 and D7, narrowed to what is justified now. With a single shared key there is no real identity to bind, so full RBAC is not justified (see rejected list). The justified minimum: when `api_key` is set, the server should not silently accept a body `actor` that contradicts a configured server-side actor label; simplest honest version, add an optional server config `actor` that overrides the body's, and document that body-supplied actor is self-asserted in all other modes.
Why existing architecture is insufficient: nothing anywhere distinguishes asserted from authenticated attribution, and the history log presents both identically.
Backward compatibility: default off, no change unless configured. Tests: server tests for override behavior. Model check: actors are abstracted away in `spec/model_check.py`, no impact. This is deliberately smaller than ADR 0006 RBAC; it documents the boundary instead of pretending to close it.

**F5. Stream `verify()` instead of `fetchall()`.**
Problem: D8, the O(n) memory half only.
Minimal design: iterate the versions query with a cursor in `verify()` (and consider the same for `blame()`'s snapshot walk in a second step).
Why: measured RSS growth in the soak record; the fix is mechanical and semantics-free.
Backward compatibility: total; same return value. Tests: existing verify and fuzz suites must pass unchanged; add a large-chain test asserting bounded behavior only if a memory assertion can be made non-flaky, otherwise rely on the soak. No property impact: P2 is about linkage, not loading strategy. The storage half of D8 (full document per row) is not addressed; delta encoding would be a format change and is rejected below.

**F6. A handoff projection helper (efficiency, lowest necessity of the accepted set).**
Problem: D9 and #003 M10.
Minimal design: a pure function in `handoff.py` (or the experiment harness) that renders a continuation bundle selecting current authoritative items: accepted decisions, active assumptions, open questions, key evidence, plus superseded items in compact one-line form with their supersession pointers. No storage change; it consumes `load_state` output.
Why existing architecture is insufficient: `load_state` returns everything or nothing; the measured cost is paid by every successor.
Backward compatibility: additive, opt-in. Tests: projection completeness tests (every accepted decision and active assumption present; no superseded item presented as current). Validation: rerun the R1, R2, and C1 tasks with projected bundles under the #003 rubric and compare M1, M3, M5, and M10 against the preserved originals; if M5 drops, the projection is wrong and should be withdrawn. This ordering matters because #003 gives no license to assume a smaller bundle is safe for revision reconstruction.

**Changes considered and REJECTED as unnecessary complexity:**
- A core revision-history table or entity store in `core.py` (new tables for decisions, assumptions, StateChange rows). Rejected for now: #003 found no revision failure to fix (M5 at ceiling), #002's contrary result is protocol-confounded, and F1 plus the section G model captures the demonstrated need inside the existing opaque-document architecture. Revisit only if a discriminating revision experiment (harder chains, no parity gate on revision elements, human grading) demonstrates a storage-level failure. Building it now would be exactly the impressive-sounding, evidence-free change Prompt 3 forbids.
- Replacing the vendored pure-Python Ed25519 with an external library. Rejected: it breaks the stdlib-only property the repo deliberately maintains, the implementation is RFC 8032 validated, and its performance (about 109 verifies per second) is adequate for tip signing, which is one signature per checkpoint, not per row. The non-constant-time caveat is documented in the module and is a real but accepted risk at this threat level.
- Delta or diff-based version storage. Rejected: full snapshots are what make `state(version=N)`, `blame`, and checkpoint resume simple and obviously correct; the cost is quantified (D8) and does not yet bind at research scale.
- A general RBAC or multi-tenant authorization system. Rejected as premature: ADR 0006 defers it, no second-party deployment exists, and F4 marks the honest boundary at a fraction of the complexity.
- Zero-knowledge audit proofs. Already evaluated and declined in the repo's own spike (`docs/research/zk-audit-spike.md`, referenced from `merkle_root`); Merkle inclusion proofs cover the demonstrated selective-disclosure need.
- Automated detection of unverifiable additions (the M7 finding). Rejected as a storage-layer change: nothing in a ledger can prevent a successor agent from writing plausible new material in its own continuation; the mitigation belongs to continuation instructions and grading, not to WORLD's architecture.
- Executing the TLA+ specification. `spec/world.tla` exists as a written specification; it has not been run through TLC in this environment (no JVM), and no claim in this audit treats it as checked. The Python explicit-state checker in `spec/model_check.py` is the executed verification artifact. Proposing TLA+ work now adds a second formalism without a property the Python checker cannot express.

## G. Revision-history design sketch

**What the current representation can reconstruct today, demonstrated from the code.**

Take a world where a decision changed across three committed updates, with one rejected attempt in between.

- `World.version` gives the seq of the latest COMMITTED row: the authoritative snapshot pointer. P3 guarantees this is the max committed seq.
- `World.state()` returns that snapshot; `World.state(version=N)` returns the complete document at any committed seq. So "what was the decision at version N" is answerable exactly, for any N, by reading the snapshot. This is the genuine strength of full-snapshot storage.
- `World.history()` returns, per row, `seq, timestamp, actor, note, status`, oldest first, REJECTED rows included. It returns no state, so from `history()` alone you know who claimed to act, when the host clock said it happened, what free-text note was attached, and whether each attempt committed.
- `World.proposal(seq)` returns the full row including its document, for committed and rejected rows alike: the rejected attempts are auditable.
- `World.blame(path)` answers, for one dot-separated path, which committed version last changed that value, with `actor`, `note`, `timestamp`, and the old and new values at that path. CLI `world diff --from A --to B` computes a leaf-level diff between two snapshots.
- `World.verify()` proves the snapshots and metadata you are reading are the ones that were appended, subject to the section A8 limits.

**What it cannot reconstruct.**

- Entity-level revision chains. Versions are document snapshots, not entity revisions. If one update changes a price target, an assumption, and a typo, all three share one seq, one actor, one note. Nothing in storage links version N's decision D1 to version N+3's decision D1 as the same entity, because core storage has no entity ids at all; identity exists only if the document author maintained ids inside the JSON (as the #002 and #003 Markdown bundles did by hand).
- Parent revision in the semantic sense. `prev_hash` chains rows, including REJECTED rows, so the chain predecessor of a committed revision may be a rejected attempt or an unrelated edit. Seq adjacency is not revision parentage.
- Supersession as data. There is no `supersedes` field, no status field, and no current-version pointer per entity anywhere in `core.py` or `handoff.py`. "Which version of this decision is authoritative" is answerable at the document level (latest committed snapshot) but not at the decision level, except by parsing whatever status convention the author happened to write into the document text. In `handoff.AgentState` there is not even a convention available: `Decision` has no status field to write.
- Reason and evidence as structure. The reason for a revision lives in the row `note` (a single free-text string per document update, not per entity) or in `Decision.rationale` inside the document. Evidence linkage (`evidence_ids`) exists only in the unimplemented state model. Neither is validated: an author can omit the note, and nothing notices.
- Who, in any authenticated sense. `actor` is self-asserted (B1).

So the accurate one-line summary: version numbers plus the chain give a complete, tamper-evident sequence of whole documents, from which a patient reader can manually reconstruct any entity's history by diffing snapshots (`blame` and CLI `diff` automate the single-path case); they do not give revision history as a queryable structure, and the claim "revision history is preserved" is true only in the snapshot sense, not in the entity sense the six M5 checklist questions ask about.

**The simplest explicit revision model that closes the gap.**

Stay inside the existing architecture: no new core tables, no migration. Put the model in the handoff document schema (change F1) and derive the chain by computation, the same way `blame` already derives authorship from snapshots.

Data (inside the document, under the `handoff` key, all additive):
- Every `Decision` carries `id` (stable across revisions, assigned by the author or by `save_state` when absent), `status` in {proposed, accepted, superseded, reversed}, `supersedes` (the id of the decision it replaces, or None), `evidence_ids` (list of `Evidence.id`).
- Every `Assumption` carries `id`, `confidence` in {low, medium, high}, `status` in {active, validated, invalidated, stale}, `validated_by` (evidence id or None).
- Every `Evidence` item carries `id` and `kind`.
- `save_state` validates referential integrity within the submitted state: a `supersedes` target must exist, a decision marked superseded must be pointed to by exactly one successor or carry status reversed, `evidence_ids` must resolve. Violations raise before the update is proposed, so a malformed revision graph never becomes a committed snapshot. This is a serialization-layer check in `handoff.py`, deliberately not a core invariant, because core must stay domain-free.

Derivation (the revision chain as a computed view, mirroring `blame`):
- A `revision_chain(world, decision_id)` helper walks committed snapshots from oldest to newest (skipping REJECTED rows, as `state()` semantics already define), extracts the decision with that id from each snapshot's handoff section, and emits one entry per snapshot where the decision's text, status, or rationale changed: `{seq, timestamp, actor, note, status, text, rationale, supersedes, evidence_ids}`. Consecutive identical entries collapse.
- The six required questions then have mechanical answers: original decision (first entry), what changed (diff of consecutive entries' text and status, the same leaf-diff the CLI already implements), who (entry `actor`, labeled self-asserted), why (entry `rationale` plus the row `note`), what evidence (entry `evidence_ids` resolved against that snapshot's evidence list), which version is authoritative now (the entry in the latest committed snapshot whose status is accepted, with the helper raising or flagging if the latest snapshot marks it superseded with no successor, which is exactly the inconsistency the `save_state` validation is designed to prevent).

Why this is sufficient and why it is the simplest sufficient thing: the storage layer already preserves every input this computation needs (complete snapshots, actor, note, timestamp, status per row) and already proves their integrity (chain plus optional signed tips). The demonstrated gap was never storage; it was that the schema could not express the fields (D1) and that no code assembled them into a chain. This design fixes both without touching the checked commit protocol, so P1 to P6 remain valid without re-verification of a changed transition system, and existing worlds are unaffected because the handoff key is opt-in.

What it still does not give, stated plainly: per-entity reasons when one update revises several decisions for different reasons (the row `note` is shared; `rationale` per decision is the mitigation, and it is author discipline, not enforcement), authenticated authorship (F4 only narrows this), and any protection against an author who simply writes a fresh decision with a new id instead of superseding the old one (validation can check the graph that is submitted; it cannot detect the graph that should have been submitted). Those are the honest limits to carry into the next experiment, whose design (harder chains, split sources, no parity gate on revision elements, human grading of a subset) is already specified in the #003 report's recommendations and is the correct gate for any future proposal to move revision structure down into core storage.

## Summary judgment

VERIFIED core: an append-only, tamper-evident, model-checked commit protocol (P1 to P6, 1,220,255 states) with OCC, idempotency, invariant judging, signed tips, and field-level crypto-shredding, at 377 passing tests. The best-supported defect is not in that core; it is the gap between the research state model and the shipped `handoff.AgentState`, which cannot express the assumption metadata that produced WORLD's only consistent experimental win (M3) or the revision structure both experiments graded. The clearest security defect is a fail-open HTTP write default (D3). Revision-history engineering beyond the schema-level model in section G is not justified by current evidence: #002 and #003 conflict, #003's ceiling result is protocol-confounded, and the discriminating experiment has not been run. Two items need a decision before implementation: the F3b hash-format question (STOP AND ASK) and approval of the F1 schema additions with their validation rules.
