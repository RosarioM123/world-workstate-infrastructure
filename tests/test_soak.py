"""Scaled-down soak gate: chain growth must not degrade write latency.

The full 1M-row soak lives in experiments/soak/soak.py (too slow for
CI). This test builds a 20k-row chain, appends 2k singles in 4 chunks,
and asserts verify() plus bounded p99 drift, guarding against O(n^2)
regressions in the append path.
"""

import time

from world import World


def _p99(xs):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(0.99 * len(xs)))]


def test_soak_no_latency_drift(tmp_path):
    w = World("soak", dir=str(tmp_path))
    for base in range(0, 20_000, 2_000):
        w.update_many([{"n": i} for i in range(base, base + 2_000)])
    assert w.version == 20_000

    p99s = []
    for c in range(4):
        lat = []
        for i in range(500):
            t0 = time.perf_counter()
            w.update({"n": 20_000 + c * 500 + i})
            lat.append(time.perf_counter() - t0)
        p99s.append(_p99(lat))
    assert w.version == 22_000
    assert w.verify()
    # No meaningful drift: last chunk p99 within 5x of the first chunk's.
    assert p99s[-1] < 5 * p99s[0], f"p99 drift: {p99s}"
    # And an absolute sanity cap (pure overhead, no chain-length effect).
    assert p99s[-1] < 0.050, f"p99 too high: {p99s[-1]*1000:.1f} ms"
