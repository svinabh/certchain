"""Block — one page of the chain.

A block is like a sealed page: it records data (records), points to the
previous page (previous_hash), and carries a fingerprint (hash) of all
its content. Change even one character and the fingerprint changes.
"""

import time
from dataclasses import dataclass, field
from typing import List

from .constants import BLOCK_VERSION, DIFFICULTY_PREFIX
from .crypto import hash_fields


@dataclass
class Block:
    index: int
    timestamp: float
    records: List[str]
    previous_hash: str
    nonce: int = 0
    version: int = BLOCK_VERSION
    hash: str = field(default="", init=False)

    def __post_init__(self):
        # Seal the block with its content hash the moment it is created.
        # (Mining later re-derives it with a nonce that satisfies PoW.)
        if not self.hash:
            self.hash = self.compute_hash()

    def _content(self) -> dict:
        """Everything that goes INTO the hash — i.e. everything except the hash itself."""
        return {
            "version": self.version,
            "index": self.index,
            "timestamp": self.timestamp,
            "records": self.records,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }

    def compute_hash(self) -> str:
        """Return the hash of the block's CURRENT content.

        Pure function — never changes the stored `hash`. Validation relies
        on this: re-compute and compare against what was stored.
        """
        return hash_fields(self._content())

    def mine(self, difficulty_prefix: str = DIFFICULTY_PREFIX) -> str:
        """Light proof-of-work: try nonces until the hash starts with the prefix.

        Real chains run the exact same puzzle, just much harder.
        The found nonce is the "proof" that work was done; it is stored
        so anyone can verify it in one hash.
        """
        self.nonce = 0
        while True:
            candidate = self.compute_hash()
            if candidate.startswith(difficulty_prefix):
                self.hash = candidate
                return candidate
            self.nonce += 1

    def to_dict(self) -> dict:
        """Full block as a dict (content + hash) — for JSON APIs later."""
        return {**self._content(), "hash": self.hash}
