# Invariant composition semantics

**Tests:** `tests/test_invariant_composition.py`.
**Date:** 2026-10-15.

## Model

An invariant is `(old, new) -> None`, raising `InvariantViolation` to
reject. The engine judges a proposal by running the invariant list in
order and short-circuiting on the first violation. Assume invariants
are pure (deterministic, no side effects) and signal only via
`InvariantViolation`; any other exception propagates uncaught (a
crashing judge is a bug, per README).

## Theorems (each a property test)

**T1, verdict order-independence.** The COMMITTED/REJECTED verdict is
the OR of the individual judgments, so it does not depend on the order
of the invariant list. Reordering invariants can change *which reason*
is reported, never the verdict. Tested end to end through
`World.update` over all 120 permutations of a 5-invariant pool x 25
random transitions.

**T2, short-circuit soundness.** Stopping at the first violation yields
the same verdict as evaluating every invariant. The short-circuit is a
performance optimization only; it cannot change outcomes.

**T3, rejection monotonicity.** Adding invariants monotonically
increases rejections: a transition rejected under a set stays rejected
under any superset. COMMITTED can flip to REJECTED; REJECTED can never
flip to COMMITTED. Consequence for operators: extending the rule set is
always safe in one direction; it can only make the world stricter.

**T4, `all_of` conjunction.** `world.invariants.all_of(*invs)` is
verdict-equivalent to listing the sub-invariants separately, and its
reason joins every sub-reason instead of reporting only the first. The
plain list answers "was it rejected"; `all_of` answers "rejected, and
here is everything wrong". `all_of()` with no sub-invariants accepts
everything. Verdicts compose associatively; the reason string reflects
the grouping (no flattening), so regrouping can reword reasons without
changing verdicts.

## Why this matters

Invariant sets are the correctness boundary of a world (README:
"Correctness contract"). These properties mean operators can reorder,
extend, and refactor rule sets with a precise understanding of what can
change: reasons may shift, verdicts only ever get stricter, and `all_of`
trades one short-circuit for complete diagnostics without changing
outcomes.
