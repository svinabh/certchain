# CertChain — Chain & Coin Spec (FINAL)

> Decided 2026-11-17: Total supply = **1 crore (10,000,000 coins)** · Coin name = **SATYA ($SATYA)**

## Coin Basics

| Spec | Value |
|---|---|
| Name / Symbol | **SATYA ($SATYA)** — सत्य = "truth" (collision-checked 2026-11-17: koi established project nahi) |
| Type | Native coin (gas + staking + governance) |
| Total supply | **10,000,000 (1 crore)** — fixed, kabhi nahi badlega |
| Decimals | 18 (ETH standard — 0.0127 jaise chhote fractions valid hain) |
| Comparison | Bitcoin = 2.1 crore supply → hamari coin usse bhi scarce |

## Distribution (1 crore me se)

| Hisa | % | Coins |
|---|---|---|
| Staking rewards (10 saal me dheere-dhire) | 40% | 40,00,000 (40 lakh) |
| Community / ecosystem (grants, hackathons) | 20% | 20,00,000 (20 lakh) |
| Team (4-saal lock) | 15% | 15,00,000 (15 lakh) |
| Early supporters / partners | 15% | 15,00,000 (15 lakh) |
| Treasury (future fund) | 10% | 10,00,000 (10 lakh) |
| **Total** | 100% | **1,00,00,000** |

- **Genesis pe turant:** 60 lakh (community + team + supporters + treasury)
- **Emission se dheere-dhire:** 40 lakh (staking rewards, 10 saal me)

## Coins Banti Kaise Hain? (sirf 2 raaste)

1. **Genesis mint** — chain shuru hote hi 60 lakh ek saath create (on-chain record, sab dekh sakte hain)
2. **Block rewards** — har block pe naye coins validator ko (~40 lakh, 10 saal me)

Na mining (PoW nahi hai), na printing — supply code me fixed hai, **koi bhi (tum khud bhi) zyada nahi bana sakte**. Yahi blockchain ka trust hai.

## Emission Math (1 crore hisaab se)

```
40 lakh coins ÷ 10 saal = 4 lakh coins/saal

1 sec block time:  31.5M blocks/saal → ~0.0127 coins/block
5 sec block time:  ~6.3M blocks/saal → ~0.063 coins/block
```

## Staking Economics

```
Agar supply ka 50% (50 lakh) stake hua:
  APY = 4,00,000 ÷ 50,00,000 = 8% / saal
 jitna zyada stake, utna kam APY (auto-balance)
```

**Validator ka business case (100 validators, coin = ₹100 maan lo):**
```
Per validator: 4,00,000 ÷ 100 = 4,000 coins/saal = ₹4,00,000/saal
Server cost:   ~₹25,000-30,000/saal
Profit:        ~₹3.7 lakh/saal  → isliye log validator banna chahenge 🔥
```

## Deflationary Touch

- Har transaction ka **base fee BURN** hota hai (EIP-1559 style)
- Zyada usage → zyada burn → supply dheere-dhire ghat ti hai
- Emission (naye coins) < burn (high usage) → net deflationary possible

## Immutable Rules (genesis me final, kabhi nahi badlenge)

- [ ] Supply = 1 crore, code-locked
- [ ] Decimals = 18
- [ ] Distribution % genesis me recorded
- [ ] Block format final

## TODO

- [x] Coin ka naam + symbol: **SATYA ($SATYA)** ✅ — सत्यमेव जयते; har verified certificate = satya ka jay. Collision-check done (CoinGecko: koi established SATYA project nahi; SEAL reject hua — already taken). Trademark/domain check Level 3 pe lawyer ke saath.
- [ ] Genesis file me ye numbers config (Phase 8: SATYA ERC-20, 1 crore fixed supply, Sepolia → Orbit CGT)
