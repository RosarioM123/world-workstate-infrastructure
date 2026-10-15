"""Mechanized verification of the WORLD commit protocol.

Runs the bounded exhaustive model checker (spec/model_check.py) over
three workload configurations: every reachable global state is explored
across all thread interleavings and all adversarial invariant verdicts,
asserting P1..P6 (seq integrity, hash-chain integrity, committed-only
version, exactly-one-winner, idempotency, judgment recorded).

The final assertion is a mutation test: with the expected_version
re-validation removed, the checker must find the P4 violation, proving
the verification has teeth.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "spec"))

from model_check import Config, check  # noqa: E402


def test_protocol_two_writers_full_domains():
    stats = check(Config({"w0": 2, "w1": 2}))
    assert stats["states"] > 100_000  # sanity: the space was actually explored


def test_protocol_three_writers_race_focused():
    stats = check(
        Config(
            {"w0": 2, "w1": 2, "w2": 2},
            ev_domain=(None, "fresh"),
            key_domain=(None,),
        )
    )
    assert stats["states"] > 100_000


def test_protocol_two_writers_sequential():
    stats = check(
        Config(
            {"w0": 3, "w1": 3},
            ev_domain=(None, "fresh"),
            key_domain=(None,),
        )
    )
    assert stats["states"] > 10_000


def test_protocol_checker_detects_injected_bug():
    # Without the atomic re-validation of expected_version, two writers
    # racing on the same "fresh" version must both win: a P4 violation
    # the checker is required to find.
    try:
        check(
            Config(
                {"w0": 1, "w1": 1},
                ev_domain=("fresh",),
                key_domain=(None,),
                inject_bug=True,
            )
        )
    except AssertionError as e:
        assert "P4 violated" in str(e)
    else:
        raise AssertionError("checker failed to detect the injected bug")
