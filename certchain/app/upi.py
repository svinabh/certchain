"""FakeUPIBank — UPI ka simulation (demo ke liye, ₹0 cost).

Asli product me is jagah Razorpay/Cashfree jaisa gateway aayega. Interface
wahi rakha hai: pay() receipt deta hai, fail hone par saaf reason. Relayer
isi receipt ke sahare "invisible" payment flow banata hai — aur chain ne
transaction reject ki to paisa REFUND hota hai (real-world behaviour).
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class UPIReceipt:
    upi_txn_id: str
    from_account: str
    to_account: str
    amount_rupees: int
    timestamp: float

    def to_dict(self) -> dict:
        return {
            "upi_txn_id": self.upi_txn_id,
            "from_account": self.from_account,
            "to_account": self.to_account,
            "amount_rupees": self.amount_rupees,
            "timestamp": self.timestamp,
        }


class FakeUPIBank:
    """In-memory UPI simulation. Naya account = ₹{default} demo balance."""

    def __init__(self, default_balance_rupees: int = 500,
                 bank_account: str = "certchain-fees@upi"):
        self.default_balance_rupees = default_balance_rupees
        self.bank_account = bank_account
        self._accounts: Dict[str, int] = {}
        self.receipts: List[UPIReceipt] = []
        self._txn_counter = 0

    def create_account(self, account_id: str) -> int:
        """Naya demo account (already exist karta ho to existing balance)."""
        if account_id not in self._accounts:
            self._accounts[account_id] = self.default_balance_rupees
        return self._accounts[account_id]

    def balance(self, account_id: str) -> Optional[int]:
        return self._accounts.get(account_id)

    def pay(self, from_account: str, amount_rupees: int) -> Tuple[Optional[UPIReceipt], Optional[str]]:
        """UPI payment: user → bank fees account. (receipt, None) ya (None, reason)."""
        if from_account not in self._accounts:
            return None, f"account nahi mila: {from_account} (pehle /accounts se banao)"
        if amount_rupees <= 0:
            return None, "amount 0 se bada hona chahiye"
        if self._accounts[from_account] < amount_rupees:
            return None, (f"insufficient balance — ₹{self._accounts[from_account]} hai, "
                          f"₹{amount_rupees} chahiye")

        self._accounts[from_account] -= amount_rupees
        self._accounts[self.bank_account] = self._accounts.get(self.bank_account, 0) + amount_rupees
        self._txn_counter += 1
        receipt = UPIReceipt(
            upi_txn_id=f"UPI{int(time.time())}{self._txn_counter:04d}",
            from_account=from_account,
            to_account=self.bank_account,
            amount_rupees=amount_rupees,
            timestamp=time.time(),
        )
        self.receipts.append(receipt)
        return receipt, None

    def refund(self, receipt: UPIReceipt) -> None:
        """Chain ne record reject kiya to paisa wapas — trust yahi banata hai."""
        self._accounts[self.bank_account] -= receipt.amount_rupees
        self._accounts[receipt.from_account] = (
            self._accounts.get(receipt.from_account, 0) + receipt.amount_rupees
        )
