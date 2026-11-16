"""Phase 2 demo: hacker nakli certificate issue karta hai — chain reject karti hai.

Run:  .venv/bin/python -m certchain.forged_cert_demo
"""

import time

from certchain.core.blockchain import Blockchain
from certchain.core.records import SignedRecord
from certchain.core.wallet import Wallet


def banner(text: str) -> None:
    print("\n" + "=" * 64)
    print(text)
    print("=" * 64)


def main() -> None:
    university = Wallet.generate()
    hacker = Wallet.generate()

    banner("CertChain Phase 2 — wallets & signatures")
    print(f"  University address : {university.address[:16]}...")
    print(f"  Hacker address     : {hacker.address[:16]}...")

    chain = Blockchain()

    banner("1) University asli certificate issue karti hai")
    block, failure = chain.add_signed_record(
        university, "ISSUE", "CERT-2026-0001", "Rahul, B.Tech CSE, 2026"
    )
    print(f"  Block {block.index} mined ✅ | hash={block.hash[:20]}...")
    print(f"  Signature verify: {chain.is_valid()[0]} — record accepted")

    banner("2) Hacker ATTACK: university ke naam pe, apni key se sign karta hai")
    forged = SignedRecord(
        record_type="ISSUE", cert_id="CERT-FAKE-001", data="Hacker, PhD, 2026",
        timestamp=time.time(), signer=university.address,
    )
    forged.sign(hacker)
    failure = forged.verification_failure()
    print(f"  Verify: {forged.verify()}")
    print(f"  Reason: {failure}")
    print("  ⛔ Chain me ghusa hi nahi — impersonation pakda gaya!")

    banner("3) Hacker ATTACK-2: sahi certificate ka data signing ke BAAD badalta hai")
    record = SignedRecord(
        record_type="ISSUE", cert_id="CERT-2026-0002", data="Priya, B.Sc, 2026",
        timestamp=time.time(), signer=university.address,
    )
    record.sign(university)
    print(f"  Pehle verify: {record.verify()} ✅")
    record.data = "Priya, PhD, 2026"  # chupke se change
    failure = record.verification_failure()
    print(f"  Badle ke baad verify: {record.verify()}")
    print(f"  Reason: {failure}")
    print("  ⛔ Signature ab match nahi karta — tampering fail!")

    banner("4) Chain ab bhi poori tarah valid hai")
    ok, reason = chain.is_valid()
    print(f"  Valid? {ok}" + (f" ({reason})" if reason else " — hacker ka kuch bhi andar nahi ghusa ✅"))


if __name__ == "__main__":
    main()
