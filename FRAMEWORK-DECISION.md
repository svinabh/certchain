# CertChain — Framework Decision (Phase 7)

> Decision date: 2026-11-17 · Status: **DECIDED** ✅
> Standing rule applied: **quality ≥ best of BTC / ETH / SOL / TRX in EVERY segment.**

## The Three Candidates (researched Nov 2026)

| | **Arbitrum Orbit** ⭐ | **OP Stack** | **Cosmos SDK (+ EVM)** |
|---|---|---|---|
| Chain type | L2 rollup (Ethereum-secured) | L2 rollup (Ethereum-secured) | L1 app-chain (own validators) |
| Our coin as gas token | ✅ **Officially supported** (ERC-20, Rollup mode) | ⚠️ Supported but **experimental** in specs | ✅ Native (perfect sovereignty) |
| Security inheritance | ✅ Inherits **Ethereum L1** | ✅ Inherits Ethereum L1 | ❌ Own validator set — 3-5 validators = weaker than ETH |
| EVM ecosystem | ✅ Full EVM (Solidity, MetaMask, ethers) | ✅ Full EVM | ⚠️ Cosmos EVM module — production use (Ondo, Mantra) BUT **$5.7M exploit in 2026** across 6 chains with patch lag |
| Deployment on Sepolia | ✅ Chain SDK, free | ✅ op-deployer, free | ✅ Free |
| Permissionless | ✅ Arbitrum Expansion Program | ✅ MIT-licensed stack | ✅ Apache 2.0 |
| Ops complexity | 1 chain process set + token bridge | 4 processes (geth/node/batcher/proposer) | Full validator network to bootstrap |
| Track record | Arbitrum One + dozens of Orbit chains | Base, OP Mainnet, many chains | 200+ app-chains |

## Scored Against the Quality Bar

| Segment | Bar (best of BTC/ETH/SOL/TRX) | Arbitrum Orbit L2 | Cosmos app-chain |
|---|---|---|---|
| **Security** | ETH (decentralization, trust) | ✅ **inherits Ethereum L1** | ❌ 3-5 validators < ETH — fails bar |
| **Ecosystem/EVM** | ETH | ✅ full EVM day one | ⚠️ EVM module exists, but $5.7M exploit history |
| **Speed/UX** | SOL (instant feel) | ⚠️ sequencer confirms ~instant; L1 finality slower — **FLAGGED below SOL bar on finality** | ✅ instant finality (but weaker security) |
| **Cheap payments** | TRX (near-zero transfers) | ✅ rollup fees are tiny | ✅ cheap |
| **Coin sovereignty** | BTC (fixed supply, own chain) | ✅ CGT officially supported | ✅ perfect |

## ✅ DECISION: **Arbitrum Orbit L2 (Rollup mode, custom gas token = our coin)**

### Why (in one line each)
1. **Security ≥ ETH is literally our bar** — only an Ethereum-secured rollup gives a small team Ethereum-grade security on day one. A 3-validator Cosmos chain cannot.
2. **Coin sovereignty is still ours** — Orbit officially supports ERC-20 gas tokens (Rollup mode): our 1-crore coin becomes the chain's gas, natively bridged at deploy.
3. **EVM = adoption cheat code** — Solidity + MetaMask + existing tools, instant.
4. **Cosmos EVM's 2026 exploit history** ($5.7M, 6 chains, patch lag) fails our security bar — ruled out as primary.

### ⚠️ Honest flags (quality-bar rule: never hide)
- **Finality vs SOL:** L2 data finality is slower than Solana's instant finality. Mitigation: sequencer soft-confirmations give instant *feel* (standard Arbitrum UX); flagged as below-SOL on pure finality until fast-finality options mature.
- **CGT prerequisites:** our coin must exist as a standard ERC-20 on the parent chain (Sepolia first), natively bridged at deployment.
- **Sequencer centralization at launch:** single sequencer initially — decentralization roadmap required before mainnet (Level 4).

### Fallback routes (if Orbit deployment blocks us)
1. OP Stack CGT (experimental) — same Ethereum security, different tooling
2. Cosmos SDK app-chain — accept validator-set tradeoff consciously, compensate with more validators + audits

## Phase 8 Plan (next)
1. Our coin as ERC-20 on Sepolia (1 crore fixed supply — mirrors CHAIN-COIN-SPEC.md)
2. Orbit chain deploy via Chain SDK with CGT = our coin
3. Explorer + MetaMask connection + faucet
4. Port the invisible-blockchain relayer to talk to the Orbit RPC

## Sources (researched 2026-11-17)
- [Arbitrum: deploy a chain (Chain SDK)](https://docs.arbitrum.io/launch-arbitrum-chain/deploy/deploy-chain)
- [Arbitrum: custom gas token (Rollup)](https://docs.arbitrum.io/launch-arbitrum-chain/chain-config/costs/custom-gas-token-rollup)
- [Arbitrum Foundation: creating new chains](https://www.arbitrum.foundation/new-arb-chains)
- [OP Stack: custom gas token guide](https://docs.optimism.io/chain-operators/guides/features/custom-gas-token-guide)
- [OP Stack spec: CGT (experimental)](https://specs.optimism.io/experimental/custom-gas-token.html)
- [Cosmos EVM docs](https://docs.cosmos.network/evm/latest/documentation/overview) · [cosmos/evm GitHub](https://github.com/cosmos/evm)
- [Cosmos EVM 2026 exploit report](https://shattered.io/cosmos-evm-vulnerability-six-chains-2026) · [rescana.com analysis](https://www.rescana.com/post/cosmos-evm-vulnerability-exploited-critical-flaw-leads-to-multi-chain-blockchain-attacks-and-5-7m-losses)
