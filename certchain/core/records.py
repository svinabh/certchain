"""SignedRecord — a transaction signed by its author.

Phase 1 tak block kisi bhi data ko accept karta tha. Phase 2 ke baad har
record apne author ki signature ke saath aata hai — aur chain sirf un
records ko aage badhata hai jinki signature sahi hai.

RECORD_VERSION rakha gaya hai taaki future me record ke naye fields add
karna ho to purane records waise ke waise valid rahen (upgradability rule).
"""

from dataclasses import dataclass
from typing import Optional

from .crypto import canonical_json, sha256_hex
from .wallet import ADDRESS_HEX_LENGTH, Wallet

RECORD_VERSION = 1


@dataclass
class SignedRecord:
    record_type: str      # "ISSUE", "VERIFY", ... — naye types version bump ke saath add honge
    cert_id: str
    data: str
    timestamp: float
    signer: str           # author ka address — CLAIMED identity
    signature: str = ""
    public_key: str = ""  # signature verify karne ke liye — PROVED identity
    version: int = RECORD_VERSION

    def signing_payload(self) -> str:
        """Exactly the string whose signature is stored — nothing more, nothing less."""
        return canonical_json({
            "version": self.version,
            "record_type": self.record_type,
            "cert_id": self.cert_id,
            "data": self.data,
            "timestamp": self.timestamp,
            "signer": self.signer,
        })

    def sign(self, wallet: Wallet) -> None:
        """Attach the author's public key and signature.

        NOTE: `signer` ko yahan overwrite nahi karte — jo address record
        MEIN likha hai wahi claim hota hai. Agar banda kisi aur ke naam pe
        apni key se sign kare, to verification_failure() usse pakad lega.
        """
        self.public_key = wallet.public_key_hex
        self.signature = wallet.sign(self.signing_payload())

    def verify(self) -> bool:
        return self.verification_failure() is None

    def verification_failure(self) -> Optional[str]:
        """Return WHY this record fails verification, or None if it is valid.

        Two separate checks:
        1. impersonation — kya signer address sach me is public key ka hai?
        2. tampering — kya signature signing_payload ka exact match hai?
        """
        if not self.signature or not self.public_key:
            return "missing signature"
        derived = sha256_hex(self.public_key)[:ADDRESS_HEX_LENGTH]
        if derived != self.signer:
            return "signer address does not match public key — impersonation"
        if not Wallet.verify(self.signing_payload(), self.signature, self.public_key):
            return "signature does not match payload — record was changed after signing"
        return None

    def to_dict(self) -> dict:
        """Block ke records me iske form me store hota hai (block hashing JSON use karta hai)."""
        return {
            "version": self.version,
            "record_type": self.record_type,
            "cert_id": self.cert_id,
            "data": self.data,
            "timestamp": self.timestamp,
            "signer": self.signer,
            "public_key": self.public_key,
            "signature": self.signature,
        }
