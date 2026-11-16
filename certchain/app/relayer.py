"""Relayer — invisible blockchain ka DIL.

User sirf UPI se ₹ pay karta hai. Relayer:
1. Payment leta hai (bank se, receipt ke saath)
2. University ki taraf se record SIGN karta hai (keys server-side — real
   product me ye HSM/secure vault me hoti hain, yahan demo me in-memory)
3. Node ko HTTP pe submit + mine karata hai
4. Node ne reject kiya to paisa REFUND

User ko crypto ka "B" nahi dikhta — bas "Payment successful ✅" aur
"Certificate on-chain ✅". Wahi hamara differentiator hai.
"""

import json
import time
from typing import Dict

import requests

from certchain.core.crypto import canonical_json
from certchain.core.records import SignedRecord
from certchain.core.wallet import Wallet
from .upi import FakeUPIBank, UPIReceipt


class Relayer:
    FEE_ISSUE_RUPEES = 5  # issue fee ₹5 — VERIFY hamesha FREE (public good)

    def __init__(self, node_url: str, bank: FakeUPIBank, issuer_wallets: Dict[str, Wallet]):
        self.node_url = node_url.rstrip("/")
        self.bank = bank
        self.issuer_wallets = issuer_wallets

    def pay_and_issue(self, user_account: str, university: str, cert_id: str,
                      holder: str, course: str) -> dict:
        """Poori invisible flow: pay → sign → submit → mine → (refund on failure)."""
        # 0) university authorized hai? (payment se PEHLE check — galat naam pe paisa na kata)
        wallet = self.issuer_wallets.get(university)
        if wallet is None:
            return {"status": "rejected",
                    "reason": f"university authorized nahi hai: {university}"}

        # 1) UPI payment
        receipt, reason = self.bank.pay(user_account, self.FEE_ISSUE_RUPEES)
        if receipt is None:
            return {"status": "rejected", "reason": reason}

        # 2) university ki taraf se sign
        data = canonical_json({"holder": holder, "course": course, "university": university})
        record = SignedRecord(
            record_type="ISSUE", cert_id=cert_id, data=data,
            timestamp=time.time(), signer=wallet.address,
        )
        record.sign(wallet)

        # 3) node ko submit — reject hua to refund
        resp = requests.post(f"{self.node_url}/transactions/new",
                             json=record.to_dict(), timeout=5)
        if resp.status_code != 201:
            self.bank.refund(receipt)
            return {"status": "rejected",
                    "reason": f"node ne record reject kiya: {resp.json().get('error')}",
                    "refunded": True}

        # 4) mine — fail hua to refund
        resp = requests.post(f"{self.node_url}/mine", timeout=30)
        if resp.status_code != 201:
            self.bank.refund(receipt)
            return {"status": "rejected", "reason": "mining fail — paisa refund ho gaya",
                    "refunded": True}

        mined = resp.json()
        return {
            "status": "issued",
            "cert_id": cert_id,
            "upi_txn_id": receipt.upi_txn_id,
            "fee_rupees": self.FEE_ISSUE_RUPEES,
            "block_index": mined["index"],
            "block_hash": mined["hash"],
        }

    def verify(self, cert_id: str) -> dict:
        """FREE verification — koi payment nahi. Chain se sach dhundho,
        signature dobara verify karo, phir details dikhao."""
        resp = requests.get(f"{self.node_url}/chain", timeout=5)
        chain = resp.json().get("chain", [])

        for block in chain:
            for record in block["records"]:
                if isinstance(record, dict) and record.get("cert_id") == cert_id:
                    parsed = SignedRecord(**record)
                    failure = parsed.verification_failure()
                    if failure:
                        return {"verified": False, "cert_id": cert_id, "reason": failure}
                    details = json.loads(parsed.data)
                    return {
                        "verified": True,
                        "cert_id": cert_id,
                        "holder": details["holder"],
                        "course": details["course"],
                        "university": details["university"],
                        "issued_by": parsed.signer[:16] + "...",
                        "block_index": block["index"],
                        "block_hash": block["hash"],
                        "fee": "₹0 (verification free hai)",
                    }
        return {"verified": False, "cert_id": cert_id,
                "reason": "certificate chain pe nahi mila"}
