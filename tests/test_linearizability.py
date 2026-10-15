"""Linearizability: real concurrent ``World.update`` histories, checked.

Generates concurrent histories against a real ``World`` (threads racing
with fresh/stale/absent ``expected_version`` under a ``monotonic("n")``
invariant, so commits, rejections and conflicts all occur) and asserts
``spec/linearizability.py`` finds a valid linearization for each.
Mutation tests flip results and assert the checker rejects them,
proving the checker has teeth.
"""

import itertools
import os
import random
import sys
import threading

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "spec"))

from linearizability import Op, is_linearizable  # noqa: E402

from world import ConflictError, InvariantViolation, World  # noqa: E402
from world.invariants import monotonic  # noqa: E402


def _run_history(seed: int, tmpdir: str, threads: int = 4,
                 ops_per_thread: int = 6) -> list[Op]:
    w = World("lin", dir=tmpdir, invariants=[monotonic("n")])
    counter = itertools.count()
    clock = threading.Lock()

    def tick() -> int:
        with clock:
            return next(counter)

    out: list[Op] = []
    out_lock = threading.Lock()

    def worker(tid: int) -> None:
        rng = random.Random(seed * 7919 + tid)
        believed = 0
        k = tid * 1000
        for _ in range(ops_per_thread):
            if rng.random() < 0.7:
                _, believed = w.read()
            e: int | None = believed
            r = rng.random()
            if r < 0.30:
                e = max(0, believed - rng.randint(1, 3))  # stale
            elif r < 0.45:
                e = None  # unguarded
            k += rng.choice([1, 1, 1, 2, 5])
            if rng.random() < 0.25:
                k -= rng.randint(1, 12)  # sometimes violate monotonic
            ik = tick()
            try:
                ret = w.update({"n": k}, expected_version=e)
                res: tuple = ("ok", ret)
            except InvariantViolation:
                res = ("rejected",)
            except ConflictError:
                res = ("conflict",)
            rk = tick()
            with out_lock:
                out.append(Op(ik, rk, e, k, res))

    ts = [threading.Thread(target=worker, args=(t,)) for t in range(threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return out


def test_concurrent_histories_are_linearizable(tmp_path):
    seen = set()
    for trial in range(5):
        hist = _run_history(20261015 + trial, str(tmp_path / f"t{trial}"),
                            threads=6, ops_per_thread=8)
        assert hist, "workload produced no ops"
        kinds = {op.result[0] for op in hist}
        seen |= kinds
        assert is_linearizable(hist), f"trial {trial}: no linearization found"
    # The test is vacuous unless the workload exercised every outcome.
    assert seen == {"ok", "rejected", "conflict"}, seen


def test_sequential_history_accepted(tmp_path):
    w = World("linseq", dir=str(tmp_path), invariants=[monotonic("n")])
    hist: list[Op] = []
    tick = itertools.count().__next__
    v = 0
    for k in (5, 9, 7):
        i0, i1 = tick(), tick()
        try:
            v = w.update({"n": k}, expected_version=v)
            hist.append(Op(i0, i1, v - 1 if v > 1 else 0, k, ("ok", v)))
        except InvariantViolation:
            hist.append(Op(i0, i1, v, k, ("rejected",)))
    assert is_linearizable(hist)


def test_mutation_ok_to_conflict_rejected(tmp_path):
    # Flipping a committed (unguarded) op to "conflict" is impossible:
    # conflicts require a non-None expected_version.
    for seed in range(20):
        hist = _run_history(999000 + seed, str(tmp_path / f"m{seed}"),
                            threads=4, ops_per_thread=6)
        assert is_linearizable(hist)
        for idx, op in enumerate(hist):
            if op.result[0] == "ok" and op.expected is None:
                bad = list(hist)
                bad[idx] = Op(op.invoke, op.resp, op.expected, op.k,
                              ("conflict",))
                assert not is_linearizable(bad), \
                    "checker accepted an impossible conflict"
                return
    pytest.fail("workload never produced an unguarded commit")


def test_mutation_stale_conflict_to_ok_rejected(tmp_path):
    # Deterministic: drive the version to 5, then an op with a stale
    # expected_version=3 conflicts. Claiming it committed cannot
    # linearize: the version exceeds 3 at every valid position.
    w = World("linmut", dir=str(tmp_path), invariants=[monotonic("n")])
    tick = itertools.count().__next__
    hist: list[Op] = []
    for i in range(1, 6):
        i0, i1 = tick(), tick()
        v = w.update({"n": i * 10})
        hist.append(Op(i0, i1, None, i * 10, ("ok", v)))
    i0, i1 = tick(), tick()
    with pytest.raises(ConflictError):
        w.update({"n": 60}, expected_version=3)
    hist.append(Op(i0, i1, 3, 60, ("conflict",)))
    assert is_linearizable(hist)
    bad = hist[:-1] + [Op(i0, i1, 3, 60, ("ok", 6))]
    assert not is_linearizable(bad), "checker accepted a stale commit"
