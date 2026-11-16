# CertChain Whitepaper (v0.1 draft)

**CertChain — The Invisible Blockchain**
*Certificate verification and India-first payments, secured by Ethereum, powered by **SATYA** — a 1-crore native coin whose name means "truth" in Sanskrit (सत्यमेव जयते — truth alone triumphs).*

> Draft: 2026-11-17 · Phase 7 deliverable · Status: work-in-progress

---

## 1. Abstract

CertChain is an **Ethereum-secured Layer-2 blockchain** with a fixed-supply
native coin (1 crore, never inflatable), designed so that ordinary people
use it **without ever knowing it is a blockchain**. No wallets, no seed
phrases, no gas jargon — just UPI-style payments in front and cryptographic
truth behind.

Our first application: **tamper-proof certificate issuance and one-second
public verification** for universities, employers, and governments.

Our standing engineering rule, applied to every decision:

> **Quality bar:** CertChain must match or beat the best of Bitcoin,
> Ethereum, Solana, and Tron in every segment — security, decentralization,
> speed, cost, and user experience. Anything below the bar is flagged,
> never hidden.

---

## 2. The Problem

**Fake credentials.** Employers spend weeks verifying degrees; forged
certificates circulate freely; centralized verification databases are
single points of failure and trust.

**Crypto's UX wall.** Existing chains demand seed phrases, gas tokens, and
technical literacy — billions of people are excluded. In India, UPI proved
that payment adoption comes from *removing* friction, not adding it.

**The gap.** No chain today combines Ethereum-grade security, sub-cent
fees, a fixed-scarcity native coin, and a fully invisible user experience.

---

## 3. The Quality Bar

Every segment, benchmarked against the best of the four major chains:

| Segment | Benchmark | CertChain approach | Status |
|---|---|---|---|
| Security / trust | **Bitcoin, Ethereum** | Ethereum-secured L2 (inherits L1 security) | ✅ matches bar |
| Decentralization | **Ethereum** | Sequencer decentralization roadmap before mainnet | ⏳ in progress |
| Speed / UX feel | **Solana** | ~instant sequencer confirmations | ⚠️ flagged: pure finality below SOL; UX-feel matched |
| Cheap payments | **Tron** | Rollup fees: fractions of a cent | ✅ matches bar |
| Scarce, honest money | **Bitcoin** | 1 crore fixed supply, code-locked, base-fee burn | ✅ matches bar |
| User experience | *Nobody does this well* | Invisible design: no wallet, no crypto vocabulary | 🏆 our edge |

Rule: if any decision ships below the bar, it is documented and flagged in
design reviews — never silent.

---

## 4. Solution: The Invisible Blockchain

Three layers, one experience:

```
┌─────────────────────────────────────────────────┐
│  EXPERIENCE LAYER (what users see)              │
│  UPI-style ₹ payments · web UI in 6 languages   │
│  "Payment successful ✅" "Verified ✅"           │
├─────────────────────────────────────────────────┤
│  RELAYER LAYER (what runs for users)            │
│  fee collection · transaction signing · gas     │
│  sponsorship · submission · refunds on failure  │
├─────────────────────────────────────────────────┤
│  TRUTH LAYER (what nobody needs to see)         │
│  Arbitrum Orbit L2 · custom gas token ·         │
│  Ethereum-secured finality · public verification│
└─────────────────────────────────────────────────┘
```

Flow (certificate issuance):
1. University issues the certificate in the web UI.
2. Student pays ₹5 via the UPI simulation (real gateway at production).
3. The relayer signs the record with the university's server-side key,
   submits it, pays the gas, and mines it.
4. Anyone on earth verifies it free, forever, in one second.
5. If any step fails, the payment **refunds automatically**.

The user's entire mental model: *"I paid ₹5 and now it's true forever."*

---

## 5. Technical Design

**Chain.** Arbitrum Orbit rollup (Rollup mode), deployed permissionlessly via
the Arbitrum Expansion Program. Chosen over OP Stack (custom gas token still
experimental) and Cosmos SDK (own-validator security + a 2026 $5.7M EVM
exploit across 6 chains fails our security bar). See FRAMEWORK-DECISION.md.

**Gas token.** Our coin is an ERC-20 on the parent chain, **natively bridged
at deployment** as the chain's gas token — official Orbit feature. Users pay
fees in the coin without knowing it; the relayer abstracts even that.

**Coin — SATYA.** Sanskrit for *truth*; every verified certificate on CertChain is a
record of it. Total supply **1 crore (10,000,000), fixed forever**: 40% staking
emission over ~10 years, 20% community, 15% team (4-year lock), 15% early
supporters, 10% treasury. Base-fee burn adds deflationary pressure under
usage. Distribution and supply are genesis-immutable.

**Verification.** Certificate hashes (not documents) live on-chain; documents
stay off-chain. `verify(cert_id)` re-checks signatures and returns holder,
issuer, block, and hash — free, public, permanent.

**Relayer network.** Fee-sponsored meta-transactions; multiple relayers at
production; keys in HSM/secure vaults; automatic refunds on submission
failure.

---

## 6. Security Model

- **Inheritance, not aspiration:** L2 data availability and fraud/validity
  guarantees come from Ethereum — the strongest security budget available.
- **Adversarial testnet:** we attack our own chain (reorgs, double-spends,
  spam, signature forgery) for months before any real value flows.
- **Bug bounty:** public program; the 2026 Cosmos EVM incident ($5.7M across
  six chains) is our cautionary tale for patch responsiveness.
- **Refund guarantee:** user funds revert on any pipeline failure.
- **Flagged weaknesses:** sequencer centralization at launch (roadmap:
  shared/decentralized sequencing); pure finality below Solana's (compensated
  by instant soft-confirmations).

---

## 7. Governance & Upgrades

- Genesis constants (supply, distribution, block format) are **immutable**.
- Everything else upgrades through: proposal → testnet → validator/DAO vote →
  activation height. No silent changes.
- Treasury (10%) funds grants, audits, and ecosystem growth, controlled by
  multi-sig until on-chain governance matures.

---

## 8. India-First Strategy

- **Vernacular UI** (6 languages at launch, JSON-extensible to any language,
  RTL supported) — no major chain ships this.
- **UPI-first payments** — the 400M+ user habit, not a new one to create.
- **Niche before world:** certificates → documents → land records →
  micro-payments. One wedge, done perfectly.
- **Distribution moat:** college hackathons, university partnerships,
  Hindi developer docs. Technology can be copied; distribution cannot.

---

## 9. Roadmap

| Level | Outcome | Cost |
|---|---|---|
| 0 ✅ | Working demo: chain, wallets, network, invisible app, UI, CI | ₹0 |
| 1 (current) | Orbit testnet on Sepolia, coin-as-gas, SDK, docs | ₹0 |
| 2 | Adversarial hardening, bounty, 90 days clean | ₹0 |
| 3 | Legal entity, FIU registration, KYC, ramp partner | 💰 |
| 4 | Mainnet genesis, killer app scale, validators 5→100 | 💰 |

---

## 10. Conclusion

Blockchains won mass trust but failed mass usability. CertChain inherits
Ethereum's security, matches the cost of the cheapest chains, holds
Bitcoin-grade scarcity in a 1-crore coin — and hides all of it behind an
experience simpler than UPI.

**The best blockchain is the one nobody notices.**

---

*References: FRAMEWORK-DECISION.md (framework research, Nov 2026) ·
CHAIN-COIN-SPEC.md (coin design) · ROADMAP.md (12-phase plan)*
