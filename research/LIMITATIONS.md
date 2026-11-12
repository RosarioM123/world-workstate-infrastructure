# Limitations and negative findings

Everything in this file is a known limit of WORLD or a result that went
against the hypothesis. These are kept in the documentation on purpose:
a limitation with an artifact behind it is worth more than a claim
without one. Sources are the README, `docs/SECURITY.md`,
`docs/spec/protocol-verification.md`, the experiment results in
`docs/experiment-001-results.md` and `docs/experiment-002/results.md`,
and the experiment folders under `experiments/`.

## Negative findings from the handoff experiments

- **Revision history does not survive.** In Experiment #002, the WORLD
  continuation scored 2 out of 5 on revision-history preservation in
  both the Intel run and the Disney replication, losing the
  old-to-new-to-trigger revision chains (R1 to R3) the state was built
  to preserve. In the replication, the raw-journal continuation scored
  4 on the same metric. This is a replicated failure on one of the four
  things the hypothesis claims structured state preserves.
  Amendment (2026-11-05, Prompt 6): Experiment #003 (2026-11-03)
  scored revision history at 1.000 in all three conditions, a ceiling
  that cannot discriminate between representations, and the Prompt 3
  revalidation found no revision regression from the projection view.
  The current status is therefore unresolved, not a settled failure:
  #002 says structured state lost revision history when the task
  demanded old-to-new-to-trigger chains; #003's parity gate on
  revision elements likely compressed the differences. The
  discriminating experiment (harder chains, no parity gate on
  revision elements, human grading) has not been run. Sources:
  `experiments/experiment-003/REPORT.md`,
  `experiments/prompt3/revalidation/RESULTS.md`.
- **Near summary parity in one run.** In the Disney replication, an
  independently written, schema-free summary came within 0.36 of the
  WORLD continuation on the reference mean (4.09 vs 4.45). The
  falsifiability condition "summary parity" therefore remains open: if
  a well-written summary can get this close, the case for
  infrastructure over convention is narrow.
- **The Experiment #001 clean sweep did not repeat.** #001 (n=1) found
  structured state ahead on essentially every measure. The harder #002
  design (blind labels, predeclared answer key, independently written
  summary, 14 metrics) produced a narrower verdict: the direction
  replicated, the specifics did not, and the journal-versus-summary
  ordering flipped between the two #002 runs. With n=1 per run, the
  ordering of the conventional alternatives is instance-sensitive.
- **No handoff was lossless.** Every condition in #002 lost
  information, including the WORLD condition (revision chains,
  superseded-decision history in the main run, evidence IDs in the
  main run, part of one thread in the replication).

## Experiment methodology limits

The bullets in this section are scoped to Experiments #001 and #002
unless a bullet says otherwise; the #003 bullet set follows them.

- **n=1 per run (#001, #002).** Each run is a single task performed
  once per condition. Results are exploratory and are not statistically
  significant; means of metrics 1 to 10 plus 14 are reported as
  reference values only, per the protocol, which forbids collapsing
  them into a single score prematurely.
- **One model family throughout.** Success criterion 3 of
  `docs/hypothesis.md` (two different models producing consistent
  continuations from the same state) is untested.
- **No genuine context isolation.** Agent A and Agent B ran as
  subagents that inherit parent-conversation context; blinding was
  procedural (relabeled files, stripped headers, off-limits
  instructions, grader compliance checks), and the experiment record
  documents a residual blinding imperfection in the main run.
- **Experimenter-built answer keys.** The keys were predeclared before
  grading, and no corrections to them were needed in either run, but
  they are still the experimenter's construction. In the replication,
  the key-only grading could not distinguish inherited detail from
  invention on the unsupported-assumptions metric.
- **Scripted agents in the concurrency experiment.** The lost-update
  experiment (`experiments/lost-update/`) used scripted agents with
  stochastic timing, not LLM agents; an LLM-agent replication was
  planned but blocked because no model API credential was available
  when it was run (2026-10-15).

Experiment #003 methodology limits (2026-11-03, from
`experiments/experiment-003/REPORT.md`):

- **Condition A never exercised the shipped code.** The structured
  bundles were hand-authored Markdown built to `docs/state-model.md`,
  not produced by `save_state`. #003 measures the representation,
  not the implementation; the Prompt 3 revalidation is the first
  code-path run and covers only 3 of the 8 tasks at n=3 per cell.
- **Grading was blind agent grading, not human grading.** Eight
  grader sessions, anchored rubrics; no human has graded any #003
  output. A 25 percent subset (18 continuations) is preserved for
  future human grading.
- **The parity gate may have compressed revision differences.** M5
  scored 1.000 in all conditions (33 chain instances per condition);
  the gate enforced information parity on revision elements, which
  the #003 report itself flags as the likely cause of the ceiling.
- **Single model family, no significance tests.** n=24 per condition
  for most metrics (21 for M3, 18 for M5); means are reported
  descriptively, and paired deltas are small-sample.
- **Unverifiable additions appeared only under structured state.**
  12 under A vs 0 under B and C (fabrications were 0 everywhere);
  a real negative finding for the structured condition, not yet
  explained.

## System limits (the primitive)

- **Tamper-evident, not immutable.** The SHA-256 hash chain detects
  edits; anyone holding the database file can rewrite the whole chain
  consistently. Optional signed tips (HMAC, and Ed25519 with key
  rotation) anchor the tip externally only if the verifier holds the
  key or public key out of band. There is no consensus and no
  third-party witnessing by default. `docs/SECURITY.md` lists exactly
  which attacks `verify()` does and does not detect, including tested
  undetected cases (for example, tail truncation and fully recomputed
  chain rewrites). One former limit narrowed (Prompt 3 F3a,
  2026-11-04): checkpoints now record the pinned row's hash and
  `state()` / `resume()` verify it before serving, so repointing a
  checkpoint's seq is detected at serve time. `verify()` itself
  still does not cover the checkpoints table, the idempotency table
  remains outside the chain (its deletion still enables a double
  apply, undetected), and an attacker who rewrites both a
  checkpoint's seq and its pinned hash defeats the pin check.
- **Invariants are code, not data.** The database cannot name the rule
  set that judged a historical version. Two handles on one world can
  judge by different rules; `world serve` is the uniform-enforcement
  point for remote writers. A persisted invariant registry is on the
  roadmap, not built.
- **No per-actor identity.** The `actor` field is self-asserted. The
  HTTP API-key gate authenticates the deployment, not the writer.
  There is no RBAC. Two partial changes (Prompt 3, 2026-11-04): the
  HTTP server now fails closed when no API key is configured (writes
  return 401 unless unauthenticated writes were explicitly allowed),
  and a server configured with a fixed `actor` overrides body-supplied
  actor labels on writes. Neither identifies an individual writer.
- **Single-writer serialization.** Appends serialize on SQLite's write
  lock by design. Measured contention behavior
  (`docs/benchmarks/contention.md`, 2026-10-15): throughput plateaus
  near 810 ops/s past 8 writer threads and p99 latency degrades
  sharply (0.93 ms to 216.70 ms from 1 to 16 threads), while
  correctness holds. `expected_version` is optimistic concurrency, not
  a transaction across documents.
- **Local-first.** One SQLite file per world. No replication, no sync
  protocol; multi-machine sharing is out of scope for the primitive.
- **`verify()` is O(n) in time.** In the 1.06M-row soak
  (`experiments/soak/RESULTS.md`), full-chain verification took 14.0s
  and 659 MB RSS because it loaded the whole chain. The memory half
  is fixed (Prompt 3 F5, 2026-11-04): `verify()` now streams rows
  from the cursor, and on a 20,000-row chain the peak-RSS delta fell
  from 19.7 MB to about 1 MB (`experiments/prompt3/BENCHMARKS.md`).
  The 1.06M-row soak has not been re-run at that scale, so the
  at-scale memory figure remains the 2026-10-15 record. Verification
  time is still linear in chain length.
- **Model checking is bounded.** The protocol verification explores
  2 to 3 writers with 2 to 3 operations each (1,220,255 states total).
  That is exhaustive for those configurations, not a proof for all N.
  The TLA+ transcription in `spec/world.tla` has not been run through
  TLC (no JVM in the build environment); the Python checker is the
  authoritative artifact.
- **Crash testing covers process death only.** 15 of 15 SIGKILL rounds
  recovered cleanly, but host-level failures (disk loss, power cut
  mid-fsync) and crash-during-contention are out of scope.

## Validation limits (the project)

- **No external users.** WORLD has no deployments, no customers, and no
  external-user feedback. Design decisions rest on the maintainer's
  experiments, not on observed demand.
- **No production readiness claim.** Version 0.1.0, working prototype,
  not deployed. There is no hosted service, no uptime or support
  commitment, and no migration tooling beyond export/import of the
  ledger rows.
- **Benchmarks are single-machine records.** All performance numbers
  were measured on one Linux x86_64 machine (Python 3.12.3) on
  2026-10-15 and are dated as such wherever they appear. They are
  records of what one run measured, not guarantees.
