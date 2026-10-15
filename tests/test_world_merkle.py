"""Tests for Merkle inclusion proofs (selective disclosure)."""

import pytest

from world import World


def _world(tmp_path, rows=7):
    w = World("merkle", dir=str(tmp_path))
    for i in range(rows):
        w.update({"n": i})
    return w


def test_merkle_root_stable_and_changes(tmp_path):
    w = _world(tmp_path)
    r1 = w.merkle_root()
    assert w.merkle_root() == r1  # deterministic
    w.update({"n": 99})
    assert w.merkle_root() != r1
    assert len(r1) == 64


def test_merkle_root_empty(tmp_path):
    r = World("empty", dir=str(tmp_path)).merkle_root()
    assert len(r) == 64
    assert World("empty2", dir=str(tmp_path)).merkle_root() == r


def test_inclusion_proof_roundtrip_all_rows(tmp_path):
    # 7 rows: odd leaf count exercises last-node duplication.
    w = _world(tmp_path, rows=7)
    for seq in range(1, 8):
        proof = w.inclusion_proof(seq)
        assert proof["root"] == w.merkle_root()
        assert World.verify_inclusion(proof)
    # Single-row log: empty sibling path.
    w1 = World("merkle1", dir=str(tmp_path))
    w1.update({"n": 0})
    p1 = w1.inclusion_proof(1)
    assert p1["siblings"] == [] and World.verify_inclusion(p1)


def test_inclusion_proof_tamper_rejected(tmp_path):
    w = _world(tmp_path)
    proof = w.inclusion_proof(3)
    bad_leaf = dict(proof, leaf="00" * 32)
    assert not World.verify_inclusion(bad_leaf)
    bad_root = dict(proof, root="ff" * 32)
    assert not World.verify_inclusion(bad_root)
    if proof["siblings"]:
        sibs = [dict(s) for s in proof["siblings"]]
        sibs[0] = dict(sibs[0], hash="00" * 32)
        assert not World.verify_inclusion(dict(proof, siblings=sibs))
    assert not World.verify_inclusion({"bogus": 1})
    assert not World.verify_inclusion("not-a-dict")


def test_inclusion_proof_unknown_seq(tmp_path):
    w = _world(tmp_path)
    with pytest.raises(KeyError):
        w.inclusion_proof(999)


def test_selective_disclosure_needs_no_database(tmp_path):
    # The verifier holds one row plus its proof; everything else stays
    # private. verify_inclusion is static and touches no database.
    w = _world(tmp_path)
    proof = w.inclusion_proof(4)
    row = w.proposal(4)
    assert World.verify_inclusion(proof)
    # The proof is self-contained: drop the world entirely.
    del w
    assert World.verify_inclusion(proof)
    assert row["seq"] == proof["seq"]
