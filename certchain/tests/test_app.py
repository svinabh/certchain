"""Phase 4 tests — FakeUPIBank, relayer flow, invisible verify API."""

import time

import pytest
import requests

from certchain.app.api import create_app
from certchain.app.relayer import Relayer
from certchain.app.upi import FakeUPIBank
from certchain.core.records import SignedRecord
from certchain.core.wallet import Wallet
from certchain.network.helpers import NodeServer, free_port, wait_up
from certchain.network.node import create_app as create_node_app


@pytest.fixture()
def university():
    return Wallet.generate()


@pytest.fixture()
def node_url(university):
    """Real chain node — relayer ise HTTP pe use karta hai (asli architecture)."""
    port = free_port()
    server = NodeServer(create_node_app(port), port)
    server.start()
    url = f"http://127.0.0.1:{port}"
    wait_up(url)
    yield url
    server.server.shutdown()
    server.server.server_close()


@pytest.fixture()
def client(university, node_url):
    app = create_app(node_url, issuer_wallets={"Demo University": university})
    return app.test_client()


def test_create_account_gives_demo_balance(client):
    resp = client.post("/accounts", json={"account_id": "test@upi"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["balance_rupees"] == 500
    assert "demo" in body["message"]


def test_bank_pay_updates_balances_and_insufficient_fails():
    bank = FakeUPIBank(default_balance_rupees=100)
    bank.create_account("a@upi")

    receipt, reason = bank.pay("a@upi", 40)
    assert receipt is not None and reason is None
    assert receipt.upi_txn_id.startswith("UPI")
    assert bank.balance("a@upi") == 60

    receipt2, reason2 = bank.pay("a@upi", 1000)
    assert receipt2 is None and "insufficient" in reason2
    assert bank.balance("a@upi") == 60  # failed payment ne kuch kata nahi


def test_issue_charges_fee_and_lands_on_chain(client, node_url):
    client.post("/accounts", json={"account_id": "rahul@upi"})

    resp = client.post("/issue", json={
        "account_id": "rahul@upi", "university": "Demo University",
        "cert_id": "CERT-TEST-1", "holder": "Rahul", "course": "B.Tech CSE",
    })
    body = resp.get_json()
    assert resp.status_code == 201
    assert body["status"] == "issued"
    assert body["fee_rupees"] == 5
    assert body["block_index"] == 1
    assert body["upi_txn_id"].startswith("UPI")

    # user ka balance ₹5 kam hua
    assert client.get("/accounts/rahul@upi").get_json()["balance_rupees"] == 495

    # chain pe record pahuncha + signature ab bhi valid
    chain = requests.get(f"{node_url}/chain", timeout=5).json()["chain"]
    record = chain[1]["records"][0]
    assert record["cert_id"] == "CERT-TEST-1"
    assert SignedRecord(**record).verify()


def test_verify_found_and_missing(client):
    client.post("/accounts", json={"account_id": "rahul@upi"})
    client.post("/issue", json={
        "account_id": "rahul@upi", "university": "Demo University",
        "cert_id": "CERT-TEST-2", "holder": "Rahul", "course": "B.Tech CSE",
    })

    found = client.get("/verify/CERT-TEST-2").get_json()
    assert found["verified"] is True
    assert found["holder"] == "Rahul"
    assert found["course"] == "B.Tech CSE"
    assert found["university"] == "Demo University"
    assert found["block_index"] == 1
    assert found["fee"].startswith("₹0")  # verify FREE

    missing = client.get("/verify/NOPE-404").get_json()
    assert missing["verified"] is False
    assert "nahi mila" in missing["reason"]


def test_verify_handles_legacy_string_data_records(client, node_url, university):
    """Phase 3 ke purane records ka data plain string tha (JSON nahi) —
    verify ko 500 nahi dena chahiye, gracefully handle karna chahiye."""
    legacy = SignedRecord(
        record_type="ISSUE", cert_id="CERT-LEGACY-1",
        data="Rahul, B.Tech CSE, 2026",  # plain string — NOT JSON
        timestamp=time.time(), signer=university.address,
    )
    legacy.sign(university)
    assert requests.post(f"{node_url}/transactions/new", json=legacy.to_dict(), timeout=5).status_code == 201
    assert requests.post(f"{node_url}/mine", timeout=30).status_code == 201

    body = client.get("/verify/CERT-LEGACY-1").get_json()
    assert body["verified"] is True, body
    assert body["holder"] == "Rahul, B.Tech CSE, 2026"
    assert "legacy" in body["university"]


def test_unknown_university_rejected_before_payment(client):
    client.post("/accounts", json={"account_id": "rahul@upi"})

    resp = client.post("/issue", json={
        "account_id": "rahul@upi", "university": "Fake College",
        "cert_id": "CERT-X", "holder": "X", "course": "Y",
    })
    assert resp.status_code == 400
    assert "authorized" in resp.get_json()["reason"]

    # payment se PEHLE reject — balance untouched
    assert client.get("/accounts/rahul@upi").get_json()["balance_rupees"] == 500


def test_refund_when_node_rejects(university, node_url):
    """Node ne record reject kiya → relayer paisa wapas karta hai."""
    bank = FakeUPIBank(default_balance_rupees=100)
    bank.create_account("user@upi")
    relayer = Relayer(node_url, bank, {"Demo University": university})

    # duplicate attack: same record do baar — dusri baar node duplicate reject karega
    record = SignedRecord(
        record_type="ISSUE", cert_id="CERT-R", data="dup", timestamp=123.0,
        signer=university.address,
    )
    record.sign(university)
    dup_dict = record.to_dict()

    first = requests.post(f"{node_url}/transactions/new", json=dup_dict, timeout=5)
    assert first.status_code == 201

    receipt, reason = bank.pay("user@upi", relayer.FEE_ISSUE_RUPEES)
    assert receipt is not None

    relayer.bank.refund(receipt)  # node reject hua — refund
    assert bank.balance("user@upi") == 100
