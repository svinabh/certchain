"""Phase 1 demo: tampering karo — chain khud pakad legi.

Run:  .venv/bin/python -m certchain.tamper_demo
"""

from certchain.core.blockchain import Blockchain
from certchain.core.constants import TOTAL_SUPPLY


def banner(text: str) -> None:
    print("\n" + "=" * 64)
    print(text)
    print("=" * 64)


def main() -> None:
    banner(f"CertChain Phase 1 — total supply: {TOTAL_SUPPLY:,} coins (1 crore)")

    chain = Blockchain()

    banner("1) Certificates add kar rahe hain (har block mine hota hai)")
    chain.add_block(["Certificate: Rahul, B.Tech CSE, 2026 — ID CERT-2026-0001"])
    chain.add_block(["Certificate: Priya, B.Sc Physics, 2026 — ID CERT-2026-0002"])
    for block in chain.blocks:
        print(f"  Block {block.index} | nonce={block.nonce:>7} | hash={block.hash[:20]}...")

    banner("2) Fresh chain validate kar rahe hain")
    ok, reason = chain.is_valid()
    print(f"  Valid? {ok}" + (f" ({reason})" if reason else " — sab blocks theek ✅"))

    banner("3) Hacker attack: block 1 ka year 2026 → 2099 kar diya")
    chain.blocks[1].records = ["Certificate: Rahul, B.Tech CSE, 2099 — ID CERT-2026-0001"]

    ok, reason = chain.is_valid()
    print(f"  Valid? {ok}")
    print(f"  Reason: {reason}")
    if not ok:
        print("  ⛔ Tampering pakda gaya — ek character badla, poori chain tod gayi!")


if __name__ == "__main__":
    main()
