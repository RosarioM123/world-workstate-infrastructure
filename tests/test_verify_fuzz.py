"""Fuzz World.verify(): random mutations must always be detected.

Each trial builds a fresh world (mixed COMMITTED/REJECTED rows), applies
one random mutation to one random row via raw SQL (bypassing the API, as
a database-write attacker would), and asserts verify() returns False.

Out of scope (documented limits, covered by tests/test_redteam.py):
tail truncation and full-chain rewrites with recomputed hashes, which an
unkeyed chain cannot detect by construction.
"""

import random
import sqlite3

from world import InvariantViolation, World
from world.invariants import monotonic

N_TRIALS = 500
N_ROWS = 12
SEED = 20261015

TEXT_COLS = ["state", "status", "note", "actor", "timestamp", "prev_hash", "hash"]


def _sql(w, stmt, params=()):
    cx = sqlite3.connect(w.path)
    try:
        cx.execute(stmt, params)
        cx.commit()
    finally:
        cx.close()


def _build_world(d, rng):
    w = World("fuzz", dir=str(d), invariants=[monotonic("n")])
    n = 0
    for i in range(N_ROWS):
        # Random walk with occasional decreases -> mixed verdicts.
        n += rng.choice([-2, -1, 1, 2, 3])
        try:
            w.update(
                {"n": n, "i": i},
                actor=rng.choice([None, "a", "b"]),
                note=rng.choice(["", "note", "a longer note here"]),
            )
        except InvariantViolation:
            pass  # rejected proposals are part of the corpus
    assert w.verify()
    return w


def _flip_text(value, rng):
    """Return a text value guaranteed different from `value`."""
    value = value if isinstance(value, str) else ""
    ops = [
        lambda v: v + "X",
        lambda v: v[:-1] if v else "X",
        lambda v: v[: len(v) // 2] + "~" + v[len(v) // 2 :],
    ]
    for _ in range(10):
        new = rng.choice(ops)(value)
        if new != value:
            return new
    return value + "!"  # fallback, always different


def _mutate(w, rng):
    """Apply one random in-place mutation. Returns (column, operator)."""
    rows = [r[0] for r in sqlite3.connect(w.path).execute(
        "SELECT seq FROM versions ORDER BY seq").fetchall()]
    seq = rng.choice(rows)
    col = rng.choice(TEXT_COLS + ["seq"])
    if col == "seq":
        # Move to an unused seq (a colliding seq would just violate the
        # PRIMARY KEY on UPDATE, which is not a verify() question).
        new_seq = seq + rng.randint(1, 1000)
        _sql(w, "UPDATE versions SET seq = ? WHERE seq = ?", (new_seq, seq))
        return ("seq", "renumber")
    if col == "status":
        cur = sqlite3.connect(w.path).execute(
            "SELECT status FROM versions WHERE seq = ?", (seq,)).fetchone()[0]
        new = "REJECTED" if cur == "COMMITTED" else "COMMITTED"
        _sql(w, "UPDATE versions SET status = ? WHERE seq = ?", (new, seq))
        return ("status", "flip")
    if col in ("prev_hash", "hash"):
        # Swap with another row's value, or corrupt the hex. For prev_hash,
        # the predecessor's hash is the *correct* value, so swapping it in
        # would be a no-op, not an attack: exclude it.
        cands = [s for s in rows if s != seq and not (col == "prev_hash" and s == seq - 1)]
        other = rng.choice(cands)
        if rng.random() < 0.5:
            _sql(w, f"UPDATE versions SET {col} = "
                    "(SELECT hash FROM versions WHERE seq = ?) "
                    "WHERE seq = ?", (other, seq))
            return (col, "cross-row-swap")
    cur = sqlite3.connect(w.path).execute(
        f"SELECT {col} FROM versions WHERE seq = ?", (seq,)).fetchone()[0]
    new = _flip_text(cur if isinstance(cur, str) else "", rng)
    _sql(w, f"UPDATE versions SET {col} = ? WHERE seq = ?", (new, seq))
    return (col, "byte-flip")


def test_verify_detects_random_mutations(tmp_path):
    rng = random.Random(SEED)
    coverage: dict[str, int] = {}
    for trial in range(N_TRIALS):
        d = tmp_path / f"t{trial}"
        d.mkdir()
        w = _build_world(d, rng)
        col, op = _mutate(w, rng)
        assert not w.verify(), (
            f"UNDETECTED mutation: trial {trial}, row column {col!r}, op {op}"
        )
        coverage[col] = coverage.get(col, 0) + 1
    # Every hashed column was attacked many times; all attacks detected.
    missing = [c for c in TEXT_COLS + ["seq"] if coverage.get(c, 0) < 10]
    assert not missing, f"columns with <10 attacks: {missing}"
    print(f"\nverify() fuzz: {N_TRIALS} mutations, "
          f"{N_TRIALS} detected (100%), coverage: {coverage}")
