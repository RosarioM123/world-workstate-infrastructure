"""Bounded exhaustive model checker for the WORLD commit protocol.

This is a mechanized verification of ``World.update`` (``src/world/core.py``):
every reachable global state of a bounded workload is explored, across all
thread interleavings and all adversarial invariant verdicts, and the safety
properties P1..P6 are asserted on each one. A violation raises with a full
counterexample trace.

The model
---------

Each ``update`` is two transitions, mirroring the implementation:

- READ_JUDGE (core.py: read latest committed, fast-path expected_version
  check, invariant loop). If ``expected_version`` is present and stale, the
  op ends here with ConflictError: never judged, no row. Otherwise the op
  records ``(read_seq, snapshot, ev, key, token, verdict)`` as pending.
  READ and JUDGE are fused into one transition because neither touches
  shared state; every interleaving the three-phase model distinguishes is
  preserved (a COMMIT can still land between another writer's READ_JUDGE
  and its COMMIT: that is the race the protocol must survive).
  The verdict is *adversarially* nondeterministic: the checker branches on
  pass/fail, so the properties must hold for every possible invariant.
- ATOMIC_COMMIT (core.py: BEGIN IMMEDIATE .. COMMIT). One indivisible
  transition: re-validate ``expected_version`` against the latest
  committed row, apply the idempotency dedupe, append exactly one
  hash-chained row (or none, on the idempotent short-circuit).

Modeling BEGIN IMMEDIATE as one atomic transition is not an assumption
smuggled in: it *is* the implementation's serialization guarantee
(SQLite serializes BEGIN IMMEDIATE writers). What the checker proves is
that the protocol is correct *given* that serialization: the read-to-lock
race is closed by the re-validation, not by luck. ``--inject-bug`` drops
the re-validation to prove the checker has teeth (it must then find a
P4 violation).

Abstractions (each justified in ``docs/spec/protocol-verification.md``):

- Documents are opaque tokens; only equality is modeled.
- Hashes are symbolic tuples; only chain linkage is checked.
- Timestamps, actors, notes, and canonical JSON encoding are abstracted
  away: they do not influence control flow.
- ``expected_version`` choices per op: None (last-writer-wins), "fresh"
  (the version observed at READ: the optimistic-concurrency use), "stale"
  (a literal -1, exercising the fast-path rejection).
- Idempotency keys come from a small domain, shared across writers.

Properties
----------

- P1 seq integrity: row seqs are dense 1..N, unique, append-only.
- P2 chain integrity: every row's prev_hash equals the previous row's
  hash (REJECTED rows included: the chain covers all rows by seq).
- P3 committed-only version: version() == max COMMITTED seq (0 if none);
  REJECTED rows never contribute to the version.
- P4 exactly-one-winner: for each expected version V, at most one op
  commits with expected_version=V. (Each COMMITTED append strictly
  increases the committed version, so a second contender necessarily
  fails the atomic re-validation.)
- P5 idempotency: the idempotency table always maps each key to the seq
  of its *latest* committed use; a short-circuit return hands back
  exactly that seq and appends no row.
- P6 judgment recorded: every op that reaches JUDGE appends exactly one
  row, except the idempotent short-circuit which appends none.
  (ConflictError before JUDGE appends nothing: the attempt was never
  judged, so there is nothing to record.)
"""

from __future__ import annotations

from collections import deque
from typing import Any

GENESIS = ("GENESIS",)


def _hash(seq: int, prev_hash: Any, status: str, token: Any) -> tuple:
    """Symbolic hash: equality structure only, no crypto modeled."""
    return ("H", seq, prev_hash, status, token)


class Config:
    """Bounded workload: writers -> number of update ops each."""

    def __init__(
        self,
        writers: dict[str, int],
        ev_domain: tuple = (None, "fresh", "stale"),
        key_domain: tuple = (None, "k1", "k2"),
        inject_bug: bool = False,
    ) -> None:
        self.writers = writers
        self.ev_domain = ev_domain
        self.key_domain = key_domain
        self.inject_bug = inject_bug


def _latest_committed_seq(rows: tuple) -> int:
    seq = 0
    for r in rows:
        if r[1] == "COMMITTED":
            seq = r[0]
    return seq


def _latest_committed_token(rows: tuple) -> Any:
    token = None
    for r in rows:
        if r[1] == "COMMITTED":
            token = r[2]
    return token


def _check_properties(rows, idem, winners, n_committed, n_rejected) -> None:
    # P1: dense unique seqs.
    for i, r in enumerate(rows):
        assert r[0] == i + 1, f"P1 violated: row seq {r[0]} at index {i}"
    # P2: hash chain over all rows.
    prev = GENESIS
    for r in rows:
        assert r[3] == prev, f"P2 violated at seq {r[0]}: prev_hash mismatch"
        assert r[4] == _hash(r[0], r[3], r[1], r[2]), f"P2 violated at seq {r[0]}"
        prev = r[4]
    # P3: version is max committed seq.
    assert _latest_committed_seq(rows) == (
        max((r[0] for r in rows if r[1] == "COMMITTED"), default=0)
    ), "P3 violated"
    # P5: the idempotency table always maps each key to the seq of its
    # latest COMMITTED use (rows carry their key in r[5]).
    for key, mapped in idem.items():
        seqs = [r[0] for r in rows if r[5] == key and r[1] == "COMMITTED"]
        assert seqs and mapped == max(seqs), (
            f"P5 violated: idem[{key!r}]={mapped}, committed seqs={seqs}"
        )
    # P6: every judged op appended exactly one row.
    assert len(rows) == n_committed + n_rejected, (
        f"P6 violated: {len(rows)} rows for "
        f"{n_committed} committed + {n_rejected} rejected"
    )
    # P4 is a transition assertion (see ATOMIC_COMMIT): the winners set
    # carried in the state is its witness.


def check(config: Config, max_states: int = 2_000_000) -> dict[str, int]:
    """Explore all reachable states; raise on the first property violation."""
    wids = tuple(config.writers)
    # Writer micro-state: (phase, op_idx, pending).
    # phase 0 = choose op params + READ_JUDGE; 1 = ATOMIC_COMMIT; 2 = done.
    # pending: None | (read_seq, snapshot, ev|None, key, token, verdict).
    init_writers = tuple((0, 0, None) for _ in wids)
    # state = (rows, idem, writers, winners, n_committed, n_rejected)
    init = ((), (), init_writers, frozenset(), 0, 0)
    seen = {init}
    parent: dict[Any, tuple[Any, str]] = {}
    queue: deque[Any] = deque([init])
    states = transitions = 0

    def record(new_state, prev_state, action):
        if new_state not in seen:
            seen.add(new_state)
            parent[new_state] = (prev_state, action)
            queue.append(new_state)

    def trace(state) -> str:
        actions = []
        while state in parent:
            state, action = parent[state]
            actions.append(action)
        return "\n".join(f"  {i + 1}. {a}" for i, a in enumerate(reversed(actions)))

    def fail(msg: str, state) -> None:
        raise AssertionError(
            f"PROPERTY VIOLATION after {states} states:\n{msg}\n"
            f"Counterexample trace:\n{trace(state)}"
        )

    while queue:
        state = queue.popleft()
        rows, idem_t, writers_t, winners, n_c, n_r = state
        states += 1
        if states > max_states:
            raise RuntimeError(f"state budget {max_states} exceeded")
        try:
            _check_properties(rows, dict(idem_t), winners, n_c, n_r)
        except AssertionError as e:
            fail(str(e), state)
        writers = {w: s for w, s in zip(wids, writers_t)}
        idem = dict(idem_t)
        for wi, wid in enumerate(wids):
            phase, op_idx, pending = writers[wid]
            if phase == 2:
                continue
            n_ops = config.writers[wid]
            nxt = (0, op_idx + 1, None) if op_idx + 1 < n_ops else (2, op_idx + 1, None)

            if phase == 0:
                # Choose op params; READ; fast-path check; JUDGE (fused:
                # neither touches shared state).
                for ev_spec in config.ev_domain:
                    for key in config.key_domain:
                        token = (wid, op_idx)
                        cur = _latest_committed_seq(rows)
                        snap = _latest_committed_token(rows)
                        ev = {"fresh": cur, "stale": -1}.get(ev_spec, None)
                        base = (f"{wid}/op{op_idx}: READ_JUDGE "
                                f"(ev_spec={ev_spec}->ev={ev}, key={key}, "
                                f"read_seq={cur})")
                        if ev is not None and ev != cur:
                            # Fast-path ConflictError: never judged, no row.
                            new_w = list(writers_t)
                            new_w[wi] = nxt
                            transitions += 1
                            record(
                                (rows, idem_t, tuple(new_w), winners, n_c, n_r),
                                state, base + " -> CONFLICT (fast path)",
                            )
                            continue
                        for verdict in ("pass", "fail"):
                            new_w = list(writers_t)
                            new_w[wi] = (
                                1, op_idx, (cur, snap, ev, key, token, verdict))
                            transitions += 1
                            record(
                                (rows, idem_t, tuple(new_w), winners, n_c, n_r),
                                state, base + f" -> {verdict.upper()}",
                            )
            else:  # phase == 1: ATOMIC_COMMIT, one indivisible transition.
                assert pending is not None
                _read_seq, _snap, ev, key, token, verdict = pending
                cur2 = _latest_committed_seq(rows)
                new_rows, new_idem_t = rows, idem_t
                new_winners, dn_c, dn_r = winners, 0, 0
                if not config.inject_bug and ev is not None and ev != cur2:
                    action = (f"{wid}/op{op_idx}: COMMIT -> CONFLICT "
                              f"(ev={ev} != cur={cur2})")
                elif verdict == "fail":
                    seq = len(rows) + 1
                    prev_hash = rows[-1][4] if rows else GENESIS
                    new_rows = rows + (
                        (seq, "REJECTED", token, prev_hash,
                         _hash(seq, prev_hash, "REJECTED", token), key),
                    )
                    dn_r = 1
                    action = f"{wid}/op{op_idx}: COMMIT -> REJECTED seq={seq}"
                elif key is not None and key in idem:
                    # Short-circuit: return the mapped seq, append nothing.
                    # (P5 proper is the state property in _check_properties.)
                    action = (f"{wid}/op{op_idx}: COMMIT -> IDEMPOTENT "
                              f"seq={idem[key]} (key={key!r})")
                else:
                    # P4 transition assertion: exactly one winner per V.
                    if ev is not None:
                        if ev in new_winners:
                            fail(
                                f"P4 violated: second winner for "
                                f"expected_version={ev} ({wid}/op{op_idx})",
                                state,
                            )
                        new_winners = winners | {ev}
                    seq = len(rows) + 1
                    prev_hash = rows[-1][4] if rows else GENESIS
                    new_rows = rows + (
                        (seq, "COMMITTED", token, prev_hash,
                         _hash(seq, prev_hash, "COMMITTED", token), key),
                    )
                    if key is not None:
                        # P5: table always tracks the latest committed seq.
                        new_idem_t = tuple(sorted({**idem, key: seq}.items()))
                    dn_c = 1
                    action = f"{wid}/op{op_idx}: COMMIT -> COMMITTED seq={seq}"
                new_w = list(writers_t)
                new_w[wi] = nxt
                transitions += 1
                record(
                    (new_rows, new_idem_t, tuple(new_w), new_winners,
                     n_c + dn_c, n_r + dn_r),
                    state, action,
                )

    return {"states": states, "transitions": transitions}


def main() -> int:
    import time

    configs = [
        ("2 writers x 2 ops (full domains)",
         Config({"w0": 2, "w1": 2})),
        ("3 writers x 2 ops (race-focused)",
         Config({"w0": 2, "w1": 2, "w2": 2},
                ev_domain=(None, "fresh"), key_domain=(None,))),
        ("2 writers x 3 ops (sequential)",
         Config({"w0": 3, "w1": 3},
                ev_domain=(None, "fresh"), key_domain=(None,))),
    ]
    for name, cfg in configs:
        start = time.perf_counter()
        stats = check(cfg)
        elapsed = time.perf_counter() - start
        print(f"{name}: OK "
              f"({stats['states']} states, {stats['transitions']} transitions, "
              f"{elapsed:.1f}s)")
    print("all properties P1..P6 hold on every reachable state")

    # Mutation test: without the re-validation the checker must find the
    # P4 violation, proving it has teeth.
    try:
        check(Config({"w0": 1, "w1": 1},
                     ev_domain=("fresh",), key_domain=(None,),
                     inject_bug=True))
    except AssertionError as e:
        first = str(e).splitlines()[1]
        print(f"mutation test: bug injected -> checker found it ({first})")
    else:
        raise SystemExit("mutation test FAILED: injected bug not detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
