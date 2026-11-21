"""GitChain — blockchain state git repo me, blocks GitHub Actions se mine hote hain.

Flow (GitHub Actions workflow har 30 min me):
  1. chain-state.json load karo (na ho to fresh genesis)
  2. naya heartbeat block mine karo (PoW — difficulty "0000")
  3. chain-state.json wapas save karo → workflow commit karke push karega

Isse tumhari chain LIVE rehti hai — bina laptop, bina server, ₹0 me.
(Honest flag: ye GitHub-hosted demo chain hai — real trustless node Orbit L2 me aayega.)
"""

import json
import time
from pathlib import Path

from certchain.core.blockchain import Blockchain

STATE_FILE = Path(__file__).parent.parent / "chain-state.json"


def load_chain() -> Blockchain:
    """chain-state.json se chain rebuild karo (ya fresh genesis banao)."""
    if STATE_FILE.exists():
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return Blockchain.from_dicts(data["blocks"])
    return Blockchain()


def save_chain(chain: Blockchain) -> None:
    blocks = [b.to_dict() for b in chain.blocks]
    STATE_FILE.write_text(
        json.dumps({"blocks": blocks, "length": len(blocks)}, indent=2),
        encoding="utf-8",
    )


def mine_heartbeat() -> None:
    """Ek heartbeat block mine karo — chain ka 'pulse'."""
    chain = load_chain()
    n = len(chain.blocks)
    stamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    record = f"CHAIN-HEARTBEAT #{n} | {stamp}"
    chain.add_block([record])

    ok, reason = chain.is_valid()
    if not ok:
        raise RuntimeError(f"mined chain invalid hai: {reason}")

    save_chain(chain)
    block = chain.blocks[-1]
    print(f"⛏️ block {block.index} mined | hash={block.hash[:20]}... | nonce={block.nonce}")
    print(f"chain length: {len(chain.blocks)} | valid: {ok}")


if __name__ == "__main__":
    mine_heartbeat()
