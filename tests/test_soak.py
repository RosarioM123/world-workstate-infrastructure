"""Scaled-down soak gate: chain growth must not degrade write latency.

The full 1M-row soak lives in experiments/soak/soak.py (too slow for
CI). This test builds a 20k-row chain, appends 2k singles in 4 chunks,
and asserts verify() plus bounded p99 drift, guarding against O(n^2)
regressions in the append path.

Load-insensitive by design: latencies are measured with
time.process_time(), which counts only CPU time consumed by this
process. Wall-clock timing (time.perf_counter()) went red whenever the
host was loaded (audit T-1: two concurrent suites produced p99 drift
[0.0016, 0.050, 0.0466, 0.0501] and failed the 5x ratio), because
descheduling inflates wall time without any change in the append path.
An O(n) append regression is extra CPU work per update, so CPU time
still catches it while host load does not move the gate.

The drift check is a row-count scaling check, not a same-window
comparison: per-update cost is measured at a 2k-row chain and again at
a 20k-row chain, and the 20k cost must stay within 5x of the 2k cost.
A same-window check (first vs last chunk over 20k to 22k rows) cannot
catch linear growth, because the chain grows only 10% across the
window; a 10x chain growth makes linear per-append cost show up as a
~10x cost ratio. The absolute cap is the second guard: per-update CPU
time at 20k rows must stay under 50 ms.
"""

import time

from world import World


def _p99(xs):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(0.99 * len(xs)))]


def _measure_chunk(w, start_n, count=500):
    lat = []
    for i in range(count):
        t0 = time.process_time()
        w.update({"n": start_n + i})
        lat.append(time.process_time() - t0)
    return _p99(lat)


def test_soak_no_latency_drift(tmp_path):
    w = World("soak", dir=str(tmp_path))
    w.update_many([{"n": i} for i in range(2_000)])
    assert w.version == 2_000
    p99_small = _measure_chunk(w, 2_000)

    w.update_many([{"n": i} for i in range(2_500, 20_000)])
    assert w.version == 20_000

    p99s = []
    for c in range(4):
        p99s.append(_measure_chunk(w, 20_000 + c * 500))
    assert w.version == 22_000
    assert w.verify()
    # Sub-linear scaling: per-update CPU cost at a 20k-row chain must stay
    # within 5x of the cost at a 2k-row chain. A linear per-append cost
    # would show up as roughly a 10x ratio across this 10x chain growth.
    assert p99s[-1] < 5 * p99_small, (
        f"p99 scaling: 2k-row {p99_small * 1000:.1f} ms vs "
        f"20k-row {[round(p * 1000, 1) for p in p99s]} ms"
    )
    # No meaningful drift across the 20k window either.
    assert p99s[-1] < 5 * p99s[0], f"p99 drift: {p99s}"
    # And an absolute sanity cap on per-update CPU time at 20k rows.
    assert p99s[-1] < 0.050, f"p99 too high: {p99s[-1] * 1000:.1f} ms"
