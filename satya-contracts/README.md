# SATYA Contracts

SATYA ($SATYA) — CertChain ka native coin. **1 crore (10,000,000) fixed supply,
minted ONCE at deploy — no mint function exists.** Supply immutable by design.

## Setup (fresh machine)

```bash
curl -L https://foundry.paradigm.xyz | bash && foundryup
cd satya-contracts
forge install foundry-rs/forge-std            # lib/forge-std restore
git clone --depth 1 https://github.com/OpenZeppelin/openzeppelin-contracts.git lib/openzeppelin-contracts
cp .env.example .env   # (ya manually banao — keys kabhi commit mat karo)
forge build && forge test
```

## Deploy

```bash
# local test chain:
anvil --port 8545   # (alag terminal)
forge script script/Deploy.s.sol --rpc-url http://127.0.0.1:8545 --broadcast --private-key $KEY

# Sepolia:
forge script script/Deploy.s.sol --rpc-url $SEPOLIA_RPC_URL --broadcast --private-key $SEPOLIA_PRIVATE_KEY
```

## Genesis invariants (tests enforce)

- `name()` = SATYA · `symbol()` = SATYA · `decimals()` = 18
- `totalSupply()` = 10,000,000 × 10^18 — **forever**
- No mint function — supply can never grow
