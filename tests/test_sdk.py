"""Tests for the WORLD client SDK (world_sdk).

Covers: validation parity with the server's constraint checks, intent
round-trip on a client-owned ledger, hash-chain interoperability with the
server ledger format, the embedding sidecar (add/search), the timestamp
index (resolve boundaries), and time-travel reads (state_at_block,
state_at_time).
"""

import math

import pytest

from world_engine.core import engine
from world_engine.core.engine import (
    SEED_CAPACITY,
    SEED_ENTITY_ID,
    check_constraints,
)
from world_sdk import EmbeddingSidecar, LocalLedger, WorldClient
from world_sdk.ledger import _hash_record as sdk_hash_record
from world_sdk.ledger import normalize_deltas


@pytest.fixture()
def ledger(tmp_path):
    return LocalLedger(tmp_path / "client.db")


@pytest.fixture()
def sidecar(tmp_path):
    return EmbeddingSidecar(tmp_path / "index.db")


@pytest.fixture()
def client(tmp_path):
    return WorldClient(
        ledger_path=tmp_path / "client.db",
        index_path=tmp_path / "index.db",
    )


# ---------------------------------------------------------------------------
# Validation parity with the server
# ---------------------------------------------------------------------------


def test_sdk_hash_matches_engine():
    """The SDK hash material is identical to the server's, pinned here."""
    from world_engine.core.engine import _hash_record as engine_hash_record

    args = (
        "2026-09-22T10:00:00+00:00",
        "node_x",
        "ALLOCATE",
        '{"a": 1}',
        "abc123",
        "COMMITTED",
    )
    assert sdk_hash_record(*args) == engine_hash_record(*args)
    genesis = (
        "2026-09-22T10:00:00+00:00",
        "node_x",
        "ALLOCATE",
        '{"a": 1}',
        None,
        "REJECTED",
    )
    assert sdk_hash_record(*genesis) == engine_hash_record(*genesis)


@pytest.mark.parametrize(
    "entity_id,action,deltas,note",
    [
        ("", "ALLOCATE", None, ""),  # empty entity_id
        ("node", "", None, ""),  # empty action
        ("node", "ALLOCATE", None, None),  # note not a string
        ("node", "ALLOCATE", {"capacity": float("nan")}, ""),  # NaN
        ("node", "ALLOCATE", {"cash": float("inf")}, ""),  # Infinity
        ("node", "ALLOCATE", {"capacity": True}, ""),  # bool is not a number
        ("node", "ALLOCATE", "nonsense", ""),  # bad deltas shape
        ("node", "ALLOCATE", (1.0, 2.0, 3.0), ""),  # bad tuple length
    ],
)
def test_malformed_intents_raise_value_error(ledger, entity_id, action, deltas, note):
    """Malformed intents raise ValueError, never produce a verdict."""
    with pytest.raises(ValueError):
        ledger.intent(entity_id, action, deltas=deltas, note=note)


def test_server_rejects_same_malformed_classes(isolated_db):
    """The server's validation rejects the same malformed classes."""
    bad = [
        {"entity_id": ""},
        {"action": ""},
        {"note": None},
        {"requested_delta_capacity": float("nan")},
        {"requested_delta_cash": float("inf")},
        {"requested_delta_capacity": True},
    ]
    for overrides in bad:
        kwargs = {
            "entity_id": "node_x",
            "action": "ALLOCATE",
            "requested_delta_capacity": 0.0,
            "requested_delta_cash": 0.0,
            "note": "",
        }
        kwargs.update(overrides)
        with pytest.raises(ValueError):
            engine.execute_deterministic_transition(engine.IntentTransaction(**kwargs))
    # None of the malformed attempts reached the ledger.
    assert engine.get_ledger(limit=10) == []


@pytest.mark.parametrize(
    "capacity,cash,status,delta_cap,delta_cash,expected",
    [
        (1000.0, 50000.0, "ACTIVE", -200.0, 5000.0, "COMMITTED"),
        (1000.0, 50000.0, "ACTIVE", -1000.0, -50000.0, "COMMITTED"),  # exact zero
        (1000.0, 50000.0, "ACTIVE", -1000.01, 0.0, "REJECTED"),  # physical
        (1000.0, 50000.0, "ACTIVE", 0.0, -50000.01, "REJECTED"),  # financial
        (1000.0, 50000.0, "LOCKED", -10.0, 0.0, "REJECTED"),  # lock first
    ],
)
def test_constraint_verdict_parity_with_server(
    capacity, cash, status, delta_cap, delta_cash, expected
):
    """The SDK verdict equals the server policy for the same inputs."""
    reason = check_constraints(capacity, cash, status, delta_cap, delta_cash)
    assert ("COMMITTED" if reason is None else "REJECTED") == expected


def test_deltas_normalization():
    assert normalize_deltas(None) == (0.0, 0.0)
    assert normalize_deltas({}) == (0.0, 0.0)
    assert normalize_deltas({"capacity": -5}) == (-5.0, 0.0)
    assert normalize_deltas({"cash": 10.5}) == (0.0, 10.5)
    assert normalize_deltas((-3.0, 7.0)) == (-3.0, 7.0)
    assert normalize_deltas([1, 2]) == (1.0, 2.0)


# ---------------------------------------------------------------------------
# Intent round-trip on the client ledger
# ---------------------------------------------------------------------------


def test_intent_round_trip_and_materialized_state(ledger):
    r = ledger.intent(SEED_ENTITY_ID, "ALLOCATE", {"capacity": -200.0}, "plan A")
    assert r["status"] == "COMMITTED"
    assert r["transaction_id"] == 1

    entity = ledger.get_entity(SEED_ENTITY_ID)
    assert entity is not None
    assert entity["capacity"] == pytest.approx(SEED_CAPACITY - 200.0)

    bad = ledger.intent(SEED_ENTITY_ID, "DRAIN", {"capacity": -999999.0})
    assert bad["status"] == "REJECTED"
    assert "Capacity cannot drop below zero" in bad["details"]["reason"]

    # Rejected attempts are logged but do not mutate state.
    entity = ledger.get_entity(SEED_ENTITY_ID)
    assert entity["capacity"] == pytest.approx(SEED_CAPACITY - 200.0)
    rows = ledger.get_ledger(limit=10)
    assert len(rows) == 2
    assert {row["status"] for row in rows} == {"COMMITTED", "REJECTED"}

    ok, bad_id = ledger.verify_chain()
    assert (ok, bad_id) == (True, None)


def test_unknown_entity_rejected_but_logged(ledger):
    r = ledger.intent("node_ghost", "SPOOF", {"capacity": 1.0})
    assert r["status"] == "REJECTED"
    assert "Unknown entity" in r["details"]["reason"]
    assert ledger.get_ledger(entity_id="node_ghost")[0]["status"] == "REJECTED"


def test_note_none_becomes_empty_string(client):
    r = client.intent(SEED_ENTITY_ID, "OBSERVE", note=None)
    assert r["status"] == "COMMITTED"
    assert r["details"]["intent"]["note"] == ""


def test_client_ledger_verifies_with_server_verifier(ledger, tmp_path, monkeypatch):
    """Strongest interop claim: the server's verify_chain accepts the
    client's ledger file when pointed at it."""
    ledger.intent(SEED_ENTITY_ID, "ALLOCATE", {"capacity": -50.0})
    ledger.intent(SEED_ENTITY_ID, "DRAIN", {"capacity": -999999.0})
    monkeypatch.setenv("WORLD_DB_PATH", str(tmp_path / "client.db"))
    assert engine.verify_chain() == (True, None)


# ---------------------------------------------------------------------------
# Embedding sidecar
# ---------------------------------------------------------------------------


def test_embedding_add_search_ordering(sidecar):
    sidecar.add(1, [1.0, 0.0])
    sidecar.add(2, [0.0, 1.0])
    sidecar.add(3, [1.0, 1.0])

    hits = sidecar.search([1.0, 0.0], k=3)
    assert [h for h, _ in hits] == [1, 3, 2]
    assert hits[0][1] == pytest.approx(1.0)
    assert hits[2][1] == pytest.approx(0.0)
    # Orthogonal vectors score exactly 0.
    assert hits[1][1] == pytest.approx(1 / math.sqrt(2))


def test_search_empty_index_returns_empty(sidecar):
    assert sidecar.search([1.0, 2.0], k=5) == []


def test_search_k_zero_and_k_larger_than_n(sidecar):
    sidecar.add(1, [1.0, 0.0])
    assert sidecar.search([1.0, 0.0], k=0) == []
    hits = sidecar.search([1.0, 0.0], k=99)
    assert len(hits) == 1


def test_dimension_mismatch_rejected(sidecar):
    sidecar.add(1, [1.0, 0.0])
    with pytest.raises(ValueError, match="[Dd]imension mismatch"):
        sidecar.add(2, [1.0, 0.0, 0.0])
    with pytest.raises(ValueError, match="[Dd]imension mismatch"):
        sidecar.search([1.0], k=1)


def test_zero_vector_scores_zero(sidecar):
    sidecar.add(1, [0.0, 0.0])
    sidecar.add(2, [1.0, 0.0])
    hits = dict(sidecar.search([1.0, 0.0], k=2))
    assert hits[1] == pytest.approx(0.0)
    assert hits[2] == pytest.approx(1.0)


def test_tie_break_is_deterministic(sidecar):
    sidecar.add(2, [1.0, 0.0])
    sidecar.add(1, [1.0, 0.0])
    hits = sidecar.search([1.0, 0.0], k=2)
    assert [h for h, _ in hits] == [1, 2]


def test_add_replaces_existing_vector(sidecar):
    sidecar.add(1, [1.0, 0.0])
    sidecar.add(1, [0.0, 1.0])
    hits = sidecar.search([0.0, 1.0], k=1)
    assert hits[0] == (1, pytest.approx(1.0))


def test_sidecar_persists_across_instances(tmp_path):
    first = EmbeddingSidecar(tmp_path / "idx.db")
    first.add(7, [3.0, 4.0])
    first.record_timestamp(7, "2026-09-22T10:00:00+00:00")
    second = EmbeddingSidecar(tmp_path / "idx.db")
    assert second.search([3.0, 4.0], k=1)[0][0] == 7
    assert second.resolve("2026-09-22T11:00:00+00:00") == 7


# ---------------------------------------------------------------------------
# Timestamp index
# ---------------------------------------------------------------------------


def test_resolve_latest_at_or_before(sidecar):
    sidecar.record_timestamp(1, "2026-09-01T00:00:00+00:00")
    sidecar.record_timestamp(2, "2026-09-02T00:00:00+00:00")
    sidecar.record_timestamp(3, "2026-09-03T00:00:00+00:00")
    assert sidecar.resolve("2026-09-02T12:00:00+00:00") == 2
    assert sidecar.resolve("2026-09-03T00:00:00+00:00") == 3  # exact match


def test_resolve_before_first_block_returns_none(sidecar):
    sidecar.record_timestamp(1, "2026-09-01T00:00:00+00:00")
    assert sidecar.resolve("2026-08-31T23:59:59+00:00") is None
    assert sidecar.resolve("2026-09-01T00:00:00+00:00") == 1


def test_equal_timestamps_resolve_to_highest_block(sidecar):
    sidecar.record_timestamp(1, "2026-09-01T00:00:00+00:00")
    sidecar.record_timestamp(2, "2026-09-01T00:00:00+00:00")
    assert sidecar.resolve("2026-09-01T00:00:00+00:00") == 2


def test_naive_datetimes_rejected(sidecar):
    from datetime import datetime

    with pytest.raises(ValueError, match="timezone-aware"):
        sidecar.record_timestamp(1, datetime(2026, 9, 1))  # noqa: DTZ001
    with pytest.raises(ValueError, match="timezone-aware"):
        sidecar.resolve(datetime(2026, 9, 1))  # noqa: DTZ001


def test_record_timestamp_upserts(sidecar):
    sidecar.record_timestamp(1, "2026-09-01T00:00:00+00:00")
    sidecar.record_timestamp(1, "2026-09-05T00:00:00+00:00")
    assert sidecar.resolve("2026-09-03T00:00:00+00:00") is None
    assert sidecar.resolve("2026-09-06T00:00:00+00:00") == 1


def test_block_height_must_be_positive(sidecar):
    with pytest.raises(ValueError):
        sidecar.add(0, [1.0])
    with pytest.raises(ValueError):
        sidecar.record_timestamp(-1, "2026-09-01T00:00:00+00:00")


# ---------------------------------------------------------------------------
# Time-travel reads
# ---------------------------------------------------------------------------


def test_state_at_block_replays_history(client):
    client.intent(SEED_ENTITY_ID, "A", {"capacity": -100.0})
    client.intent(SEED_ENTITY_ID, "B", {"capacity": -100.0})
    client.intent(SEED_ENTITY_ID, "C", {"capacity": -100.0})

    assert client.state_at_block(0)[SEED_ENTITY_ID]["capacity"] == pytest.approx(
        SEED_CAPACITY
    )
    assert client.state_at_block(1)[SEED_ENTITY_ID]["capacity"] == pytest.approx(
        SEED_CAPACITY - 100.0
    )
    assert client.state_at_block(3)[SEED_ENTITY_ID]["capacity"] == pytest.approx(
        SEED_CAPACITY - 300.0
    )
    # Overshoot clamps to the latest height.
    assert client.state_at_block(999)[SEED_ENTITY_ID]["capacity"] == pytest.approx(
        SEED_CAPACITY - 300.0
    )
    with pytest.raises(ValueError):
        client.state_at_block(-1)


def test_state_at_time_resolves_then_replays(client):
    from datetime import UTC, datetime

    t0 = datetime(2026, 9, 1, tzinfo=UTC)
    client.intent(SEED_ENTITY_ID, "A", {"capacity": -100.0})
    h1 = client.latest_height()
    client.record_timestamp(h1, t0)

    client.intent(SEED_ENTITY_ID, "B", {"capacity": -100.0})
    h2 = client.latest_height()
    client.record_timestamp(h2, datetime(2026, 9, 2, tzinfo=UTC))

    state = client.state_at_time(datetime(2026, 9, 1, 12, tzinfo=UTC))
    assert state[SEED_ENTITY_ID]["capacity"] == pytest.approx(SEED_CAPACITY - 100.0)

    state = client.state_at_time("2026-09-03T00:00:00+00:00")
    assert state[SEED_ENTITY_ID]["capacity"] == pytest.approx(SEED_CAPACITY - 200.0)

    with pytest.raises(ValueError, match="No block"):
        client.state_at_time("2026-08-01T00:00:00+00:00")


def test_intent_auto_records_timestamp(client):
    client.intent(SEED_ENTITY_ID, "A", {"capacity": -10.0})
    height = client.latest_height()
    assert client.index.resolve("2999-01-01T00:00:00+00:00") == height


# ---------------------------------------------------------------------------
# Importing server rows
# ---------------------------------------------------------------------------


def test_import_server_ledger_rows(isolated_db, tmp_path):
    """Rows committed by the server import verbatim and keep verifying."""
    engine.execute_deterministic_transition(
        engine.IntentTransaction(SEED_ENTITY_ID, "ALLOCATE", -50.0, 0.0)
    )
    engine.execute_deterministic_transition(
        engine.IntentTransaction(SEED_ENTITY_ID, "DRAIN", -999999.0, 0.0)
    )
    server_rows = engine.get_ledger(limit=10)

    client = WorldClient(
        ledger_path=tmp_path / "synced.db", index_path=tmp_path / "synced_idx.db"
    )
    inserted = client.import_ledger_rows(server_rows)
    assert inserted == 2
    assert client.verify() == (True, None)

    # Materialized state matches the server's.
    assert client.ledger.get_entity(SEED_ENTITY_ID)["capacity"] == pytest.approx(
        engine.get_entity(SEED_ENTITY_ID)["capacity"]
    )
    # Imported history is time-travelable.
    state = client.state_at_block(1)
    assert state[SEED_ENTITY_ID]["capacity"] == pytest.approx(SEED_CAPACITY - 50.0)

    # Re-importing is idempotent.
    assert client.import_ledger_rows(server_rows) == 0


def test_import_rejects_incomplete_rows(ledger):
    with pytest.raises(ValueError, match="missing keys"):
        ledger.import_ledger_rows([{"transaction_id": 1}])


def test_import_rejects_broken_chain(ledger):
    rows = [
        {
            "transaction_id": 1,
            "timestamp": "2026-09-22T10:00:00+00:00",
            "entity_id": SEED_ENTITY_ID,
            "action": "X",
            "payload": "{}",
            "previous_hash": None,
            "record_hash": "tampered",
            "status": "COMMITTED",
        }
    ]
    with pytest.raises(ValueError, match="hash chain"):
        ledger.import_ledger_rows(rows)


def test_client_verify_detects_tampering(client, tmp_path):
    client.intent(SEED_ENTITY_ID, "A", {"capacity": -10.0})
    assert client.verify() == (True, None)
    import sqlite3

    conn = sqlite3.connect(tmp_path / "client.db")
    conn.execute("UPDATE state_ledger SET payload = '{}' WHERE transaction_id = 1")
    conn.commit()
    conn.close()
    ok, bad_id = client.verify()
    assert ok is False and bad_id == 1


# ---------------------------------------------------------------------------
# Adversarial sidecar: the ledger always wins
# ---------------------------------------------------------------------------


def test_state_at_time_phantom_sidecar_height_clamps_to_ledger(client):
    """A timestamp index entry for a height the ledger never reached
    (drifted sidecar) must not break time-travel: the ledger's actual
    latest height wins."""
    client.intent(SEED_ENTITY_ID, "ALLOCATE", {"capacity": -10.0})
    latest = client.latest_height()
    # Phantom entry: the sidecar claims a block far beyond the ledger.
    client.record_timestamp(latest + 1000, "2030-01-01T00:00:00+00:00")
    state = client.state_at_time("2030-01-01T00:00:00+00:00")
    assert state == client.state_at_block(latest)


def _delete_sidecar_files(tmp_path):
    for suffix in ("", "-wal", "-shm", "-journal"):
        p = tmp_path / f"index.db{suffix}"
        if p.exists():
            p.unlink()


def test_deleted_sidecar_degrades_gracefully(tmp_path):
    """Deleting the disposable sidecar loses index data, never ledger
    truth: ledger ops keep working, search/resolve degrade cleanly."""
    ledger_path = tmp_path / "client.db"
    index_path = tmp_path / "index.db"
    client = WorldClient(ledger_path=ledger_path, index_path=index_path)
    client.intent(SEED_ENTITY_ID, "ALLOCATE", {"capacity": -10.0})
    client.add_embedding(1, [1.0, 0.0])
    assert client.verify() == (True, None)

    _delete_sidecar_files(tmp_path)
    rebuilt = WorldClient(ledger_path=ledger_path, index_path=index_path)
    # Ledger truth intact.
    assert rebuilt.verify() == (True, None)
    assert rebuilt.state_at_block(1) == client.state_at_block(1)
    # Index degrades cleanly: empty search, clear resolve failure.
    assert rebuilt.search([1.0, 0.0]) == []
    with pytest.raises(ValueError, match="No block recorded"):
        rebuilt.state_at_time("2030-01-01T00:00:00+00:00")
    # New intents keep working and re-populate the timestamp index.
    r = rebuilt.intent(SEED_ENTITY_ID, "ALLOCATE", {"capacity": -5.0})
    assert r["status"] == "COMMITTED"
    assert rebuilt.state_at_time("2030-01-01T00:00:00+00:00") == rebuilt.state_at_block(
        rebuilt.latest_height()
    )


def test_stale_sidecar_never_returns_unknown_heights(client):
    """A sidecar that stopped being updated returns a subset of the
    ledger's heights, never heights the ledger does not have."""
    client.intent(SEED_ENTITY_ID, "ALLOCATE", {"capacity": -10.0})
    client.intent(SEED_ENTITY_ID, "ALLOCATE", {"capacity": -10.0})
    client.intent(SEED_ENTITY_ID, "ALLOCATE", {"capacity": -10.0})
    # Only the first block was ever indexed.
    client.add_embedding(1, [1.0, 0.0])
    hits = client.search([1.0, 0.0], k=10)
    assert hits, "expected the one indexed vector back"
    assert all(h <= client.latest_height() for h, _ in hits)
    assert [h for h, _ in hits] == [1]


def test_timestamp_index_rebuilds_from_ledger_rows(tmp_path):
    """The documented rebuild path works: re-record timestamps from the
    ledger's own rows after sidecar loss, and time-travel works again."""
    ledger_path = tmp_path / "client.db"
    index_path = tmp_path / "index.db"
    client = WorldClient(ledger_path=ledger_path, index_path=index_path)
    client.intent(SEED_ENTITY_ID, "ALLOCATE", {"capacity": -10.0})
    before = client.state_at_time("2030-01-01T00:00:00+00:00")

    _delete_sidecar_files(tmp_path)
    rebuilt = WorldClient(ledger_path=ledger_path, index_path=index_path)
    # Rebuild: the ledger's own rows carry authoritative timestamps.
    for row in rebuilt.ledger.get_ledger(limit=100000):
        rebuilt.record_timestamp(int(row["transaction_id"]), str(row["timestamp"]))
    after = rebuilt.state_at_time("2030-01-01T00:00:00+00:00")
    assert after == before
