"""Stateful model-based testing for the World primitive.

A Hypothesis ``RuleBasedStateMachine`` drives the real ``World.update``
through random sequences of operations and checks every step against a
pure-Python reference model of the update contract:

- ``expected_version`` mismatch -> ``ConflictError``, no row appended
- invariant violation -> REJECTED row appended, ``InvariantViolation``
  carrying the rejected row's seq
- repeated idempotency key on a committed update -> original seq, no append
- every judged proposal appends exactly one row (dense seqs)
- ``version()`` / ``read()`` always agree with the model
- ``state(version=N)`` time travel matches the model's committed history
- ``verify()`` holds after every step

The model shares the *same* invariant function objects as the system under
test, so it cannot drift from judgment semantics; it only re-implements the
protocol logic (conflict / reject / dedupe / append). Any divergence is a
real protocol bug. ``test_stateful_catches_mutation`` proves the machine
has teeth by running it against a deliberately broken World.
"""

import tempfile

import pytest

from world import ConflictError, InvariantViolation, World
from world.invariants import monotonic

pytest.importorskip("hypothesis")

from hypothesis import assume, settings, strategies as st  # noqa: E402
from hypothesis.stateful import (  # noqa: E402
    RuleBasedStateMachine,
    invariant,
    rule,
    run_state_machine_as_test,
)

OPS = [0]


class RefModel:
    """Pure-Python reference model of the World.update protocol."""

    def __init__(self, invariants):
        self._invariants = invariants
        self.row_seq = 0  # every judged proposal appends exactly one row
        self.version = 0  # seq of the latest COMMITTED row
        self.doc = {}
        self.seen = {}  # idempotency_key -> seq, committed updates only
        self.committed_docs = {}  # version -> document, for time travel

    def update(self, state, expected_version=None, idempotency_key=None):
        # 1. Stale expected_version aborts before judgment: no row appended.
        if expected_version is not None and expected_version != self.version:
            return ("conflict",)
        # 2. Every proposal is judged, even repeats of a seen key.
        violation = None
        for inv in self._invariants:
            try:
                inv(self.doc, state)
            except InvariantViolation as e:
                violation = e
                break
        # 3. Rejections are always recorded: a repeated key can never mask
        #    a rejection from the audit trail.
        if violation is not None:
            self.row_seq += 1
            return ("rejected", self.row_seq)
        # 4. Idempotent duplicates of a committed update return the original
        #    seq without appending.
        if idempotency_key is not None and idempotency_key in self.seen:
            return ("ok", self.seen[idempotency_key])
        self.row_seq += 1
        self.version = self.row_seq
        self.doc = state
        self.committed_docs[self.version] = state
        if idempotency_key is not None:
            self.seen[idempotency_key] = self.version
        return ("ok", self.version)


class WorldMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self._tmp = tempfile.TemporaryDirectory()
        invs = [monotonic("n")]
        self.world = World("stateful", dir=self._tmp.name, invariants=invs)
        self.model = RefModel(invs)

    def teardown(self):
        self._tmp.cleanup()
        super().teardown()

    @rule(
        n=st.integers(min_value=-10, max_value=30),
        extra=st.dictionaries(
            st.text(min_size=1, max_size=4).filter(lambda s: s != "n"),
            st.integers(min_value=-99, max_value=99),
            max_size=2,
        ),
        ev_choice=st.sampled_from(["none", "fresh", "stale", "future"]),
        key=st.one_of(st.none(), st.sampled_from(["k1", "k2", "k3"])),
        actor=st.one_of(st.none(), st.sampled_from(["a", "b"])),
    )
    def do_update(self, n, extra, ev_choice, key, actor):
        state = dict(extra)
        state["n"] = n
        if ev_choice == "none":
            ev = None
        elif ev_choice == "fresh":
            ev = self.model.version
        elif ev_choice == "stale":
            ev = max(0, self.model.version - 1)
        else:
            ev = self.model.version + 3
        try:
            seq = self.world.update(
                state,
                actor=actor,
                note="sm",
                expected_version=ev,
                idempotency_key=key,
            )
            got = ("ok", seq)
        except ConflictError:
            got = ("conflict",)
        except InvariantViolation as e:
            got = ("rejected", e.seq)
        want = self.model.update(
            state, expected_version=ev, idempotency_key=key
        )
        assert got == want, f"SUT {got} != model {want} for {state=} {ev=} {key=}"
        assert self.world.version == self.model.version
        assert self.world.read() == (self.model.doc, self.model.version)
        OPS[0] += 1

    @rule(v=st.integers(min_value=1, max_value=200))
    def check_time_travel(self, v):
        assume(1 <= v <= self.model.version)
        assert self.world.state(version=v) == self.model.committed_docs[v]

    @invariant()
    def chain_always_verifies(self):
        assert self.world.verify()


def test_stateful_world_matches_reference_model(capsys):
    OPS[0] = 0
    run_state_machine_as_test(
        WorldMachine, settings=settings(max_examples=30, deadline=None)
    )
    print(f"\nstateful ops executed: {OPS[0]}")
    assert OPS[0] >= 500, f"too few update ops executed: {OPS[0]}"


def test_stateful_catches_mutation(monkeypatch):
    """Teeth: a World that skips invariant judgment must fail the machine."""
    real_init = World.__init__

    def broken_init(self, name, *, dir=None, invariants=()):
        real_init(self, name, dir=dir, invariants=[])

    monkeypatch.setattr(World, "__init__", broken_init)
    with pytest.raises(AssertionError):
        run_state_machine_as_test(
            WorldMachine, settings=settings(max_examples=10, deadline=None)
        )
