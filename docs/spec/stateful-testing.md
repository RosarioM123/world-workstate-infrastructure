# Stateful model-based testing

`tests/test_stateful.py` runs a Hypothesis `RuleBasedStateMachine` against the
real `World.update` and checks every step against a pure-Python reference
model of the update protocol. Where the explicit-state model checker
(`spec/model_check.py`) proves properties over an abstract transition system,
this test checks the *actual implementation* against the *actual contract*,
operation by operation, over randomized sequences.

## Contract under test

The reference model (`RefModel`) re-implements only the protocol logic:

1. Stale `expected_version` aborts with `ConflictError` before judgment; no
   row is appended.
2. Every proposal is judged by the invariants, even repeats of a seen
   idempotency key.
3. A violation appends one REJECTED row (the attempt is evidence) and raises
   `InvariantViolation` carrying the rejected row's seq.
4. A repeated idempotency key on a committed update returns the original seq
   with no new row appended.
5. Every judged proposal appends exactly one row, so seqs stay dense.

The model shares the *same invariant function objects* as the system under
test (`monotonic("n")`), so it cannot drift from judgment semantics; it only
re-implements steps 1-5. Any divergence is a protocol bug in `World.update`.

## Cross-checks per step

Each `do_update` rule additionally asserts:

- `world.version` equals the model's committed version,
- `world.read()` equals `(model.doc, model.version)`,
- a `check_time_travel` rule asserts `world.state(version=v)` matches the
  model's committed history for random committed versions,
- an `@invariant` asserts `world.verify()` after every step.

## Results

- **1,526 update operations** across 30 generated examples: 0 divergences.
- `verify()` held after every step; time-travel reads matched throughout.
- The harness caught a real bug on its first run: the reference model
  incremented its row counter for idempotent duplicates, which the
  implementation correctly does not append. The model was fixed; the
  implementation was already right. This is the harness working as intended.
- `test_stateful_catches_mutation` runs the machine against a deliberately
  broken `World` (invariant judgment removed) and asserts it fails, proving
  the machine has teeth.

## Running

Hypothesis is an optional test dependency. Without it the module skips
(`pytest.importorskip`). With it installed:

```
pip install hypothesis
pytest tests/test_stateful.py -q
```

## Limits

- Sequential only: the machine drives one client at a time, so it cannot
  catch the audit-seq divergence documented by the linearizability checker;
  that is covered by `spec/linearizability.py` and `spec/detsim.py`.
- One invariant shape (`monotonic("n")`) keeps the model small; the protocol
  logic under test is invariant-agnostic.
