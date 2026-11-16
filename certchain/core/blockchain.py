"""Blockchain — the chain that links blocks and guards the whole history.

Three responsibilities:
1. Create the genesis block (chain's birth certificate)
2. add_block(): link a new block to the latest one and mine it
3. is_valid(): re-derive every hash and re-check every link
"""

import time
from typing import List, Optional, Tuple

from .block import Block
from .constants import (
    DIFFICULTY_PREFIX,
    GENESIS_MESSAGE,
    GENESIS_PREVIOUS_HASH,
    GENESIS_TIMESTAMP,
)
from .records import SignedRecord
from .wallet import Wallet


class Blockchain:
    def __init__(self, difficulty_prefix: str = DIFFICULTY_PREFIX):
        self.difficulty_prefix = difficulty_prefix
        self.blocks: List[Block] = [self._create_genesis()]

    @staticmethod
    def _create_genesis() -> Block:
        """Block 0: created, not mined — timestamp FIXED (GENESIS_TIMESTAMP) so
        every node's genesis is byte-identical → same hash → syncable."""
        return Block(
            index=0,
            timestamp=GENESIS_TIMESTAMP,
            records=[GENESIS_MESSAGE],
            previous_hash=GENESIS_PREVIOUS_HASH,
        )

    def add_block(self, records: list) -> Block:
        """Mine a new block for the given records (str or signed dict) and append it."""
        last = self.blocks[-1]
        block = Block(
            index=len(self.blocks),
            timestamp=time.time(),
            records=list(records),
            previous_hash=last.hash,
        )
        block.mine(self.difficulty_prefix)
        self.blocks.append(block)
        return block

    def add_signed_record(
        self, wallet: Wallet, record_type: str, cert_id: str, data: str
    ) -> Tuple[Optional[Block], Optional[str]]:
        """Sign a record with `wallet`, verify it, and mine it into a block.

        Returns (block, None) on success, or (None, reason) when verification
        fails — the chain never accepts an unverified author.
        """
        record = SignedRecord(
            record_type=record_type,
            cert_id=cert_id,
            data=data,
            timestamp=time.time(),
            signer=wallet.address,
        )
        record.sign(wallet)
        failure = record.verification_failure()
        if failure:
            return None, failure
        block = self.add_block([record.to_dict()])
        return block, None

    def is_valid(self) -> Tuple[bool, Optional[str]]:
        """Validate the entire chain. Returns (ok, reason).

        Re-derives every block's hash from its content and compares against
        what was stored — so ANY past tampering shows up here.
        """
        if not self.blocks:
            return False, "chain is empty"

        for i, block in enumerate(self.blocks):
            # 1) stored hash must match freshly computed content hash
            if block.compute_hash() != block.hash:
                return False, f"hash mismatch in block {i} — content was tampered"
            # 2) every block (except genesis) must link to the one before it
            if i > 0 and block.previous_hash != self.blocks[i - 1].hash:
                return False, f"broken link at block {i} — previous_hash does not match"
            # 3) every block (except genesis) must carry valid proof-of-work
            if i > 0 and not block.hash.startswith(self.difficulty_prefix):
                return False, f"invalid proof-of-work in block {i}"
            # 4) every signed record must verify against its claimed author
            for j, record in enumerate(block.records):
                if isinstance(record, dict) and "signature" in record:
                    failure = SignedRecord(**record).verification_failure()
                    if failure:
                        return False, f"record {j} in block {i} rejected: {failure}"

        return True, None

    @classmethod
    def from_dicts(cls, blocks: List[dict], difficulty_prefix: str = DIFFICULTY_PREFIX) -> "Blockchain":
        """Rebuild a Blockchain from JSON dicts (e.g., a peer chain that won consensus).

        TRUSTS the data it is given — caller must run validate_chain_dicts()
        first. That separation keeps consensus logic honest: validate, then adopt.
        """
        chain = cls.__new__(cls)
        chain.difficulty_prefix = difficulty_prefix
        chain.blocks = []
        for d in blocks:
            block = Block(
                index=d["index"],
                timestamp=d["timestamp"],
                records=d["records"],
                previous_hash=d["previous_hash"],
                nonce=d["nonce"],
                version=d["version"],
            )
            block.hash = d["hash"]
            chain.blocks.append(block)
        return chain


def validate_chain_dicts(blocks: List[dict], difficulty_prefix: str = DIFFICULTY_PREFIX) -> Optional[str]:
    """Validate a JSON chain received from a peer — WITHOUT trusting it.

    Full re-hash + link check + proof-of-work + record signatures, same rules
    as Blockchain.is_valid() but on plain dicts. Returns failure reason or None.
    """
    if not blocks:
        return "chain is empty"
    for i, d in enumerate(blocks):
        try:
            block = Block(
                index=d["index"],
                timestamp=d["timestamp"],
                records=d["records"],
                previous_hash=d["previous_hash"],
                nonce=d["nonce"],
                version=d["version"],
            )
        except (KeyError, TypeError):
            return f"block {i} malformed"
        if block.compute_hash() != d.get("hash"):
            return f"hash mismatch in block {i} — content was tampered"
        if i == 0:
            if d["previous_hash"] != GENESIS_PREVIOUS_HASH:
                return "genesis does not link to 64 zeros"
        else:
            if d["previous_hash"] != blocks[i - 1]["hash"]:
                return f"broken link at block {i}"
            if not d["hash"].startswith(difficulty_prefix):
                return f"invalid proof-of-work in block {i}"
            for j, record in enumerate(d["records"]):
                if isinstance(record, dict) and "signature" in record:
                    failure = SignedRecord(**record).verification_failure()
                    if failure:
                        return f"record {j} in block {i} rejected: {failure}"
    return None
