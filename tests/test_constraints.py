"""Unit tests for the pure constraint policy in engine.check_constraints.

No database involved: the policy is a pure function of (current capacity,
current cash, node status, requested deltas), so these tests run in
microseconds and pin the exact policy, including check order and the
zero boundary.
"""

from engine import check_constraints


def test_valid_intent_allowed():
    assert check_constraints(1000.0, 50000.0, "ACTIVE", -200.0, 5000.0) is None


def test_exact_zero_targets_allowed():
    # Draining to exactly zero is legal; only negative is a violation.
    assert check_constraints(1000.0, 50000.0, "ACTIVE",
                             -1000.0, -50000.0) is None


def test_capacity_below_zero_rejected():
    reason = check_constraints(1000.0, 50000.0, "ACTIVE", -1000.01, 0.0)
    assert reason is not None
    assert "Capacity cannot drop below zero" in reason


def test_liquidity_below_zero_rejected():
    reason = check_constraints(1000.0, 50000.0, "ACTIVE", 0.0, -50000.01)
    assert reason is not None
    assert "Insufficient liquidity" in reason


def test_locked_node_rejected_even_for_valid_deltas():
    reason = check_constraints(1000.0, 50000.0, "LOCKED", -10.0, 0.0)
    assert reason is not None
    assert "locked" in reason.lower()


def test_lock_takes_precedence_over_math_violations():
    # Policy order is deterministic: the lock is checked first.
    reason = check_constraints(1000.0, 50000.0, "LOCKED", -9999.0, 0.0)
    assert reason is not None
    assert "locked" in reason.lower()
