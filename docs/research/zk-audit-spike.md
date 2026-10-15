# Research spike: privacy-preserving audit proofs

**Date:** 2026-10-15. **Outcome:** full zero-knowledge proofs not
recommended; Merkle inclusion proofs shipped instead.

## Question

Can a WORLD holder prove audit statements (chain integrity, "every
committed row passed the invariants", "version N's document had field
X = v") *without revealing the log contents*?

## What ZK would require

1. **Arithmetizing the hash chain.** WORLD rows are SHA-256 chained.
   SHA-256 needs on the order of tens of thousands of R1CS constraints
   per compression; proving a 10k-row log means hundreds of millions
   of constraints, minutes to hours of prover time and gigabytes of
   RAM, per proof. (A Poseidon-based chain would be ZK-friendly, but
   changing the chain hash breaks every existing verifier and the
   threat model's "independent reimplementation" story.)
2. **Arithmetizing the invariants.** Invariants are arbitrary Python
   callables, the engine's core design choice ("anything else is a
   plain function you write"). They cannot be put in a circuit without
   rewriting them in a circuit DSL, which destroys the DX advantage.
3. **Toolchain weight.** circom/snarkjs or arkworks are non-stdlib,
   native-dependency toolchains with trusted-setup considerations for
   some schemes, at odds with the primitive's stdlib-pure posture.

## What the threat model actually needs

WORLD's audit model assumes auditors *can* read the log; tamper
evidence is about detecting modification, not hiding content. The real
privacy need is narrower: **selective disclosure**, proving one row's
membership without revealing the others (e.g., showing a regulator a
single decision's audit trail without opening the whole ledger).

## Shipped instead

- `World.merkle_root()` / `inclusion_proof(seq)` /
  `World.verify_inclusion(proof)`: O(log n) inclusion proofs against a
  published root; the verifier needs only the row and its proof.
- Combined with `sign_tip`, a signed Merkle root becomes the trust
  anchor: the holder publishes one signed root, and anyone can check
  individual rows against it while the rest of the log stays private.

## Revisit if

A genuine cross-organization flow appears where the verifier must not
see the data at all (not just "need not see the rest"). At that point
the honest design is a separate ZK-friendly sidecar chain, not
retrofitting the SHA-256 main chain.
