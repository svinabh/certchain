"""Wallet — key pair, address, signing (Ed25519 via PyNaCl).

Think of it like UPI:
- private key  = PIN (kabhi kisi ko nahi dete, sirf sign karne ke kaam aata hai)
- public key   = account number (duniya ko dikhta hai)
- address      = account number ka chhota fingerprint (kaun bhej raha hai, wo dikhane ke liye)

Signature verify karne ke liye private key ki zaroorat NAHI hoti —
public key se hi koi bhi check kar sakta hai. Yahi asymmetric magic hai.
"""

import hashlib
from typing import Optional

from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey, VerifyKey

# Address = first 40 hex chars (20 bytes) of SHA-256(public key) — ETH-style short identity
ADDRESS_HEX_LENGTH = 40


def address_from_public_key(public_key_hex: str) -> str:
    """Derive the address that belongs to a public key (deterministic)."""
    return hashlib.sha256(public_key_hex.encode("utf-8")).hexdigest()[:ADDRESS_HEX_LENGTH]


class Wallet:
    def __init__(self, signing_key: SigningKey):
        self._signing_key = signing_key
        self._verify_key: VerifyKey = signing_key.verify_key

    @classmethod
    def generate(cls) -> "Wallet":
        """Brand-new wallet — cryptographically random key pair."""
        return cls(SigningKey.generate())

    @property
    def public_key_hex(self) -> str:
        return self._verify_key.encode().hex()

    @property
    def address(self) -> str:
        return address_from_public_key(self.public_key_hex)

    def sign(self, message: str) -> str:
        """Sign a UTF-8 message with the PRIVATE key; returns hex signature."""
        signed = self._signing_key.sign(message.encode("utf-8"))
        return signed.signature.hex()

    @staticmethod
    def verify(message: str, signature_hex: str, public_key_hex: str) -> bool:
        """Verify a signature with only the PUBLIC key — no private key needed.

        Returns False (instead of raising) on any mismatch — callers just
        want a yes/no answer.
        """
        try:
            verify_key = VerifyKey(bytes.fromhex(public_key_hex))
            verify_key.verify(message.encode("utf-8"), bytes.fromhex(signature_hex))
            return True
        except (BadSignatureError, ValueError):
            return False
