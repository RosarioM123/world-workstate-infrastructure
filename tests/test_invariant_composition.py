"""Invariant composition semantics, as property tests.

T1 Verdict order-independence: for pure invariants, the COMMITTED /
REJECTED verdict is the OR of the individual judgments, so it does not
depend on the order of the invariant list. Only the reported reason
varies with order.
T2 Short-circuit soundness: the engine stops at the first violation;
the verdict equals evaluating every invariant.
T3 Rejection monotonicity: adding invariants can only flip COMMITTED to
REJECTED, never the reverse.
T4 all_of: verdict-equivalent to the plain list, with every sub-reason
reported instead of just the first.
"""

import itertools
import random

import pytest

from world import InvariantViolation, World
from world.invariants import all_of, monotonic, no_negative, require_keys


def _pool():
    return [
        monotonic("n"),
        monotonic("n", strict=True),
        no_negative("n"),
        no_negative("m"),
        require_keys("id"),
    ]


def _judges_reject(invs, old, new) -> bool:
    try:
        for inv in invs:
            inv(old, new)
        return False
    except InvariantViolation:
        return True


def _engine_verdict(invs, old, new, tmp_path, tag) -> bool:
    """True = COMMITTED through the real World.update path."""
    w = World(f"cmp{tag}", dir=str(tmp_path), invariants=list(invs))
    w.update(old)
    try:
        w.update(new)
        return True
    except InvariantViolation:
        return False


def _docs(rng):
    # `old` is always committable (setup); `new` exercises violations.
    for _ in range(25):
        yield (
            {"n": rng.randint(0, 10), "m": rng.randint(0, 10), "id": 1},
            {"n": rng.randint(-2, 10), "m": rng.randint(-2, 10),
             **({"id": 1} if rng.random() < 0.7 else {})},
        )


def test_verdict_order_independent(tmp_path):
    # T1, end to end through World.update: every permutation of the
    # invariant list yields the same COMMITTED/REJECTED verdict.
    rng = random.Random(20261015)
    pool = _pool()
    perms = list(itertools.permutations(pool))
    for di, (old, new) in enumerate(_docs(rng)):
        verdicts = {
            _engine_verdict(p, old, new, tmp_path, f"{di}x{pi}")
            for pi, p in enumerate(perms)
        }
        assert len(verdicts) == 1, (old, new, verdicts)


def test_rejection_monotone_in_invariants():
    # T3: a rejecting set keeps rejecting when invariants are added.
    rng = random.Random(77)
    pool = _pool()
    for old, new in _docs(rng):
        for k in range(len(pool)):
            small, big = pool[:k], pool[: k + 1]
            if _judges_reject(small, old, new):
                assert _judges_reject(big, old, new), (old, new, k)


def test_all_of_matches_list_and_reports_all(tmp_path):
    # T4: same verdict as the plain list; reason joins every violation.
    rng = random.Random(31337)
    pool = _pool()
    for di, (old, new) in enumerate(_docs(rng)):
        list_reject = _judges_reject(pool, old, new)
        try:
            all_of(*pool)(old, new)
            combo_reject, reason = False, ""
        except InvariantViolation as e:
            combo_reject, reason = True, e.reason
        assert combo_reject == list_reject
        if combo_reject:
            sub_reasons = []
            for inv in pool:
                try:
                    inv(old, new)
                except InvariantViolation as e:
                    sub_reasons.append(e.reason)
            for sr in sub_reasons:
                assert sr in reason
    # Empty conjunction accepts everything.
    all_of()({}, {"anything": True})
    # End to end: all_of as a single engine invariant.
    w = World("cmpall", dir=str(tmp_path), invariants=[all_of(*pool)])
    w.update({"n": 1, "m": 1, "id": 1})
    with pytest.raises(InvariantViolation):
        w.update({"n": -5, "m": -6})  # violates no_negative twice + require_keys


def test_short_circuit_matches_full_evaluation(tmp_path):
    # T2: the engine's first-violation short-circuit agrees with judging all.
    rng = random.Random(555)
    pool = _pool()
    for di, (old, new) in enumerate(_docs(rng)):
        engine = _engine_verdict(pool, old, new, tmp_path, f"s{di}")
        full = not _judges_reject(pool, old, new)
        assert engine == full
