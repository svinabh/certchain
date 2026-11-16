"""Phase 3 tests — node APIs, mempool, aur longest-valid-chain consensus.

Ye Flask test_client pe chalte hain (real ports nahi kholte) —
real-HTTP adversarial integration alag se chalta hai (network_demo + agent).
"""

import time

import pytest

from certchain.core.blockchain import Blockchain, validate_chain_dicts
from certchain.core.records import SignedRecord
from certchain.core.wallet import Wallet
from certchain.network.node import NodeState, create_app, normalize_peer, resolve_consensus


@pytest.fixture()
def university():
    return Wallet.generate()


def make_record(wallet: Wallet, cert_id: str = "CERT-X") -> SignedRecord:
    record = SignedRecord(
        record_type="ISSUE", cert_id=cert_id, data="Rahul, B.Tech CSE, 2026",
        timestamp=time.time(), signer=wallet.address,
    )
    record.sign(wallet)
    return record


def build_signed_chain(wallet: Wallet, extra_blocks: int) -> Blockchain:
    """genesis + `extra_blocks` signed-record blocks wali chain."""
    chain = Blockchain()
    for i in range(extra_blocks):
        record = make_record(wallet, cert_id=f"CERT-{i}")
        assert record.verify()
        chain.add_block([record.to_dict()])
    return chain


def test_normalize_peer():
    assert normalize_peer("http://127.0.0.1:5001/") == "127.0.0.1:5001"
    assert normalize_peer("localhost:6000") == "localhost:6000"
    assert normalize_peer("no-port-given") is None
    assert normalize_peer("") is None
    assert normalize_peer(123) is None


def test_register_peers_and_health():
    app = create_app(1, initial_peers=["127.0.0.1:6001"])
    client = app.test_client()
    resp = client.post("/nodes/register", json={"peers": ["http://127.0.0.1:6002/", "127.0.0.1:6001"]})
    assert resp.status_code == 201
    assert resp.get_json()["peers"] == ["127.0.0.1:6001", "127.0.0.1:6002"]
    health = client.get("/health").get_json()
    assert health["chain_length"] == 1
    assert health["valid"] is True
    assert health["mempool"] == 0


def test_transactions_new_rejects_bad_signature(university):
    app = create_app(1)
    client = app.test_client()
    hacker = Wallet.generate()
    forged = SignedRecord(
        record_type="ISSUE", cert_id="CERT-FAKE", data="Hacker, PhD, 2026",
        timestamp=time.time(), signer=university.address,
    )
    forged.sign(hacker)
    resp = client.post("/transactions/new", json=forged.to_dict())
    assert resp.status_code == 400
    assert "impersonation" in resp.get_json()["error"]
    assert client.get("/pending").get_json()["count"] == 0


def test_transactions_accept_then_mine_grows_chain(university):
    app = create_app(1)
    client = app.test_client()
    record = make_record(university, cert_id="CERT-OK")

    resp = client.post("/transactions/new", json=record.to_dict())
    assert resp.status_code == 201
    assert client.get("/pending").get_json()["count"] == 1

    resp = client.post("/mine")
    assert resp.status_code == 201
    assert resp.get_json()["chain_length"] == 2

    chain_body = client.get("/chain").get_json()
    assert chain_body["length"] == 2
    assert chain_body["chain"][1]["records"][0]["cert_id"] == "CERT-OK"

    ok, reason = app.config["STATE"].chain.is_valid()
    assert ok, reason


def test_mine_with_empty_mempool_fails():
    app = create_app(1)
    resp = app.test_client().post("/mine")
    assert resp.status_code == 400


def test_validate_chain_dicts_catches_tamper(university):
    good = [b.to_dict() for b in build_signed_chain(university, 1).blocks]
    assert validate_chain_dicts(good) is None
    good[1]["records"] = ["TAMPERED!"]
    assert validate_chain_dicts(good) is not None


def test_resolve_adopts_longer_valid_chain(university):
    state = NodeState(chain=Blockchain(), peers={"127.0.0.1:6001"})
    candidate = [b.to_dict() for b in build_signed_chain(university, 2).blocks]  # 3 blocks
    replaced, peer = resolve_consensus(state, lambda p: candidate)
    assert replaced and peer == "127.0.0.1:6001"
    assert len(state.chain.blocks) == 3
    assert validate_chain_dicts([b.to_dict() for b in state.chain.blocks]) is None


def test_resolve_ignores_invalid_longer_chain(university):
    state = NodeState(chain=Blockchain(), peers={"127.0.0.1:6001"})
    candidate = [b.to_dict() for b in build_signed_chain(university, 2).blocks]
    candidate[1]["records"] = ["TAMPERED!"]  # lambi PAR invalid
    replaced, _ = resolve_consensus(state, lambda p: candidate)
    assert replaced is False
    assert len(state.chain.blocks) == 1, "invalid chain kabhi adopt nahi honi chahiye"


def test_resolve_ignores_other_network_chain(university):
    state = NodeState(chain=Blockchain(), peers={"127.0.0.1:6001"})
    candidate = [b.to_dict() for b in build_signed_chain(university, 2).blocks]
    candidate[0]["hash"] = "f" * 64  # alag genesis = doosri network
    replaced, _ = resolve_consensus(state, lambda p: candidate)
    assert replaced is False
