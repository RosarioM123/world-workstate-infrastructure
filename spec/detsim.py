"""Deterministic simulation testing for ``World`` (FoundationDB-style).

Real OS threads race, but a seeded scheduler decides the exact
interleaving: workers block at instrumented yield points (the
fast-path read, each invariant judgment) and the scheduler wakes them
one at a time, so only one worker ever runs between yield points. The
same seed therefore reproduces the same interleaving exactly.

Yield points are added by monkeypatching (scoped to the simulation,
restored afterwards), so the *real* ``World.update`` runs unmodified:

- ``World._latest_committed`` yields, except inside the atomic section
  (the re-check must not yield: the worker holds the SQLite write lock
  there, and another worker's ``BEGIN IMMEDIATE`` would block the OS
  thread and deadlock the single-logical-thread simulation).
- Each invariant yields before judging (judgment is always lock-free).
- A connection proxy sniffs ``BEGIN IMMEDIATE`` / ``COMMIT`` /
  ``ROLLBACK`` to track the atomic section and assert it is never
  re-entered (atomic sections contain no yield points, so SQLite-level
  serialization is real but uncontended by construction).

What this explores beyond the threaded linearizability test: exact,
reproducible interleavings of reads and judgments against commits,
including rare ones (a judgment against v5 whose REJECTED row lands
after a concurrent v6 commit). What it does not do: it cannot explore
interleavings *inside* the atomic section, which is correct because
SQLite serializes those for real.
"""

from __future__ import annotations

import random
import threading
from typing import Any, Callable

from world import World

_tls = threading.local()


class _SimConnection:
    """Proxy tracking atomic-section entry/exit for the simulator."""

    def __init__(self, real: Any, sim: "Simulation"):
        self._real = real
        self._sim = sim

    def execute(self, sql: str, *args: Any, **kwargs: Any) -> Any:
        if isinstance(sql, str) and sql.strip().upper().startswith("BEGIN"):
            self._sim.sched.enter_atomic()
        return self._real.execute(sql, *args, **kwargs)

    def commit(self) -> Any:
        self._sim.sched.exit_atomic()
        return self._real.commit()

    def rollback(self) -> Any:
        self._sim.sched.exit_atomic()
        return self._real.rollback()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._real, name)


class Scheduler:
    """Seeded deterministic scheduler over worker threads."""

    def __init__(self, seed: int, script: list[int] | None = None):
        self.rng = random.Random(seed)
        self.script = list(script) if script is not None else None
        self._script_pos = 0
        self.mu = threading.Lock()
        self.cv = threading.Condition(self.mu)
        self.waiting: dict[int, str] = {}
        self.granted: set[int] = set()
        self.running: int | None = None
        self.finished: set[int] = set()
        self.nclients = 0
        self.atomic_holder = False
        self.tick_counter = 0
        self.log: list[tuple[int, int, str]] = []  # (tick, cid, point)
        self.errors: dict[int, BaseException] = {}

    # -- called from workers ------------------------------------------------
    def yield_point(self, cid: int | None, name: str) -> None:
        if cid is None:
            return
        with self.cv:
            self.tick_counter += 1
            self.log.append((self.tick_counter, cid, name))
            self.waiting[cid] = name
            self.cv.notify_all()
            self.cv.wait_for(lambda: cid in self.granted)
            self.granted.discard(cid)

    def tick(self) -> int:
        with self.mu:
            self.tick_counter += 1
            return self.tick_counter

    def finish(self, cid: int) -> None:
        with self.cv:
            self.finished.add(cid)
            self.waiting.pop(cid, None)
            self.cv.notify_all()

    def enter_atomic(self) -> None:
        assert not self.atomic_holder, "atomic section re-entered"
        self.atomic_holder = True

    def exit_atomic(self) -> None:
        self.atomic_holder = False

    # -- scheduler loop ------------------------------------------------------
    def _choose(self) -> int:
        if self.script is not None and self._script_pos < len(self.script):
            nxt = self.script[self._script_pos]
            self._script_pos += 1
            if nxt not in self.waiting:
                raise AssertionError(
                    f"script[{self._script_pos - 1}]={nxt} not waiting; "
                    f"waiting={sorted(self.waiting)}"
                )
            return nxt
        return self.rng.choice(sorted(self.waiting))

    def _wrap(self, cid: int, fn: Callable[[int], None]) -> None:
        _tls.cid = cid
        try:
            fn(cid)
        except Exception as e:  # noqa: BLE001 - collected and re-raised
            self.errors[cid] = e
        finally:
            self.finish(cid)

    def run(self, clients: list[tuple[int, Callable[[int], None]]]) -> None:
        self.nclients = len(clients)
        threads = []
        # Sequential startup: deterministic registration order.
        for cid, fn in clients:
            t = threading.Thread(target=self._wrap, args=(cid, fn), daemon=True)
            t.start()
            threads.append(t)
            with self.cv:
                self.cv.wait_for(lambda: cid in self.waiting or cid in self.finished)
        with self.cv:
            while len(self.finished) < self.nclients:
                self.cv.wait_for(
                    lambda: (bool(self.waiting) and self.running is None)
                    or len(self.finished) == self.nclients
                )
                if len(self.finished) == self.nclients:
                    break
                nxt = self._choose()
                del self.waiting[nxt]
                self.running = nxt
                self.granted.add(nxt)
                self.cv.notify_all()
                self.cv.wait_for(lambda: nxt in self.waiting or nxt in self.finished)
                self.running = None
        for t in threads:
            t.join()


class Simulation:
    """Scoped deterministic simulation around one real ``World``."""

    def __init__(self, seed: int, script: list[int] | None = None):
        self.sched = Scheduler(seed, script)
        self.ops: list[dict[str, Any]] = []  # recorded op outcomes
        self._op_lock = threading.Lock()
        self._saved: dict[str, Any] = {}

    # -- monkeypatching (instance-scoped, restored by unpatch) ---------------
    def patch(self, w: World) -> None:
        sim = self

        orig_connect = w._connect
        orig_latest = w._latest_committed
        orig_invariants = w._invariants
        self._saved = {
            "_connect": orig_connect,
            "_latest_committed": orig_latest,
            "_invariants": orig_invariants,
        }

        def sim_connect() -> _SimConnection:
            return _SimConnection(orig_connect(), sim)

        def sim_latest(cx: Any) -> Any:
            if not sim.sched.atomic_holder:
                sim.sched.yield_point(getattr(_tls, "cid", None), "read")
            return orig_latest(cx)

        def wrap_inv(inv: Callable) -> Callable:
            def check(old: dict[str, Any], new: dict[str, Any]) -> None:
                sim.sched.yield_point(getattr(_tls, "cid", None), "judge")
                return inv(old, new)

            return check

        w._connect = sim_connect  # type: ignore[method-assign]
        w._latest_committed = sim_latest  # type: ignore[method-assign]
        w._invariants = tuple(wrap_inv(i) for i in orig_invariants)

    def unpatch(self, w: World) -> None:
        w._connect = self._saved["_connect"]
        w._latest_committed = self._saved["_latest_committed"]
        w._invariants = self._saved["_invariants"]
        self._saved = {}

    def record_op(self, cid: int, invoke: int, resp: int,
                  expected: int | None, k: int, result: tuple) -> None:
        with self._op_lock:
            self.ops.append({
                "cid": cid, "invoke": invoke, "resp": resp,
                "expected": expected, "k": k, "result": result,
            })
