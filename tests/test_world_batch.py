"""Tests for World.update_many: one transaction, sequential semantics.

The core property is differential: update_many must produce the same
observable log as sequential update() calls with the same arguments,
only faster. Timestamps are the one legitimate difference (per-row
_clocks), so history comparison excludes them.
"""

import pytest

from world import ConflictError, InvariantViolation, World
from world.invariants import monotonic


def _history_no_ts(w):
    return [
        {k: v for k, v in row.items() if k != "timestamp"}
        for row in w.history()
    ]


def _sequential(dir, states, *, invariants=(), actor="a", note="n", keys=None):
    """Sequential update() calls, stopping at the first rejection.

    Returns (world, seqs, rejected_seq): the differential oracle for
    update_many, which raises on the first rejection instead of
    continuing.
    """
    w = World("seq", dir=dir, invariants=list(invariants))
    seqs = []
    rejected = None
    for i, s in enumerate(states):
        k = keys[i] if keys else None
        try:
            seqs.append(w.update(s, actor=actor, note=note, idempotency_key=k))
        except InvariantViolation as e:
            rejected = e.seq
            break
    return w, seqs, rejected


def test_update_many_matches_sequential(tmp_path):
    # Randomized differential test: same args, batch vs sequential.
    import random

    rng = random.Random(20261015)
    for trial in range(10):
        n = rng.randint(1, 12)
        states = [{"n": rng.randint(0, 9), "tag": rng.randint(0, 3)} for _ in range(n)]
        keys = [rng.choice([None, "k1", "k2"]) for _ in range(n)]
        d1, d2 = tmp_path / f"b{trial}", tmp_path / f"s{trial}"
        d1.mkdir()
        d2.mkdir()
        wb = World("b", dir=str(d1), invariants=[monotonic("n")])
        ws, seq_seqs, seq_rejected = _sequential(
            str(d2), states, invariants=[monotonic("n")], keys=keys
        )
        if seq_rejected is None:
            seqs = wb.update_many(
                states, actor="a", note="n", idempotency_keys=keys
            )
            assert seqs == seq_seqs
        else:
            with pytest.raises(InvariantViolation) as ei:
                wb.update_many(
                    states, actor="a", note="n", idempotency_keys=keys
                )
            assert ei.value.seq == seq_rejected
        assert wb.version == ws.version
        assert wb.read() == ws.read()
        assert _history_no_ts(wb) == _history_no_ts(ws)
        assert wb.verify() and ws.verify()
        for v in range(1, wb.version + 1):
            assert wb.state(version=v) == ws.state(version=v)


def test_update_many_empty_is_noop(tmp_path):
    w = World("b", dir=str(tmp_path))
    assert w.update_many([]) == []
    assert w.version == 0
    assert w.history() == []


def test_update_many_expected_version_guard(tmp_path):
    w = World("b", dir=str(tmp_path))
    w.update({"n": 1})
    with pytest.raises(ConflictError):
        w.update_many([{"n": 2}, {"n": 3}], expected_version=0)
    assert w.version == 1
    assert len(w.history()) == 1  # nothing from the batch appended
    assert w.update_many([{"n": 2}, {"n": 3}], expected_version=1) == [2, 3]


def test_update_many_rejection_mid_batch(tmp_path):
    d1, d2 = tmp_path / "b", tmp_path / "s"
    d1.mkdir()
    d2.mkdir()
    states = [{"n": 1}, {"n": 2}, {"n": 0}, {"n": 3}]
    wb = World("b", dir=str(d1), invariants=[monotonic("n")])
    ws, seq_seqs, seq_rejected = _sequential(
        str(d2), states, invariants=[monotonic("n")]
    )
    with pytest.raises(InvariantViolation) as ei:
        wb.update_many(states, actor="a", note="n")
    # Same outcome as sequential: earlier items committed, rejection recorded.
    assert ei.value.seq == seq_rejected == 3
    assert seq_seqs == [1, 2]
    assert wb.version == ws.version == 2
    assert _history_no_ts(wb) == _history_no_ts(ws)
    assert [r["status"] for r in wb.history()] == ["COMMITTED"] * 2 + ["REJECTED"]


def test_update_many_idempotency_within_batch(tmp_path):
    # A duplicate key mid-batch appends nothing; the next item must be
    # judged against the true document, not the deduped proposal.
    w = World("b", dir=str(tmp_path), invariants=[monotonic("n")])
    seqs = w.update_many(
        [{"n": 1}, {"n": 5}, {"n": 3}],
        idempotency_keys=["k1", "k1", None],
    )
    assert seqs == [1, 1, 2]  # second item deduped to seq 1
    assert w.version == 2  # only two rows appended
    # {"n": 3} committed against {"n": 1}: if judgment had used the
    # deduped {"n": 5} as old, monotonic would have rejected it.
    assert w.read() == ({"n": 3}, 2)


def test_update_many_rejected_with_seen_key_still_recorded(tmp_path):
    # Judgment comes before dedupe: a repeated key never masks a rejection.
    w = World("b", dir=str(tmp_path), invariants=[monotonic("n")])
    w.update_many([{"n": 1}], idempotency_keys=["k1"])
    with pytest.raises(InvariantViolation) as ei:
        w.update_many([{"n": 0}], idempotency_keys=["k1"])
    assert ei.value.seq == 2
    assert [r["status"] for r in w.history()] == ["COMMITTED", "REJECTED"]


def test_update_many_idempotency_across_batches(tmp_path):
    w = World("b", dir=str(tmp_path))
    assert w.update_many([{"n": 1}], idempotency_keys=["k"]) == [1]
    assert w.update_many([{"n": 2}], idempotency_keys=["k"]) == [1]
    assert w.version == 1


def test_update_many_validates_upfront(tmp_path):
    w = World("b", dir=str(tmp_path))
    with pytest.raises(TypeError):
        w.update_many([{"n": 1}, "not-a-dict"])
    with pytest.raises(ValueError, match="not JSON-serializable"):
        w.update_many([{"n": 1}, {"bad": object()}])
    with pytest.raises(ValueError, match="length"):
        w.update_many([{"n": 1}], idempotency_keys=["k1", "k2"])
    assert w.version == 0  # nothing appended
    assert w.history() == []
