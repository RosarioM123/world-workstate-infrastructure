"""A mini linearizability checker for ``World.update`` (a la Knossos).

Records real concurrent histories of ``update`` calls (invoke/response
event indices plus results) and searches for a linearization: a total
order extending the real-time order (A < B when A responds before B is
invoked) under which a sequential spec of ``update`` produces exactly
the observed results.

Abstract spec: the world is ``(version, n)`` where ``version`` is the
max committed seq and ``n`` the current committed ``n`` field. The
workload uses the ``monotonic("n")`` invariant, but the spec models the
implementation's *contract*, not the invariant's wish: judgment runs
against a possibly stale fast-path read, so under concurrency a commit
may legally land any ``k`` (last-writer-wins without ``expected_version``).
What the implementation does guarantee, and what the spec enforces:

- ``("ok", ret)``: ``expected_version`` was None or equaled the version
  at the atomic commit point, and ``ret`` (the new version) exceeds the
  old one. New state ``(ret, k)``.
- ``("rejected",)``: ``expected_version`` was None or equaled the
  version at some point in the interval, and the proposal lost to the
  ``n`` there (``k < n``). State unchanged.
- ``("conflict",)``: ``expected_version`` was not None and differed
  from the version at the decision point. State unchanged.

Known subtlety (documented, not a violation): the audit log's row seq
order can diverge from the linearization order under concurrency. A
REJECTED row is appended after its judgment, so it may carry a higher
seq than a concurrent commit it never observed. The abstract
(version, n) state is linearizable; the (seq, version) pair is not.
Sequential clients never observe the divergence.

Scope: no idempotency keys in the workload; the spec covers the
non-idempotent path (idempotency was model-checked separately).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Op:
    """One recorded ``update`` call."""

    invoke: int  # global event index of invocation
    resp: int  # global event index of response
    expected: Optional[int]  # expected_version passed by the client
    k: int  # proposed n value
    # ("ok", new_version) | ("rejected",) | ("conflict",)
    result: tuple


def _step(version: int, n: Optional[int], op: Op):
    """Apply the sequential spec; return the new (version, n) or None."""
    e = op.expected
    kind = op.result[0]
    if kind == "conflict":
        if e is not None and e != version:
            return (version, n)
        return None
    if kind == "rejected":
        if (e is None or e == version) and n is not None and op.k < n:
            return (version, n)
        return None
    if kind == "ok":
        new_v = op.result[1]
        if (e is None or e == version) and new_v > version:
            return (new_v, op.k)
        return None
    raise AssertionError(f"unknown result {op.result!r}")


def is_linearizable(history: list[Op],
                    initial_version: int = 0,
                    initial_n: Optional[int] = None) -> bool:
    """Search for a linearization of ``history`` via backtracking.

    Complete for the given history: returns True iff some total order
    extending the real-time order validates every op under the spec.
    ``initial_version`` / ``initial_n`` describe the abstract state before
    the first op (default: empty world). Worst case exponential
    (linearizability is NP-complete); practical for the bounded histories
    used in tests, with memoization of dead ends and a response-order
    candidate heuristic.
    """
    n = len(history)
    if n == 0:
        return True
    pred = [
        {j for j, q in enumerate(history) if q.resp < op.invoke}
        for op in history
    ]
    # Try earlier-responding ops first: they are the most constrained.
    order = sorted(range(n), key=lambda i: history[i].resp)
    dead: set[tuple[frozenset, int, Optional[int]]] = set()

    def rec(placed: frozenset, version: int, cur_n: Optional[int]) -> bool:
        if len(placed) == n:
            return True
        key = (placed, version, cur_n)
        if key in dead:
            return False
        for i in order:
            if i in placed or not pred[i] <= placed:
                continue
            nxt = _step(version, cur_n, history[i])
            if nxt is None:
                continue
            if rec(placed | {i}, nxt[0], nxt[1]):
                return True
        dead.add(key)
        return False

    return rec(frozenset(), initial_version, initial_n)
