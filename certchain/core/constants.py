"""Genesis-level constants — immutable once the chain goes live."""

# Block format version — bump ONLY via coordinated upgrade when block structure changes
BLOCK_VERSION = 1

# Light proof-of-work: a mined block's hash must start with this prefix
# (4 zero hex chars = 1 in 65,536 chance per try — a few 100ms per block on a laptop)
DIFFICULTY_PREFIX = "0000"

# Genesis block links to "nothing" via 64 zeros
GENESIS_PREVIOUS_HASH = "0" * 64

# Coin spec (CHAIN-COIN-SPEC.md) — fixed forever, code-locked
TOTAL_SUPPLY = 10_000_000  # 1 crore — no one can mint beyond this

GENESIS_MESSAGE = "GENESIS: CertChain — SATYA, total supply 1 crore (10,000,000)"

# Genesis timestamp FIXED — har node ka genesis block EXACTLY same banega
# (same content → same hash). Yahi cheez nodes ko sync ke laayak banati hai.
# Genesis-level value: live chain me ise change karna = nayi chain.
GENESIS_TIMESTAMP = 0.0
