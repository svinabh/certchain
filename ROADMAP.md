# CertChain — Complete Roadmap (12 Phases)

> PLAN.md (6 phases) + MASTERPLAN.md (5 levels) ka merged view.
> Har phase ka rule: end me ek CHALTA HUA product hona chahiye.

```
LEVEL 0 (free demo)     → Phase 1-6   → ~2 hafte     → ₹0
LEVEL 1 (testnet)       → Phase 7-9   → 3-6 mahine   → ₹0
LEVEL 2 (security)      → Phase 10    → 2-4 mahine   → ₹0 (free path)
LEVEL 3 (coin+legal)    → Phase 11    → 2 mahine     → 💰
LEVEL 4 (mainnet)       → Phase 12    → ongoing      → 💰💰
```

---

## LEVEL 0 — Learning Demo (laptop + GitHub, free)

### Phase 1: Blockchain Core — ~2-3 din
- Kya banega: Block class, Blockchain class, SHA-256 hashing, chain linking,
  light PoW (hash starting with 0000), tamper validation
- End me demo: ek block badlo → poori chain reject ho jaati hai
- Sikhoge: hashing, immutability, consensus ka basic idea

### Phase 2: Wallets & Signatures — ~2 din
- Kya banega: key pair generation, transaction signing, signature verification
- End me demo: galat signature → transaction reject
- Sikhoge: asymmetric cryptography, ownership kaise prove hota hai

### Phase 3: P2P Network — ~3-4 din
- Kya banega: Flask node API, 3 nodes chalana, /nodes/register, chain sync,
  longest-valid-chain consensus
- End me demo: Node A pe transaction → mine → B aur C auto-sync
- Sikhoge: networking, decentralization, consensus conflicts

### Phase 4: App Layer (CertChain) — ~3 din
- Kya banega: /issue + /verify endpoints, fake UPI wallet, relayer (gas sponsor)
- End me demo: ₹ simulate karke certificate issue, verify turant ✅/❌
- Sikhoge: invisible blockchain / gas abstraction kaise kaam karta hai

### Phase 5: UI + Explorer — ~2-3 din
- Kya banega: web page (Issue form, Verify form, Block explorer) — Hindi + English
- End me demo: non-tech dost bina samjhaye page use kar le
- Sikhoge: chain ko user-friendly banana

### Phase 6: GitHub Polish — ~1 din
- Kya banega: README (screenshots ke saath), GitHub Actions CI, MIT license
- End me demo: public repo — har push pe tests green ✅
- Sikhoge: professional development workflow

**🏁 Level 0 complete = portfolio repo + har blockchain concept hands-on**

---

## LEVEL 1 — Real Protocol (testnet, free)

### Phase 7: Framework + Whitepaper — ~2-4 hafte
- Kya banega: OP Stack vs Cosmos SDK comparison spike, EVM route finalize,
  10-15 page whitepaper (problem, design, coin-lite)
- End me demo: whitepaper + "hello world" test chain khadi
- Decision point: L2 rollup (recommended) ya app-chain

### Phase 8: Chain on Testnet — ~1-2 mahine
- Kya banega: framework se chain deploy, explorer, JSON-RPC, MetaMask connect,
  faucet, validator setup
- End me demo: MetaMask se testnet chain me connect, transaction fire
- Sikhoge: real chain internals (tumhara Phase 1-3 ka knowledge yahan kaam aayega)

### Phase 9: SDK + Docs — ~1 mahina
- Kya banega: JS + Python SDK, docs site (GitHub Pages), Hindi tutorials shuru
- End me demo: koi aur developer tumhari chain pe app bana le
- Milestone: PEHLA OUTSIDE DEVELOPER 🎉

**🏁 Level 1 complete = live testnet + doosre devs use kar rahe hain**

---

## LEVEL 2 — Security Hardening

### Phase 10: Adversarial Testing — ~2-4 mahine
- Kya banega: khud apni chain todne ki koshish (reorg, double-spend, spam),
  fuzzing, bug bounty program (Immunefi), multi-sig treasury, upgrade runbook
- End me demo: 90 din testnet pe 0 critical bugs
- Yahi phase serious projects ko jokey projects se alag karta hai

**🏁 Level 2 complete = chain battle-tested**

---

## LEVEL 3 — Coin & Legal

### Phase 11: Tokenomics + Compliance — ~2 mahine
- Kya banega: coin economics final (1B supply, staking emission, distribution),
  entity (Pvt Ltd), FIU-IND registration, KYC pipeline, UPI ramp partner
  (Onramp.money type API), web3 lawyer
- End me demo: legal docs signed + tokenomics model + KYC'd test users
- Yahan se paisa lagta hai — isliye pehle Level 2 tak sab free

**🏁 Level 3 complete = legally ready to launch coin**

---

## LEVEL 4 — Mainnet + Ecosystem (ongoing)

### Phase 12: Mainnet Launch + Growth
- Kya banega: genesis launch (5 validators), killer app = invisible-blockchain
  certificate verification (UPI + Hindi UI), validators 5 → 25 → 100,
  grants program, college hackathons, second app (land records/documents)
- End me demo: real users, real certificates, real ₹ flow
- Success metrics: 25+ validators, 3+ apps, 1000+ certificates verified,
  10k+ monthly verify queries

**🏁 Level 4 = "Sabse badhiya in YOUR market" 🏆**

---

## Timeline (honest)

```
Month 0      1-2        3-6           9-12          12-18
  |-----------|----------|-------------|--------------|
  Level 0     Level 1    Level 2      Level 3       Level 4
  (2 hafte)   (testnet)  (security)   (coin+legal)  (mainnet+)
```

- ₹0 cost: Level 0-2 tak (poora learning + testnet + security)
- 💰 starts: Level 3 se (legal, audit, ecosystem)
- Full journey: 12-18 mahine (small team, honest estimate)

## Abhi kahan hain?
- [x] Phase 1 — Blockchain Core ✅ (2026-11-17)
- [x] Phase 2 — Wallets & Signatures ✅
- [x] Phase 3 — P2P Network (3 nodes + consensus) ✅
- [x] Phase 4 — Invisible Blockchain App (UPI + relayer + verify) ✅
- [x] Phase 5 — Web UI + Explorer + 6-language i18n ✅
- [x] Phase 6 — GitHub Actions CI + polish ✅

🎉 **LEVEL 0 COMPLETE** — 34 tests green, live web UI, portfolio repo on GitHub!

Next: **Level 1 → Phase 7** (framework decision + whitepaper) jab ready ho.
