# WORLD: Status Dashboard

**Purpose:** single-pointer dashboard. Long-form state lives in
`research/RESEARCH_OVERVIEW.md` and the evidence register in
`research/EVIDENCE_REGISTER.md`.

**Updated 2026-11-26** (Mission Day 15, Prompt 2). **Version:** 0.1.0.
**License:** MIT. **Not deployed, not production-ready, no external
users.**

**Tests:** 504 passing, 0 failing (full suite run locally
2026-11-26, Python 3.12.3, on the mission Day 15 branch tree).
**Model checker:** 1,220,255 states explored (three
configurations), properties P1 to P6 hold; mutation test catches
the injected P4 violation. **CI:** pytest on Python 3.11, 3.12,
3.13; ruff and mypy in a separate lint job on Python 3.12
(unpinned tool installs, a known weakness, see open items).

**Committed and pushed 2026-11-11:** Prompt 3 (below) and
Experiment #003 were committed locally as `0dca725` (Experiment #003),
`8288dd4` (Prompt 3), and `9ef3591` (Prompt 6), and pushed to remote
main (remote commits `44b0ff2`, `db5b477`, `5e38886`, plus CI follow-ups
to `b2d63c4`). Local main (`2c5c3b2`) and remote main (`b2d63c4`) have
diverged histories but content-identical trees (verified by the mission
Day 1 audit, 2026-11-12). The work is unreviewed; every Prompt 3 line
below describes the shipped tree, not a working-tree-only state.

---

## Shipped (primitive, `src/world/`)

**World primitive.** One named world = one SQLite file. Stateless
handles, opaque JSON document, invariants judge every proposal,
COMMITTED and REJECTED verdicts appended to a SHA-256 hash
chain. Optimistic concurrency (`expected_version`: exactly one
winner), idempotent retries, checkpoints, committed-only time
travel via full snapshots, `blame`, `update_many` batches,
atomic `read()`. Documented in `docs/adr/0008-world-primitive.md`.

**Prompt 3 architecture strengthening (2026-11-04, committed locally
2026-11-11 as `8288dd4`, pushed as `db5b477`).**

- F1: handoff schema upgrade (`Assumption`, decision `id`,
  `status`, `supersedes`, `evidence_ids`, referential-integrity
  validation in `save_state`), `revision_chain` view.
- F2: HTTP server fails closed; `--allow-unauthenticated` is the
  explicit local-development opt-in.
- F3a: checkpoint `pinned_hash` tamper evidence (verify on read
  and resume).
- F4: server-side actor override.
- F5: streaming `verify()` and `blame()`; peak-RSS delta on a
  20,000-version chain 19.7 MB to 0.8 MB.
- F6: `project_state` projection view.

**Optional layers.** Signed tips (HMAC, Ed25519 with rotation),
Merkle inclusion proofs, per-field encryption with
crypto-shredding redaction, transcript producer.

**Surfaces.** Python API, `world` CLI, `world serve` HTTP API.
Core dependency-free (stdlib only).

---

## Experiments (handoff evidence, `docs/` and `experiments/`)

- **#001 Block (2026-09-17):** WORLD won on governance, 5/5
  decisions with rationales, 7/7 assumptions with confidence,
  zero errors. n=1. DOCUMENTED.
- **#002 Intel + Disney replication (2026-09-17 to 23):** WORLD
  preserved decision governance best in both runs (Intel 3.92 vs
  3.58 vs 3.33; Disney 4.45 vs 4.09 vs 2.82, reference means);
  failed revision history in both runs (2/5). n=1 per run.
  DOCUMENTED, preliminary.
- **#003 (2026-11-03, preregistered, 8 tasks, 72 continuations,
  blind graded):** assumption retention is the one consistent
  advantage (A 0.721 vs B 0.500 vs C 0.488); decisions slightly
  favored baselines; revision history tied at ceiling (1.000
  all); unverifiable additions only under A (12); bundles cost
  2.7x to 3.3x the words. PRELIMINARY, single model family.
  Condition A was hand-authored Markdown; the `World` class was
  never exercised. Committed locally 2026-11-11 as `0dca725`, pushed
  as `44b0ff2`.
- **Prompt 3 revalidation (2026-11-04):** first runs through the
  shipped code path (R1, R2, C1, n=3 per cell). Preservation at
  or near the #003 structured level; no revision regression
  from projection. PRELIMINARY.

---

## Verification (primitive)

- **Model checker:** 1,220,255 states, P1 to P6 hold; mutation
  test proves it can fail. `docs/spec/protocol-verification.md`.
- **Lost-update:** 33/50 lost unprotected vs 0/50 with
  `expected_version` + retry (scripted agents). DOCUMENTED.
- **Crash consistency:** 15/15 recorded mid-transaction kills
  recovered; 39 further rounds (2026-11-02) with zero durability
  violations.
- **Soak:** 1.06M rows, integrity held; `verify()` at 75,921
  rows/s and 659 MB RSS in the 2026-10-15 run. Pre-F5 record;
  the soak has not been re-run at scale since streaming
  `verify()` landed.
- **Independent C# verifier:** reproduces chain verification
  with no shared code.
- **Coverage:** 95.16% total over the package plus `tools/`,
  `demo/`, and the root shims (measured 2026-11-24 with the CI
  command, mission Day 13); the CI gate is 85%.

---

## Open items (designed gaps and open decisions)

- **Revision history: unresolved.** #002 failure (2/5, both
  runs) against #003 ceiling (1.000, all conditions). Next:
  harder revision chains with no parity gate on revision
  elements, plus human grading of the preserved #003 25%
  subset.
- **F3b undecided:** bind idempotency keys into the row hash.
  Would break verification of existing databases; the
  idempotency table currently sits outside the chain.
- **Invariants are code, not data:** the database cannot name
  the rule set that judged a historical version. Persisted
  registry is designed, not built.
- **No per-actor identity:** `actor` is self-asserted; no RBAC.
- **External validation: pending.** The protocol is written
  (`experiments/prompt6/VALIDATION_PROTOCOL.md`); zero external
  reviewers have completed it.
- **Release blockers:** Prompt 3 and #003 unreviewed; no release
  approval. See
  `experiments/prompt6/RELEASE_READINESS.md`.
- **Legacy `world_engine` package** still ships in the repo;
  retire-or-merge is a roadmap item.
