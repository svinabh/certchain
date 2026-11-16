# CertChain — Project Plan

> A free-to-build blockchain demo where certificates (degrees, IDs, documents)
> get verified on-chain — and the user never sees any crypto.
> ("Invisible Blockchain": UPI in front, blockchain behind the scenes.)

## Why this project

- **One specific problem:** Fake certificates are everywhere; verification is slow and manual.
- **Our differentiator:** Instant verification + Hindi-friendly UI + zero crypto knowledge needed.
- **Constraint honored:** 100% free to build and run (laptop + GitHub only).

## The Core Idea (Gas Abstraction / Invisible Blockchain)

```
1. University issues a certificate  → relayer writes cert_hash on-chain
2. Student pays ₹ via UPI (simulated in demo) → record gets anchored
3. Employer verifies → public API, free, instant ✅/❌
```

- Users never hold tokens → no wallet, no gas, no seed phrases.
- Only the **hash** of a certificate goes on-chain (privacy), full document stays off-chain.

## Goals vs Non-Goals

| Goals ✅ | Non-Goals (for now) ❌ |
|---|---|
| Learn real blockchain concepts (hashing, signatures, consensus, P2P) | Real cryptocurrency/token |
| Runs free on localhost, code lives on GitHub | Real UPI gateway integration (we simulate it) |
| Portfolio-ready repo with tests + README | Production security audits |

## Phases

### Phase 1 — Blockchain Core (single node) — ~2-3 days
- `Block`: index, timestamp, records[], previous_hash, nonce, hash
- `Blockchain`: genesis block, add_block, is_valid (re-hash everything)
- Light proof-of-work: hash must start with `0000` (adjustable difficulty)
- **Demo moment:** edit one block → every block after it becomes invalid

### Phase 2 — Wallets & Signed Transactions — ~2 days
- Generate key pairs (Ed25519 or ECDSA), sign records, verify signatures
- Record shape: `{type: ISSUE|VERIFY, cert_id, cert_hash, signer, timestamp, signature}`
- Invalid signature → transaction rejected (just like real chains)

### Phase 3 — P2P Network (3 nodes) — ~3-4 days
- Each node = Flask/FastAPI server: `/chain`, `/mine`, `/transactions/new`, `/nodes/register`, `/nodes/resolve`
- Consensus: longest valid chain wins
- **Demo moment:** tx on Node A → mine → Nodes B & C auto-sync

### Phase 4 — CertChain App Layer — ~3 days
- Relayer endpoints: `/issue` (university admin), `/verify/<cert_id>`
- Fake UPI: demo balance wallet + `/pay` endpoint (₹ simulation)
- Relayer pays gas, user just sees "Payment successful ✅"

### Phase 5 — UI + Explorer — ~2-3 days
- One HTML/JS page with 3 tabs:
  1. **Issue** — university form
  2. **Verify** — enter cert ID → ✅/❌ + link to the block
  3. **Explorer** — browse blocks and records
- Hindi + English labels (our differentiator!)

### Phase 6 — GitHub Polish — ~1 day
- README with screenshots + setup guide, MIT license
- GitHub Actions: run pytest automatically on every push
- Public repo → portfolio piece 🎯

## Data Models

```json
// Record (goes inside a block)
{
  "type": "ISSUE",
  "cert_id": "CERT-2026-00042",
  "cert_hash": "sha256(certificate file/json)",
  "signer": "university_public_key",
  "timestamp": 1737000000,
  "signature": "..."
}

// Block
{
  "index": 1,
  "timestamp": 1737000000,
  "records": [ ...records... ],
  "previous_hash": "000a3f...",
  "nonce": 2718,
  "hash": "000c81..."
}
```

## Tech Stack (recommended — all free)

| Part | Choice | Alternative |
|---|---|---|
| Language | Python 3.11+ | Node.js (if JS preferred) |
| API server | Flask | FastAPI / Express |
| Hashing | `hashlib` (built-in) | — |
| Signatures | `ecdsa` or `PyNaCl` lib | `elliptic` (JS) |
| Tests | pytest | Jest |
| CI | GitHub Actions | — |
| Hosting (later) | localhost → Render/HF Spaces free tier | Oracle Cloud free tier |

## Architecture

```
[University Admin]                          [Employer / Verifier]
      |  POST /issue                              |  GET /verify/<id>
      v                                           v
[ Fake UPI ₹ ] ---> [ Relayer Backend ] <----> [ Blockchain Nodes ]
  (simulated)         pays gas, signs tx        3x localhost nodes
                        |                        longest-chain consensus
                        v
                  [ Web UI / Explorer ]
```

## Regulations note (India, as of Nov 2026)

- **No token for users → VDA crypto rules (FIU-IND, 30% tax, 1% TDS) do not apply.**
- This is just a record-keeping app: normal business KYC + UPI merchant account is enough at real-launch time.
- If we ever launch a real token: FIU-IND registration, KYC, Travel Rule — take legal advice first.

## Future upgrades (real product stage)

1. Real UPI via payment gateway + registered ramp partner (e.g., Onramp.money API)
2. Deploy nodes on free cloud tiers for a live demo
3. Migrate to EVM-compatible or Cosmos/Substrate if scale demands
4. Token economics only after legal setup

## Success checklist

- [ ] Tampering a block breaks the chain (demonstrated)
- [ ] 3 nodes stay in sync without a central server
- [ ] A fake certificate gets rejected at verification
- [ ] A real (issued) certificate verifies in < 1 second
- [ ] GitHub Actions green ✅ on every push
- [ ] Non-tech friend can use the verify page without help
