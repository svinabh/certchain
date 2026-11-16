"""Phase 2 tests — wallets, signatures, impersonation, forged records."""

import time

import pytest

from certchain.core.block import Block
from certchain.core.blockchain import Blockchain
from certchain.core.crypto import sha256_hex
from certchain.core.records import SignedRecord
from certchain.core.wallet import Wallet


@pytest.fixture()
def university():
    return Wallet.generate()


@pytest.fixture()
def chain(university):
    chain = Blockchain()
    _, failure = chain.add_signed_record(
        university, "ISSUE", "CERT-2026-0001", "Rahul, B.Tech CSE, 2026"
    )
    assert failure is None, "university ka asli record accept hona chahiye"
    return chain


def test_address_is_deterministic_from_public_key():
    wallet = Wallet.generate()
    assert wallet.address == sha256_hex(wallet.public_key_hex)[:40]
    assert len(wallet.address) == 40


def test_sign_and_verify_roundtrip():
    wallet = Wallet.generate()
    message = "Certificate: Rahul, B.Tech, 2026"
    signature = wallet.sign(message)
    assert Wallet.verify(message, signature, wallet.public_key_hex)
    # ek character badla → verification fail
    assert not Wallet.verify("Certificate: Rahul, B.Tech, 2099", signature, wallet.public_key_hex)


def test_impersonation_is_rejected(university):
    hacker = Wallet.generate()
    # hacker UNIVERSITY ke naam pe record banata hai, apni key se sign karta hai
    record = SignedRecord(
        record_type="ISSUE", cert_id="CERT-FAKE", data="Hacker, PhD, 2026",
        timestamp=time.time(), signer=university.address,
    )
    record.sign(hacker)
    failure = record.verification_failure()
    assert failure is not None and "impersonation" in failure


def test_tampered_payload_is_rejected(university):
    record = SignedRecord(
        record_type="ISSUE", cert_id="CERT-0009", data="Priya, B.Sc, 2026",
        timestamp=time.time(), signer=university.address,
    )
    record.sign(university)
    assert record.verify(), "sahi signature pass hona chahiye"

    record.data = "Priya, PhD, 2026"  # signing ke BAAD data badla
    failure = record.verification_failure()
    assert failure is not None and "signature" in failure


def test_university_can_issue_and_chain_stays_valid(chain, university):
    ok, reason = chain.is_valid()
    assert ok, reason
    record = chain.blocks[1].records[0]
    assert record["signer"] == university.address
    assert record["cert_id"] == "CERT-2026-0001"


def test_forged_signature_breaks_chain(university):
    chain = Blockchain()
    hacker = Wallet.generate()
    forged = SignedRecord(
        record_type="ISSUE", cert_id="CERT-FAKE", data="Hacker, PhD, 2026",
        timestamp=time.time(), signer=university.address,
    )
    forged.sign(hacker)  # nakli key, university ke naam se

    # hacker khud block mine karke chain me ghusata hai
    block = Block(
        index=1, timestamp=time.time(),
        records=[forged.to_dict()],
        previous_hash=chain.blocks[0].hash,
    )
    block.mine()
    chain.blocks.append(block)

    ok, reason = chain.is_valid()
    assert not ok, "forged record wali chain invalid honi chahiye"
    assert reason is not None and "rejected" in reason and "impersonation" in reason
