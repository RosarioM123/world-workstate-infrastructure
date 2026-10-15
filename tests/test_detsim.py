"""Deterministic simulation: seeded scheduler, reproducible interleavings."""

import os
import random
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "spec"))

from detsim import Simulation  # noqa: E402
from linearizability import Op, is_linearizable  # noqa: E402

from world import ConflictError, InvariantViolation, World  # noqa: E402
from world.invariants import monotonic  # noqa: E402


def _client_full(sim, w, cid, rounds, seed):
    rng = random.Random(seed * 100003 + cid)
    believed = 0
    k = cid * 1000
    for _ in range(rounds):
        sim.sched.yield_point(cid, "round")
        _, believed = w.read()
        e: int | None = believed
        x = rng.random()
        if x < 0.30:
            e = max(0, believed - rng.randint(1, 2))  # stale
        elif x < 0.40:
            e = None  # unguarded
        k += rng.choice([1, 2, 3])
        if rng.random() < 0.20:
            k -= rng.randint(1, 20)  # sometimes violate monotonic
        inv = sim.sched.tick()
        try:
            ret = w.update({"n": k, "cid": cid}, expected_version=e)
            res = ("ok", ret)
        except ConflictError:
            res = ("conflict",)
        except InvariantViolation:
            res = ("rejected",)
        resp = sim.sched.tick()
        sim.record_op(cid, inv, resp, e, k, res)


def _run(seed, tmpdir, nclients=4, rounds=6, script=None):
    sim = Simulation(seed, script=script)
    w = World("detsim", dir=str(tmpdir), invariants=[monotonic("n")])
    sim.patch(w)
    try:
        clients = [
            (cid, lambda c, _cid=cid: _client_full(sim, w, _cid, rounds, seed))
            for cid in range(nclients)
        ]
        sim.sched.run(clients)
        if sim.sched.errors:
            raise AssertionError(f"client errors: {sim.sched.errors}")
        assert not sim.sched.atomic_holder
    finally:
        sim.unpatch(w)
    return sim, w


def _history(sim):
    return [
        Op(o["invoke"], o["resp"], o["expected"], o["k"], o["result"])
        for o in sim.ops
    ]


def _overlapped(history) -> bool:
    for i, a in enumerate(history):
        for b in history[i + 1:]:
            if a.invoke < b.invoke < a.resp or b.invoke < a.invoke < b.resp:
                return True
    return False


def test_detsim_deterministic(tmp_path):
    # Same seed, fresh worlds: identical interleaving, identical outcomes.
    sim1, _ = _run(20261015, tmp_path / "a")
    sim2, _ = _run(20261015, tmp_path / "b")
    assert sim1.sched.log == sim2.sched.log
    assert [(o["invoke"], o["resp"], o["expected"], o["k"], o["result"])
            for o in sim1.ops] == [
               (o["invoke"], o["resp"], o["expected"], o["k"], o["result"])
               for o in sim2.ops]


def test_detsim_interleavings_valid(tmp_path):
    kinds, overlapped = set(), False
    for seed in range(20):
        sim, w = _run(5000 + seed, tmp_path / f"s{seed}")
        assert w.verify(), f"seed {seed}: hash chain broken"
        hist = _history(sim)
        assert is_linearizable(hist), f"seed {seed}: not linearizable"
        kinds |= {o["result"][0] for o in sim.ops}
        overlapped |= _overlapped(hist)
    assert kinds == {"ok", "rejected", "conflict"}, kinds
    assert overlapped, "simulator never actually interleaved operations"


def test_detsim_audit_seq_divergence(tmp_path):
    # Scripted interleaving reproducing the linearizability-doc finding:
    # A judges n=3 against v5 (REJECTED decided, e=None so no re-check
    # conflict); B commits v6 in between; A's REJECTED row lands after
    # B's commit with a higher seq. Prestart runs each client to its
    # first ("read") yield; scripted grants then do: A judge, B judge,
    # B commit, A append.
    sim = Simulation(seed=1, script=[0, 1, 1, 0])
    w = World("div", dir=str(tmp_path), invariants=[monotonic("n")])
    for i in range(1, 6):
        w.update({"n": i})
    sim.patch(w)
    outcomes: dict = {}

    def client_a(_cid):
        inv = sim.sched.tick()
        try:
            w.update({"n": 3})  # unguarded: judgment cannot become conflict
            outcomes["a"] = ("ok",)
        except InvariantViolation as ex:
            outcomes["a"] = ("rejected", ex.seq)
        except ConflictError:
            outcomes["a"] = ("conflict",)
        sim.record_op(0, inv, sim.sched.tick(), None, 3, outcomes["a"])

    def client_b(_cid):
        inv = sim.sched.tick()
        try:
            ret = w.update({"n": 10}, expected_version=5)
            outcomes["b"] = ("ok", ret)
        except ConflictError:
            outcomes["b"] = ("conflict",)
        except InvariantViolation:
            outcomes["b"] = ("rejected",)
        sim.record_op(1, inv, sim.sched.tick(), 5, 10, outcomes["b"])

    try:
        sim.sched.run([(0, client_a), (1, client_b)])
        if sim.sched.errors:
            raise AssertionError(f"client errors: {sim.sched.errors}")
    finally:
        sim.unpatch(w)

    assert outcomes["b"] == ("ok", 6)
    assert outcomes["a"] == ("rejected", 7)
    assert w.verify()
    # The abstract state still linearizes (the divergence is audit-only).
    # Initial abstract state: the sequential setup left version=5, n=5.
    assert is_linearizable(_history(sim), initial_version=5, initial_n=5)
