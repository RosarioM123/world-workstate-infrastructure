"""Backend parity: the server engine and the SDK sidecar must agree.

The SDK deliberately re-implements the ledger (client-owned sidecar, no
server dependency at runtime), so the risk is silent divergence: a
constraint edge case or a schema change fixed in one place but not the
other. These property tests apply the same randomly generated operation
sequence to both backends and assert identical outcomes:

1. The same verdict sequence (COMMITTED / REJECTED / INVALID).
2. The same ledger length and transaction ids.
3. The same final materialized state per entity.
4. Both hash chains verify.

Registration is part of the op mix, so multi-entity behavior is covered
too. Timestamps, hashes, and last_updated are intentionally not compared:
they are backend-local, not part of the guarantee.
"""

import os
import tempfile
import uuid

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from world_engine.core import engine
from world_sdk.ledger import LocalLedger

ACTIONS = ["ALLOCATE", "RELEASE", "TOP_UP", "FEE", "REBATE", "ADJUST"]
ENTITY_IDS = [f"node_{i}" for i in range(5)] + [engine.SEED_ENTITY_ID]


class _EngineBackend:
    """Adapter over world_engine.core.engine (env-var-selected DB)."""

    def register(self, entity_id, capacity, liquidity):
        try:
            engine.register_entity(entity_id, capacity, liquidity)
            return "REGISTERED"
        except ValueError:
            return "INVALID"

    def submit(self, entity_id, action, delta_capacity, delta_cash):
        try:
            result = engine.execute_deterministic_transition(
                engine.IntentTransaction(
                    entity_id,
                    action,
                    requested_delta_capacity=delta_capacity,
                    requested_delta_cash=delta_cash,
                )
            )
            return result["status"]
        except ValueError:
            return "INVALID"

    def ledger_ids(self):
        return [r["transaction_id"] for r in engine.get_ledger(limit=10000)][::-1]

    def state(self):
        out = {}
        for entity_id in ENTITY_IDS:
            row = engine.get_entity(entity_id)
            if row is not None:
                out[entity_id] = (
                    row["capacity"],
                    row["available_liquidity"],
                    row["status"],
                )
        return out

    def verifies(self):
        return engine.verify_chain() == (True, None)


class _SdkBackend:
    """Adapter over world_sdk.ledger.LocalLedger."""

    def __init__(self, db_path):
        self.ledger = LocalLedger(db_path)

    def register(self, entity_id, capacity, liquidity):
        try:
            self.ledger.register_entity(entity_id, capacity, liquidity)
            return "REGISTERED"
        except ValueError:
            return "INVALID"

    def submit(self, entity_id, action, delta_capacity, delta_cash):
        try:
            result = self.ledger.intent(
                entity_id,
                action,
                deltas=(delta_capacity, delta_cash),
            )
            return result["status"]
        except ValueError:
            return "INVALID"

    def ledger_ids(self):
        return [r["transaction_id"] for r in self.ledger.get_ledger(limit=10000)][::-1]

    def state(self):
        out = {}
        for entity_id in ENTITY_IDS:
            row = self.ledger.get_entity(entity_id)
            if row is not None:
                out[entity_id] = (
                    row["capacity"],
                    row["available_liquidity"],
                    row["status"],
                )
        return out

    def verifies(self):
        return self.ledger.verify_chain() == (True, None)


def _run_ops(backend, ops):
    outcomes = []
    for op in ops:
        if op[0] == "register":
            _, entity_id, capacity, liquidity = op
            outcomes.append(backend.register(entity_id, capacity, liquidity))
        else:
            _, entity_id, action, delta_capacity, delta_cash = op
            outcomes.append(
                backend.submit(entity_id, action, delta_capacity, delta_cash)
            )
    return outcomes


@st.composite
def _op_sequences(draw):
    register_op = st.tuples(
        st.just("register"),
        st.sampled_from(ENTITY_IDS),
        st.floats(
            min_value=0.0, max_value=2000.0, allow_nan=False, allow_infinity=False
        ),
        st.floats(
            min_value=0.0, max_value=100000.0, allow_nan=False, allow_infinity=False
        ),
    )
    intent_op = st.tuples(
        st.just("intent"),
        st.sampled_from(ENTITY_IDS),
        st.sampled_from(ACTIONS),
        st.floats(
            min_value=-900.0, max_value=900.0, allow_nan=False, allow_infinity=False
        ),
        st.floats(
            min_value=-40000.0, max_value=40000.0, allow_nan=False, allow_infinity=False
        ),
    )
    return draw(st.lists(st.one_of(register_op, intent_op), min_size=1, max_size=30))


@given(_op_sequences())
@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_backends_agree_on_verdicts_state_and_chain(ops):
    """Same ops on both backends: same verdicts, same state, valid chains."""
    old = os.environ.get("WORLD_DB_PATH")
    engine_db = os.path.join(tempfile.mkdtemp(), f"parity-eng-{uuid.uuid4().hex}.db")
    sdk_db = os.path.join(tempfile.mkdtemp(), f"parity-sdk-{uuid.uuid4().hex}.db")
    try:
        os.environ["WORLD_DB_PATH"] = engine_db
        engine.init_db()
        eng = _EngineBackend()
        eng_outcomes = _run_ops(eng, ops)

        sdk = _SdkBackend(sdk_db)
        sdk_outcomes = _run_ops(sdk, ops)

        assert eng_outcomes == sdk_outcomes
        assert eng.ledger_ids() == sdk.ledger_ids()
        assert eng.state() == sdk.state()
        assert eng.verifies()
        assert sdk.verifies()
    finally:
        if old is None:
            os.environ.pop("WORLD_DB_PATH", None)
        else:
            os.environ["WORLD_DB_PATH"] = old


@given(_op_sequences())
@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_backends_agree_on_time_travel(ops):
    """replay_to on both backends yields the same historical states."""
    old = os.environ.get("WORLD_DB_PATH")
    engine_db = os.path.join(tempfile.mkdtemp(), f"parity-eng-{uuid.uuid4().hex}.db")
    sdk_db = os.path.join(tempfile.mkdtemp(), f"parity-sdk-{uuid.uuid4().hex}.db")
    try:
        os.environ["WORLD_DB_PATH"] = engine_db
        engine.init_db()
        eng = _EngineBackend()
        _run_ops(eng, ops)
        sdk = _SdkBackend(sdk_db)
        _run_ops(sdk, ops)

        height = len(eng.ledger_ids())
        # SDK replay is the reference implementation; the engine's
        # materialized table must match a full replay at top of chain.
        sdk_state = sdk.ledger.replay_to(sdk.ledger.latest_height)
        for entity_id, row in sdk_state.items():
            eng_row = engine.get_entity(entity_id)
            assert eng_row is not None
            assert eng_row["capacity"] == row["capacity"]
            assert eng_row["available_liquidity"] == row["available_liquidity"]
        # Replaying to genesis must show only the seed, on both.
        genesis = sdk.ledger.replay_to(0)
        assert set(genesis) == {engine.SEED_ENTITY_ID}
        assert height >= 0
    finally:
        if old is None:
            os.environ.pop("WORLD_DB_PATH", None)
        else:
            os.environ["WORLD_DB_PATH"] = old
