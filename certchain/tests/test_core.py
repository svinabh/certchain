"""Phase 1 tests — the 4 checks GitHub Actions will run on every push."""

import pytest

from certchain.core.blockchain import Blockchain
from certchain.core.constants import DIFFICULTY_PREFIX, GENESIS_PREVIOUS_HASH


@pytest.fixture()
def chain():
    chain = Blockchain()
    chain.add_block(["Certificate: Rahul, B.Tech CSE, 2026 — ID CERT-2026-0001"])
    chain.add_block(["Certificate: Priya, B.Sc Physics, 2026 — ID CERT-2026-0002"])
    return chain


def test_genesis_links_to_nothing(chain):
    assert chain.blocks[0].previous_hash == GENESIS_PREVIOUS_HASH


def test_blocks_are_linked(chain):
    assert chain.blocks[1].previous_hash == chain.blocks[0].hash
    assert chain.blocks[2].previous_hash == chain.blocks[1].hash


def test_mined_blocks_satisfy_proof_of_work(chain):
    for block in chain.blocks[1:]:
        assert block.hash.startswith(DIFFICULTY_PREFIX)


def test_tampering_is_detected(chain):
    ok, _ = chain.is_valid()
    assert ok, "a freshly built chain must be valid"

    # a hacker edits one record inside block 1
    chain.blocks[1].records = ["Certificate: Rahul, B.Tech CSE, 2099 — ID CERT-2026-0001"]

    ok, reason = chain.is_valid()
    assert not ok, "chain must become invalid after tampering"
    assert reason is not None and "block 1" in reason
